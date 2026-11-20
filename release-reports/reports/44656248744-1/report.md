# 节点版本审查报告

## 检查批次 2026-11-20 01:58:35 UTC

### alephium

#### v4.7.2 · 正式版 · 完整审查
<!-- watch-repo: alephium/alephium -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 强烈建议升级 · 需关注
- **建议理由：** 上游明确强烈建议升级，请核对当前节点的适用条件并尽快安排维护窗口；该声明不等同于已确认的重大代码风险。 上游升级建议，发行说明原文：「Fixed a mempool cache issue, highly recommended for mining pools and node operators.」

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 内存池依赖图移除节点及祖先时，v4.7.1 在节点存在重复父边或祖先路径重叠的情况下会对同一祖先多次执行移除副作用，v4.7.2 改为按 parent.key 递归使每个节点只移除一次（测试断言 removed is Seq(1, 0)、Seq(2, 1, 0)）；影响范围限于内存池缓存维护，发行说明称 highly recommended for mining pools and node operators，不涉及共识或区块有效性。，代码路径：`flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala`、`flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala` 代码证据：{"path": "flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala", "quote": "  def removeNodeAndAncestors(node: N, sideEffect: N => Unit): Unit = {\n    removeNodeFromGraph(node)\n    sideEffect(node)\n    node.getParents().foreach(_.foreach(parent => removeNodeAndAncestors(parent.key, sideEffect)))\n  }"} 代码证据：{"path": "flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala", "quote": "    flow.addNewNode(flow.newNode(1, Seq(0, 0)))\n    var removed = Seq.empty[Int]\n\n    flow.removeNodeAndAncestors(1, node => removed = removed :+ node.value)\n\n    removed is Seq(1, 0)\n    flow.isEmpty is true\n    flow.checkSources()"}

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
