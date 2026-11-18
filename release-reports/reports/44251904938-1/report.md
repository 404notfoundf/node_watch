# 节点版本审查报告

## 检查批次 2026-11-18 07:02:07 UTC

### tari

#### v6.3.0-pre.2 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** ✅ **安全**（修复） · ✅ **稳定性/数据**（修复）
- **处置建议：** 预发布版生产暂缓 · 需关注
- **建议理由：** 包含已确认的重要修复或风险，建议在维护窗口升级。 当前为预发布版，生产升级建议等待正式版发布后再评估。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 安全：** `applications/minotari_app_grpc/src/conversions/unblinded_output.rs` 用 Drop 守卫在所有退出路径清零 `spending_key` 与 `script_private_key`，并在 `applications/minotari_app_grpc/build.rs` 跳过含私钥消息的 Debug 输出，避免私钥残留在内存或日志。
2. **已确认 — 安全：** `applications/minotari_app_grpc/src/authentication/basic_auth.rs` 将逐请求 Argon2id 校验改为常量时间比对，`applications/minotari_app_grpc/src/authentication/server_interceptor.rs` 新增按源 IP 的失败退避，消除鉴权请求的高 CPU 开销并限制暴力尝试。
3. **已确认 — 安全：** `base_layer/core/src/base_node/sync/header_sync/synchronizer.rs` 在短头批次结束时校验累计难度与对端声称值一致，防止恶意同步对端虚报难度把节点引向低工作量分叉，`base_layer/core/tests/tests/header_sync.rs` 的用例确认诚实短批次不被误封。
4. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 与 `base_layer/core/src/validation/block_body/block_body_partial_validator.rs` 修正同哈希重复输出的花费实例配对、剪枝与花费状态上报，修复钱包查询与剪枝节点 horizon 同步中的数据错误。
5. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs` 在把 body 视为头承诺的 body 前要求 inputs/outputs/kernels 有序，`base_layer/core/tests/tests/node_comms_interface.rs` 与 `base_layer/core/tests/tests/block_sync.rs` 的测试确认乱序 body 无法顶替规范 body 或污染 bad_blocks。
6. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs` 的 `get_vm_key_for_candidate_header` 改为 `.optional()`，使高度超过本地 tip 的逐块到达分叉能正常入库，此前跨 RandomX VM key 边界会入库失败。
7. **已确认 — 稳定性/数据：** `infrastructure/libtor/Cargo.toml` 将内置 Tor 升级到 0.4.9.15，对应发行说明所述基础节点在当前 Tor consensus 下退出的修复，版本升级本身已在目标差异中确认。

##### 版本信息

发布于 2026-10-29T01:28:17Z · 比较 `v6.3.0-pre.1` → `v6.3.0-pre.2` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.2)


#### v6.3.0-pre.4 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** ✅ **稳定性/数据**（修复） · ⚠️ **重大发行说明待核实：** 共识/硬分叉声明
- **处置建议：** 预发布版声明待核实 · 重点关注
- **建议理由：** 预发布版中的重大声明尚未确认，不据此决定生产升级；等待正式版或更多证据。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs` 把一致性检查高度收敛到 header tip 并在写锁下复检，配合 `base_layer/core/src/chain_storage/lmdb_db/helpers.rs` 将解码失败归为 ConversionError，修复基线中健康库被误判损坏并可能被回退的数据完整性缺陷。
2. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/blockchain_database.rs` 与 `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 将越过修剪视界的回退改为单次写入原子重置到创世块，修复旧非原子擦除留下指向空块的孤儿 tip 与半成品状态的基线缺陷，触发场景限于 pruned 节点的深回退。
3. **已确认 — 稳定性/数据：** `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 修复孤儿链 tip 索引一致性，累计数据缺失的 tip 跳过并排入修复且孤儿按子树清理，避免旧实现直接返回 ValueNotFound 中断并留下无父孤儿。

**待核实的发行说明主张**
4. **待核实 — 硬分叉/共识：** 发行说明原文：「fix(validation): check chain-linked timelocks at the height the body is mined at」，`base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 的拒绝条件由 min_spendable_height 大于区块高度加一收紧为大于区块高度，但 `aggregate_body_internal_validator.rs` 在区块高度做同等 maturity 检查的入参证据缺失，无法确认旧版完整验证是否曾接受此类 body，最终有效区块集合是否收窄待核实。

##### 版本信息

发布于 2026-11-10T11:57:54Z · 比较 `v6.3.0-pre.2` → `v6.3.0-pre.4` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.4)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
