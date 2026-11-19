# 节点版本审查报告

## 检查批次 2026-11-19 06:38:56 UTC

### alephium

#### v4.7.2 · 正式版 · 完整审查
<!-- watch-repo: alephium/alephium -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 建议升级 · 需关注
- **建议理由：** 包含已确认的重要修复或风险，建议在维护窗口升级。 上游升级建议，发行说明原文：「Fixed a mempool cache issue, highly recommended for mining pools and node operators.」

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** mempool 交易依赖图在存在重复父边或重叠祖先路径时，`flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala` 的 removeNodeAndAncestors 会沿每条父边递归，对同一祖先节点重复执行移除副作用，v4.7.2 改为按 key 只移除并处理每个祖先一次。影响限于 mempool 交易移除与缓存处理路径，发行说明将其描述为 mempool 缓存问题并建议矿池和节点运营者升级。 代码证据：{"path": "flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala", "quote": "def removeNodeAndAncestors(node: N, sideEffect: N => Unit): Unit = {\n    removeNodeFromGraph(node)\n    sideEffect(node)\n    node.getParents().foreach(_.foreach(parent => removeNodeAndAncestors(parent.key, sideEffect)))\n  }"} 代码证据：{"path": "flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala", "quote": "it should \"remove each ancestor once with duplicate parent edges\" in {\n    val flow = Flow(ConcurrentHashMap.empty[K, N], ConcurrentHashMap.empty, _ => 0)\n    flow.addNewNode(flow.newNode(0, Seq.empty))\n    flow.addNewNode(flow.newNode(1, Seq(0, 0)))\n    var removed = Seq.empty[Int]\n\n    flow.removeNodeAndAncestors(1, node => removed = removed :+ node.value)\n\n    removed is Seq(1, 0)\n    flow.isEmpty is true\n    flow.checkSources()\n  }"} 代码证据：{"path": "flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala", "quote": "flow.addNewNode(flow.newNode(1, Seq(0)))\n    flow.addNewNode(flow.newNode(2, Seq(1, 0)))\n    var removed = Seq.empty[Int]\n\n    flow.removeNodeAndAncestors(2, node => removed = removed :+ node.value)\n\n    removed is Seq(2, 1, 0)\n    flow.isEmpty is true\n    flow.checkSources()"}

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


### xbt

#### v29.5.knots20260508 · 正式版 · 完整审查
<!-- watch-repo: bitcoinknots/bitcoin -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 可暂缓 · 不重要
- **建议理由：** 未发现需要立即处理的重大变更。

##### AI 审查

未发现需要单独报告的重大变更。

##### 版本信息

发布于 2026-11-06T18:40:26Z · 比较 `v29.4.3.knots20260508` → `v29.5.knots20260508` · [打开 Release](https://github.com/bitcoinknots/bitcoin/releases/tag/v29.5.knots20260508)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
