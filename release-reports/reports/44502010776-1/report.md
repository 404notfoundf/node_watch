# 节点版本审查报告

## 检查批次 2026-11-19 10:21:33 UTC

### aleo

#### v4.13.1 · 正式版 · 完整审查
<!-- watch-repo: aleo-labs-protocol/snarkOS -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 建议升级 · 需关注
- **建议理由：** 存在 P2 级变化或修复；先核对适用平台、节点模式及配置，受影响时再安排维护窗口，不属于强制升级要求。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 验证器模式新增升级监视器出块闸门：当委员会成员声明的共识排程领先、且本节点连接的验证者 stake 未构成 quorum 反驳时，该验证器在特定高度拒绝构建区块（区块同步仍推进）。触发依赖委员会成员声明与连接 stake 分布，属条件性可用性风险，非全网节点必然受影响。，代码路径：`node/bft/src/helpers/upgrade_monitor.rs`、`node/consensus/src/lib.rs` 代码证据：{"path": "node/bft/src/helpers/upgrade_monitor.rs", "quote": "if is_claimed && !self.is_refuted(&state, committee, connected, Some(height)) {\n            return Err(BlockHeldBack(format!(\n                \"Validators may run a newer consensus version than this build at height {height}, and connected \\\n                 validators holding a quorum of stake have not refuted it\"\n            ))\n            .into());\n        }"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "self.bft.primary().gateway().ensure_block_may_be_built(block_height)?;"}
2. **已确认 — 兼容性：** `snarkos_consensus_unconfirmed_transactions_total` 与 `snarkos_consensus_unconfirmed_solutions_total` 由 gauge 改为 counter，会破坏把二者按 gauge 采集或告警的监控查询，需更新对应面板与 PromQL。，代码路径：`node/consensus/src/lib.rs`、`node/metrics/src/names.rs` 代码证据：{"path": "node/metrics/src/names.rs", "quote": "pub(super) const COUNTER_NAMES: [&str; 7] = [\n    bft::LEADERS_ELECTED,\n    bft::PEER_PROPOSALS_MALFORMED,\n    consensus::STALE_UNCONFIRMED_TRANSACTIONS,\n    consensus::STALE_UNCONFIRMED_SOLUTIONS,\n    consensus::DROPPED_TRANSACTIONS,\n    consensus::UNCONFIRMED_SOLUTIONS,\n    consensus::UNCONFIRMED_TRANSACTIONS,\n];"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "metrics::increment_counter(metrics::consensus::UNCONFIRMED_SOLUTIONS);"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "                metrics::increment_gauge(metrics::consensus::UNCONFIRMED_SOLUTIONS, 1f64);"}
3. **已确认 — 兼容性：** 网关握手与事件协议升至版本 12，握手在旧布局后追加 `HandshakeTrailer` 并新增共识排程与创世哈希校验，创世哈希不匹配的对端被断开；接受下限仍为 10，v4.12.x 与 v4.13.x 仍可双向互连。，代码路径：`node/bft/events/src/helpers/handshake.rs`、`node/bft/events/src/lib.rs`、`node/bft/src/gateway.rs` 代码证据：{"path": "node/bft/events/src/lib.rs", "quote": "    pub const MINIMUM_VERSION: u32 = 10;"} 代码证据：{"path": "node/bft/events/src/lib.rs", "quote": "    pub const VERSION: u32 = 12;"} 代码证据：{"path": "node/bft/events/src/helpers/handshake.rs", "quote": "        let signature = Data::read_le(&mut reader)?;\n        let trailer = HandshakeTrailer::read_le(&mut reader)?;\n\n        Ok(Self { info, signature, trailer })"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "        if info.version >= HandshakeTrailer::FIRST_VERSION && trailer.schedule.is_none() {\n            warn!(\n                \"{CONTEXT} Handshake with '{peer_addr}' failed (version {} sent no consensus schedule)\",\n                info.version\n            );\n            return Some(DisconnectReason::ProtocolViolation);\n        }"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "        if let Some(genesis_hash) = &trailer.genesis_hash\n            && genesis_hash[..] != expected_genesis_hash[..]\n        {\n            warn!(\"{CONTEXT} Handshake with '{peer_addr}' failed (incorrect genesis hash)\");\n            return Some(DisconnectReason::GenesisMismatch);\n        }"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "                if version < Event::<N>::MINIMUM_VERSION {\n                    bail!(\"Dropping '{peer_ip}' on event version {version} (outdated)\");\n                }"}
4. **已确认 — 兼容性：** `snarkos developer` 的端点处理改变：带查询字符串的 URL 被拒绝，端点路径须以 API 版本（v1 或 v2）结尾，未标注版本的端点默认改走 v2。显式指定 /v1、/v2 的端点行为不变，仅影响使用该命令的脚本。，代码路径：`cli/src/commands/developer/mod.rs`、`cli/src/helpers/args.rs` 代码证据：{"path": "cli/src/helpers/args.rs", "quote": "pub(crate) fn prepare_endpoint(endpoint: Uri) -> Result<Uri> {\n    ensure!(endpoint.query().is_none(), \"The endpoint URL must not have a query string\");"} 代码证据：{"path": "cli/src/helpers/args.rs", "quote": "pub(crate) fn api_version_of(path: &str) -> Option<ApiVersion> {\n    match path.trim_end_matches('/').rsplit('/').next() {\n        Some(API_VERSION_V1) => Some(ApiVersion::V1),\n        Some(API_VERSION_V2) => Some(ApiVersion::V2),\n        _ => None,\n    }\n}"} 代码证据：{"path": "cli/src/commands/developer/mod.rs", "quote": "        let api_version = api_version_of(base_url.path())\n            .context(\"The endpoint URL must end in an API version (v1 or v2). Use `prepare_endpoint` first\")?;"}
5. **已确认 — 安全：** 依赖安全更新：tracing-subscriber 升至 0.3.23（RUSTSEC-2025-0055）、libz-sys 升至 1.1.33（RUSTSEC-2026-0544），并从依赖审计忽略清单移除对应条目。未显示漏洞在节点运行中的可利用路径，按低影响依赖修复处理。，代码路径：`Cargo.lock`、`Cargo.toml`、`deny.toml` 代码证据：{"path": "Cargo.toml", "quote": "[workspace.dependencies.tracing-subscriber]\nversion = \"0.3.23\""} 代码证据：{"path": "Cargo.lock", "quote": "[[package]]\nname = \"tracing-subscriber\"\nversion = \"0.3.23\""} 代码证据：{"path": "Cargo.lock", "quote": "[[package]]\nname = \"libz-sys\"\nversion = \"1.1.33\""} 代码证据：{"path": "deny.toml", "quote": "  \"RUSTSEC-2025-0055\","}

