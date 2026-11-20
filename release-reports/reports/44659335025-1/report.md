# 节点版本审查报告

## 检查批次 2026-11-20 02:19:57 UTC

### aleo

#### v4.13.1 · 正式版 · 完整审查
<!-- watch-repo: aleo-labs-protocol/snarkOS -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 按需升级 · 需关注
- **建议理由：** 存在 P2 级变化或修复；先核对适用平台、节点模式及配置，受影响时再安排维护窗口，不属于强制升级要求。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 新增升级安全闸门（`node/bft/src/helpers/upgrade_monitor.rs`）在委员会成员声明更高共识版本、且连接 quorum stake 未反驳时，经 `node/consensus/src/lib.rs` 的 `ensure_block_may_be_built` 阻止该验证器在特定高度出块；在验证器模式下，恶意/故障成员配合连接的非反驳 stake 不足 quorum 时可条件性阻碍出块（区块同步仍推进），为有界可用性风险。 代码证据：{"path": "node/bft/src/helpers/upgrade_monitor.rs", "quote": "if is_claimed && !self.is_refuted(&state, committee, connected, Some(height)) {\n            return Err(BlockHeldBack(format!(\n                \"Validators may run a newer consensus version than this build at height {height}, and connected \\\n                 validators holding a quorum of stake have not refuted it\"\n            ))\n            .into());\n        }"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "self.bft.primary().gateway().ensure_block_may_be_built(block_height)?;"}
2. **已确认 — 兼容性：** `snarkos_consensus_unconfirmed_transactions_total` 与 `snarkos_consensus_unconfirmed_solutions_total` 由 gauge 改为 counter（`node/metrics/src/names.rs`、`node/consensus/src/lib.rs`），会破坏把二者当 gauge 的既有监控/告警查询，监控消费方需更新。 代码证据：{"path": "node/metrics/src/names.rs", "quote": "pub(super) const COUNTER_NAMES: [&str; 7] = [\n    bft::LEADERS_ELECTED,\n    bft::PEER_PROPOSALS_MALFORMED,\n    consensus::STALE_UNCONFIRMED_TRANSACTIONS,\n    consensus::STALE_UNCONFIRMED_SOLUTIONS,\n    consensus::DROPPED_TRANSACTIONS,\n    consensus::UNCONFIRMED_SOLUTIONS,\n    consensus::UNCONFIRMED_TRANSACTIONS,\n];"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "metrics::increment_counter(metrics::consensus::UNCONFIRMED_SOLUTIONS);"}
3. **已确认 — 兼容性：** `snarkos developer` 未标注 API 版本的 `--endpoint` 默认改走 `/v2`（此前默认 v1），并拒绝带查询字符串的 URL（`cli/src/helpers/args.rs`）；显式 `/v1`、`/v2` 端点行为不变。，代码路径：`cli/src/commands/developer/mod.rs` 代码证据：{"path": "cli/src/helpers/args.rs", "quote": "pub(crate) fn prepare_endpoint(endpoint: Uri) -> Result<Uri> {\n    ensure!(endpoint.query().is_none(), \"The endpoint URL must not have a query string\");"} 代码证据：{"path": "cli/src/helpers/args.rs", "quote": "pub(crate) fn api_version_of(path: &str) -> Option<ApiVersion> {\n    match path.trim_end_matches('/').rsplit('/').next() {\n        Some(API_VERSION_V1) => Some(ApiVersion::V1),\n        Some(API_VERSION_V2) => Some(ApiVersion::V2),\n        _ => None,\n    }\n}"} 代码证据：{"path": "cli/src/commands/developer/mod.rs", "quote": "        let api_version = api_version_of(base_url.path())\n            .context(\"The endpoint URL must end in an API version (v1 or v2). Use `prepare_endpoint` first\")?;"}
4. **已确认 — 兼容性：** 握手与事件协议版本升至 12，新增共识排程与创世哈希交换及 GenesisMismatch 断开（`node/bft/events/src/lib.rs`、`node/bft/src/gateway.rs`）；接受下限保持 10，trailer 位于旧布局之后，v4.12.x 节点仍可与本版本互连。，代码路径：`node/bft/events/src/helpers/handshake.rs` 代码证据：{"path": "node/bft/events/src/lib.rs", "quote": "    pub const MINIMUM_VERSION: u32 = 10;"} 代码证据：{"path": "node/bft/events/src/lib.rs", "quote": "    pub const VERSION: u32 = 12;"} 代码证据：{"path": "node/bft/events/src/helpers/handshake.rs", "quote": "        let signature = Data::read_le(&mut reader)?;\n        let trailer = HandshakeTrailer::read_le(&mut reader)?;\n\n        Ok(Self { info, signature, trailer })"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "        if info.version >= HandshakeTrailer::FIRST_VERSION && trailer.schedule.is_none() {\n            warn!(\n                \"{CONTEXT} Handshake with '{peer_addr}' failed (version {} sent no consensus schedule)\",\n                info.version\n            );\n            return Some(DisconnectReason::ProtocolViolation);\n        }"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "        if let Some(genesis_hash) = &trailer.genesis_hash\n            && genesis_hash[..] != expected_genesis_hash[..]\n        {\n            warn!(\"{CONTEXT} Handshake with '{peer_addr}' failed (incorrect genesis hash)\");\n            return Some(DisconnectReason::GenesisMismatch);\n        }"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "                if version < Event::<N>::MINIMUM_VERSION {\n                    bail!(\"Dropping '{peer_ip}' on event version {version} (outdated)\");\n                }"}
5. **已确认 — 安全：** 依赖安全更新：`tracing-subscriber` 升至 0.3.23、`libz-sys` 升至 1.1.33，对应 RUSTSEC-2025-0055、RUSTSEC-2026-0544（`Cargo.toml`、`Cargo.lock`）；未展示漏洞在节点运行中的可利用路径，按低影响处理。 代码证据：{"path": "Cargo.toml", "quote": "[workspace.dependencies.tracing-subscriber]\nversion = \"0.3.23\""} 代码证据：{"path": "Cargo.lock", "quote": "[[package]]\nname = \"tracing-subscriber\"\nversion = \"0.3.23\""} 代码证据：{"path": "Cargo.lock", "quote": "[[package]]\nname = \"libz-sys\"\nversion = \"1.1.33\""}

##### 版本信息

发布于 2026-11-17T16:31:34Z · 比较 `v4.12.1` → `v4.13.1` · [打开 Release](https://github.com/aleo-labs-protocol/snarkOS/releases/tag/v4.13.1)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
