# 节点版本审查报告

## 检查批次 2026-11-18 23:44:52 UTC

### aleo

#### v4.13.1 · 正式版 · 完整审查
<!-- watch-repo: aleo-labs-protocol/snarkOS -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 可暂缓 · 不重要
- **建议理由：** 未发现需要立即处理的重大变更。

##### AI 审查

未发现需要单独报告的重大变更。

##### 版本信息

发布于 2026-11-17T16:31:34Z · 比较 `v4.12.1` → `v4.13.1` · [打开 Release](https://github.com/aleo-labs-protocol/snarkOS/releases/tag/v4.13.1)


### alephium

#### v4.7.2 · 正式版 · 完整审查
<!-- watch-repo: alephium/alephium -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 建议升级 · 需关注
- **建议理由：** 包含已确认的重要修复或风险，建议在维护窗口升级。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** `flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala` 中 removeNodeAndAncestors 原先递归遍历父节点对象，在重复父边或重叠祖先路径下会对同一祖先重复调用 sideEffect，本次改为按 `parent.key` 查找后再递归，已从图中移除的节点不会被二次处理，`flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala` 新增测试验证每个祖先只移除一次。影响范围限于内存池依赖链清理时的缓存状态一致性，对矿池和运行交易转发的节点有实际意义，未证明崩溃或不可恢复后果。

##### 版本信息

发布于 2026-10-12T09:49:42Z · 比较 `v4.7.1` → `v4.7.2` · [打开 Release](https://github.com/alephium/alephium/releases/tag/v4.7.2)


#### v4.7.3 · 正式版 · 快速预检
<!-- watch-repo: alephium/alephium -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 可暂缓 · 不重要
- **建议理由：** 未发现需要立即处理的重大变更。

##### AI 审查

未发现需要单独报告的重大变更。

##### 版本信息

发布于 2026-10-21T08:48:37Z · 比较 `v4.7.2` → `v4.7.3` · [打开 Release](https://github.com/alephium/alephium/releases/tag/v4.7.3)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
