# 节点版本审查报告

## 检查批次 2026-11-18 07:57:36 UTC

### tari

#### v6.3.0-pre.2 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** 🚨 **破坏性变更**（已确认）：`base_layer/core/src/chain_storage/active_validator_node.rs` 的 `ValidatorNodeEntry` 新增必需字段 `original_registration` 旧库条目解码失败，代码要求重同步数据库 · 🚨 **重大共识变更**（已确认）：`base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 对同哈希输出重新挖出后的花费改为接受，旧归档节点对同一区块判无效，发行说明未声明硬分叉 · ✅ **稳定性/数据**（修复）：`infrastructure/libtor/Cargo.toml` 升级捆绑 Tor 至 0.4.9.15 修复基节点在当前 Tor 共识下退出，另有 `base_layer/core/src/chain_storage/blockchain_database.rs` 与 `base_layer/core/src/base_node/comms_interface/inbound_handlers.rs` 的跟链与输出查询修复 · ✅ **安全**（修复）：`applications/minotari_app_grpc/src/authentication/server_interceptor.rs` 与 `basic_auth.rs` 取消每请求 Argon2id 改为常数时间比较并按来源 IP 退避，修复未认证 gRPC 认证端点的 CPU 内存放大 DoS
- **处置建议：** 预发布版重大事项 · 重点关注
- **建议理由：** 已确认硬分叉或重大共识变更，应核对网络生效条件和节点兼容要求。 当前为预发布版，不建议直接用于生产升级；应评估现网影响并跟进正式版。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 此前预发布已确认的捆绑依赖缺陷，使用捆绑 Tor 的基节点在当前 Tor 共识下会直接退出，`infrastructure/libtor/Cargo.toml` 将 `libtor` 换为 `tari-libtor-core` 49.15.2（Tor 0.4.9.15）后不再退出，影响使用捆绑 libtor 的构建，外置 Tor 用户不受此影响。
2. **已确认 — 硬分叉/共识：** `base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 中同哈希输出被再次挖出后，花费其历史实例的交易由拒绝改为接受，保留花费历史的旧归档节点会对同一 mainnet 区块判无效而新节点接受，同时修复了归档与剪枝节点此前的判定分歧。
3. **已确认 — 破坏性变更：** `base_layer/core/src/chain_storage/active_validator_node.rs` 为 `ValidatorNodeEntry` 新增必需字段后旧版本写入的条目解码失败，升级节点读取验证节点集合（`base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 的 fetch 类接口）会报错并要求重同步数据库。
4. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs` 的 `get_vm_key_for_candidate_header` 改为可选查询，修复分叉增长越过主链 tip 时无法接纳该分叉导致跟链重组失败的问题。
5. **已确认 — 稳定性/数据：** `base_layer/core/src/base_node/comms_interface/inbound_handlers.rs`、`base_layer/core/src/base_node/rpc/query_service.rs` 配合 `base_layer/core/src/chain_storage/utxo_mined_info.rs` 的 `MinedInfo::latest`，修复重新挖出的输出被误报为已花费影响钱包判定的问题。
6. **已确认 — 安全：** `applications/minotari_app_grpc/src/authentication/server_interceptor.rs` 删除每请求 Argon2id 校验，旧版暴露 gRPC 认证端点的节点可被未认证来源以低成本放大 CPU 与内存开销，新版改为常数时间凭据比较并按来源 IP 指数退避。
7. **已确认 — 安全：** `applications/minotari_app_grpc/src/conversions/unblinded_output.rs` 用 Drop 守卫覆盖全部退出路径并脱敏 Debug，修复提前返回时 spending key 留存堆内存的问题，利用需额外的内存泄露或转储条件，影响有限。

##### 版本信息

发布于 2026-10-29T01:28:17Z · 比较 `v6.3.0-pre.1` → `v6.3.0-pre.2` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.2)


#### v6.3.0-pre.4 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** 🚨 **重大共识变更**（已确认）：`base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 与 `base_layer/transaction_components/src/validation/aggregate_body/aggregate_body_internal_validator.rs` 收紧时间锁与 burn 内核规则，新旧节点对同一 mainnet 区块接受结果不同，发行说明未声明硬分叉 · ✅ **稳定性/数据**（修复）：`base_layer/core/src/chain_storage/blockchain_database.rs` 修复一致性检查把健康库误判为损坏并在 autocorrect 下无复检回滚健康链的既有问题 · ✅ **安全**（修复）：`base_layer/core/src/base_node/sync/horizon_state_sync/synchronizer.rs` 对对端 outputs 与 kernels 流加上条目预算，修复剪枝节点 horizon sync 期间可被恶意同步对端拖垮 CPU 与内存的既有问题
- **处置建议：** 预发布版重大事项 · 重点关注
- **建议理由：** 已确认硬分叉或重大共识变更，应核对网络生效条件和节点兼容要求。 当前为预发布版，不建议直接用于生产升级；应评估现网影响并跟进正式版。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 矿工模板修复 `base_layer/core/src/mempool/unconfirmed_pool/unconfirmed_pool.rs` 与 `base_layer/core/src/mempool/mempool.rs` 现按模板高度过滤未成熟输入和被锁定内核并重检高度敏感脚本，pre.2 的模板可能包含在出块高度即无效的交易导致矿工产出被拒区块。
2. **已确认 — 硬分叉/共识：** `base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 将链上时间锁校验从 header.height+1 改为 header.height，高度 h 区块中内核 lock_height 或输入 maturity 为 h+1 的交易 pre.2 接受、pre.4 拒绝，同一 mainnet 区块在新旧节点接受不同，代码与测试未声明网络分叉或激活高度。
3. **已确认 — 硬分叉/共识：** `base_layer/transaction_components/src/validation/aggregate_body/aggregate_body_internal_validator.rs` 与 `base_layer/transaction_components/src/transaction_builder/builder.rs` 新增拒绝非 burn 内核携带 burn_commitment，pre.2 接受此类区块而 pre.4 拒绝。
4. **已确认 — 硬分叉/共识：** `base_layer/core/src/validation/difficulty_calculator.rs`、`base_layer/core/src/validation/header/header_full_validator.rs` 与 `base_layer/core/src/chain_storage/blockchain_database.rs` 改用候选自身链的 RandomX VM key 计算侧链难度，同一深分叉区块 pre.2 因取主链 key 而拒绝、pre.4 接受。
5. **已确认 — 硬分叉/共识：** `base_layer/core/src/chain_storage/lmdb_db/validator_node_store.rs` 修正 validator node 激活 epoch 的限额归属，仅在存在多 sidechain 注册且触及每 epoch 上限时 epoch 边界头的 validator_node_mr 在新旧版本间不同。
6. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 与 `base_layer/core/src/chain_storage/db_transaction.rs` 把越过 pruning horizon 的 rewind 改为单次原子重置到创世，主网剪枝节点深回退后需从创世全量重同步，取代 pre.2 留下不一致状态的部分删除行为。
7. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs` 修复一致性检查在与重组并发时误报 CorruptedDatabase 并在 autocorrect 下回滚健康链的问题，现改为复检后才回滚并区分存储访问失败。
8. **已确认 — 稳定性/数据：** `base_layer/core/src/base_node/sync/header_sync/validator.rs` 修正中位时间戳窗口按高度序维护，pre.2 会拒绝合法头并写入 bad block 造成误拉黑，pre.4 不再误封。
9. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs` 与 `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 修复孤儿链 tip 的难度索引与悬空 tip 残留，启动时修复损坏 tip 并整棵清理孤儿子树。
10. **已确认 — 安全：** `base_layer/core/src/base_node/sync/horizon_state_sync/synchronizer.rs` 为 outputs 与 kernels 流新增条目预算与慢速投放限制，pre.2 在剪枝节点 horizon sync 期间对恶意同步对端无上限验证并累积条目可造成远程资源耗尽。
11. **已确认 — 安全：** `comms/dht/src/network_discovery/admission.rs`、`comms/dht/src/inbound/dht_handler/join_gate.rs` 与 `comms/dht/src/dedup/mod.rs` 为 Join 与 OnConnect 对等入库加来源预算与冷却并限制复制洪泛，pre.2 任一来源可无限写入对等库挤掉诚实记录，同时 `comms/dht/src/inbound/metrics.rs` 修正转发流量误计导致诚实中继被封禁的问题。
12. **已确认 — 安全：** `comms/core/src/protocol/rpc/client/mod.rs` 改为每请求武装一次读截止时间，pre.2 中恶意对端持续投递被忽略的旧 request_id 帧可无限期拖住单次 RPC 请求。
13. **已确认 — 安全：** `base_layer/core/src/mempool/unconfirmed_pool/unconfirmed_pool.rs` 改为仅按输出承诺匹配已上链花费，pre.2 中一个携带伪造 burn_commitment 的区块即可把无关待确认交易从全网节点 mempool 驱逐，另 `base_layer/core/src/base_node/comms_interface/inbound_handlers.rs` 将 gossip 新块难度门槛的回退遍历加界并限制 RandomX key 取用，封堵公告触发的无界数据库遍历。

##### 版本信息

发布于 2026-11-10T11:57:54Z · 比较 `v6.3.0-pre.2` → `v6.3.0-pre.4` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.4)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
