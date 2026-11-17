<!-- watch-release-keys: W1sidGFyaSIsInRhcmktcHJvamVjdC90YXJpIiwidjYuMy4wLXByZS4yIl0sWyJ0YXJpIiwidGFyaS1wcm9qZWN0L3RhcmkiLCJ2Ni4zLjAtcHJlLjQiXV0 -->
# 节点版本审查报告

## 检查批次 2026-11-17 07:03:08 UTC

### tari

#### v6.3.0-pre.2 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** 🚨 **破坏性变更**（已确认） · 🚨 **重大共识变更**（已确认） · ✅ **安全**（修复） · 🚨 **稳定性/数据**（风险）
- **处置建议：** 预发布版重大事项 · 重点关注
- **建议理由：** 已确认硬分叉或重大共识变更，应核对网络生效条件和节点兼容要求。 当前为预发布版，不建议直接用于生产升级；应评估现网影响并跟进正式版。

##### AI 审查

**代码已确认的发现**

1. **破坏性变更**：`base_layer/core/src/chain_storage/active_validator_node.rs` 为 `ValidatorNodeEntry` 新增必填字段 `original_registration`，`deserialize_original_registration` 对旧版本写入的条目直接报错并提示必须 resync 链库。受支持的原地升级在 `validator_node_store.rs`/`lmdb_db.rs` 的验证节点读取路径解码失败，节点只能重建链库。

