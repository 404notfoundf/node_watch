# 节点版本审查报告

## 检查批次 2026-11-19 01:27:57 UTC

### aleo

#### v4.13.1 · 正式版 · 完整审查
<!-- watch-repo: aleo-labs-protocol/snarkOS -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 必须升级 · 不重要
- **建议理由：** 已确认破坏性或兼容性变更，需要升级并核对现有配置。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** `node/bft/src/helpers/upgrade_monitor.rs` 与 `node/consensus/src/lib.rs` 引入的升级监控可在单个持质押成员声明超前 `ConsensusSchedule` 且本节点非超前连接不足 quorum 时扣留本地区块产出（测试 `a_block_is_held_back_without_a_quorum_where_a_member_is_ahead` 证实），影响仅限本地出块活性，节点不崩溃、同步继续、无链分歧，触发需要恶意或故障委员会成员与低连接质量，属有条件低影响风险。
2. **已确认 — 兼容性：** `node/metrics/src/names.rs` 与 `node/consensus/src/lib.rs` 将 `snarkos_consensus_unconfirmed_transactions_total`、`snarkos_consensus_unconfirmed_solutions_total` 由 gauge 改为 counter（重复入队不再计数），与发行说明一致，沿用 gauge 语义的监控面板或告警需调整，不影响节点与挖矿运行。

##### 版本信息

发布于 2026-11-17T16:31:34Z · 比较 `v4.12.1` → `v4.13.1` · [打开 Release](https://github.com/aleo-labs-protocol/snarkOS/releases/tag/v4.13.1)


### alephium

#### v4.7.2 · 正式版 · 快速预检
<!-- watch-repo: alephium/alephium -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 可暂缓 · 不重要
- **建议理由：** 未发现需要立即处理的重大变更。

##### AI 审查

未发现需要单独报告的重大变更。

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
