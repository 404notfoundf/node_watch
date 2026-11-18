# 节点版本审查报告

## 检查批次 2026-11-18 12:37:19 UTC

### tari

#### v6.3.0-pre.2 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** ✅ **稳定性/数据**（修复）：`infrastructure/libtor/Cargo.toml` 将捆绑 Tor 升至 0.4.9.15，修复 unix 启用内置 Tor 的构建在当前 Tor 共识下基节点退出的问题
- **处置建议：** 预发布版重大事项 · 重点关注
- **建议理由：** 已确认破坏性或兼容性变更，需要升级并核对现有配置。 当前为预发布版，不建议直接用于生产升级；应评估现网影响并跟进正式版。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 稳定性/数据：** unix 启用内置 Tor 的构建此前会在当前 Tor 共识下基节点直接退出，`infrastructure/libtor/Cargo.toml` 升级捆绑 Tor 至 0.4.9.15 后恢复正常运行，其他构建不受影响。
2. **已确认 — 破坏性变更：** `base_layer/core/src/chain_storage/active_validator_node.rs` 为 ValidatorNodeEntry 新增强制字段 original_registration，升级前已写入验证节点注册条目的节点在 `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 读取时报错并需重同步数据库，无此类条目的节点不受影响。
3. **已确认 — 安全：** `applications/minotari_app_grpc/src/authentication/basic_auth.rs` 用常数时间比对替代每请求 Argon2id，并在 `applications/minotari_app_grpc/src/server_interceptor.rs` 增加按 IP 有界退避，修复 gRPC 远程暴露且开启 Basic 认证时的 CPU/内存放大，默认本机绑定影响有限。
4. **已确认 — 稳定性/数据：** `base_layer/core/src/base_node/sync/horizon_state_sync/synchronizer.rs` 与 `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs` 修复同一 output 被花费后再挖出时的丢失或错误剪枝，仅在该罕见链上场景影响剪枝或 horizon 同步节点。

##### 版本信息

发布于 2026-10-29T01:28:17Z · 比较 `v6.3.0-pre.1` → `v6.3.0-pre.2` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.2)


#### v6.3.0-pre.4 · 预发布版 · 完整审查
<!-- watch-repo: tari-project/tari -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** ✅ **安全**（修复）：`comms/dht/src/inbound/dht_handler/task.rs` 与 `comms/dht/src/network_discovery/on_connect.rs` 旧路径允许远程对端无按源限额注入 Join 记录并慢速滴流拖住 OnConnect peer 同步，本版在 `comms/dht/src/network_discovery/admission.rs` 增加按源预算与同步截止时间
- **处置建议：** 预发布版生产暂缓 · 重点关注
- **建议理由：** 包含已确认的重要修复或风险，建议在维护窗口升级。 当前为预发布版，生产升级建议等待正式版发布后再评估。

##### AI 审查

**代码已确认的发现**
1. **已确认 — 安全：** 远程对端可无按源限额注入 Join 记录并慢速滴流拖住 OnConnect peer 同步，造成长期占用 DHT 发现路径的资源耗尽，本版修复（基线缺陷，升级前仍存在）。`comms/dht/src/inbound/dht_handler/task.rs` 新增基于 `comms/dht/src/network_discovery/admission.rs` 的按源预算与超额丢弃，`comms/dht/src/network_discovery/on_connect.rs` 加入同步截止时间，影响限于 DHT 网络发现与 peer 库，不触及区块验证。
2. **已确认 — 稳定性/数据：** 内置 Tor 构建的节点启动失败已修复（基线缺陷）。`infrastructure/libtor/src/tor.rs` 旧版日志路径被上游转小写，在内置 Tor 构建、大小写敏感文件系统且数据目录路径含大写字母时 Tor 初始化报找不到路径、节点无法启动，本版改用保留大小写的日志指令，其余构建不受影响。
3. **已确认 — 稳定性/数据：** 剪枝节点被对端虚高高度声明提前剪枝、丢失本地保留数据并需重同步的风险已修复（仅剪枝/快照同步节点）。`base_layer/core/src/base_node/state_machine_service/states/sync_decide.rs` 旧版按同步对端声称高度计算剪枝目标，本版改用已验证头链，并在 header sync 新增 `PeerSentInaccurateChainHeight` 高度声明校验。
4. **已确认 — 稳定性/数据：** 剪枝节点越过剪枝地平线的深回退现为一次写入的原子重置到创世，且只允许强于本节点全部链的分叉触发重置。`base_layer/core/src/chain_storage/blockchain_database.rs` 与 `base_layer/core/src/chain_storage/db_transaction.rs` 旧版分批删除会遗留孤儿链 tip 与残留累计数据，触发场景限于剪枝节点深回退。
5. **已确认 — 稳定性/数据：** 一致性检查把瞬时存储访问失败误报为数据库损坏的风险已修复，属手动 check-db autocorrect 场景下的有限运维风险。`base_layer/core/src/chain_storage/blockchain_database.rs` 现区分存储访问失败与数据损坏并在写锁下复核后再回退，旧版可能把健康库回退到更早高度。
6. **已确认 — 安全：** DHT flood-ban 计数可被规避并误封诚实中继的问题已修复（基线缺陷）。`comms/dht/src/connectivity/metrics.rs` 旧版把转发消息计入单一限额，女巫身份经诚实中继转发即可短时封禁中继且可借断线重连或队列溢出规避自身封禁，本版拆分 Own/Forwarded 计数并跨断线保留样本。
7. **已确认 — 安全：** gossip 预校验门的远端资源消耗已受限（基线缺陷，范围有限）。`base_layer/core/src/base_node/comms_interface/inbound_handlers.rs` 旧版对 gossip 新块逐头回溯找难度并对未知祖先无预算执行 RandomX 哈希，本版按 tip 缓存难度目标并限制回溯范围与每对端检查预算，仅影响 gossip 预校验，不改变共识。
8. **已确认 — 安全：** 同步流程可被慢速对端长期拖延的问题已修复（基线缺陷）。`base_layer/core/src/base_node/sync/block_sync/synchronizer.rs` 与 `base_layer/core/src/base_node/sync/header_sync/synchronizer.rs` 新增每次尝试的网络等待预算与短封禁，旧版在拨号、RPC 协商和首块前流等待均无超时。

##### 版本信息

发布于 2026-11-10T11:57:54Z · 比较 `v6.3.0-pre.2` → `v6.3.0-pre.4` · [打开 Release](https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.4)


---

审查范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整审查”标识为准。
