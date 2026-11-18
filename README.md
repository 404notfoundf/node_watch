# GitHub Release Watch

这个仓库用 GitHub Actions 按配置的频率检查公开 GitHub 仓库。发现新 Release 后，会比较相应 Release tag 之间的代码差异，调用配置的 AI 做静态审阅。每轮生成一份按币种和版本分段的完整报告；所有新 Release 都会发布网页、Markdown Artifact 并记录在汇总 Issue 中。只有达到严格重大事项门槛时，Issue 才会 @通知配置的用户：有代码证据支持的 P0/P1 或重点类别，或发行说明明确要求在硬分叉条件前升级，或 Breaking Changes 章节中有可逐字核实的具体影响声明。Pages 历史报告和已处理版本记录保存在独立的 `gh-pages` 分支中，超过 180 天的报告目录会在下次发布时从当前网站清理；版本去重记录不会随报告过期。分支的 Git 提交历史仍保留先前内容。报告不会提交到默认分支的 `reports/` 目录。

## 配置监控对象

将 [config/watch.example.yaml](config/watch.example.yaml) 复制为 `config/watch.yaml`，再替换币种、仓库、真实 Release tag、AI 服务地址和模型等示例值：

```yaml
ai:
  api_url: https://your-compatible-api.example/v1
  model: your-model
  diff_chunk_chars: 120000

coins:
  tari:
    repo: tari-project/tari
    running_version: v6.4.0
    network: mainnet
```

每个币种配置一个仓库，`repo` 使用 `owner/repository` 格式。`running_version` 必须是矿池当前实际运行、且已发布的 GitHub Release tag；脚本只分析比它新的 Release，并按版本顺序逐个比较差异。升级矿池节点后，请同步更新该值，后续报告会以新版本作为比较起点。`network` 填矿池实际运行的网络（例如 Tari 的 `mainnet`），用于让 AI 区分主网与测试/本地网络影响；不填写时，AI 不会假定受影响的是主网。主网节点不需要审查预发布版时，可设置 `include_prereleases: false`，跳过 GitHub 标记的预发布版及 tag 中的 pre、rc、test、testnet 等发布线。工作流只读取 `config/watch.yaml`，示例文件不会自动加载。

`review.mode` 同时作用于 GitHub Actions 和本地 Codex CLI。默认 `auto` 对预发布版和正式版使用相同的风险判断，并读取 Release 标题和正文：普通更新快速预检，只向 AI 发送发行说明、完整变更文件清单和本地启发式扫描发现的可疑代码片段；发行说明涉及硬分叉、共识/区块验证、认证凭据、密钥清零、交易 gossip 封禁、内存泄漏/OOM、数据库损坏或重置等风险，diff 新增命令执行、外部下载、动态加载、疑似密钥外传代码或 CI 权限，或变更 Actions、构建/安装/发布脚本及认证、加密、钱包、共识、验证路径时，自动改为完整审查。该本地扫描只覆盖已知风险特征，不等同完整安全审查。低风险快速预检最多按 `review.fast_batch_size` 合并 3 个版本；每个版本有独立编号，缺项、重复项、格式异常或批量内容过长时会自动退回逐版本预检。高风险版本与完整审查不会批量化。大差异优先按完整文件分段，超过单段字符上限的文件才会在文件内部按行拆分。最终审查结果要求 AI 返回严格 JSON，由脚本校验后生成报告；格式错误会重试，持续无效的结果不会被记录。大差异分段时，每段只发送命中的重大发行说明条目和自定义审查要求，最终汇总仍收到完整发行说明；已完成的分段仅在仓库、比较版本、代码内容、模型、接口地址和提示词均相同时从断点缓存复用。正式版紧接同系列预发布版时，会引用已有预发布审查作为历史证据；只沿用有明确代码依据的结论，未确认项仍标为待核实，旧发现不会说成本次新增。`fast` 强制快速预检，`full` 强制审查完整 diff。报告会标明实际审查模式；快速预检不会宣称未发送的代码安全。`review.max_releases_per_run` 默认是 `3`，限制单轮最多审查的新版本数；剩余版本会在下一轮继续，避免积压版本拖慢单次工作流。

AI 使用 OpenAI Chat Completions 兼容接口。`api_url` 可填写服务商的 API 根地址（例如以 `/v1` 结尾），脚本会补上 `/chat/completions`。`diff_chunk_chars` 控制顺序审查时每个代码差异分段的字符数，默认建议 120,000；应根据所用模型的上下文窗口设置。在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 添加名为 `AI_API_KEY` 的 Secret。所有仓库共用该密钥；可在全局或单仓库 `ai` 配置中覆盖 `api_url`、`model`、`prompt` 和 `diff_chunk_chars`。

