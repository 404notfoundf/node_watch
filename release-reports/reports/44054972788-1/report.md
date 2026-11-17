# 节点版本审查报告

## 检查批次 2026-11-17 10:00:08 UTC

### tari

#### v6.3.0-pre.2 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** 🚨 **破坏性变更**（已确认） · ✅ **安全**（修复） · ⚠️ **重大发行说明待核实：** 稳定性/数据声明
- **处置建议：** 预发布版重大事项 · 需关注
- **建议理由：** 已确认破坏性或兼容性变更，需要升级并核对现有配置。 当前为预发布版，不建议直接用于生产升级；应评估现网影响并跟进正式版。

##### AI 审查

发行说明未声明硬分叉。

**代码已确认的发现**

1. 破坏性变更：`base_layer/core/src/chain_storage/active_validator_node.rs` 中 `ValidatorNodeEntry` 新增 `original_registration` 字段，pre.1 写入的旧格式条目在目标版本读取验证节点集合（含 `validator_node_mr` 计算路径）时反序列化报错并要求重新同步链库。从 v6.3.0-pre.1 升级且链库中已有验证节点条目的 mainnet 节点无法沿用现有数据库，需全量重新同步，若主网不存在此类存量条目则影响有限。

2. 安全：`applications/minotari_app_grpc/src/conversions/unblinded_output.rs` 的派生 `Debug` 曾输出 `spending_key` 与 `script_private_key`，且提前返回路径未清零密钥，目标版本在所有退出路径清零并配合 `applications/minotari_app_grpc/build.rs` 对携带私钥消息 `skip_debug`。此为修复基线密钥暴露面，未证实存在实际输出该 Debug 表示的生产调用路径，影响有界。

**待核实的发行说明主张**

3. 稳定性/数据：发行说明原文：「fix(libtor): bundle Tor 0.4.9.15 so the base node no longer exits on the current Tor consensus」。本次差异仅见 `infrastructure/libtor/Cargo.toml` 的 Tor 依赖升级，无法核实基线版本在当前 Tor consensus 下退出的代码路径，也无法仅由依赖变更本身证实修复，影响使用内置 Tor 的 mainnet 节点。

##### 版本信息

发布于 2026-10-29T01:28:17Z · 比较 `v6.3.0-pre.1` → `v6.3.0-pre.2` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.2)


#### v6.3.0-pre.4 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **重点标记：** 🚨 **重大共识变更**（已确认） · ✅ **安全**（修复） · ✅ **稳定性/数据**（修复）
- **处置建议：** 预发布版重大事项 · 重点关注
- **建议理由：** 已确认硬分叉或重大共识变更，应核对网络生效条件和节点兼容要求。 当前为预发布版，不建议直接用于生产升级；应评估现网影响并跟进正式版。

##### AI 审查

**代码已确认的发现**

1. `base_layer/transaction_components/src/validation/aggregate_body/aggregate_body_internal_validator.rs` 与 `base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs` 的 `check_total_burned` 拒绝“非 burn kernel 携带 burn_commitment”的 body，v6.3.0-pre.2 接受而目标版本拒绝，仅影响特制 kernel，普通交易与主网正常出块不受影响。另 `base_layer/core/src/chain_storage/lmdb_db/validator_node_store.rs` 的 `get_next_activation_epoch` 修复跨 sidechain 计数，多 sidechain 满 epoch 注册时 header 的 `validator_node_mr` 判定在新旧节点间可能分歧（主网是否存在此类注册场景无证据），发行说明均未声明硬分叉。

2. `base_layer/core/src/mempool/unconfirmed_pool/unconfirmed_pool.rs` 移除按 `kernel.burn_commitment` 匹配驱逐的逻辑，修复攻击者以伪造 burn_commitment 的已上链内核把产出相同 commitment 的未确认交易从各节点 mempool 驱逐的定向审查路径。`comms/core/src/protocol/rpc/client/mod.rs` 将读超时改为每请求固定 deadline，修复恶意对端以陈旧帧滴灌使 RPC 客户端请求被无限期挂起的拒绝服务路径。

3. `base_layer/core/src/chain_storage/blockchain_database.rs` 与 `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 将越过修剪高度的 rewind 改为单次写入内原子重置到创世，修复深回退中途失败留下半删除不一致库状态的风险，触发该路径的修剪节点需从头重同步。一致性检查区分存储访问失败与数据损坏并在写锁下复核，不再把健康库误报为损坏并自动回退健康链数据。

##### 版本信息

发布于 2026-11-10T11:57:54Z · 比较 `v6.3.0-pre.2` → `v6.3.0-pre.4` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.4)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