2. **硬分叉/共识**：`base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 的 `find_unknown_inputs` 将 `ContainsSTxO` 与 `UnknownInput` 同分支处理，同一 body 内重新铸造并再次花费已花费输出的 body 由旧版拒绝变为新版接受且无高度门控，可接受区块集合随之变化。发行说明未声明硬分叉。

3. **安全**：`applications/minotari_app_grpc/src/authentication/` 用随机填充常数时间比较与每 IP 退避（5 次/60 秒）替换每请求 Argon2id（PR #8170），修复认证 CPU 消耗。多来源 IP 可摊薄退避限制，认证强度依赖口令熵。

4. **安全**：`base_layer/core/src/mempool/service/inbound_handlers.rs` 对加密交易 gossip 直接丢弃，明文来源验证失败一律封禁 `source_peer`（PR #8173），消除加密中继规避封禁的路径。

5. **安全**：`applications/minotari_app_grpc/src/conversions/unblinded_output.rs` 的 `ZeroizeOutputKeys` Drop guard 在所有返回路径清零 `spending_key`/`script_private_key` 并将 Debug 输出脱敏（PR #8166），消除密钥残留与日志泄露。

6. **安全**：`base_layer/core/src/base_node/sync/header_sync/synchronizer.rs` 对短头批次校验声明的累计难度并回 `PeerSentInaccurateChainMetadata`（PR #8160），阻止对端以超报难度误导同步。属同步/对端校验路径，不构成共识变更。

7. **稳定性/数据（修复）**：`base_layer/core/src/chain_storage/blockchain_database.rs` 的 `get_vm_key_for_candidate_header` 改用 `.optional()`（PR #8174），修复孤儿分叉高度超过本地 tip 时祖先查询报 `ValueNotFound` 导致区块无法入库、竞争分叉无法累积的问题。

8. **稳定性/数据（修复）**：`lmdb_db.rs` 重写 `fetch_mined_info_by_output_hash_in_txn` 生命周期配对并让 `prune_output` 只剪枝实际花费的实例，RPC 改用 `MinedInfo::latest`（PR #8175），修复重复输出场景下 `query_deleted` 等查询与剪枝的不一致。

9. **稳定性/数据（修复）**：`blockchain_database.rs` 的 `inputs_and_outputs_match_header` 在比对 MMR 根前要求 body 唯一且有序（PR #8193），乱序 body 不再被当作该头承诺的 body，配套测试覆盖同步封禁与孤儿标记路径。

10. **稳定性/数据（修复）**：libtor 依赖升级捆绑 Tor 0.4.9.15（PR #8194），对应发行说明所述基节点在当前 Tor 共识下退出的修复。

11. **稳定性/数据（风险）**：`applications/minotari_miner/src/stratum/stratum_controller/controller.rs` 改为 16 容量 `sync_channel` 并经 `try_send_to_client` 发送，队列满时丢弃 `FoundSolution` 并计入 dropped 统计。客户端阻塞或突发负载下可能丢失待提交 share 甚至区块方案。

##### 版本信息

发布于 2026-10-29T01:28:17Z · 比较 `v6.3.0-pre.1` → `v6.3.0-pre.2` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.2)


#### v6.3.0-pre.4 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** 🚨 **重大共识变更**（已确认） · 🚨 **兼容性**（已确认） · ✅ **安全**（修复） · 🚨 **稳定性/数据**（风险）
- **处置建议：** 预发布版重大事项 · 重点关注
- **建议理由：** 已确认硬分叉或重大共识变更，应核对网络生效条件和节点兼容要求。 当前为预发布版，不建议直接用于生产升级；应评估现网影响并跟进正式版。

##### AI 审查

**代码已确认的发现**

1. **硬分叉/共识**：`base_layer/core/src/chain_storage/lmdb_db/validator_node_store.rs` 的 `get_next_activation_epoch`（#8197、#8203）改为读取并校验 seek 落点 key 的 sidechain 前缀与 epoch 段，多 sidechain 注册下 VN 激活 epoch 由错误后移变为正确值，新测试直接核对 epoch 边界 header 的 `validator_node_mr`。同一链在旧、新版本会算出不同的 header VN MR，含多 sidechain 注册时存在跨版本分歧风险，发行说明未声明硬分叉。
2. **硬分叉/共识**：`base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 的 `verify_timelocks`（#8319）由 `min_spendable > current_height + 1` 收紧为 `> current_height`，body 在挖矿高度 `header.height` 检查时间锁，旧版接受的高度 h 花费 maturity/lock_height 为 h+1 的区块体在新版被拒（测试 `block_body_timelocks_are_checked_at_the_header_height` 固化）。若链上无其它等价检查提前拒绝此类区块，最终有效区块集合随之变化，升级需注意分叉风险。
3. **硬分叉/共识**：`transaction_components/aggregate_body_internal_validator.rs` 的 `check_total_burned` 与 `transaction_builder/builder.rs`（#8323）新增拒绝非 burn kernel 携带 `burn_commitment`，属区块体校验收紧，旧版是否曾完整接受此类交易未确认，是否改变最终有效交易集合待核实。
4. **兼容性**：`comms/dht/src/config.rs` 对 `flood_ban_max_msg_count`（1..=1,000,000）与 `flood_ban_timespan`（1..=86,400 秒）新增硬性反序列化边界，此前可加载的越界存量配置在目标版本加载报错，节点无法启动。
5. **安全**：`base_layer/mmr/src/merkle_proof.rs`（#8294）的 `MerkleProof::verify` 新增拒绝非叶位置与越界位置，修复此前空 path/peaks 的伪造证明可在父节点位置通过验证的问题，`find_leaf_index` 改为仅比对叶子哈希。
6. **稳定性/数据**：`applications/minotari_app_utilities/src/identity_management.rs` 在存档身份签名校验失败时直接 `id.sign()` 重签写回磁盘，本地被篡改的 `public_addresses` 保留并获得合法签名（测试 `invalid_stored_signature_is_replaced_without_changing_identity` 篡改端口后仍通过 `verify`），身份文件的防篡改检测被削弱。
7. **稳定性/数据**：`blockchain_database.rs` 的 `rewind_or_reset_to_height`（#8260）在越过剪枝边界时改为单事务 `reset_chain_to_genesis`，清空 headers/块/孤儿/UTXO/JMT 并重播创世状态，深度重组时剪枝节点需整链重新同步且孤儿链被丢弃。
8. **稳定性/数据**：`blockchain_database.rs`、`lmdb_db.rs` 的一致性检查与孤儿 tip 修复（#8245、#8246）区分存储访问失败与数据损坏并在复核后才回退，同时修复孤儿 tip 索引，健康库不再被报为损坏。
9. **稳定性/数据**：`header_sync/synchronizer.rs` 的 `record_chain_change` 在 30 分钟内第 3 次因本节点链在同步期间变化而封禁 sync peer（`RepeatedChainChangesDuringSync` 短封禁），链变化可由第三方传播区块促成，诚实 sync peer 可能被误封。
10. **稳定性/数据**：`comms/dht/src/connectivity/metrics.rs` 的新 flood-ban 双序列计数把本节点未签名重广播计入邻居 forwarded 序列且不受 ForwardBudget 约束，代码注释承认邻居使用非默认 `flood_ban_*` 参数时可封禁诚实中继（需较高消息速率或配置不一致才触发）。
11. **稳定性/数据**：`state_machine_service/states/listening.rs` 初始同步判定改为去重 peer 后 60 秒无更强链迹象即宣告 initial sync，`determine_sync_mode` 传播容差边界由 `>` 改为 `>=`，节点 `is_synced` 可能提前为真。

**待核实的发行说明主张**

12. 发行说明称 “fix(sync): keep median timestamp windows in height order”（#8195），提供的分段审查未报告对应代码证据，窗口排序对中位时间戳计算与校验的具体行为差异及影响未核实。
13. 发行说明称 “fix(mempool): keep height-expired spends out of block templates”（#8244），提供的分段审查未报告对应代码证据，矿工区块模板中是否曾包含过期花费及其后果未核实。

##### 版本信息

发布于 2026-11-10T11:57:54Z · 比较 `v6.3.0-pre.2` → `v6.3.0-pre.4` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.4)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
