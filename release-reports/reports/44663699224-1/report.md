# 节点版本审查报告

## 检查批次 2026-11-20 03:02:30 UTC

### aleo

#### v4.13.1 · 正式版 · 完整审查
<!-- watch-repo: aleo-labs-protocol/snarkOS -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 按需升级 · 需关注
- **建议理由：** 存在 P2 级变化或修复；先核对适用平台、节点模式及配置，受影响时再安排维护窗口，不属于强制升级要求。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 新增出块闸门在有对端声称更高的共识排程且连接的验证器未以 quorum 反驳时返回 BlockHeldBack，阻止该 validator 在特定高度出块（node/bft/src/helpers/upgrade_monitor.rs、node/consensus/src/lib.rs）。仅影响 validator 出块模式，且需要存在声称更新排程的对端（本版本 mainnet 无新共识版本/激活高度）。，代码路径：`node/bft/src/helpers/upgrade_monitor.rs`、`node/consensus/src/lib.rs` 代码证据：{"path": "node/bft/src/helpers/upgrade_monitor.rs", "quote": "if is_claimed && !self.is_refuted(&state, committee, connected, Some(height)) {\n            return Err(BlockHeldBack(format!(\n                \"Validators may run a newer consensus version than this build at height {height}, and connected \\\n                 validators holding a quorum of stake have not refuted it\"\n            ))\n            .into());\n        }"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "self.bft.primary().gateway().ensure_block_may_be_built(block_height)?;"}
2. **已确认 — 兼容性：** 监控指标 snarkos_consensus_unconfirmed_transactions_total 与 snarkos_consensus_unconfirmed_solutions_total 由 gauge 改为 counter（node/metrics/src/names.rs、node/consensus/src/lib.rs），把二者按 gauge 处理的监控/告警查询会失效，需要更新。，代码路径：`node/consensus/src/lib.rs`、`node/metrics/src/names.rs` 代码证据：{"path": "node/metrics/src/names.rs", "quote": "pub(super) const COUNTER_NAMES: [&str; 7] = [\n    bft::LEADERS_ELECTED,\n    bft::PEER_PROPOSALS_MALFORMED,\n    consensus::STALE_UNCONFIRMED_TRANSACTIONS,\n    consensus::STALE_UNCONFIRMED_SOLUTIONS,\n    consensus::DROPPED_TRANSACTIONS,\n    consensus::UNCONFIRMED_SOLUTIONS,\n    consensus::UNCONFIRMED_TRANSACTIONS,\n];"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "metrics::increment_counter(metrics::consensus::UNCONFIRMED_SOLUTIONS);"}
3. **已确认 — 兼容性：** snarkos developer 的端点处理变更：未标注 API 版本的 --endpoint 默认改走 v2（此前 v1），带查询串的 URL 被拒绝（cli/src/helpers/args.rs）；显式 /v1、/v2 端点行为不变。，代码路径：`cli/src/commands/developer/mod.rs`、`cli/src/helpers/args.rs` 代码证据：{"path": "cli/src/helpers/args.rs", "quote": "pub(crate) fn prepare_endpoint(endpoint: Uri) -> Result<Uri> {\n    ensure!(endpoint.query().is_none(), \"The endpoint URL must not have a query string\");"} 代码证据：{"path": "cli/src/helpers/args.rs", "quote": "pub(crate) fn api_version_of(path: &str) -> Option<ApiVersion> {\n    match path.trim_end_matches('/').rsplit('/').next() {\n        Some(API_VERSION_V1) => Some(ApiVersion::V1),\n        Some(API_VERSION_V2) => Some(ApiVersion::V2),\n        _ => None,\n    }\n}"} 代码证据：{"path": "cli/src/commands/developer/mod.rs", "quote": "        let api_version = api_version_of(base_url.path())\n            .context(\"The endpoint URL must end in an API version (v1 or v2). Use `prepare_endpoint` first\")?;"}
4. **已确认 — 兼容性：** 网关握手事件版本升至 12 并追加 HandshakeTrailer，新增共识排程与创世哈希校验（node/bft/events/src/lib.rs、node/bft/src/gateway.rs），创世哈希不匹配的对端被断开；接受下限保持 10，v4.12.x 与 v4.13.x 双向互联不受影响。，代码路径：`node/bft/events/src/helpers/handshake.rs`、`node/bft/events/src/lib.rs`、`node/bft/src/gateway.rs` 代码证据：{"path": "node/bft/events/src/lib.rs", "quote": "    pub const MINIMUM_VERSION: u32 = 10;"} 代码证据：{"path": "node/bft/events/src/lib.rs", "quote": "    pub const VERSION: u32 = 12;"} 代码证据：{"path": "node/bft/events/src/helpers/handshake.rs", "quote": "        let signature = Data::read_le(&mut reader)?;\n        let trailer = HandshakeTrailer::read_le(&mut reader)?;\n\n        Ok(Self { info, signature, trailer })"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "        if info.version >= HandshakeTrailer::FIRST_VERSION && trailer.schedule.is_none() {\n            warn!(\n                \"{CONTEXT} Handshake with '{peer_addr}' failed (version {} sent no consensus schedule)\",\n                info.version\n            );\n            return Some(DisconnectReason::ProtocolViolation);\n        }"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "        if let Some(genesis_hash) = &trailer.genesis_hash\n            && genesis_hash[..] != expected_genesis_hash[..]\n        {\n            warn!(\"{CONTEXT} Handshake with '{peer_addr}' failed (incorrect genesis hash)\");\n            return Some(DisconnectReason::GenesisMismatch);\n        }"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "                if version < Event::<N>::MINIMUM_VERSION {\n                    bail!(\"Dropping '{peer_ip}' on event version {version} (outdated)\");\n                }"}
5. **已确认 — 安全：** 依赖安全更新：tracing-subscriber 0.3.19→0.3.23、libz-sys →1.1.33，对应 RUSTSEC-2025-0055、RUSTSEC-2026-0544（Cargo.toml、Cargo.lock）；未展示漏洞在节点运行中的可利用路径。，代码路径：`Cargo.lock`、`Cargo.toml` 代码证据：{"path": "Cargo.toml", "quote": "[workspace.dependencies.tracing-subscriber]\nversion = \"0.3.23\""} 代码证据：{"path": "Cargo.lock", "quote": "[[package]]\nname = \"tracing-subscriber\"\nversion = \"0.3.23\""} 代码证据：{"path": "Cargo.lock", "quote": "[[package]]\nname = \"libz-sys\"\nversion = \"1.1.33\""}

