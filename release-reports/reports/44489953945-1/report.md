# 节点版本审查报告

## 检查批次 2026-11-19 09:16:09 UTC

### aleo

#### v4.13.1 · 正式版 · 完整审查
<!-- watch-repo: aleo-labs-protocol/snarkOS -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 必须升级 · 需关注
- **建议理由：** 已确认破坏性或兼容性变更，需要升级并核对现有配置。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 升级监视器的出块闸门在存在未被 quorum 反驳的更新共识时间表声明时拒绝该验证器在特定高度出块（`node/bft/src/helpers/upgrade_monitor.rs`，由 `node/consensus/src/lib.rs` 在建块前调用）。验证器模式下若委员会成员声明或误配更新的共识时间表、且本节点连接的反驳 stake 不足 quorum，可能被选择性阻碍出块（区块同步仍推进），属条件性可用性风险。 代码证据：{"path": "node/bft/src/helpers/upgrade_monitor.rs", "quote": "if is_claimed && !self.is_refuted(&state, committee, connected, Some(height)) {\n            return Err(BlockHeldBack(format!(\n                \"Validators may run a newer consensus version than this build at height {height}, and connected \\\n                 validators holding a quorum of stake have not refuted it\"\n            ))\n            .into());\n        }"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "self.bft.primary().gateway().ensure_block_may_be_built(block_height)?;"}
2. **已确认 — 兼容性：** `snarkos_consensus_unconfirmed_transactions_total` 与 `snarkos_consensus_unconfirmed_solutions_total` 由 gauge 改为 counter（`node/metrics/src/names.rs`、`node/consensus/src/lib.rs`），会破坏按 gauge 语义编写的监控/告警查询，与发行说明 Metrics 项一致。 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "                metrics::increment_gauge(metrics::consensus::UNCONFIRMED_SOLUTIONS, 1f64);"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "                metrics::increment_counter(metrics::consensus::UNCONFIRMED_SOLUTIONS);"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "                metrics::increment_gauge(metrics::consensus::UNCONFIRMED_TRANSACTIONS, 1f64);"} 代码证据：{"path": "node/consensus/src/lib.rs", "quote": "                metrics::increment_counter(metrics::consensus::UNCONFIRMED_TRANSACTIONS);"} 代码证据：{"path": "node/metrics/src/names.rs", "quote": "pub(super) const COUNTER_NAMES: [&str; 4] = ["} 代码证据：{"path": "node/metrics/src/names.rs", "quote": "pub(super) const COUNTER_NAMES: [&str; 7] = ["} 代码证据：{"path": "node/metrics/src/names.rs", "quote": "pub(super) const GAUGE_NAMES: [&str; 33] = ["} 代码证据：{"path": "node/metrics/src/names.rs", "quote": "pub(super) const GAUGE_NAMES: [&str; 31] = ["}
3. **已确认 — 兼容性：** 握手与事件协议升级到版本 12，`HandshakeTrailer` 追加在旧布局之后、接受下限保持 10，并对不同创世哈希的对端断开连接（GenesisMismatch）；事件版本低于 10 的对端才被拒绝，旧版互通保留。，代码路径：`node/bft/events/src/helpers/handshake.rs`、`node/bft/events/src/lib.rs`、`node/bft/src/gateway.rs` 代码证据：{"path": "node/bft/events/src/lib.rs", "quote": "    pub const MINIMUM_VERSION: u32 = 10;"} 代码证据：{"path": "node/bft/events/src/lib.rs", "quote": "    pub const VERSION: u32 = 12;"} 代码证据：{"path": "node/bft/events/src/helpers/handshake.rs", "quote": "        let signature = Data::read_le(&mut reader)?;\n        let trailer = HandshakeTrailer::read_le(&mut reader)?;\n\n        Ok(Self { info, signature, trailer })"} 代码证据：{"path": "node/bft/events/src/helpers/handshake.rs", "quote": "        let bytes = ResponderInfo { info, trailer }.to_bytes_le().unwrap();\n        assert_eq!(PeerInfo::<CurrentNetwork>::from_bytes_le(&bytes).unwrap(), info);"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "        if info.version >= HandshakeTrailer::FIRST_VERSION && trailer.schedule.is_none() {\n            warn!(\n                \"{CONTEXT} Handshake with '{peer_addr}' failed (version {} sent no consensus schedule)\",\n                info.version\n            );\n            return Some(DisconnectReason::ProtocolViolation);\n        }"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "        if let Some(genesis_hash) = &trailer.genesis_hash\n            && genesis_hash[..] != expected_genesis_hash[..]\n        {\n            warn!(\"{CONTEXT} Handshake with '{peer_addr}' failed (incorrect genesis hash)\");\n            return Some(DisconnectReason::GenesisMismatch);\n        }"} 代码证据：{"path": "node/bft/src/gateway.rs", "quote": "                if version < Event::<N>::MINIMUM_VERSION {\n                    bail!(\"Dropping '{peer_ip}' on event version {version} (outdated)\");\n                }"}
4. **已确认 — 兼容性：** `snarkos developer` 的端点若未标注 API 版本则默认改走 v2（此前默认 v1），并拒绝带查询字符串的 URL；显式 /v1、/v2 端点行为不变。，代码路径：`cli/src/commands/developer/mod.rs`、`cli/src/helpers/args.rs` 代码证据：{"path": "cli/src/helpers/args.rs", "quote": "pub(crate) fn prepare_endpoint(endpoint: Uri) -> Result<Uri> {\n    ensure!(endpoint.query().is_none(), \"The endpoint URL must not have a query string\");"} 代码证据：{"path": "cli/src/helpers/args.rs", "quote": "pub(crate) fn api_version_of(path: &str) -> Option<ApiVersion> {\n    match path.trim_end_matches('/').rsplit('/').next() {\n        Some(API_VERSION_V1) => Some(ApiVersion::V1),\n        Some(API_VERSION_V2) => Some(ApiVersion::V2),\n        _ => None,\n    }\n}"} 代码证据：{"path": "cli/src/commands/developer/mod.rs", "quote": "        let api_version = api_version_of(base_url.path())\n            .context(\"The endpoint URL must end in an API version (v1 or v2). Use `prepare_endpoint` first\")?;"}
5. **已确认 — 安全：** 依赖安全更新：`tracing-subscriber` 升至 0.3.23（RUSTSEC-2025-0055）、`libz-sys` 升至 1.1.33（RUSTSEC-2026-0544）已写入 `Cargo.toml`/`Cargo.lock`；现有证据未显示节点运行中的可利用路径，按低影响处理。 代码证据：{"path": "Cargo.toml", "quote": "[workspace.dependencies.tracing-subscriber]\nversion = \"0.3.23\""} 代码证据：{"path": "Cargo.lock", "quote": "[[package]]\nname = \"tracing-subscriber\"\nversion = \"0.3.23\""} 代码证据：{"path": "Cargo.lock", "quote": "[[package]]\nname = \"libz-sys\"\nversion = \"1.1.33\""}

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
1. **已确认 — 稳定性/数据：** 修复 `flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala` 中内存池祖先清理在重复父边或重叠祖先路径下对同一祖先重复移除/重复执行 sideEffect 的问题（对应发行说明所述 mempool cache issue），影响矿池与节点的内存池维护路径；升级后每个祖先只移除一次，区块有效性不受影响。，代码路径：`flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala` 代码证据：{"path": "flow/src/main/scala/org/alephium/flow/mempool/KeyedFlow.scala", "quote": "    node.getParents().foreach(_.foreach(parent => removeNodeAndAncestors(parent.key, sideEffect)))"} 代码证据：{"path": "flow/src/test/scala/org/alephium/flow/mempool/KeyedFlowSpec.scala", "quote": "  it should \"remove each ancestor once with duplicate parent edges\" in {\n    val flow = Flow(ConcurrentHashMap.empty[K, N], ConcurrentHashMap.empty, _ => 0)\n    flow.addNewNode(flow.newNode(0, Seq.empty))\n    flow.addNewNode(flow.newNode(1, Seq(0, 0)))\n    var removed = Seq.empty[Int]\n\n    flow.removeNodeAndAncestors(1, node => removed = removed :+ node.value)\n\n    removed is Seq(1, 0)"}

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
- **处置建议：** 建议升级 · 不重要
- **建议理由：** 包含已确认的重要修复或风险，建议在维护窗口升级。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 修复 `src/util/fs_helpers.cpp` 的 `AllocateFileRange` 与 `src/streams.cpp` 的 `AutoFile` 文件位置处理：升级前分配范围会移动调用方 FILE 流位置而不恢复、失败的 seek/读写后仍沿用陈旧缓存位置，在分配与写入共用同一流（Windows 及无 posix_fallocate 回退路径）时可致缓冲写入落到错误偏移；升级后改为保存/恢复流位置、在读写之间重新定位并在失败后重新查询文件位置。 代码证据：{"path": "src/util/fs_helpers.cpp", "quote": "    const int64_t pos{FileTell64(file)};\n    if (pos < 0 || FileSeek64(file, pos, SEEK_SET) != 0) return;\n    AllocateFileRangeUnsynced(file, offset, length);\n    FileSeek64(file, pos, SEEK_SET);"} 代码证据：{"path": "src/util/fs_helpers.cpp", "quote": "        if (0 != FileSeek64(file, -static_cast<int64_t>(rlen), SEEK_CUR)) {\n            return;\n        }\n        fwrite(buf, 1, now, file); // allowed to fail; this function is advisory anyway\n        if (0 != FileSeek64(file, 0, SEEK_CUR)) {\n            return;\n        }\n        length -= now;"} 代码证据：{"path": "src/streams.cpp", "quote": "    if (FileSeek64(m_file, offset, origin) != 0) {\n        m_position_cache.reset();\n        throw std::ios_base::failure(feof() ? \"AutoFile::seek: end of file\" : \"AutoFile::seek: fseek failed\");\n    }"} 代码证据：{"path": "src/streams.cpp", "quote": "    size_t ret = std::fread(dst.data(), 1, dst.size(), m_file);\n    if (m_obfuscation) {\n        if (!m_position_cache.has_value()) throw std::ios_base::failure(\"AutoFile::read: position unknown\");\n        m_obfuscation(dst.subspan(0, ret), *m_position_cache);\n    }\n    if (m_position_cache.has_value()) *m_position_cache += ret;"}

##### 版本信息

发布于 2026-11-06T18:40:26Z · 比较 `v29.4.3.knots20260508` → `v29.5.knots20260508` · [打开 Release](https://github.com/bitcoinknots/bitcoin/releases/tag/v29.5.knots20260508)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