可选地，在 **Settings → Secrets and variables → Actions → Variables** 设置 `NOTIFY_LOGINS`，填写逗号分隔的 GitHub 用户名作为重大事项的 @通知接收人。留空时默认 @提及仓库所有者；仓库属于组织时，组织账号提及不保证通知所有成员，建议填写具体用户。代码类通知要求 AI 在重点依据或“代码已确认的发现”中引用的文件确实属于本次 diff 或已确认的同系列预发布证据；待验证标记、普通修复和低风险事项不会触发通知。明确的硬分叉升级要求及 Breaking Changes 章节下有具体影响、且原文引用可核实的声明是单独的通知条件。注意：仓库 Watch 设置为接收 Issues 或所有活动的用户，仍可能收到每一条新 Issue 的通知；若只想接收被 @提及时的通知，应将仓库通知设为 **Participating and @mentions**。

## 在 GitHub Actions 中运行

1. 将本项目推送到 GitHub 默认分支。
2. 按上文填写 `config/watch.yaml` 并添加 `AI_API_KEY` Secret。
3. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。Pages 报告是公开网页。
4. 在仓库 **Settings → Actions → General → Workflow permissions** 允许工作流 token 写入仓库内容；工作流会把历史网页保存在 `gh-pages` 分支，另外使用 `issues: write` 创建汇总 Issue、使用 Pages 部署权限发布网页。可设置 `NOTIFY_LOGINS` 指定通知用户；未设置时默认提及仓库所有者。
5. 打开 **Actions → 节点版本审查 → Run workflow** 手动启动一次。默认配置下工作流每 30 分钟尝试轮询一次；GitHub schedule 可能延迟或漏掉触发。每个新版本都会生成完整报告并发布网页、Artifact，同时为本轮更新创建一条汇总 Issue。只有达到上述重大事项条件时，Issue 才会 @通知接收人。所有已处理版本的去重键保存在 `gh-pages`，不会重复审查。GitHub Actions Artifact 最长保留 90 天；Pages 网页历史保留 180 天，并在下一次发布时清理过期报告。

调整轮询频率时，编辑 [.github/workflows/watch-releases.yml](.github/workflows/watch-releases.yml) 中的 `schedule`。例如每 15 分钟运行一次：

```yaml
on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:
```

将 `cron` 替换为想要的频率即可；保留一条 schedule，避免同时启用多个定时频率。默认使用 `7,37 * * * *`，每小时在第 7 分和第 37 分运行一次；北京时间对应 08:07、08:37、09:07、09:37 等，仍是每 30 分钟一次，并避开整点启动高峰。`*/30 * * * *` 表示每小时第 0 分和第 30 分运行，`0 * * * *` 表示每小时运行一次。GitHub Actions 的最短 schedule 间隔为 5 分钟；默认按 UTC 调度，运行也可能延迟。详见 [GitHub schedule 文档](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule)。

### 可选：上次运行结束 10 分钟后再轮询（测试间隔）

默认固定 cron 按时刻触发，不会从上次审查结束时间开始计时。如需“审查结束后至少间隔 10 分钟”，可启用独立 dispatcher：它每 5 分钟检查一次主工作流状态；上次默认分支审查完成满 10 分钟且当前没有审查运行时，才派发下一轮。这样不会因 `workflow_run` 递归触发限制而只运行一轮，也不会在长审查期间排队。GitHub schedule 可能延迟，因此下一轮会在 10 分钟后的某个检查 tick 启动，不保证精确到秒。

1. 在 **Settings → Secrets and variables → Actions → Variables** 新增 `RELEASE_POLL_COOLDOWN_ENABLED`，值设为 `true`。
2. 打开 **Actions → 节点版本审查 → Run workflow** 手动启动一次，作为首次轮询。

启用后，主工作流原有固定 schedule 会被跳过，只有 dispatcher 检查到期后才会派发新审查；被跳过的 schedule 记录不会启动审查，也不会重置 10 分钟计时。dispatcher 只根据默认分支最近一次 `workflow_dispatch` 的完成时间计时；如果该仓库还没有这类运行，需要先手动启动一次主工作流。之前创建的 `release-poll-cooldown` Environment 和 Wait timer 不再需要。要恢复默认固定 cron，删除该变量或将值改为 `false`。

## 在本地运行

需要 Python 3.13、Git 和可访问的公开上游仓库。PowerShell 示例：

```powershell
python -m pip install -r requirements.txt
$env:AI_API_KEY = "your-api-key"
# 本地也可以改用已登录的 Codex CLI；启用后无需设置 AI_API_KEY。
# $env:AI_BACKEND = "codex_cli"
python .github/scripts/watch_releases.py
```