##### 版本信息

发布于 2026-11-17T16:31:34Z · 比较 `v4.12.1` → `v4.13.1` · [打开 Release](https://github.com/aleo-labs-protocol/snarkOS/releases/tag/v4.13.1)


### alephium

#### v4.7.2 · 正式版 · 完整审查
<!-- watch-repo: alephium/alephium -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 建议升级 · 需关注
- **建议理由：** 上游明确建议运营者升级，建议尽快安排维护窗口并核对适用条件；该声明不等同于已确认的重大代码风险。 上游升级建议，发行说明原文：「Fixed a mempool cache issue, highly recommended for mining pools and node operators.」

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 修复 mempool 依赖图去重缺陷：`flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala` 的 removeNodeAndAncestors 旧实现按节点递归父边，重复父边/重叠祖先路径下同一祖先被多次 sideEffect，现按 key 去重移除，测试覆盖两种图形态且断言每祖先仅移除一次；影响限于依赖图含重复边的 mempool 清理路径。，代码路径：`flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala` 代码证据：{"path": "flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala", "quote": "  def removeNodeAndAncestors(node: N, sideEffect: N => Unit): Unit = {\n    removeNodeFromGraph(node)\n    sideEffect(node)\n    node.getParents().foreach(_.foreach(parent => removeNodeAndAncestors(parent.key, sideEffect)))\n  }"} 代码证据：{"path": "flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala", "quote": "    flow.addNewNode(flow.newNode(1, Seq(0, 0)))\n    var removed = Seq.empty[Int]\n\n    flow.removeNodeAndAncestors(1, node => removed = removed :+ node.value)\n\n    removed is Seq(1, 0)\n    flow.isEmpty is true\n    flow.checkSources()"} 代码证据：{"path": "flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala", "quote": "    flow.addNewNode(flow.newNode(2, Seq(1, 0)))\n    var removed = Seq.empty[Int]\n\n    flow.removeNodeAndAncestors(2, node => removed = removed :+ node.value)\n\n    removed is Seq(2, 1, 0)"}

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