##### 版本信息

发布于 2026-11-17T16:31:34Z · 比较 `v4.12.1` → `v4.13.1` · [打开 Release](https://github.com/aleo-labs-protocol/snarkOS/releases/tag/v4.13.1)


### alephium

#### v4.7.2 · 正式版 · 完整审查
<!-- watch-repo: alephium/alephium -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 强烈建议升级 · 需关注
- **建议理由：** 上游明确强烈建议升级，请核对当前节点的适用条件并尽快安排维护窗口；该声明不等同于已确认的重大代码风险。 上游升级建议，发行说明原文：「Fixed a mempool cache issue, highly recommended for mining pools and node operators.」

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** mempool 交易依赖图中存在重复父边或共享祖先路径时，v4.7.1 的 `removeNodeAndAncestors` 会沿多条父边重复遍历并对同一祖先多次执行移除副作用，可能导致 mempool 缓存记录不一致；`flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala` 改为按 key 查找后每个祖先只移除一次，新增测试验证结果为 `Seq(1, 0)`。影响限于 mempool 依赖图含共享祖先的移除流程，节点与矿池升级后即生效，属修复基线缺陷。，代码路径：`flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala` 代码证据：{"path": "flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala", "quote": "node.getParents().foreach(_.foreach(parent => removeNodeAndAncestors(parent.key, sideEffect)))"} 代码证据：{"path": "flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala", "quote": "flow.removeNodeAndAncestors(1, node => removed = removed :+ node.value)\n\n    removed is Seq(1, 0)\n    flow.isEmpty is true\n    flow.checkSources()"}

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