完整报告中每个 Release 的 Markdown 版式由 [.github/scripts/upstream_release_report.md](.github/scripts/upstream_release_report.md) 控制；脚本负责分组和填入数据。本地运行发现新 Release 时会在 `reports/` 下为本轮生成一份报告，不会创建 Issue 或上传 Artifact。默认使用 `config/watch.yaml` 中的 API；设置 `AI_BACKEND=codex_cli` 后改用本机已安装并登录的 Codex CLI，生成的报告仍保存在 `reports/`。本地 Codex 模式默认从当前 GitHub 仓库读取 Issue 去重标记，仓库名从 `GITHUB_REPOSITORY` 或当前目录的 Git `origin` remote 获取；公开仓库不需要 GitHub CLI 或 token，私有仓库需要设置 `GH_TOKEN`。本地临时跳过线上 Issue 历史时，可设置 `SKIP_GITHUB_ISSUE_HISTORY=1`，此时只按本地 `reports/` 去重。GitHub Actions 始终使用 workflow token 读取 Issue 历史，并只以机器人 Issue 中的 release keys 去重；Pages 仅保存报告和历史审查材料。

## 检查范围

Release Notes 若有独立的 `Breaking Changes` 或 `Breaking Notes` 标题，只有标题下存在具体行为或运维影响、且报告引用的原文能与该章节逐字对应时，才作为发行说明重点声明；代码差异尚未确认时会标明“代码影响待核实”。标题单独不会被当作具体影响或代码证据，也不会单独触发通知。

审查会按配置的 `network` 判断是否影响实际运行网络。只影响其他网络的共识或升级变化，不会当作当前网络的重大风险。配置校验收紧会与上游默认值、官方预设和支持范围对照；默认配置仍在新范围内时，不会声称默认节点启动失败。脚本不会读取矿池机器上的 `config.toml`，因此对未提供的自定义配置只会说明哪些取值可能导致启动失败，不会断言你的节点使用了这些取值。

发行说明若明确指出硬分叉激活区块高度或升级期限，并要求节点按条件升级或说明旧版本会分叉离网，报告和 Issue 会将它作为紧急提醒置于最前。若发行说明明确要求升级，正式版处置建议会按上游要求显示“必须升级”，同时单独标明代码影响是否待核实；预发布版仍不会建议直接部署生产。

工作流不运行上游程序或测试。AI 阅读 Release Notes 和代码差异，只报告会实质影响矿工、节点运行、共识、兼容性、安全、内存、稳定性或数据的变更；常规重构、文档、测试、普通依赖更新和低影响修复会略过。最终审查结果要求 AI 返回严格 JSON，由脚本校验字段、类别、状态和发现之间的一致性，再渲染为报告；格式错误会重试，仍无效则本次审查失败且不记录为已处理。预发布版根据 GitHub Release 的 `prerelease` 标志或 tag 中的 `pre`、`alpha`、`beta`、`rc`、`dev` 后缀识别。正式版紧接同系列预发布版时会引用已确认的预发布证据；若缺少预发布报告或其中仍有重大待核实项，会改为从上一个正式版到当前正式版做完整差异审查，无法证明首次引入版本时会明确写出。某个币种较早的 Release 审查失败时，本轮会停止处理该币种的后续版本，避免跳过失败版本；后续轮询重试。每个正式版会根据已确认风险给出升级建议；预发布版会逐版本审查，但不会建议直接用于生产升级。该建议未读取矿池节点的实际运行版本，也不会自动升级节点。Issue 摘要和完整报告会为每个非“无”的重点标记单独列出发行说明声明或代码证据。“发行说明待核实”表示发行说明明确提到该类变更，但代码差异和可用历史证据仍未证实，不代表已发现相应问题。破坏性变更只有在代码证据证明改动破坏了仍受支持的升级、迁移、恢复或运行路径，且造成实质后果时才标记为已确认；只影响不受支持的旧版只读工具时不作为兼容性问题。代码差异按文件边界合并到 `diff_chunk_chars` 上限附近；单个超大文件才会在文件内部按行拆分，全部差异仍会被审查，不会省略尾部代码。AI 静态审阅不能替代人工安全审查。

AI 请求遇到网络错误、超时、响应 JSON 解析错误，或 HTTP 408、429、500、502、503、504 时最多尝试 4 次（首次请求加最多 3 次重试），重试间隔为 5、10、20 秒。其他 HTTP 错误立即报告为检查失败；该 Release 不会标记为已处理，后续轮询会重试。
