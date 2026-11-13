# GitHub Actions 报告在线发布方式调研

日期：2026-11-13
问题：Actions 生成的完整报告能否公开在线阅读，避免手机用户下载 Artifact？

## 结论

有实际项目采用这种方式。常见结构是：Actions 生成 HTML 报告并发布到 GitHub Pages；Issue、PR 或 Actions Summary 只放简短结论和报告链接。Pages 是浏览器可打开的静态网页，完整内容不需要塞进 Markdown Summary。

对于本仓库，建议仅在发现新 Release 并生成报告时部署；每个本轮报告生成一个独立页面，路径带 Actions run ID 或时间戳。Issue 链接指向该页面，Artifact 继续保留作下载备份。若保留历史页面，则在 Pages 内容分支清理超过保留期限的旧目录。不要用固定的 `latest/` 地址作为历史 Issue 的唯一链接，否则每次部署会覆盖旧报告。

## 实际项目

### Grafana：Artifact → Pages → PR 评论链接

[Grafana plugin-actions 的 Playwright Pages 说明](https://github.com/grafana/plugin-actions/blob/main/playwright-gh-pages/README.md)描述了完整流程：测试任务上传报告 Artifact，独立的部署任务将报告发布到 Pages，并在 PR 评论中放置结果和链接；旧报告按保留策略清理。它还将写权限限制在部署任务，并跳过无法安全写入的 fork PR。该项目使用 `gh-pages` 分支保存站点内容。

这与本仓库“生成一份报告、Issue 提供入口、保留 Artifact 备份”的工作流最接近。差别是 Grafana 报告的是 Playwright 测试结果，而不是 AI 代码审查。

### 定时监控：生成静态 HTML → Pages

[Weekly Paper Report](https://github.com/hqrrr/weekly-paper-report)是定时监控 Crossref 新论文的项目。它按周触发 Actions，运行 Python 程序生成 `report/index.html`，然后使用 `actions/upload-pages-artifact` 和 `actions/deploy-pages` 发布。报告有固定的 Pages URL，README 提供在线示例页面。

这是与本仓库“定时检查外部数据并生成报告”最相似的公开示例。它发布最新网页；若需要每轮报告的永久独立链接，则还要加入带 run ID 的历史目录和清理逻辑。

### Allure：每轮独立链接、Summary 和历史报告

[Allure Deployer Action](https://github.com/deivydasp/allure-deployer-action-v2)提供每轮唯一报告 URL、汇总首页、PR 评论链接和历史保留数量，并支持多项目分区。它的说明明确将历史保存在 `gh-pages` 分支。

[Allure Dashboard](https://github.com/marketplace/actions/allure-dashboard)展示了另一种部署方式：工作流将生成目录作为 Pages Artifact 上传，再调用 `actions/deploy-pages`，无需向 `gh-pages` 分支提交生成文件。它同时建议在 Actions Summary 展示链接。此方式本身不会自动提供所有历史报告；如需历史，需要额外持久化数据或报告。

## GitHub 平台约束

- [GitHub Pages 官方指南](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)支持通过 Actions 生成静态站点文件并部署。部署源可以是 Actions workflow；官方流程使用 Pages Artifact 和部署任务。
- Pages 默认公开可访问，即使源码仓库是私有的也可能如此；报告内容应按公开信息处理。
- [Actions Job Summary 官方说明](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#step-isolation-and-limits)规定单个步骤的 Summary 上限为 1 MiB，超限只会导致该步骤的 Summary 上传失败。将内容折叠不会改变 Markdown 正文大小。因此 Summary 更适合放短摘要和链接；较大的完整报告应由独立 HTML 页面承载。

## 对当前仓库的适配

当前 `.github/workflows/watch-releases.yml` 只有在 `watch_releases.py` 产出 `report_path` 时才上传报告并创建 Issue。因此可以只在同一条件成立时发布 Pages，不会因为每 30 分钟轮询而重复部署空报告。

建议的职责划分：

1. 保持现有 Issue 为入口，列出币种、版本和最重要的发现，并添加“在线查看完整报告”链接。
2. 从当前报告生成静态网页，按币种和 Release 版本组织内容；若页面很长，可将每个 Release 放入单独页面，由本轮目录的 `index.html` 汇总链接。
3. 发布任务只取得 Pages 所需写权限；现有 Artifact 继续作为原始 Markdown 备份。
4. 为每轮使用不覆盖的 URL，并按既定保留期限清理 Pages 历史目录。

这不要求把报告提交到默认分支的 `reports/` 目录；若选择 `gh-pages` 历史方案，报告仍会保存在专用发布分支中。若完全不保留历史，则只能提供一个会被新报告覆盖的当前页。

## 适用性与风险

这些项目证明“Actions 生成静态报告并由 Pages 在线阅读”是可行且在测试报告、定时监控报告中确实使用的模式，但没有证据表明它专门用于 AI 审查区块链 Release 的场景。

发布前需把 Release note、文件名和 AI 输出视为不可信文本，安全转义后再生成 HTML，避免上游内容被当作网页标签或脚本执行。还需为 Pages 报告设置历史清理策略；仅部署一个 `index.html` 会覆盖上一轮的内容。

## 来源

- [Grafana `playwright-gh-pages` README](https://github.com/grafana/plugin-actions/blob/main/playwright-gh-pages/README.md)
- [Weekly Paper Report README](https://github.com/hqrrr/weekly-paper-report)
- [Weekly Paper Report 定时部署 workflow](https://github.com/hqrrr/weekly-paper-report/blob/main/.github/workflows/update_github_pages.yml)
- [Allure Deployer Action](https://github.com/deivydasp/allure-deployer-action-v2)
- [Allure Dashboard](https://github.com/marketplace/actions/allure-dashboard)
- [GitHub Pages 官方指南](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [GitHub Actions Job Summary 官方限制](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#step-isolation-and-limits)
