# 节点版本审查报告

## 检查批次 2026-11-19 06:07:07 UTC

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
- **建议理由：** 包含已确认的重要修复或风险，建议在维护窗口升级。 上游升级建议，发行说明原文：「Fixed a mempool cache issue, highly recommended for mining pools and node operators.」

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** `flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala` 的 `removeNodeAndAncestors` 改为按键递归移除祖先，使重复父边或祖先路径重叠时每个祖先只执行一次移除副作用，修复 v4.7.1 中 mempool 缓存可能被重复移除而失衡的问题，影响挖矿池与运行 mempool 的节点，建议按上游推荐升级。 代码证据：{"path": "flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala", "quote": "    node.getParents().foreach(_.foreach(parent => removeNodeAndAncestors(parent.key, sideEffect)))"} 代码证据：{"path": "flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala", "quote": "    flow.addNewNode(flow.newNode(1, Seq(0, 0)))\n    var removed = Seq.empty[Int]\n\n    flow.removeNodeAndAncestors(1, node => removed = removed :+ node.value)\n\n    removed is Seq(1, 0)\n    flow.isEmpty is true\n    flow.checkSources()"}

##### 版本信息

发布于 2026-10-12T09:49:42Z · 比较 `v4.7.1` → `v4.7.2` · [打开 Release](https://github.com/alephium/alephium/releases/tag/v4.7.2)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
