# GitHub Actions 完成后间隔轮询调研

日期：2026-11-18
范围：GitHub Actions 定时调度、并发队列、完成事件、完成后延迟方案；仅使用 GitHub 官方文档和公开仓库源码。

## 结论

1. 当前工作流的 `7,37 * * * *` 是有效的半小时固定时刻计划，会在每小时的第 7、37 分钟触发。它避开了整点，但 GitHub 不保证按时启动：Actions 高负载时可能延迟，负载足够高时也可能丢弃排队的计划任务。因此不能靠改成另一个 cron 来保证每次都准时运行。
2. 当前工作流的并发组限制同组同时最多一个运行中的 run，默认还只保留一个 pending run。新的 run 到来时会取消并替换已有 pending run。`cancel-in-progress: false` 只表示不取消正在运行的 run，不代表保留所有后续轮询。`queue: max` 可保留最多 100 个 pending run，但长任务会积累旧轮询，随后连续补跑，不符合“任务结束后再等 30 分钟”的期望。
3. 通用 Actions 没有一个 cron 配置能表达“上一个 workflow 完成后，再等 30 分钟触发下一次”。`workflow_run: completed` 可以响应完成事件，但没有延迟参数；官方还限制 `workflow_run` 最多串联三层。
4. GitHub 原生组件可以拼出一个近似完成相对轮询的方案：用一个单独的完成处理 workflow 监听审查 workflow 的 `workflow_run: completed`，让它引用配置了 30 分钟 wait timer 的 environment；等待后用 `GITHUB_TOKEN` 调 `workflow_dispatch` 重新启动审查 workflow。等待时间不计入可计费运行时间，且 wait timer 在工作流任务派发后开始计时。`workflow_dispatch` 是 `GITHUB_TOKEN` 可以创建新 workflow run 的例外。此方案不会让审查任务在轮询间隔内占用 runner，但会留下等待中的 workflow/job（以及通常的 environment 部署记录）；仍受 GitHub 事件处理、任务调度和 runner 可用性的延迟影响，不能提供硬实时保证。
5. 抽样查看的公开仓库/官方示例采用的是错开分钟的固定 cron，并常提供手动触发或并发保护；没有在这些样例中发现普通 Actions workflow 实现“上次完成后再延迟”的通用做法。GitHub Agentic Workflows 有专门的 `cooldown` 配置，但它属于 Agentic Workflows 的编译器/运行模型，不是普通 Actions YAML 的 `on:` 触发器。

## GitHub 的固定 schedule 行为

`schedule` 使用 POSIX cron 表达墙上时钟时间，默认 UTC；最短间隔是五分钟。它以默认分支上的最新提交运行。官方明确提示：Actions 高负载时 schedule 可能延迟，尤其是整点开始时；负载足够高时，排队中的 schedule 任务可能被丢弃。官方建议把时间错开整点以降低延迟概率，但没有承诺精确触发或不丢失。

所以，当前配置中的 `7,37 * * * *` 本身没有 cron 语法问题，而且已经错开整点。它表达的是每小时 :07 和 :37 两个固定时刻，不是“本次处理结束后 30 分钟”。若某次审查耗时超过半小时，后续计划事件就可能与它重叠并进入并发组。

