# 节点版本审查报告

## 检查批次 2026-11-18 09:42:13 UTC

### tari

#### v6.3.0-pre.2 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** 🔎 **共识/区块有效性差异**（已确认）：`base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 与 `base_layer/core/src/validation/block_body/block_body_partial_validator.rs` 使同哈希输出重建后被花费的区块新旧版本判定不同，仅影响含该重复输出形态的链，未证明 mainnet 历史存在该形态，发行说明未声明硬分叉 · ✅ **稳定性/数据**（修复）：`infrastructure/libtor/Cargo.toml` 升级内置 Tor 0.4.9.15 修复当前 Tor consensus 下基础节点退出，`base_layer/core/src/chain_storage/blockchain_database.rs` 拒绝乱序 body 避免被当作该头承诺的块存库，`base_layer/core/src/chain_storage/active_validator_node.rs` 对旧格式验证人条目要求重同步 · ✅ **安全**（修复）：`applications/minotari_app_grpc/src/authentication/basic_auth.rs` 以常数时间比对替代每请求 Argon2id 校验消除未认证请求的 CPU 放大，`applications/minotari_app_grpc/src/conversions/unblinded_output.rs` 在所有退出路径清零私钥并对 Debug 打码
- **处置建议：** 预发布版重大事项 · 重点关注
- **建议理由：** 已确认硬分叉或重大共识变更，应核对网络生效条件和节点兼容要求。 当前为预发布版，不建议直接用于生产升级；应评估现网影响并跟进正式版。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** 内置 Tor 崩溃修复（此前预发布差异已确认并仍存在于目标 tag）：`infrastructure/libtor/Cargo.toml` 将捆绑库换为 tari-libtor 49.15.2（Tor 0.4.9.15）。发行说明称旧版基础节点在当前 Tor consensus 下直接退出，升级后不再退出，影响范围限于 unix 使用内置 Tor 的构建，崩溃机制位于捆绑库内。
2. **已确认 — 硬分叉/共识：** 范围受限的区块判定差异：`base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 现放行同 body 内重建并花费同哈希输出的交易，`base_layer/core/src/validation/block_body/block_body_partial_validator.rs` 改按本次花费实例配对，含重复输出形态的链上新旧版本对同一区块接受与否不同。未证明 mainnet 历史存在该形态，发行说明未声明硬分叉，不构成全网升级要求。
3. **已确认 — 稳定性/数据：** 升级需重同步（条件性风险）：`base_layer/core/src/chain_storage/active_validator_node.rs` 的 `ValidatorNodeEntry` 新增必需字段 `original_registration`，旧版本写入的验证人条目反序列化报错并提示 must be resynced，查询验证人存储失败需重同步。仅影响链库已有旧格式验证人条目的节点，mainnet 是否存在此类条目未证明。
4. **已确认 — 稳定性/数据：** 同步数据完整性修复：`base_layer/core/src/chain_storage/blockchain_database.rs` 现要求 body 有序才视为其头承诺的块，修复前恶意同步对端可让乱序 body 被当作该头的块存库，修复后拒绝并封禁对端。范围限于同步/取块路径的远程对端。
5. **已确认 — 安全：** gRPC 认证 CPU 放大修复：`applications/minotari_app_grpc/src/authentication/basic_auth.rs` 用常数时间比对替代每请求一次的 Argon2id 校验，并在拦截器增加按源 IP 失败退避，修复未认证请求触发高成本口令校验的 CPU 消耗。仅影响开启 Basic auth 且暴露 gRPC 的节点。
6. **已确认 — 安全：** 密钥暴露修复：`applications/minotari_app_grpc/src/conversions/unblinded_output.rs` 用 Drop 守卫在所有退出路径清零 `spending_key` 与 `script_private_key` 并手写 Debug 打码，修复出错路径残留私钥及派生 Debug 打印密钥的问题。
7. **已确认 — 稳定性/数据：** 分叉接收修复：`base_layer/core/src/chain_storage/blockchain_database.rs` 对候选头的链头查找改用 optional，修复分叉高度高于主 tip 时无法存储分叉块的问题，长分叉重组接收更稳定。

##### 版本信息

发布于 2026-10-29T01:28:17Z · 比较 `v6.3.0-pre.1` → `v6.3.0-pre.2` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.2)


#### v6.3.0-pre.4 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** 🔎 **共识/区块有效性差异**（已确认）：`base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 的链上 timelock 校验高度收紧使 `min_spendable_height` 为 H+1 的区块旧版接受而新版拒绝，另有 `base_layer/core/src/chain_storage/lmdb_db/validator_node_store.rs` 的激活 epoch 修复可能使新旧节点算出不同 `validator_node_mr`，发行说明未声明硬分叉或激活高度且未证明主网历史存在这些形态 · ✅ **稳定性/数据**（修复）：`base_layer/core/src/chain_storage/blockchain_database.rs` 与 `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 修复一致性检查误报损坏和非原子深回卷，`infrastructure/libtor/src/tor.rs` 修复内置 Tor 日志路径大小写导致的启动失败 · ✅ **安全**（修复）：`comms/dht/src/network_discovery/admission.rs` 与 `comms/dht/src/inbound/dht_handler/join_gate.rs` 修复远程 Join 灌注 peer DB 并拖停同步的资源耗尽，`comms/core/src/protocol/rpc/client/mod.rs` 修复远端陈旧帧可无限挂起 RPC 客户端请求
- **处置建议：** 预发布版重大事项 · 重点关注
- **建议理由：** 已确认硬分叉或重大共识变更，应核对网络生效条件和节点兼容要求。 当前为预发布版，不建议直接用于生产升级；应评估现网影响并跟进正式版。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 硬分叉/共识：** `base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 将链上 timelock 校验由 min_spendable_height 大于 H+1 才拒绝收紧为大于 H 即拒绝且 spend_height 为区块自身高度，min_spendable_height 恰为 H+1 的区块旧版接受而新版拒绝。这是区块有效性规则收紧，发行说明未声明硬分叉或激活高度，未证明主网历史存在该形态。
2. **已确认 — 硬分叉/共识：** `base_layer/core/src/chain_storage/lmdb_db/validator_node_store.rs` 的 `get_next_activation_epoch` 修复旧版比较搜索 key 造成的死循环与跨 sidechain 误计，旧版对含 sidechain VN 注册的区块可能算出不同的 validator_node_mr 并与新版互相拒绝，前提是目标网络已启用 VN/sidechain 注册且未证明 mainnet 现状。
3. **已确认 — 硬分叉/共识：** `base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 与 `base_layer/transaction_components/src/validation/aggregate_body/aggregate_body_internal_validator.rs` 新增非 burn kernel 不得携带 burn commitment 的检查，旧版放行该组合而新版拒绝，仅影响未来构造的异常交易形态且未证明主网历史存在该形态。
4. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs` 与 `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 修复一致性检查在重组或瞬时存储失败时把健康库误判为损坏并 autocorrect 回卷，旧版在开启 autocorrect 的一致性检查路径上可能把剪枝节点重置到创世并要求全量重同步。
5. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs`、`base_layer/core/src/chain_storage/db_transaction.rs` 与 `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 把剪枝节点越过剪枝界的深回卷改为单事务原子重置到创世，旧版分段删除会遗留不一致的孤儿链 tip 状态，仅影响剪枝节点深回卷场景。
6. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs` 与 `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 修复孤儿链 tip 累计难度索引并在启动时重索引，旧版索引错误可使弱分叉被优先尝试或掩盖强分叉从而影响重组选链，不改变区块最终有效性规则。
7. **已确认 — 稳定性/数据：** `infrastructure/libtor/src/tor.rs` 修复内置 Tor 日志路径含大写字母时被转小写导致 Tor 初始化失败节点起不来的问题，仅影响使用内置 Tor 且日志路径含大写字母并运行在大小写敏感文件系统的构建。
8. **已确认 — 安全：** `comms/dht/src/network_discovery/admission.rs`、`comms/dht/src/inbound/dht_handler/join_gate.rs` 与 `comms/dht/src/network_discovery/on_connect.rs` 为 Join 中继和 OnConnect 同步加入按来源预算与冷却，旧版任一连接对端可持续投递新身份 Join 灌注 peer DB 并拖停其他同步连接，属受支持 p2p 路径的远程资源耗尽修复。
9. **已确认 — 安全：** `comms/core/src/protocol/rpc/client/mod.rs` 将 RPC 客户端读超时改为每请求一次共享 deadline，旧版远端服务端可不断发送陈旧帧使客户端请求被无限期挂起，流式响应仍保持每项独立 deadline。
10. **已确认 — 安全：** `comms/dht/src/connectivity/metrics.rs`、`comms/dht/src/inbound/metrics.rs` 与 `comms/dht/src/dedup/mod.rs` 重写洪泛封禁计数使断线重连不再清零样本，旧版洪泛对端可借重连逃过封禁，属范围有限的防御性修复。
11. **已确认 — 安全：** `base_layer/mmr/src/merkle_proof.rs` 与 `base_layer/mmr/src/merkle_mountain_range.rs` 为 `MerkleProof::verify` 加入叶位置与边界检查并修复叶索引查找，旧版可用空 path 与 peaks 的伪造证明通过校验，本次差异未展示其共识或资金调用路径故影响范围有限。

##### 版本信息

发布于 2026-11-10T11:57:54Z · 比较 `v6.3.0-pre.2` → `v6.3.0-pre.4` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.4)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
