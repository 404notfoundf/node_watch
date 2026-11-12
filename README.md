# GitHub Release Watch

这个仓库用 GitHub Actions 每 30 分钟检查 YAML 中配置的公开 GitHub 仓库。发现新 Release 后，会比较相邻 Release tag 之间的代码差异，调用配置的 AI 做静态审阅，并把所有结果累计写入同一份[报告](reports/index.md)。报告按检查批次、币种和版本分段；每个版本显示仓库来源、Release note、变更文件和 AI 结论。

## 配置监控对象

编辑 [config/watch.yaml](config/watch.yaml)，在 `coins` 下填写币种、仓库和起始 Release：

```yaml
ai:
  api_url: https://your-compatible-api.example/v1
  model: your-model

coins:
  tari:
    repositories:
      - repo: tari-project/tari
        from_release: v6.4.0
```

`repo` 使用 `owner/repository` 格式。`from_release` 必须是该仓库已发布的 GitHub Release tag；配置的版本会纳入分析，并与前一个 Release 比较。之后只处理尚未记录的 Release。当前 YAML 默认没有启用任何仓库。

AI 使用 OpenAI Chat Completions 兼容接口。`api_url` 可填写服务商的 API 根地址（例如以 `/v1` 结尾），脚本会补上 `/chat/completions`。在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 添加名为 `AI_API_KEY` 的 Secret。所有仓库共用该密钥；可在全局或单仓库 `ai` 配置中覆盖 `api_url`、`model` 和 `prompt`。

## 在 GitHub Actions 中运行

1. 将本项目推送到 GitHub 默认分支。
2. 按上文填写 `config/watch.yaml` 并添加 `AI_API_KEY` Secret。
3. 在仓库 **Settings → Actions → General → Workflow permissions** 中允许工作流读写仓库内容，以便提交报告。
4. 打开 **Actions → Watch upstream releases → Run workflow** 手动启动一次。之后工作流每 30 分钟轮询，并将新报告提交到默认分支。

如果分支保护规则禁止 `github-actions[bot]` 推送，报告生成后无法自动提交，需要调整规则或手动保留报告。GitHub 的定时工作流可能延迟启动。

## 在本地运行

需要 Python 3.13、Git 和可访问的公开上游仓库。PowerShell 示例：

```powershell
python -m pip install -r requirements.txt
$env:AI_API_KEY = "your-api-key"
python .github/scripts/watch_releases.py
```

本地运行会更新 `reports/index.md`，不会自动提交。API 地址、模型和监控列表仍从 `config/watch.yaml` 读取。

## 检查范围

工作流不运行上游程序或测试。AI 阅读 Release note 和两个 tag 之间的代码差异，关注硬分叉、兼容性、内存、崩溃、安全和可疑代码，并给出需要人工复核的依据。单次发送给 AI 的代码差异上限为 120,000 个字符；AI 静态审阅不能替代人工安全审查。