来源：[GitHub Actions schedule 事件](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)、[GitHub 官方关于定时运行延迟/丢弃的排查说明](https://docs.github.com/en/actions/how-tos/troubleshoot-workflows#scheduled-workflows-running-at-unexpected-times)。

### 本仓库实际运行记录

查询该工作流的公开 Actions runs API（筛选 `event=schedule`）时，返回了 20 次定时运行，时间从 2026-11-12 11:43 UTC 到 2026-11-17 23:56 UTC。相邻记录间隔约 4.0 到 14.6 小时；在这段约 132 小时的时间里，固定半小时 cron 理论上有约 264 个触发时刻。截图里中国时间 11 月 18 日 07:56 对应 API 最新记录 11 月 17 日 23:56 UTC。

这说明最近的实际运行频率远低于 YAML 表达的频率。但 runs API 只能展示已创建的 run，无法区分每个缺口是 GitHub schedule 延迟/丢弃、并发 pending 替换，还是其他未创建 run 的原因；不能仅凭这个历史断言是哪一个原因造成了全部缺口。API：[本仓库定时运行记录](https://api.github.com/repos/404notfoundf/node_watch/actions/workflows/watch-releases.yml/runs?event=schedule&per_page=100)。

## 并发组和 `queue: max`

在同一并发组中，GitHub 最多允许一个 run 正在运行。默认 `queue: single` 最多保留一个 pending run；更新的 run 进入同组时，旧 pending 会被取消并被新 pending 替换。`cancel-in-progress: false` 阻止取消正在运行的 run，但不改变 pending 的替换规则。

`queue: max` 可以把同组 pending 上限提高到 100。达到上限后新 run 会被取消。官方说明队列按 run 开始等待并发组的先后顺序处理。它的语义是“把触发的 run 排起来”，不是“等正在运行的任务结束 30 分钟后再生成一个新触发”。如果任务常常超过 30 分钟，队列会滞后；任务结束后可能立即连续运行积压的检查。

对照当前 [`.github/workflows/watch-releases.yml`](../../../.github/workflows/watch-releases.yml)：工作流级并发组 `watch-upstream-releases`、`cancel-in-progress: false` 与默认单 pending 配置相符。因此，只要已有 run 仍在运行，后续触发就可能进入 pending；再有新触发时，旧 pending 会被替换。这个队列行为与 schedule 的高负载延迟/丢弃是两个不同来源，单看 YAML 或 Actions 历史不能把所有缺失都归因于其中一个。

来源：[GitHub 官方并发控制文档](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)。

## 完成事件与延迟

`workflow_run` 的 `completed` activity type 可在指定 workflow 完成时触发另一个 workflow；它本身没有“完成后延迟 N 分钟”的字段。该事件的工作流文件必须存在于默认分支。官方也限制最多三层 `workflow_run` 链，因此不宜将它当作无限递归调度器。

一个官方原生等待组件是 deployment environment 的 **wait timer**：它在 job 被触发后延迟该 job，支持 1 到 43,200 分钟，等待时间不计入 billable time。对 GitHub Free、Pro、Team 计划，wait timer 仅对公开仓库可用；私有/内部仓库需要符合相应计划要求。environment 的保护规则通过后，job 才会被派发给 runner。这里的 wait timer 是 job 的保护/门控，不是通用的“完成事件定时器”。

REST API 的 `workflow_dispatch` endpoint 可启动配置了 `workflow_dispatch` 的 workflow；fine-grained token 需要仓库 `Actions: write` 权限。官方说明 `GITHUB_TOKEN` 执行的 `workflow_dispatch` 和 `repository_dispatch` 总会创建 workflow run，即不会像普通 token 触发的 push 等事件那样被递归触发保护拦截。

来源：[workflow_run 事件及三层限制](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#workflow_run)、[environment wait timer 规则和适用范围](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments#wait-timer)、[workflow dispatch REST API 与权限](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event)、[GITHUB_TOKEN 对 workflow_dispatch 的例外](https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs)。

### 可选的完成相对轮询拼法

```text
审查 workflow 完成
        ↓ workflow_run: completed
独立的 cooldown/dispatcher workflow
        ↓ environment wait timer = 30 分钟（runner 尚未执行该 job）
workflow_dispatch 审查 workflow（GITHUB_TOKEN，Actions: write）
```

这能把下一轮审查放在上一轮完成约 30 分钟后启动，而不是固定在墙钟 :07/:37。它是多个 GitHub 原语组合出的方案，不是 Actions 提供的单个“完成后延时”触发器。定时等待的计时起点是 cooldown job 被触发，不保证与前一个 run 的 `completed_at` 精确相差 30:00；`workflow_run` 事件投递、job 启动及 runner 调度都会带来额外延迟。还需要避免手动触发、cron 兜底和 dispatcher 同时形成重复轮询链。使用 environment wait timer 会使 dispatcher run/job 在等待期间保持等待状态；应为它使用独立 environment，避免给现有 Pages 发布环境加等待规则。

如果不希望 Actions 历史中保留等待中的 run，可以使用外部持久调度器：完成事件/webhook 记录下一次到期时间，到时调用 workflow dispatch API。这仍不能保证 GitHub runner 当时立刻可用；它只把“等待计时”移出 Actions runner，并避免占用一个 Actions run 等待。

## 公开仓库中看到的常见配置

以下仅是源码样本，不是整个 GitHub 上的统计结论：

- GitHub 官方维护的 [`actions/stale` README 示例](https://github.com/actions/stale/blob/main/README.md#basic) 使用每天 `01:30` 的固定 cron；多个配置示例仍沿用这个固定时刻。
- [`googleworkspace/cli` 的 stale workflow](https://github.com/googleworkspace/cli/blob/main/.github/workflows/stale.yml) 使用每天 `01:30` 的 cron，并保留 `workflow_dispatch` 手动入口。
- [`openclaw/openclaw` 的 stale workflow](https://github.com/openclaw/openclaw/blob/main/.github/workflows/stale.yml) 使用每天 `03:17` UTC 的固定 cron，并提供手动入口。

这些例子与 GitHub 的官方建议一致：使用固定 cron，错开常见整点，并视任务情况加入并发控制/手动运行。它们没有表达“任务结束后再等半小时”。

一个特殊例外是 [GitHub Agentic Workflows 的 `cooldown`](https://github.github.com/gh-aw/reference/triggers/#cooldown)：文档允许设置例如 `cooldown: 4h`，从最近一次启动过 `agent` job 的已完成 run 起算，并至少设置五分钟。它是面向 Agentic Workflows 的专用功能；不能把这个字段直接加到常规 `.yml` Actions workflow 中。

## 对本仓库的判断

- cron 配置不是写错；它已经每半小时触发并避开整点。
- 目前“任务耗时可超过 30 分钟，但下一轮还想在上次完成后再等 30 分钟”的需求与固定 cron 不同；把 cron 继续改成 `*/30`、换成其他分钟，或改用 `queue: max` 都无法表达这个语义。
- 若接受等待中的 dispatcher run，environment wait timer 加 `workflow_dispatch` 是纯 GitHub 原生、且不占用 runner 等待时间的候选方案。若更看重 Actions 历史中每个 run 都尽快结束，则使用外部调度器更合适。
- 任一方案都只能做到尽力调度，不能承诺严格半小时准点；GitHub 官方对 schedule 明确记录了延迟/丢弃，事件型方案也仍需等 GitHub 创建后续 run 并分配 runner。
