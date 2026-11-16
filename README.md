# GitHub Release Watch

这个仓库用 GitHub Actions 按配置的频率检查公开 GitHub 仓库。发现新 Release 后，会比较相邻 Release tag 之间的代码差异，调用配置的 AI 做静态审阅。每轮生成一份按币种和版本分段的完整报告，醒目标出破坏性变更、硬分叉/共识、兼容性、内存问题、安全和稳定性/数据相关事项。工作流创建一条汇总 Issue，将完整报告发布为可在线阅读的 GitHub Pages 网页，并保留 90 天的 Markdown Artifact 供下载。Pages 历史报告保存在独立的 `gh-pages` 分支中，超过 180 天的目录会在下次发布时从当前网站清理；分支的 Git 提交历史仍保留先前内容。报告不会提交到默认分支的 `reports/` 目录。

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
```

每个币种配置一个仓库，`repo` 使用 `owner/repository` 格式。`running_version` 必须是矿池当前实际运行、且已发布的 GitHub Release tag；脚本只分析比它新的 Release，并按版本顺序逐个比较差异。升级矿池节点后，请同步更新该值，后续报告会以新版本作为比较起点。工作流只读取 `config/watch.yaml`，示例文件不会自动加载。

`review.mode` 同时作用于 GitHub Actions 和本地 Codex CLI。默认 `auto` 对预发布版和正式版使用相同的风险判断，并读取 Release 标题和正文：普通更新快速预检，只向 AI 发送发行说明、完整变更文件清单和本地启发式扫描发现的可疑代码片段；发行说明涉及硬分叉、共识/区块验证、认证凭据、密钥清零、交易 gossip 封禁、内存泄漏/OOM、数据库损坏或重置等风险，diff 新增命令执行或疑似密钥外传代码，或变更 Actions、构建/安装/发布脚本及认证、加密、钱包、共识、验证路径时，自动改为完整审查。该本地扫描只覆盖已知风险特征，不等同完整安全审查。大差异分段时，每段只发送命中的重大发行说明条目和自定义审查要求，最终汇总仍收到完整发行说明。正式版紧接同系列预发布版时，会引用已有预发布审查作为历史证据；只沿用有明确代码依据的结论，未确认项仍标为待核实，旧发现不会说成本次新增。`fast` 强制快速预检，`full` 强制审查完整 diff。报告会标明实际审查模式；快速预检不会宣称未发送的代码安全。`review.max_releases_per_run` 默认是 `3`，限制单轮最多审查的新版本数；剩余版本会在下一轮继续，避免积压版本拖慢单次工作流。

AI 使用 OpenAI Chat Completions 兼容接口。`api_url` 可填写服务商的 API 根地址（例如以 `/v1` 结尾），脚本会补上 `/chat/completions`。`diff_chunk_chars` 控制顺序审查时每个代码差异分段的字符数，默认建议 120,000；应根据所用模型的上下文窗口设置。在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 添加名为 `AI_API_KEY` 的 Secret。所有仓库共用该密钥；可在全局或单仓库 `ai` 配置中覆盖 `api_url`、`model`、`prompt` 和 `diff_chunk_chars`。

可选地，在 **Settings → Secrets and variables → Actions → Variables** 设置 `NOTIFY_LOGINS`，填写逗号分隔的 GitHub 用户名以 @提及多个接收人。留空时默认 @提及仓库所有者；仓库属于组织时，组织账号提及不保证通知所有成员，建议填写具体用户。

## 在 GitHub Actions 中运行

1. 将本项目推送到 GitHub 默认分支。
2. 按上文填写 `config/watch.yaml` 并添加 `AI_API_KEY` Secret。
3. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。Pages 报告是公开网页。
4. 在仓库 **Settings → Actions → General → Workflow permissions** 允许工作流 token 写入仓库内容；工作流会把历史网页保存在 `gh-pages` 分支，另外使用 `issues: write` 创建汇总 Issue、使用 Pages 部署权限发布网页。可设置 `NOTIFY_LOGINS` 指定通知用户；未设置时默认提及仓库所有者。
5. 打开 **Actions → 节点版本审查 → Run workflow** 手动启动一次。之后工作流每 30 分钟轮询；发现更新时先上传完整报告 Artifact、发布网页，再创建带在线报告链接的汇总 Issue。已处理版本记录在 Issue 中，避免重复报告。GitHub Actions Artifact 最长保留 90 天；Pages 网页历史保留 180 天，并在下一次发布时清理过期报告。

调整轮询频率时，编辑 [.github/workflows/watch-releases.yml](.github/workflows/watch-releases.yml) 中的 `schedule`。例如每 15 分钟运行一次：

```yaml
on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:
```

将 `cron` 替换为想要的频率即可；保留一条 schedule，避免同时启用多个定时频率。默认使用 `7,37 * * * *`，每小时在第 7 分和第 37 分运行一次；北京时间对应 08:07、08:37、09:07、09:37 等，仍是每 30 分钟一次，并避开整点启动高峰。`*/30 * * * *` 表示每小时第 0 分和第 30 分运行，`0 * * * *` 表示每小时运行一次。GitHub Actions 的最短 schedule 间隔为 5 分钟；默认按 UTC 调度，运行也可能延迟。详见 [GitHub schedule 文档](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule)。

## 在本地运行

需要 Python 3.13、Git 和可访问的公开上游仓库。PowerShell 示例：

```powershell
python -m pip install -r requirements.txt
$env:AI_API_KEY = "your-api-key"
# 本地也可以改用已登录的 Codex CLI；启用后无需设置 AI_API_KEY。
# $env:AI_BACKEND = "codex_cli"
python .github/scripts/watch_releases.py
```

完整报告中每个 Release 的 Markdown 版式由 [.github/scripts/upstream_release_report.md](.github/scripts/upstream_release_report.md) 控制；脚本负责分组和填入数据。本地运行发现新 Release 时会在 `reports/` 下为本轮生成一份报告，不会创建 Issue 或上传 Artifact。默认使用 `config/watch.yaml` 中的 API；设置 `AI_BACKEND=codex_cli` 后改用本机已安装并登录的 Codex CLI，生成的报告仍保存在 `reports/`。本地 Codex 模式默认从当前 GitHub 仓库读取 Issue 去重标记，仓库名从 `GITHUB_REPOSITORY` 或当前目录的 Git `origin` remote 获取；公开仓库不需要 GitHub CLI 或 token，私有仓库需要设置 `GH_TOKEN`。本地临时跳过线上 Issue 历史时，可设置 `SKIP_GITHUB_ISSUE_HISTORY=1`，此时只按本地 `reports/` 去重。GitHub Actions 始终使用 workflow token 读取 Issue 历史。

## 检查范围

Release Notes 若有独立的 `Breaking Changes` 或 `Breaking Notes` 标题，会直接作为上游明确标出的重点事项显示；如果代码差异尚未确认具体影响，报告会标明“代码影响待核实”，升级建议为“需人工确认”。标题本身不会被当作代码证据，也不会单独抬高风险级别。

发行说明若明确指出硬分叉激活区块高度，并要求节点在该高度前升级或说明旧版本会分叉离网，报告和 Issue 会将它作为紧急提醒置于最前，突出激活高度与升级时限。若发行说明明确要求升级，正式版处置建议会按上游要求显示“必须升级”，同时单独标明代码影响是否待核实；预发布版仍不会建议直接部署生产。

工作流不运行上游程序或测试。AI 阅读 Release note 和两个 tag 之间的完整代码差异，只报告会实质影响矿工、节点运行、共识、兼容性、安全、内存、稳定性或数据的变更；常规重构、文档、测试、普通依赖更新和低影响修复会略过。预发布版根据 GitHub Release 的 `prerelease` 标志或 tag 中的 `pre`、`alpha`、`beta`、`rc`、`dev` 后缀识别。每个正式版会根据已确认的风险和重点标记给出升级建议：已确认硬分叉/重大共识、破坏性变更、兼容性变更、安全风险或 P0 为“必须升级”；只有发行说明待核实或 AI 输出不完整为“需人工确认”；内存、安全、稳定性修复或 P1/P2 为“建议升级”；其余 P3 为“可暂缓”。预发布版仍会逐版本审查和记录相同的风险，但会标记为“预发布版”，不会建议直接用于生产升级；重大事项提示评估现网影响并跟进正式版。该建议未读取矿池节点的实际运行版本，也不会自动升级节点。Issue 摘要和完整报告会为每个非“无”的重点标记单独列出发行说明声明或代码证据。“发行说明待核实”表示发行说明明确提到该类变更，但相邻 tag 的代码差异没有证实，不表示已发现相应问题。破坏性变更只有在代码证据证明改动破坏了仍受支持的升级、迁移、恢复或运行路径，且造成实质后果时才标记为已确认；只影响不受支持的旧版只读工具时归为兼容性提示。代码差异按 `diff_chunk_chars` 设置顺序分段审查后再汇总，不会省略尾部代码；分段越多，串行调用次数和运行时间越长。任一分段审查失败，该版本不会标记为已处理，会在后续轮询重试。AI 静态审阅不能替代人工安全审查。

AI 请求遇到网络错误、超时、响应 JSON 解析错误，或 HTTP 408、429、500、502、503、504 时最多尝试 4 次（首次请求加最多 3 次重试），重试间隔为 5、10、20 秒。其他 HTTP 错误立即报告为检查失败；该 Release 不会标记为已处理，后续轮询会重试。
