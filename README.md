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

审核保护规则：`auto` 对链、P2P、RPC、存储、数据库、交易等核心路径的改动（包括删除）也使用完整审核。代码已确认的发现必须提供文件路径和可匹配该文件差异的原文代码片段；仅有文件名、注释、历史 AI 文本或 PR 元数据不能触发代码证据通知。片段匹配只能证明引用确实存在，不能替代人工核实因果关系。历史预发布发现缺少当前代码时，正式版会回退到累计完整 diff。AI 响应截断会重试；分块必须返回匹配的完成标记才可缓存，旧版缓存不再复用。后续 tag 获取失败时，会先审核已准备好的较早版本，并停止该币种的后续版本。自动硬分叉升级提醒要求条目明确适用于配置的 `network`；其他网络或网络不明确的条目不会仅凭正则强制升级。

可选地，在 **Settings → Secrets and variables → Actions → Variables** 设置 `NOTIFY_LOGINS`，填写逗号分隔的 GitHub 用户名作为重大事项的 @通知接收人。留空时默认 @提及仓库所有者；仓库属于组织时，组织账号提及不保证通知所有成员，建议填写具体用户。代码类通知要求 AI 在重点依据或“代码已确认的发现”中引用的文件确实属于本次 diff 或已确认的同系列预发布证据；待验证标记、普通修复和低风险事项不会触发通知。明确的硬分叉升级要求及 Breaking Changes 章节下有具体影响、且原文引用可核实的声明是单独的通知条件。注意：仓库 Watch 设置为接收 Issues 或所有活动的用户，仍可能收到每一条新 Issue 的通知；若只想接收被 @提及时的通知，应将仓库通知设为 **Participating and @mentions**。

上游升级建议独立于 AI 代码风险等级：`auto` 会对明确推荐运营者升级，以及面向矿池、节点运营者或所有用户的“重要／关键更新”等同类声明使用完整审查，覆盖 `highly/strongly recommended`、`recommend upgrading`、`encouraged/advised to upgrade`、`should/must upgrade`、强烈建议升级、矿池重要更新等常见说法。标题和 Markdown 章节中的网络与对象范围也会纳入判断；其他网络、否定／暂缓建议、仅钱包或开发工具的更新建议、代码围栏中的示例不会单独触发此规则。未说明网络的通用运营者建议会保留，但不会据此假定存在主网共识风险。正式版即使 AI 返回 P3 且没有确认发现，也会显示“建议升级 · 需关注”，并在完整报告和 Issue 中引用上游原文；已有的“必须升级”或“需人工确认”不会被它降级，预发布版仍不建议直接部署生产。上游推荐不会被伪装成代码已确认的发现，也不会单独提升 P0/P1 或触发 @通知。`fast`/`full` 强制模式仍优先于自动规则；如果希望每个版本都审查完整 diff，可以设置 `review.mode: full`。

这些文字规则只识别有明确依据的常见表述，不是任意自然语言的语义判断器；遇到漏判的新表述，应增加对应回归用例。规则变更不会自动重写历史报告或清除已处理版本标记，手动再运行工作流也不会重新审查已经去重的版本。

版本调度采用“待审少的先完成 + 长期等待保护”。每轮先查询全部配置币种的 Release，再按现有规则排除测试／预发布版和已审核版本，按实际待审数量从少到多处理；数量相同时保持配置顺序。一个币种没有待审版本就不占名额，其他币种可以继续使用剩余额度。`include_prereleases: false` 时，测试／预发布版既不参与排序，也不占审核额度；主动开启时则正常计入。每个币种内部仍按版本顺序比较，不会自动升级节点或修改 `running_version`。`review.max_releases_per_run` 是单轮进入准备／审核的版本总上限，包含失败尝试；某个币种失败后停止其后续版本，其他币种继续使用尚未尝试的额度。

某币种连续 3 轮查询到待审版本、却没有一次进入准备／审核时，下一轮先为它安排 1 个保护名额，再按剩余待审数量处理其他额度；多个币种需要保护时，等待轮数最多的先获得机会。获得尝试机会（即使失败）或队列为空后，等待计数清零；Release 查询失败时保留旧计数，不凭未知结果增加或清零。等待状态沿用 `.release-review-cache/scheduler-v1.json` 的原子缓存写入，本地跨次运行保留，Actions 沿用现有 checkpoint 缓存恢复／保存步骤，不需要新数据库或工作流权限。修改仓库、实际运行版本、网络或预发布版开关后，对应队列按新身份重新计数。缓存丢失、被清理或无效时，等待计数从零开始，但不会清除已有版本去重记录；轮数按完成调度统计，不保证固定分钟数。

## 在 GitHub Actions 中运行

1. 将本项目推送到 GitHub 默认分支。
2. 按上文填写 `config/watch.yaml` 并添加 `AI_API_KEY` Secret。
3. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。Pages 报告是公开网页。
4. 在仓库 **Settings → Actions → General → Workflow permissions** 允许工作流 token 写入仓库内容；工作流会把历史网页保存在 `gh-pages` 分支，另外使用 `issues: write` 创建汇总 Issue、使用 Pages 部署权限发布网页。可设置 `NOTIFY_LOGINS` 指定通知用户；未设置时默认提及仓库所有者。
5. 在 **Settings → Environments** 新建 `release-poll-cooldown` Environment，并把 **Wait timer** 设置为 15 分钟。
6. 在 **Settings → Secrets and variables → Actions → Variables** 新增 `RELEASE_POLL_COOLDOWN_ENABLED`，值设为 `true`。
7. 打开 **Actions → 节点版本审查 → Run workflow** 手动启动一次。此后每轮审查和报告发布完成后，`schedule-next` job 会等待 15 分钟，再通过 `workflow_dispatch` 启动下一轮。Environment 等待期间不占用 runner；实际启动时间还会受 GitHub runner 排队影响。

每个新版本都会生成完整报告并发布网页、Artifact，同时为本轮更新创建一条汇总 Issue。只有达到上述重大事项条件时，Issue 才会 @通知接收人。所有已处理版本的去重键保存在 `gh-pages`，不会重复审查。GitHub Actions Artifact 最长保留 90 天；Pages 网页历史保留 180 天，并在下一次发布时清理过期报告。

要暂停自动轮询，将 `RELEASE_POLL_COOLDOWN_ENABLED` 改为 `false`；当前正在等待的 Environment job 仍需在 Actions 页面手动取消。恢复时重新改为 `true`，再手动运行一次 **节点版本审查**。不要重复手动启动；额外运行只会进入同一并发队列，可能替换已排队的运行，并不会让轮询更快。

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
