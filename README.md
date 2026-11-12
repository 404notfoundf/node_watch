# GitHub Release Watch

这个仓库用 GitHub Actions 按配置的频率检查公开 GitHub 仓库。发现新 Release 后，会比较相邻 Release tag 之间的代码差异，调用配置的 AI 做静态审阅。每轮生成一份按币种和版本分段的完整报告，醒目标出破坏性变更、硬分叉/共识、兼容性、内存问题、安全和稳定性/数据相关事项。工作流创建一条汇总 Issue，并将完整报告上传为保留 90 天的 Artifact；新生成的完整报告不会提交到仓库。

## 配置监控对象

将 [config/watch.example.yaml](config/watch.example.yaml) 复制为 `config/watch.yaml`，再替换币种、仓库、真实 Release tag、AI 服务地址和模型等示例值：

```yaml
ai:
  api_url: https://your-compatible-api.example/v1
  model: your-model

coins:
  tari:
    repo: tari-project/tari
    from_release: v6.4.0
```

每个币种配置一个仓库，`repo` 使用 `owner/repository` 格式。`from_release` 必须是该仓库已发布的 GitHub Release tag；配置的版本会纳入分析，并与前一个 Release 比较。之后只处理尚未记录的 Release。工作流只读取 `config/watch.yaml`，示例文件不会自动加载。

AI 使用 OpenAI Chat Completions 兼容接口。`api_url` 可填写服务商的 API 根地址（例如以 `/v1` 结尾），脚本会补上 `/chat/completions`。在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 添加名为 `AI_API_KEY` 的 Secret。所有仓库共用该密钥；可在全局或单仓库 `ai` 配置中覆盖 `api_url`、`model` 和 `prompt`。

可选地，在 **Settings → Secrets and variables → Actions → Variables** 设置 `NOTIFY_LOGINS`，填写逗号分隔的 GitHub 用户名以 @提及多个接收人。留空时默认 @提及仓库所有者；仓库属于组织时，组织账号提及不保证通知所有成员，建议填写具体用户。

## 在 GitHub Actions 中运行

1. 将本项目推送到 GitHub 默认分支。
2. 按上文填写 `config/watch.yaml` 并添加 `AI_API_KEY` Secret。
3. 在仓库 **Settings → Actions → General → Workflow permissions** 中允许工作流读取仓库内容；工作流使用 `issues: write` 创建汇总 Issue。可设置 `NOTIFY_LOGINS` 指定通知用户；未设置时默认提及仓库所有者。
4. 打开 **Actions → Watch upstream releases → Run workflow** 手动启动一次。之后工作流每 30 分钟轮询；发现更新时先上传完整报告 Artifact，再创建汇总 Issue。已处理版本记录在 Issue 中，避免重复报告。

调整轮询频率时，编辑 [.github/workflows/watch-releases.yml](.github/workflows/watch-releases.yml) 中的 `schedule`。例如每 15 分钟运行一次：

```yaml
on:
  schedule:
    - cron: '*/15 * * * *'
  workflow_dispatch:
```

将 `cron` 替换为想要的频率即可；保留一条 schedule，避免同时启用多个定时频率。`*/30 * * * *` 表示每 30 分钟，`0 * * * *` 表示每小时。GitHub Actions 的最短 schedule 间隔为 5 分钟；默认按 UTC 调度，运行也可能延迟。详见 [GitHub schedule 文档](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule)。

## 在本地运行

需要 Python 3.13、Git 和可访问的公开上游仓库。PowerShell 示例：

```powershell
python -m pip install -r requirements.txt
$env:AI_API_KEY = "your-api-key"
python .github/scripts/watch_releases.py
```

本地运行发现新 Release 时会在 `reports/` 下生成报告并更新索引，不会创建 Issue 或上传 Artifact。API 地址、模型和监控列表仍从 `config/watch.yaml` 读取。

## 检查范围

工作流不运行上游程序或测试。AI 阅读 Release note 和两个 tag 之间的代码差异，关注硬分叉、兼容性、内存泄漏/OOM、崩溃、安全和可疑代码，并给出需要人工复核的依据。单次发送给 AI 的代码差异上限为 120,000 个字符；超过上限会在报告中注明省略字符数，并把相关结论标为待验证。AI 调用失败的版本不会标记为已处理，会在后续轮询重试。AI 静态审阅不能替代人工安全审查。

AI 请求遇到网络错误、超时、响应 JSON 解析错误，或 HTTP 408、429、500、502、503、504 时最多尝试 4 次（首次请求加最多 3 次重试），重试间隔为 5、10、20 秒。其他 HTTP 错误立即报告为检查失败；该 Release 不会标记为已处理，后续轮询会重试。
