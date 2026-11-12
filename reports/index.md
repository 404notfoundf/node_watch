# 上游 Release 监控报告

本报告按检查批次汇总更新，并在每个批次内按币种和版本分段；每个版本内的变更文件和 AI 发现分别从 1 开始编号，条目会标明仓库。

## 检查批次 2026-11-12 03:22 UTC

### tari

<!-- watch-release: eyJjb2luIjogInRhcmkiLCAicHVibGlzaGVkX2F0IjogIjIwMjYtMTAtMTlUMTE6NDE6NDRaIiwgInJlcG8iOiAidGFyaS1wcm9qZWN0L3RhcmkiLCAicmlzayI6ICJQMSIsICJ0YWciOiAidjYuMi4wLXByZS4yIn0 -->
#### v6.2.0-pre.2

- 仓库：[`tari-project/tari`](https://github.com/tari-project/tari)
- 发布日期：2026-10-19T11:41:44Z
- Release：https://github.com/tari-project/tari/releases/tag/v6.2.0-pre.2
- 代码比较：`v6.2.0-pre.1` → `v6.2.0-pre.2`
- AI 风险级别：P1

##### Release note

## What's Changed
* fix(wallet): reject coin_split_even when fee exceeds total input value by @Vallejo1921 in https://github.com/tari-project/tari/pull/8112
* fix(cli): use resolved network when computing common.base_path by @Vallejo1921 in https://github.com/tari-project/tari/pull/8113
* fix(cli): parse key-value overrides using split_once to preserve values with equals and whitespace by @Vallejo1921 in https://github.com/tari-project/tari/pull/8114
* fix(common): replace serde_yaml with serde-saphyr to drop unsafe-libyaml by @sdbondi in https://github.com/tari-project/tari/pull/8116
* ci(ledger): stop passing --locked to comms_testing builds by @SWvheerden in https://github.com/tari-project/tari/pull/8117
* fix(comms): stop culled and idle RPC sessions promptly and bound internal channel sends by @SWvheerden in https://github.com/tari-project/tari/pull/8118
* fix(cli): merge duplicate test modules in common_cli_args by @SWvheerden in https://github.com/tari-project/tari/pull/8121
* docs(deps_only): describe what the placeholder crate actually does by @SWvheerden in https://github.com/tari-project/tari/pull/8120
* fix(comms): admit liveness by token, bound inbound handshakes and cap inbound connections by @SWvheerden in https://github.com/tari-project/tari/pull/8119
* fix(comms): lossless peer DB addresses, row cap and GC, direction-aware reaper, persisted bans by @SWvheerden in https://github.com/tari-project/tari/pull/8124
* fix(comms): bound messaging queues, fair inbound delivery, yamux window cap by @SWvheerden in https://github.com/tari-project/tari/pull/8125
* fix(identity): prevent secret key leakage from malformed identity errors by @Vallejo1921 in https://github.com/tari-project/tari/pull/8115
* fix(validation): require the canonical script on side-chain claimable burns by @sdbondi in https://github.com/tari-project/tari/pull/8126
* feat(mempool): add bans for gossip transactions by @SWvheerden in https://github.com/tari-project/tari/pull/8127
* fix(sidechain): weigh quorum certificates by signer voting power by @sdbondi in https://github.com/tari-project/tari/pull/8128
* perf(utxo-selection): make branch-and-bound search iterative by @SWvheerden in https://github.com/tari-project/tari/pull/8129
* fix: harden validation by @SWvheerden in https://github.com/tari-project/tari/pull/8132
* feat(offline-signing): render payload summaries before signing and show recipient output features by @SWvheerden in https://github.com/tari-project/tari/pull/8130
* refactor(covenants): defer token parsing and bound evaluation work by @SWvheerden in https://github.com/tari-project/tari/pull/8131
* fix(wallet): derive imported transaction details from recovered output data by @SWvheerden in https://github.com/tari-project/tari/pull/8133

## New Contributors
* @Vallejo1921 made their first contribution in https://github.com/tari-project/tari/pull/8112

**Full Changelog**: https://github.com/tari-project/tari/compare/v6.2.0-pre.1...v6.2.0-pre.2

##### 变更文件

1. `.github/workflows/ci.yml`
2. `Cargo.lock`
3. `Cargo.toml`
4. `applications/minotari_app_grpc/proto/wallet.proto`
5. `applications/minotari_app_grpc/tests/decoder_parity.rs`
6. `applications/minotari_app_utilities/src/common_cli_args.rs`
7. `applications/minotari_app_utilities/src/identity_management.rs`
8. `applications/minotari_console_wallet/Cargo.toml`
9. `applications/minotari_console_wallet/log4rs_sample.yml`
10. `applications/minotari_console_wallet/src/automation/commands.rs`
11. `applications/minotari_console_wallet/src/grpc/wallet_grpc_server.rs`
12. `applications/minotari_console_wallet/src/ui/components/transactions_tab.rs`
13. `applications/minotari_console_wallet/src/ui/state/app_state.rs`
14. `applications/minotari_console_wallet/src/wallet_modes.rs`
15. `applications/minotari_ledger_wallet/comms_testing/Cargo.lock`
16. `applications/minotari_ledger_wallet/comms_testing/Cargo.toml`
17. `applications/minotari_ledger_wallet/comms_testing/README.md`
18. `applications/minotari_ledger_wallet/wallet/Cargo.lock`
19. `applications/minotari_ledger_wallet/wallet/Cargo.toml`
20. `applications/minotari_miner/Cargo.toml`
21. `applications/minotari_node/Cargo.toml`
22. `applications/minotari_node/src/bootstrap.rs`
23. `applications/minotari_node/src/grpc/base_node_grpc_server.rs`
24. `applications/minotari_node/src/http/handler/json_rpc/mod.rs`
25. `applications/minotari_offline_signer/Cargo.toml`
26. `applications/minotari_offline_signer/README.md`
27. `applications/minotari_offline_signer/src/cli.rs`
28. `applications/minotari_peer_sync/Cargo.toml`
29. `base_layer/common_types/src/types/bullet_rangeproofs.rs`
30. `base_layer/common_types/src/types/mod.rs`
31. `base_layer/core/Cargo.toml`
32. `base_layer/core/src/base_node/rpc/service.rs`
33. `base_layer/core/src/base_node/service/service.rs`
34. `base_layer/core/src/base_node/sync/block_sync/synchronizer.rs`
35. `base_layer/core/src/base_node/sync/horizon_state_sync/synchronizer.rs`
36. `base_layer/core/src/chain_storage/blockchain_backend.rs`
37. `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs`
38. `base_layer/core/src/chain_storage/tests/lmdb_unit_tests.rs`
39. `base_layer/core/src/mempool/mempool.rs`
40. `base_layer/core/src/mempool/mempool_storage.rs`
41. `base_layer/core/src/mempool/service/inbound_handlers.rs`
42. `base_layer/core/src/mempool/service/initializer.rs`
43. `base_layer/core/src/mempool/service/mod.rs`
44. `base_layer/core/src/mempool/service/peer_bans.rs`
45. `base_layer/core/src/mempool/sync_protocol/mod.rs`
46. `base_layer/core/src/mempool/sync_protocol/test.rs`
47. `base_layer/core/src/mempool/test_utils/mod.rs`
48. `base_layer/core/src/proto/transaction.rs`
49. `base_layer/core/src/test_helpers/blockchain.rs`
50. `base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs`
51. `base_layer/core/src/validation/block_body/test.rs`
52. `base_layer/core/src/validation/error.rs`
53. `base_layer/core/src/validation/test.rs`
54. `base_layer/core/src/validation/traits.rs`
55. `base_layer/core/src/validation/transaction/transaction_chain_validator.rs`
56. `base_layer/core/tests/helpers/nodes.rs`
57. `base_layer/core/tests/tests/mempool.rs`
58. `base_layer/p2p/src/config.rs`
59. `base_layer/p2p/src/initialization.rs`
60. `base_layer/sidechain/src/commit_proof.rs`
61. `base_layer/sidechain/src/validations.rs`
62. `base_layer/sidechain/tests/commit_proof.rs`
63. `base_layer/transaction_components/src/coinbase_builder.rs`
64. `base_layer/transaction_components/src/consensus/consensus_constants.rs`
65. `base_layer/transaction_components/src/helpers/mod.rs`
66. `base_layer/transaction_components/src/helpers/terminal_safe.rs`
67. `base_layer/transaction_components/src/key_manager/interface.rs`
68. `base_layer/transaction_components/src/key_manager/manager.rs`
69. `base_layer/transaction_components/src/key_manager/mod.rs`
70. `base_layer/transaction_components/src/offline_signing/mod.rs`
71. `base_layer/transaction_components/src/offline_signing/models.rs`
72. `base_layer/transaction_components/src/offline_signing/offline_signer.rs`
73. `base_layer/transaction_components/src/offline_signing/one_sided_signer.rs`
74. `base_layer/transaction_components/src/offline_signing/payload_summary.rs`
75. `base_layer/transaction_components/src/test_helpers/mod.rs`
76. `base_layer/transaction_components/src/test_helpers/test_helpers_functions.rs`
77. `base_layer/transaction_components/src/transaction_builder/builder.rs`
78. `base_layer/transaction_components/src/transaction_builder/error.rs`
79. `base_layer/transaction_components/src/transaction_components/covenants/arguments.rs`
80. `base_layer/transaction_components/src/transaction_components/covenants/context.rs`
81. `base_layer/transaction_components/src/transaction_components/covenants/covenant.rs`
82. `base_layer/transaction_components/src/transaction_components/covenants/decoder.rs`
83. `base_layer/transaction_components/src/transaction_components/covenants/encoder.rs`
84. `base_layer/transaction_components/src/transaction_components/covenants/error.rs`
85. `base_layer/transaction_components/src/transaction_components/covenants/filters/absolute_height.rs`
86. `base_layer/transaction_components/src/transaction_components/covenants/filters/field_eq.rs`
87. `base_layer/transaction_components/src/transaction_components/covenants/filters/fields_hashed_eq.rs`
88. `base_layer/transaction_components/src/transaction_components/covenants/filters/fields_preserved.rs`
89. `base_layer/transaction_components/src/transaction_components/covenants/filters/filter.rs`
90. `base_layer/transaction_components/src/transaction_components/covenants/filters/not.rs`
91. `base_layer/transaction_components/src/transaction_components/covenants/filters/or.rs`
92. `base_layer/transaction_components/src/transaction_components/covenants/filters/output_hash_eq.rs`
93. `base_layer/transaction_components/src/transaction_components/covenants/filters/xor.rs`
94. `base_layer/transaction_components/src/transaction_components/covenants/macros.rs`
95. `base_layer/transaction_components/src/transaction_components/covenants/matching.rs`
96. `base_layer/transaction_components/src/transaction_components/covenants/mod.rs`
97. `base_layer/transaction_components/src/transaction_components/covenants/output_set.rs`
98. `base_layer/transaction_components/src/transaction_components/covenants/scan.rs`
99. `base_layer/transaction_components/src/transaction_components/covenants/test.rs`
100. `base_layer/transaction_components/src/transaction_components/covenants/work.rs`
101. `base_layer/transaction_components/src/transaction_components/memo_field.rs`
102. `base_layer/transaction_components/src/transaction_components/range_proof_type.rs`
103. `base_layer/transaction_components/src/transaction_components/test.rs`
104. `base_layer/transaction_components/src/transaction_components/transaction_output.rs`
105. `base_layer/transaction_components/src/transaction_components/wallet_output.rs`
106. `base_layer/transaction_components/src/transaction_components/wallet_output_builder.rs`
107. `base_layer/transaction_components/src/utxo_selection/branch_and_bound/branch_and_bound_selector.rs`
108. `base_layer/transaction_components/src/utxo_selection/branch_and_bound/branch_bound_builder.rs`
109. `base_layer/transaction_components/src/utxo_selection/mod.rs`
110. `base_layer/transaction_components/src/validation/aggregate_body/aggregate_body_internal_validator.rs`
111. `base_layer/transaction_components/src/validation/error.rs`
112. `base_layer/transaction_components/src/validation/helpers.rs`
113. `base_layer/transaction_components/src/validation/transaction/transaction_internal_validator.rs`
114. `base_layer/transaction_components/tests/covenant_decode_heap.rs`
115. `base_layer/transaction_key_manager/src/legacy_key_manager/inner.rs`
116. `base_layer/transaction_key_manager/src/legacy_key_manager/wrapper.rs`
117. `base_layer/wallet/migrations/2026-10-15-000000_completed_transactions_source_address_claimed/down.sql`
118. `base_layer/wallet/migrations/2026-10-15-000000_completed_transactions_source_address_claimed/up.sql`
119. `base_layer/wallet/src/output_manager_service/handle.rs`
120. `base_layer/wallet/src/output_manager_service/recovery/standard_outputs_recoverer.rs`
121. `base_layer/wallet/src/output_manager_service/service.rs`
122. `base_layer/wallet/src/output_manager_service/storage/models.rs`
123. `base_layer/wallet/src/schema.rs`
124. `base_layer/wallet/src/transaction_service/handle.rs`
125. `base_layer/wallet/src/transaction_service/service.rs`
126. `base_layer/wallet/src/transaction_service/storage/database.rs`
127. `base_layer/wallet/src/transaction_service/storage/models.rs`
128. `base_layer/wallet/src/transaction_service/storage/sqlite_db.rs`
129. `base_layer/wallet/src/utxo_scanner_service/mod.rs`
130. `base_layer/wallet/src/utxo_scanner_service/utxo_scanner_task.rs`
131. `base_layer/wallet/src/wallet.rs`
132. `base_layer/wallet/tests/output_manager_service_tests/service.rs`
133. `base_layer/wallet/tests/support/output_manager_service_mock.rs`
134. `base_layer/wallet/tests/transaction_service_tests/service.rs`
135. `base_layer/wallet/tests/transaction_service_tests/storage.rs`
136. `base_layer/wallet_ffi/Cargo.toml`
137. `base_layer/wallet_ffi/src/lib.rs`
138. `base_layer/wallet_ffi/wallet.h`
139. `buildtools/deps_only/src/main.rs`
140. `changelog-Mainnet.md`
141. `changelog-development.md`
142. `common/Cargo.toml`
143. `common/config/presets/c_base_node_c.toml`
144. `common/config/presets/d_console_wallet.toml`
145. `common/src/logging.rs`
146. `comms/core/src/builder/comms_node.rs`
147. `comms/core/src/builder/mod.rs`
148. `comms/core/src/builder/tests.rs`
149. `comms/core/src/connection_manager/common.rs`
150. `comms/core/src/connection_manager/dialer.rs`
151. `comms/core/src/connection_manager/error.rs`
152. `comms/core/src/connection_manager/listener.rs`
153. `comms/core/src/connection_manager/manager.rs`
154. `comms/core/src/connection_manager/metrics.rs`
155. `comms/core/src/connection_manager/peer_connection.rs`
156. `comms/core/src/connection_manager/self_liveness.rs`
157. `comms/core/src/connection_manager/tests/listener_limits.rs`
158. `comms/core/src/connection_manager/tests/manager.rs`
159. `comms/core/src/connection_manager/tests/mod.rs`
160. `comms/core/src/connectivity/config.rs`
161. `comms/core/src/connectivity/connection_pool.rs`
162. `comms/core/src/connectivity/manager.rs`
163. `comms/core/src/connectivity/proactive_dialer.rs`
164. `comms/core/src/connectivity/test.rs`
165. `comms/core/src/message/inbound.rs`
166. `comms/core/src/multiplexing/yamux.rs`
167. `comms/core/src/net_address/mod.rs`
168. `comms/core/src/net_address/multiaddr_with_stats.rs`
169. `comms/core/src/net_address/mutliaddresses_with_stats.rs`
170. `comms/core/src/peer_manager/config.rs`
171. `comms/core/src/peer_manager/manager.rs`
172. `comms/core/src/peer_manager/metrics.rs`
173. `comms/core/src/peer_manager/mod.rs`
174. `comms/core/src/peer_manager/peer.rs`
175. `comms/core/src/peer_manager/peer_identity_claim.rs`
176. `comms/core/src/peer_manager/peer_storage_sql.rs`
177. `comms/core/src/peer_manager/storage/database.rs`
178. `comms/core/src/peer_manager/storage/migrations/2026-10-08-000000_address_bytes/down.sql`
179. `comms/core/src/peer_manager/storage/migrations/2026-10-08-000000_address_bytes/up.sql`
180. `comms/core/src/peer_manager/storage/schema.rs`
181. `comms/core/src/peer_validator/error.rs`
182. `comms/core/src/peer_validator/helpers.rs`
183. `comms/core/src/protocol/error.rs`
184. `comms/core/src/protocol/messaging/extension.rs`
185. `comms/core/src/protocol/messaging/inbound.rs`
186. `comms/core/src/protocol/messaging/metrics.rs`
187. `comms/core/src/protocol/messaging/outbound.rs`
188. `comms/core/src/protocol/messaging/protocol.rs`
189. `comms/core/src/protocol/messaging/test.rs`
190. `comms/core/src/protocol/protocols.rs`
191. `comms/core/src/protocol/rpc/client/mod.rs`
192. `comms/core/src/protocol/rpc/server/early_close.rs`
193. `comms/core/src/protocol/rpc/server/error.rs`
194. `comms/core/src/protocol/rpc/server/metrics.rs`
195. `comms/core/src/protocol/rpc/server/mod.rs`
196. `comms/core/src/protocol/rpc/server/request_codec.rs`
197. `comms/core/src/protocol/rpc/status.rs`
198. `comms/core/src/protocol/rpc/test/greeting_service.rs`
199. `comms/core/src/protocol/rpc/test/smoke.rs`
200. `comms/core/src/utils/cidr.rs`
201. `comms/core/src/utils/datetime.rs`
202. `comms/core/src/utils/mod.rs`
203. `comms/core/src/utils/mpsc.rs`
204. `comms/core/src/utils/text.rs`
205. `comms/core/tests/tests/messaging.rs`
206. `comms/core/tests/tests/mod.rs`
207. `comms/dht/src/inbound/decryption.rs`
208. `comms/dht/src/network_discovery/discovering.rs`
209. `comms/dht/src/outbound/message_send_state.rs`
210. `comms/dht/src/outbound/mock.rs`
211. `comms/dht/src/peer_validator.rs`
212. `comms/dht/src/rpc/peer_info.rs`
213. `docs/guide/applications_overview.md`
214. `docs/src/09_adding_tari_to_your_exchange.md`
215. `integration_tests/src/world.rs`
216. `integration_tests/tests/features/OfflineSigning.feature`
217. `integration_tests/tests/steps/offline_signing_steps.rs`
218. `package-lock.json`
219. `scripts/ledger_speculos.sh`
220. `supply-chain/config.toml`

##### AI 审查

风险级别：P1

**审查范围说明**：提供的 diff 在 `base_layer/core/src/base_node/service/service.rs` 处被截断。发行说明中多项改动（comms RPC/会话回收、peer DB 上限与 GC、yamux 窗口、mempool ban、sidechain quorum 加权、UTXO branch-and-bound、covenants 重构、validation harden、wallet coin_split 修复等）的实现代码**未包含在本次提供的 diff 中**，对其只能标注“证据不足”。以下结论仅基于可见 diff 与发行说明的对照。

## 重要发现

1. **共识/兼容性敏感：range proof 解码新增 577 字节硬上限（代码支持，结论待验证）**
   - 文件：`base_layer/common_types/src/types/bullet_rangeproofs.rs`、`types/mod.rs`（`MAX_RANGE_PROOF_BYTES = 577`）
   - 代码支持：`BulletRangeProof` 改为经 `ValidatedDecode` 解码，borsh/bincode/serde/`from_canonical_bytes` 在长度超限时拒绝，且 borsh 在分配前先校验长度前缀（防大长度 DoS）；测试覆盖 577/578 边界，`decoder_parity.rs` 中超限样本期望由接受改为拒绝。
   - 待验证：“任何合法 proof 都不超过 577 字节”只是注释声明（`1 + 32 * (1 + 5 + 2 * log2(64*1))`）。若该上限与实际 BulletProofPlus 序列化或参数（位宽/聚合因子）不一致，新旧节点/钱包对同一消息的接受性会不一致，属兼容性风险。编码格式测试显示序列化字节不变，这降低了升级破坏风险，但无法覆盖跨版本互操作。

2. **共识/兼容性敏感：covenant 校验收紧（行为变化证据充分，实现代码证据不足）**
   - 文件：`applications/minotari_app_grpc/tests/decoder_parity.rs`
   - 代码支持：测试中“超过 token 总数上限的 covenant”和“非最小编码长度的 covenant”期望从可解码变为被拒绝（`false`），说明解码/校验层确有收紧。
   - 证据不足：对应实现（发行说明称在 PR #8131/#8132）不在 diff 中，无法确认这是仅影响解码（拒绝畸形编码）还是会拒绝旧版本节点认可的合法区块/交易。若属后者且未提升网络/共识版本，存在链分裂风险。发行说明未声明硬分叉。

3. **离线签名的 fail-closed 默认被削弱（代码支持，安全权衡需人工确认）**
   - 文件：`applications/minotari_offline_signer/src/cli.rs`、`applications/minotari_console_wallet/src/automation/commands.rs`
   - 代码支持：旧代码在 stdin 非终端且未传 `--yes` 时**拒绝签名**（注释明确称人工确认是唯一防伪造检查，因 payload 完整性签名用可共享的 view key）；新代码在非交互/无终端时**打印摘要后直接签名**，且 `--yes` 被弃用为“无任何效果”。摘要含控制字符转义（`escape_bytes_for_terminal`），且确认发生在取用密钥之前，是改进；但自动化流水线中现在无需显式 opt-in 即可签名。请人工确认这是有意的运维决策。

4. **`common.base_path` 解析改变，可能导致升级后“找不到”既有数据（代码支持）**
   - 文件：`applications/minotari_app_utilities/src/common_cli_args.rs`
   - 代码支持：`get_config_property_overrides` 现使用解析后的 network（`get_base_path_for`）计算 `common.base_path`，此前忽略该参数。当网络来自配置文件而非 `--network` 时，数据目录后缀会变化。文件未被删除，但用户可能看到钱包/节点数据“消失”，属破坏性升级体验风险，需在发行说明中明示迁移方式。

5. **YAML 解析栈替换：serde_yaml → serde-saphyr，log4rs 移除 `yaml_format`（正面 + 待验证）**
   - 文件：`Cargo.lock`、`Cargo.toml`、`common`（依赖变更）、各应用 `Cargo.toml`、`log4rs_sample.yml`
   - 代码支持：`unsafe-libyaml`（C 绑定）从依赖树移除，降低原生代码攻击面，是明确改进；`serde_yaml` 已废弃。
   - 待验证：① 旧配置文件在 serde-saphyr 下的语义差异（重复键、锚点/别名、隐式类型等）可能改变解析结果；② log4rs 的 `yaml_format` 特性被移除但仓库仍提供 `log4rs_sample.yml`，需要确认运行时日志配置解析走哪条路径、旧 YAML 日志配置是否仍可用。
   - 无恶意迹象，但新增注册表依赖 `serde-saphyr 2.0.0`、`granit-parser 2.0.0`、`annotate-snippets`、`encoding_rs_io` 等，建议按供应链流程核查来源与维护者（diff 仅显示 checksum，未审查其源码）。

6. **身份文件解析错误不再泄露 secret key（代码支持的修复）**
   - 文件：`applications/minotari_app_utilities/src/identity_management.rs`
   - 代码支持：`IdentityError` 不再透传 `json5::Error` 内容，只输出行列号，并有回归测试断言错误信息不含私钥十六进制。与发行说明一致。

7. **`source_address_claimed` 标记与 memo 不再决定交易类型/费用（代码支持，向后兼容性良好）**
   - 文件：`applications/minotari_app_grpc/proto/wallet.proto`、`wallet_grpc_server.rs`、`ui/components/transactions_tab.rs`、`ui/state/app_state.rs`
   - 代码支持：新增 proto 字段（编号 22，加性变更）；UI/gRPC 明确标注 memo 中的来源地址为“claimed/未经认证”，并禁止 memo 覆盖交易状态、类型与 fee 展示。这是针对伪造 memo 误导展示的加固，未见风险。

8. **恶意迹象与其它**
   - 未在可见 diff 中发现恶意代码、后门、密钥/凭据外传或混淆迹象。版本号从 6.2.0-pre.1 → 6.2.0-pre.2 在各 crate 一致。
   - CI 移除 `--locked`（`ci.yml`、`comms_testing` README）仅影响该独立测试工作区的构建可复现性，注释给出了合理理由，风险很低。
   - `read_payload_file`/`read_input_file` 对 FIFO、目录、超大文件的防护（`O_NONBLOCK`、regular file 检查、10MB 上限、TOCTOU 上在已打开句柄上做检查）是明确的健壮性改进，代码支持。

9. **证据不足、无法核实的声明（diff 未提供实现）**
   - comms：RPC 会话及时回收与有界发送、liveness 令牌准入、入站握手/连接上限、peer DB 地址无损存储与行上限/GC、方向感知回收器、持久化 ban、消息队列有界与公平投递、yamux 窗口上限（#8118/#8119/#8124/#8125）。
   - mempool：gossip 交易 ban（#8127，可见部分仅 `PeerBanPeriods` 接线）；持久化 ban 与新 ban 策略会影响 P2P 兼容面与被误封风险，需重点复核。
   - sidechain：quorum 证书按投票权加权（#8128）——这可能是侧链共识规则变化，未见代码。
   - 其余：UTXO 选择迭代化（#8129）、validation harden（#8132）、covenants 延迟解析与求值上限（#8131）、coin_split_even 手续费校验（#8112）、canonical script 校验（#8126）。
   - `base_node/service/service.rs` 中可见部分：入站 `BaseNodeRequest` 每 peer 限额、丢弃由他人身份签名的请求；丢弃请求会让请求方超时并可能反向封禁我们（注释已承认），是否有实测影响待验证。

## 人工复核建议

1. 在合并/发布前补全完整 diff，重点复核未提供的 comms、mempool、sidechain、validation 代码。
2. 跨版本互操作测试：pre.1 与 pre.2 节点互连、同步、中继含边界 range proof/covenant 的交易与区块，确认不会出现“一边接受一边拒绝”的分叉；如属共识收紧，应显式声明硬分叉/提升网络版本并给出激活高度。
3. 核对 `MAX_RANGE_PROOF_BYTES = 577` 与实际 BulletProofPlus 序列化输出（含各种参数）逐字节验证，而不只依赖注释推导。
4. 确认非交互自动签名（原 fail-closed）是产品决策；若保留，建议要求显式 opt-in 标志（等价于旧 `--yes`）而非默认放行。
5. 为升级用户写明 `common.base_path` 变化带来的目录迁移影响；确认旧 YAML 日志/节点配置在 serde-saphyr 与移除 `yaml_format` 后仍能加载。
6. 对新增第三方 crate（serde-saphyr、granit-parser 等）做供应链核查。



<!-- watch-release: eyJjb2luIjogInRhcmkiLCAicHVibGlzaGVkX2F0IjogIjIwMjYtMTAtMTlUMTE6NDU6MTJaIiwgInJlcG8iOiAidGFyaS1wcm9qZWN0L3RhcmkiLCAicmlzayI6ICJQMyIsICJ0YWciOiAidjYuMi4wIn0 -->
#### v6.2.0

- 仓库：[`tari-project/tari`](https://github.com/tari-project/tari)
- 发布日期：2026-10-19T11:45:12Z
- Release：https://github.com/tari-project/tari/releases/tag/v6.2.0
- 代码比较：`v6.2.0-pre.2` → `v6.2.0`
- AI 风险级别：P3

##### Release note

## v6.2.0 (2026-10-19)

> ### ⚠️ Breaking Changes
> This release changes on-disk database behaviour, and wallet export behaviour. Review before upgrading:
> * **common_sqlite:** owner-only database files, WAL set in `create_pool`, per-database profiles in [#8107](https://github.com/tari-project/tari/pull/8107)
> * **wallet:** remove private-key UTXO export, which leaked the spend key in [#8102](https://github.com/tari-project/tari/pull/8102)

## What's Changed

### Features
* feat(mempool): add bans for gossip transactions in [#8127](https://github.com/tari-project/tari/pull/8127)
* feat(offline-signing): render payload summaries before signing and show recipient output features in [#8130](https://github.com/tari-project/tari/pull/8130)
* feat(base_node): use mimalloc as the global allocator in [#8111](https://github.com/tari-project/tari/pull/8111)
* feat(jellyfish): make the JMT hash scheme an explicit parameter in [#8096](https://github.com/tari-project/tari/pull/8096)
* feat(jellyfish): native minicbor encoding, inline NibblePath and bitmap InternalNode children in [#8101](https://github.com/tari-project/tari/pull/8101)

### Bug Fixes
* fix(cli): merge duplicate test modules in common_cli_args in [#8121](https://github.com/tari-project/tari/pull/8121)
* fix(cli): parse key-value overrides using split_once to preserve values with equals and whitespace in [#8114](https://github.com/tari-project/tari/pull/8114)
* fix(cli): use resolved network when computing common.base_path in [#8113](https://github.com/tari-project/tari/pull/8113)
* fix(common): replace serde_yaml with serde-saphyr to drop unsafe-libyaml in [#8116](https://github.com/tari-project/tari/pull/8116)
* fix(comms): admit liveness by token, bound inbound handshakes and cap inbound connections in [#8119](https://github.com/tari-project/tari/pull/8119)
* fix(comms): bound messaging queues, fair inbound delivery, yamux window cap in [#8125](https://github.com/tari-project/tari/pull/8125)
* fix(comms): lossless peer DB addresses, row cap and GC, direction-aware reaper, persisted bans in [#8124](https://github.com/tari-project/tari/pull/8124)
* fix(comms): stop culled and idle RPC sessions promptly and bound internal channel sends in [#8118](https://github.com/tari-project/tari/pull/8118)
* fix: harden validation in [#8132](https://github.com/tari-project/tari/pull/8132)
* fix(identity): prevent secret key leakage from malformed identity errors in [#8115](https://github.com/tari-project/tari/pull/8115)
* fix(sidechain): weigh quorum certificates by signer voting power in [#8128](https://github.com/tari-project/tari/pull/8128)
* fix(validation): require the canonical script on side-chain claimable burns in [#8126](https://github.com/tari-project/tari/pull/8126)
* fix(wallet): derive imported transaction details from recovered output data in [#8133](https://github.com/tari-project/tari/pull/8133)
* fix(wallet): reject coin_split_even when fee exceeds total input value in [#8112](https://github.com/tari-project/tari/pull/8112)
* fix(common_sqlite): owner-only database files, WAL set in create_pool, per-database profiles in [#8107](https://github.com/tari-project/tari/pull/8107)
* fix(comms/dht): bound per-peer flood-ban metrics and drop stale entries in [#8110](https://github.com/tari-project/tari/pull/8110)
* fix(comms): bound memory held for stalled yamux peers, RPC/sync streams and gRPC GetBlocks in [#8108](https://github.com/tari-project/tari/pull/8108)
* fix(key_manager): low-impact hardening from the key manager security analysis in [#8106](https://github.com/tari-project/tari/pull/8106)
* fix(ledger): sign device sender-offset keys only through the reviewed metadata instruction in [#8104](https://github.com/tari-project/tari/pull/8104)
* fix(node): enable HTTP/2 and TCP keepalives on the base node gRPC server in [#8109](https://github.com/tari-project/tari/pull/8109)
* fix: bound protobuf decode on every peer-reachable path in [#8095](https://github.com/tari-project/tari/pull/8095)
* fix(jellyfish): reject non-monotonic versions in batch_put_value_set in [#8092](https://github.com/tari-project/tari/pull/8092)
* fix(jellyfish): remove public-API panics, bound traversal, check store integrity in [#8094](https://github.com/tari-project/tari/pull/8094)
* fix(key_manager): refuse degenerate nonces in [#8103](https://github.com/tari-project/tari/pull/8103)
* fix(ledger): keep alpha out of reach of the legacy host-indexed nonce instruction in [#8098](https://github.com/tari-project/tari/pull/8098)
* fix: refuse root-bearing key ids as commitment masks and in offline signing payloads in [#8099](https://github.com/tari-project/tari/pull/8099)
* fix: refuse to sign offline transactions that leave no change output in [#8093](https://github.com/tari-project/tari/pull/8093)
* fix(wallet): remove private-key UTXO export, which leaked the spend key in [#8102](https://github.com/tari-project/tari/pull/8102)

**Full Changelog**: https://github.com/tari-project/tari/compare/v6.1.0...v6.2.0

##### 变更文件

1. `Cargo.lock`
2. `Cargo.toml`
3. `applications/minotari_ledger_wallet/comms_testing/Cargo.lock`
4. `applications/minotari_ledger_wallet/comms_testing/Cargo.toml`
5. `applications/minotari_ledger_wallet/wallet/Cargo.lock`
6. `applications/minotari_ledger_wallet/wallet/Cargo.toml`
7. `supply-chain/config.toml`

##### AI 审查

风险级别：P3

## 宱要说明

本次对比的两个 tag（v6.2.0-pre.2 → v6.2.0）之间，提供的代码差异**仅包含版本号字符串的修改**，不包含任何功能、共识、协议或行为代码的变化。所有发行说明中描述的改动（包括 Breaking Changes）都**不在本 diff 的可验证范围内**，属于“证据不足”。

## 重要发现

1. **发行说明中的 Breaking Changes 无法在本次 diff 中验证**
   - 说明声称 `common_sqlite` 改为 owner-only 数据库文件、WAL 在 `create_pool` 中设置、按数据库区分 profile（#8107），以及钱包移除泄露花费密钥的私钥 UTXO 导出（#8102）。
   - 本 diff 中没有任何 `common_sqlite/` 或 `base_layer/wallet/` 的源代码变更。
   - 分类：**待验证**。需要检查 v6.1.0 → v6.2.0 的完整变更，或单独拉取 #8107、#8102 的补丁才能确认。

2. **声明的安全修复（密钥泄露、nonce 硬化、Ledger 指令限制等）无对应代码证据**
   - 例如 #8102（spend key 泄露）、#8115（identity 错误中的密钥泄露）、#8103（退化 nonce 拒绝）、#8098/#8104（Ledger 签名指令收紧）等。
   - 本 diff 未触及这些模块。
   - 分类：**证据不足**。不能断言“已修复”或“未修复”；只能确认发行说明做了如此声明。

3. **共识/兼容性相关声明无法确认**
   - 发行说明提到 sidechain quorum 按投票权加权（#8128）、side-chain claimable burns 要求 canonical script（#8126）、jellyfish 拒绝非单调版本（#8092）等可能影响共识或状态存储语义的改动。
   - 本次 diff 没有 `base_layer/sidechain/`、`infrastructure/jellyfish/`、`base_layer/core/` 的变更，因此是否存在硬分叉或共识不兼容行为无法判断。
   - 分类：**证据不足**。升级前需人工比对 v6.1.0→v6.2.0 的完整变更或对应 PR。

4. **实际可见的代码改动是纯机械版本号提升（无风险）**
   - `Cargo.toml`、`Cargo.lock`、`applications/minotari_ledger_wallet/{wallet,comms_testing}/Cargo.{toml,lock}`、`supply-chain/config.toml` 中 `6.2.0-pre.2` → `6.2.0`。
   - `supply-chain/config.toml` 中 `exemptions.which` 的版本号也随之更新（`which` 6.2.0 是外部 crate 的巧合同名版本，未引入新的豁免条目，仅修改了已有条目的版本字段）。
   - 分类：**代码支持**，无安全或兼容性影响。

5. **未发现恶意代码迹象**
   - diff 中没有新增依赖、没有网络/执行/权限相关代码、没有 build script 或 CI 脚本改动。
   - 分类：**代码支持**（基于本 diff 的范围）。

## 相关文件

- `Cargo.toml`（workspace 版本与依赖版本）
- `Cargo.lock`
- `applications/minotari_ledger_wallet/wallet/Cargo.toml` / `Cargo.lock`
- `applications/minotari_ledger_wallet/comms_testing/Cargo.toml` / `Cargo.lock`
- `supply-chain/config.toml`

## 人工复核建议

1. 确认发布流程：本次对比很可能是“仅打 tag、无新增提交”的发布。请核实 v6.2.0 与 v6.2.0-pre.2 之间实际提交历史，以排除 diff 采集不完整的情况。
2. 若需评估发行说明中的 Breaking Changes 与安全修复，请对比 **v6.1.0 → v6.2.0**（发行说明底部指向的完整变更区间），或逐一审查 #8107、#8102、#8115、#8103、#8098、#8104、#8126、#8128 等 PR。
3. 特别关注 #8102 的“移除私钥 UTXO 导出”：这是作者自述的历史密钥泄露修复，若属实，建议评估此前导出数据的泄露影响面与轮换需求。
4. 关于共识相关改动（sidechain quorum 权重、burn script 校验、jellyfish 版本单调性）：需人工确认是否存在激活高度/网络升级开关，以判断是否构成硬分叉；本 diff 无任何线索。
5. 在本次 diff 范围内，没有重大问题，也没有发现恶意代码迹象；但由于证据仅限于版本号变更，上述所有安全与兼容性声明均应视为**待人工复核**。



<!-- watch-release: eyJjb2luIjogInRhcmkiLCAicHVibGlzaGVkX2F0IjogIjIwMjYtMTAtMjhUMTM6MDU6MzhaIiwgInJlcG8iOiAidGFyaS1wcm9qZWN0L3RhcmkiLCAicmlzayI6ICJQMiIsICJ0YWciOiAidjYuMy4wLXByZS4wIn0 -->
#### v6.3.0-pre.0

- 仓库：[`tari-project/tari`](https://github.com/tari-project/tari)
- 发布日期：2026-10-28T13:05:38Z
- Release：https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.0
- 代码比较：`v6.2.0` → `v6.3.0-pre.0`
- AI 风险级别：P2

##### Release note

## What's Changed
* fix(transaction-components): strict amount grammar, wider terminal escaping, hasher network docs by @SWvheerden in https://github.com/tari-project/tari/pull/8138
* fix(comms-dht): ban only the provably culpable party for invalid DHT messages by @SWvheerden in https://github.com/tari-project/tari/pull/8139
* fix(comms): check resolved dial addresses, per-address dialer failures, tokio-util 0.7 and tower 0.5 by @SWvheerden in https://github.com/tari-project/tari/pull/8140
* fix(wallet): skip undecodable rows in completed transaction lists by @SWvheerden in https://github.com/tari-project/tari/pull/8145
* fix(comms-dht): relay received bytes verbatim, require canonical encodin by @SWvheerden in https://github.com/tari-project/tari/pull/8146
* fix(offline-signing): make multisig deposit and withdraw outputs recoverable by the recipient by @SWvheerden in https://github.com/tari-project/tari/pull/8147
* chore(deps): upgrade utoipa-swagger-ui to 10.0.2 (zip 9) by @sdbondi in https://github.com/tari-project/tari/pull/8152
* fix(identity): check 0600 permissions in load_from_json (#8034) by @Vallejo1921 in https://github.com/tari-project/tari/pull/8144
* fix(comms-dht): canonical dedup key, non-blocking and flood-resistant dedup cache by @SWvheerden in https://github.com/tari-project/tari/pull/8151
* fix(wallet): shut down non-interactive gRPC console wallet on SIGTERM or SIGINT by @Vallejo1921 in https://github.com/tari-project/tari/pull/8122
* chore(sidechain): use the published tari_sidechain 7.0.0 and tari_jellyfish crates by @sdbondi in https://github.com/tari-project/tari/pull/8153
* fix(common-types): refuse identity and non-point address keys, harden seed and wallet storage by @SWvheerden in https://github.com/tari-project/tari/pull/8154


**Full Changelog**: https://github.com/tari-project/tari/compare/v6.2.0-pre.2...v6.3.0-pre.0

##### 变更文件

1. `.cargo/audit.toml`
2. `Cargo.lock`
3. `Cargo.toml`
4. `applications/minotari_app_grpc/Cargo.toml`
5. `applications/minotari_app_grpc/src/conversions/burn_output_proof.rs`
6. `applications/minotari_app_utilities/src/identity_management.rs`
7. `applications/minotari_console_wallet/src/cli.rs`
8. `applications/minotari_console_wallet/src/grpc/shutdown_grace.rs`
9. `applications/minotari_console_wallet/src/grpc/wallet_grpc_server.rs`
10. `applications/minotari_console_wallet/src/lib.rs`
11. `applications/minotari_console_wallet/src/main.rs`
12. `applications/minotari_console_wallet/src/ui/ui_burnt_proof.rs`
13. `applications/minotari_console_wallet/src/utils/mod.rs`
14. `applications/minotari_console_wallet/src/utils/signal_handler.rs`
15. `applications/minotari_console_wallet/src/wallet_modes.rs`
16. `applications/minotari_ledger_wallet/comms_testing/Cargo.lock`
17. `applications/minotari_ledger_wallet/comms_testing/Cargo.toml`
18. `applications/minotari_ledger_wallet/wallet/Cargo.lock`
19. `applications/minotari_ledger_wallet/wallet/Cargo.toml`
20. `applications/minotari_node/Cargo.toml`
21. `applications/minotari_node/src/bootstrap.rs`
22. `applications/minotari_node/src/grpc/base_node_grpc_server.rs`
23. `applications/minotari_peer_sync/src/main.rs`
24. `base_layer/common_types/Cargo.toml`
25. `base_layer/common_types/src/burn_proof.rs`
26. `base_layer/common_types/src/encryption.rs`
27. `base_layer/common_types/src/payment_reference.rs`
28. `base_layer/common_types/src/seeds/cipher_seed.rs`
29. `base_layer/common_types/src/seeds/error.rs`
30. `base_layer/common_types/src/seeds/mnemonic.rs`
31. `base_layer/common_types/src/tari_address/dual_address.rs`
32. `base_layer/common_types/src/tari_address/mod.rs`
33. `base_layer/common_types/src/tari_address/single_address.rs`
34. `base_layer/common_types/src/types/bullet_rangeproofs.rs`
35. `base_layer/common_types/src/types/fixed_hash.rs`
36. `base_layer/core/Cargo.toml`
37. `base_layer/core/src/chain_storage/async_db.rs`
38. `base_layer/core/src/chain_storage/blockchain_database.rs`
39. `base_layer/core/tests/tests/async_db.rs`
40. `base_layer/p2p/Cargo.toml`
41. `base_layer/service_framework/Cargo.toml`
42. `base_layer/sidechain/Cargo.toml`
43. `base_layer/sidechain/src/burn_proof.rs`
44. `base_layer/sidechain/src/command.rs`
45. `base_layer/sidechain/src/commit_proof.rs`
46. `base_layer/sidechain/src/error.rs`
47. `base_layer/sidechain/src/lib.rs`
48. `base_layer/sidechain/src/serde.rs`
49. `base_layer/sidechain/src/shard_group.rs`
50. `base_layer/sidechain/src/validations.rs`
51. `base_layer/sidechain/tests/commit_proof.rs`
52. `base_layer/sidechain/tests/fixtures/README.md`
53. `base_layer/sidechain/tests/fixtures/commit_proof.json`
54. `base_layer/sidechain/tests/support/mod.rs`
55. `base_layer/transaction_components/Cargo.toml`
56. `base_layer/transaction_components/src/coinbase_builder.rs`
57. `base_layer/transaction_components/src/consensus/consensus_encoding/hashing.rs`
58. `base_layer/transaction_components/src/helpers/mod.rs`
59. `base_layer/transaction_components/src/helpers/terminal_safe.rs`
60. `base_layer/transaction_components/src/helpers/terminal_safe_table.rs`
61. `base_layer/transaction_components/src/key_manager/error.rs`
62. `base_layer/transaction_components/src/key_manager/interface.rs`
63. `base_layer/transaction_components/src/key_manager/manager.rs`
64. `base_layer/transaction_components/src/lib.rs`
65. `base_layer/transaction_components/src/offline_signing/mod.rs`
66. `base_layer/transaction_components/src/offline_signing/offline_signer.rs`
67. `base_layer/transaction_components/src/offline_signing/one_sided_signer.rs`
68. `base_layer/transaction_components/src/rpc/models/generate_burn_output_proof.rs`
69. `base_layer/transaction_components/src/tari_amount.rs`
70. `base_layer/transaction_components/src/transaction_builder/builder.rs`
71. `base_layer/transaction_components/src/transaction_builder/models.rs`
72. `base_layer/transaction_components/src/transaction_components/burn_output_proof.rs`
73. `base_layer/transaction_components/src/transaction_components/encrypted_data.rs`
74. `base_layer/transaction_components/src/transaction_components/memo_field.rs`
75. `base_layer/transaction_components/src/transaction_components/test.rs`
76. `base_layer/transaction_key_manager/src/legacy_key_manager/wrapper.rs`
77. `base_layer/transaction_key_manager/src/storage/sqlite_db/imported_keys.rs`
78. `base_layer/transaction_key_manager/src/storage/sqlite_db/key_manager_state.rs`
79. `base_layer/transaction_key_manager/src/storage/sqlite_db/mod.rs`
80. `base_layer/wallet/Cargo.toml`
81. `base_layer/wallet/src/output_manager_service/recovery/standard_outputs_recoverer.rs`
82. `base_layer/wallet/src/output_manager_service/service.rs`
83. `base_layer/wallet/src/storage/database.rs`
84. `base_layer/wallet/src/storage/serializers.rs`
85. `base_layer/wallet/src/storage/sqlite_db/models.rs`
86. `base_layer/wallet/src/storage/sqlite_db/wallet.rs`
87. `base_layer/wallet/src/transaction_service/error.rs`
88. `base_layer/wallet/src/transaction_service/protocols/check_faux_transaction_status.rs`
89. `base_layer/wallet/src/transaction_service/service.rs`
90. `base_layer/wallet/src/transaction_service/storage/database.rs`
91. `base_layer/wallet/src/transaction_service/storage/sqlite_db.rs`
92. `base_layer/wallet/src/utxo_scanner_service/utxo_scanner_task.rs`
93. `base_layer/wallet/src/wallet.rs`
94. `base_layer/wallet/tests/output_manager_service_tests/service.rs`
95. `base_layer/wallet/tests/transaction_service_tests/service.rs`
96. `base_layer/wallet_ffi/src/error.rs`
97. `base_layer/wallet_ffi/src/lib.rs`
98. `base_layer/wallet_ffi/wallet.h`
99. `changelog-development.md`
100. `common/config/presets/c_base_node_c.toml`
101. `common/config/presets/d_console_wallet.toml`
102. `comms/core/Cargo.toml`
103. `comms/core/src/connection_manager/dialer.rs`
104. `comms/core/src/connection_manager/tests/listener_dialer.rs`
105. `comms/core/src/multiplexing/yamux.rs`
106. `comms/core/src/net_address/dial_address_policy.rs`
107. `comms/core/src/net_address/mod.rs`
108. `comms/core/src/net_address/multiaddr_range.rs`
109. `comms/core/src/net_address/multiaddr_with_stats.rs`
110. `comms/core/src/net_address/mutliaddresses_with_stats.rs`
111. `comms/core/src/noise/crypto_resolver.rs`
112. `comms/core/src/peer_manager/error.rs`
113. `comms/core/src/peer_manager/identity_signature.rs`
114. `comms/core/src/peer_manager/peer.rs`
115. `comms/core/src/peer_validator/config.rs`
116. `comms/core/src/peer_validator/error.rs`
117. `comms/core/src/peer_validator/helpers.rs`
118. `comms/core/src/transports/dns/error.rs`
119. `comms/core/src/transports/dns/system.rs`
120. `comms/core/src/transports/hidden_service_transport.rs`
121. `comms/core/src/transports/mod.rs`
122. `comms/core/src/transports/socks.rs`
123. `comms/core/src/transports/tcp.rs`
124. `comms/core/src/transports/tcp_with_tor.rs`
125. `comms/dht/Cargo.toml`
126. `comms/dht/migrations/2026-10-20-120000_dedup_cache_trim_columns/down.sql`
127. `comms/dht/migrations/2026-10-20-120000_dedup_cache_trim_columns/up.sql`
128. `comms/dht/src/actor.rs`
129. `comms/dht/src/config.rs`
130. `comms/dht/src/dedup/dedup_cache.rs`
131. `comms/dht/src/dedup/mod.rs`
132. `comms/dht/src/dht.rs`
133. `comms/dht/src/discovery/service.rs`
134. `comms/dht/src/envelope.rs`
135. `comms/dht/src/inbound/decryption.rs`
136. `comms/dht/src/inbound/deserialize.rs`
137. `comms/dht/src/inbound/dht_handler/task.rs`
138. `comms/dht/src/inbound/forward.rs`
139. `comms/dht/src/inbound/message.rs`
140. `comms/dht/src/inbound/mod.rs`
141. `comms/dht/src/message_signature.rs`
142. `comms/dht/src/network_discovery/discovering.rs`
143. `comms/dht/src/network_discovery/error.rs`
144. `comms/dht/src/network_discovery/rebootstrap.rs`
145. `comms/dht/src/network_discovery/test.rs`
146. `comms/dht/src/outbound/broadcast.rs`
147. `comms/dht/src/outbound/message_params.rs`
148. `comms/dht/src/outbound/mod.rs`
149. `comms/dht/src/outbound/serialize.rs`
150. `comms/dht/src/peer_validator.rs`
151. `comms/dht/src/proto/envelope.proto`
152. `comms/dht/src/proto/mod.rs`
153. `comms/dht/src/schema.rs`
154. `comms/dht/tests/attacks.rs`
155. `comms/dht/tests/dht.rs`
156. `docs/src/09_adding_tari_to_your_exchange.md`
157. `docs/src/payref_userguide.md`
158. `infrastructure/jellyfish/Cargo.toml`
159. `infrastructure/jellyfish/src/bit_iter.rs`
160. `infrastructure/jellyfish/src/cbor.rs`
161. `infrastructure/jellyfish/src/error.rs`
162. `infrastructure/jellyfish/src/hash.rs`
163. `infrastructure/jellyfish/src/lib.rs`
164. `infrastructure/jellyfish/src/memory_store.rs`
165. `infrastructure/jellyfish/src/store.rs`
166. `infrastructure/jellyfish/src/tree.rs`
167. `infrastructure/jellyfish/src/types.rs`
168. `integration_tests/src/wallet_process.rs`
169. `integration_tests/tests/features/WalletTransactions.feature`
170. `integration_tests/tests/steps/wallet_steps.rs`
171. `package-lock.json`
172. `scripts/decoder_parity_check.py`
173. `scripts/gen_terminal_safe_table.py`
174. `scripts/publish_crates.sh`
175. `supply-chain/config.toml`

##### AI 审查

风险级别：P2

（依据：所给 diff 中未发现确凿的安全漏洞或恶意代码，但存在若干兼容性/格式/持久化变化和未纳入 diff 的关键依赖替换，需要人工复核；diff 本身在 `cipher_seed.rs` 测试部分被截断，多个发行说明声称的模块未提供。）

1. 侧链/Jellyfish 依赖从本地代码改为 crates.io 发布版本，且代码不在 diff 中（待验证）
   - 发行说明称“使用已发布的 tari_sidechain 7.0.0 与 tari_jellyfish”；`Cargo.toml` / `Cargo.lock` 显示 `base_layer/sidechain`、`infrastructure/jellyfish` 从 workspace members 移除，`tari_sidechain = { version = "7.0.0" }`（checksum 516db8…）、`tari_jellyfish 6.2.1`（checksum a92810…）改为 registry 依赖，且是 major 版本跳变（6.2.0 → 7.0.0）。
   - 相关文件：`Cargo.toml`、`Cargo.lock`、`applications/minotari_app_grpc/src/conversions/burn_output_proof.rs`、`base_layer/common_types/src/burn_proof.rs`。
   - `BurnOutputProof`/`MmrInclusionProof`/`OutputHashPreimage` 从 `tari_common_types` 移入 `tari_sidechain`，属于对外类型/API 破坏性移动。发布的 crate 内部代码未提供，无法审计其验证逻辑是否与原地等价。
   - 建议：对 crates.io 上这两个版本做来源与内容比对（与原 `base_layer/sidechain`、`infrastructure/jellyfish` diff），确认无逻辑/序列化差异，并核对 checksum 与 tag 一致。

2. 同一构建中并存两个 `tari_hashing` 版本，存在哈希域一致性风险（待验证）
   - `Cargo.lock` 显示本地 `tari_hashing 6.3.0-pre.0`（core/wallet 等使用）与 registry `tari_hashing 6.2.0`（`tari_sidechain 7.0.0`、`tari_jellyfish 6.2.1` 使用）同时被链接。
   - 若 6.3.0-pre.0 的 hashing 域标签/MAC 输入顺序有变动（发行说明提到“hasher network docs”，但 hashing 源码未提供），而侧链证明验证仍用 6.2.0 计算，可能出现跨 crate 哈希不一致，涉及共识/证明验证。
   - 建议：比对 `hashing` 目录 v6.2.0 与 v6.3.0-pre.0 的域分离标签，确认纯文档变更；若任何标签有改动即升级为共识问题。

3. CipherSeed 序列化/兼容性格式变化（代码支持，影响待验证）
   - `base_layer/common_types/src/seeds/cipher_seed.rs`：`Serialize` 现在写“加密后”形式（人类可读为 hex，否则 bytes），`Deserialize` 只接受该形式或人类可读的旧明文结构；新增版本 3（Argon2id，仅在用户提供口令时写出）。`decrypt_bytes_integral_nonce` 返回值改为 `Hidden<Vec<u8>>`（安全正向）。
   - 风险点：（a）此前以非人类可读格式（如 bincode/serde）持久化了明文结构体形式的 `CipherSeed` 的数据，新代码无法回读——若钱包/备份/导出存在此类数据属破坏性升级；（b）版本 3 种子会被仅支持版本 2 的旧钱包拒绝（代码注释已声明此设计）；（c）`Serialize` 用固定默认口令 `TARI_CIPHER_SEED` 加密，只是混淆而非保密，不应被当作加密存储。
   - 建议：盘点 `CipherSeed` 的所有持久化/导出路径（钱包 DB、seed 词、JSON 导出），验证新旧双向迁移；diff 在测试部分被截断，需人工查看完整测试与调用方。

4. 身份/Tor 身份文件统一强制 0600 权限检查，可能造成启动失败（代码支持，属预期的破坏性配置变化）
   - `applications/minotari_app_utilities/src/identity_management.rs`：`load_from_json` 现在对所有调用执行 `check_identity_file`；`load_tor_identity` 签名改为 `ExitError`，node 与 peer_sync 改用它（`applications/minotari_node/src/bootstrap.rs`、`applications/minotari_peer_sync/src/main.rs`）。
   - 原先宽松权限下可运行的部署升级后会在启动时报 `ExitCode::ConfigError` 拒启（有测试覆盖）。发行说明“check 0600 permissions in load_from_json”与代码一致。需注意非 Unix 平台/挂载卷（如 Docker 卷、网络盘）上 chmod 不可用的部署。

5. 钱包 gRPC 错误语义与 CancelTransaction 行为变化（代码支持，客户端兼容性）
   - `applications/minotari_console_wallet/src/grpc/wallet_grpc_server.rs`：查库失败由 `NOT_FOUND`/`UNKNOWN` 改为 `INTERNAL`，不可解码行改报 `DATA_LOSS: undecodable rows: skipped=…`；`CancelTransaction` 在行不可解码时绕过状态检查直接调用 `cancel_pending_transaction`；`get_payment_by_reference` 历史 PayRef 查询失败由静默返回空改为报错。
   - 依赖 `TransactionStorageError::UndecodableRows`、`CompletedTransactionConversionError` 等新/改错误变体（其所在存储层代码未提供，无法确认“跳过不可解码行”是否可能掩盖真实数据损坏）。这是 API 行为变化，依赖旧行为（把失败当空结果）的客户端可能出错。

6. gRPC 钱包关闭路径与强制退出（代码支持，建议复核时序）
   - 新增 `applications/minotari_console_wallet/src/utils/signal_handler.rs`：第二次 SIGINT/SIGTERM 直接 `std::process::exit(130)`（SIGTERM 也返回 130 而非 143，仅语义小节问题）；`wallet_modes.rs` 的 `grpc_mode` 用新的 `grpc_shutdown` 替换 `wallet.shutdown_signal` 并用转发任务桥接原信号。
   - 强制 `exit` 会绕过析构/落盘，属设计意图但可能在 shutdown 卡住时中断数据库写入；替换 shutdown signal 的桥接若触发顺序异常可能影响其它服务的优雅关闭。建议人工复核 `WalletSqlite::shutdown_signal` 的所有消费方。

7. 挖矿 coinbase 请求预校验（代码支持，兼容性变化）
   - `applications/minotari_node/src/grpc/base_node_grpc_server.rs` 新增 `coinbase_target_addresses` + `validate_coinbase_request`：按索引拒绝非法地址、identity/非点地址键、超长 payment id/coinbase extra，并不再混淆这些错误信息（注释称只描述调用方自身输入）。
   - 会拒绝此前可能被接受的 coinbase 目标（如仅交互式单地址、identity 键），对矿池是行为破坏；节点侧模板构造，未见共识常量改动，不构成硬分叉证据（共识代码未完整提供，无法完全排除）。
   - 附带正向：`GetAllCompletedTransactions` 中 `Vec::with_capacity(total_requested…)` 改为 `Vec::new()`，消除由超大 `limit` 触发的潜在内存耗尽。

8. 发行说明中多项声明在所给 diff 中无对应代码（证据不足）
   - “strict amount grammar, wider terminal escaping”“ban only the provably culpable party”“relay received bytes verbatim, require canonical encoding”“canonical dedup key, non-blocking flood-resistant dedup cache”“check resolved dial addresses… tower 0.5”“offline-signing multisig … recoverable”“refuse identity and non-point address keys, harden seed and wallet storage”（后两项只见部分 seed/coinbase 相关代码）——`comms/dht`、`comms/core`、`transaction_components`、`offline_signing` 的源码均未出现在 diff 中。
   - DHT 中继/去重/封禁规则变化是 P2P 兼容性与 DoS 面的关键改动，目前只能标记为“作者声明，无法核实”。`tower 0.4→0.5`、`tokio-util 0.6→0.7`、`utoipa 5→6`、`utoipa-swagger-ui 9→10`（zip 3→9）、`rustls-webpki/webpki-roots` 升级在 lock 文件中可见，未见异常来源。
   - `.cargo/audit.toml` 仅加了一个尾逗号，未新增审计豁免（正向）。

9. 恶意代码迹象
   - 在所给 diff 内未发现恶意或可疑行为。测试代码中的 `unsafe extern "C" { fn raise(...) }` 仅用于测试信号处理，注释与用途一致。注意：由于 `tari_sidechain 7.0.0`、`tari_jellyfish 6.2.1`、`tari_hashing 6.2.0` 三个 registry crate 的源码未提供，本次结论不覆盖它们。

人工复核建议（按优先级）：
1. 获取并比对 crates.io 上 `tari_sidechain 7.0.0`、`tari_jellyfish 6.2.1`、`tari_hashing 6.2.0` 与原仓库代码，重点核对序列化、哈希域与证明验证逻辑；确认与本地 `tari_hashing 6.3.0-pre.0` 的域分离标签一致。
2. 用完整 diff 复核 `comms/dht`（ban/relay/dedup）与 `comms/core`（dial）改动的网络兼容性与资源使用（缓存是否有界、是否可被 flood 耗尽）。
3. 测试 `CipherSeed` 新旧序列化互操作与钱包数据库迁移路径，确认没有旧格式数据被新版拒读。
4. 评估 gRPC 错误码与 coinbase 校验收紧对现有矿池/客户端的破坏面，并在升级公告中注明；确认 0600 权限检查在目标部署环境不会导致拒启。
5. 复核 gRPC 钱包 shutdown 桥接与第二次信号强制 `exit(130)` 的落盘时序。



<!-- watch-release: eyJjb2luIjogInRhcmkiLCAicHVibGlzaGVkX2F0IjogIjIwMjYtMTAtMjhUMTM6MDU6NTZaIiwgInJlcG8iOiAidGFyaS1wcm9qZWN0L3RhcmkiLCAicmlzayI6ICJQMiIsICJ0YWciOiAidjYuMy4wLXByZS4xIn0 -->
#### v6.3.0-pre.1

- 仓库：[`tari-project/tari`](https://github.com/tari-project/tari)
- 发布日期：2026-10-28T13:05:56Z
- Release：https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.1
- 代码比较：`v6.3.0-pre.0` → `v6.3.0-pre.1`
- AI 风险级别：P2

##### Release note

## What's Changed
* chore(deps): use tari_sidechain 8.0.0 so pre-release crates can be published by @SWvheerden in https://github.com/tari-project/tari/pull/8158


**Full Changelog**: https://github.com/tari-project/tari/compare/v6.3.0-pre.0...v6.3.0-pre.1

##### 变更文件

1. `Cargo.lock`
2. `Cargo.toml`
3. `applications/minotari_ledger_wallet/comms_testing/Cargo.lock`
4. `applications/minotari_ledger_wallet/comms_testing/Cargo.toml`
5. `applications/minotari_ledger_wallet/wallet/Cargo.lock`
6. `applications/minotari_ledger_wallet/wallet/Cargo.toml`
7. `supply-chain/config.toml`

##### AI 审查

风险级别：P2

本次发布（v6.3.0-pre.0 → v6.3.0-pre.1）的提供的差异仅包含 Cargo 清单、锁文件和 cargo-vet 供应链配置的改动，未包含任何 Rust 源码变更。发行说明声称的“使用 tari_sidechain 8.0.0 以便发布预发布 crate”与差异整体一致（版本号统一 bump + 依赖升级），但差异中存在若干需人工确认的点：

1. **外部依赖主版本升级，共识/兼容性影响无法从提供的差异验证（待验证）**
   - `tari_sidechain` 7.0.0 → 8.0.0（`Cargo.toml`、`Cargo.lock`），校验和亦变更；
   - `tari_jellyfish` 6.2.1 → 7.0.0（Merkle 树库），依赖从 `tari_hashing 6.2.0` 改为直接使用 `blake2`，其哈希/承诺构造方式可能发生变化；
   - 这两个 crate 来自 crates.io registry，其源码**未包含在提供的差异中**，无法确认是否存在序列化格式、Merkle 承诺、验证逻辑或侧链状态证明的变化。`tari_sidechain` 被 `tari_common_types`（进而被 `tari_core` 等）依赖，若涉及承诺结构，可能影响侧链相关共识或跨版本兼容性。
   - 结论：发行说明“仅为发布流程”的说法**待验证**；提供的差异中**没有**硬分叉激活高度、共识常量或协议版本变更的证据，但由于外部 crate 源码不可见，不能排除。

2. **`tari_hashing` 双版本收敛（待验证，倾向于良性）**
   - 之前 Cargo.lock 中同时存在 registry 版 `tari_hashing 6.2.0`（被 `tari_sidechain`、`tari_jellyfish` 使用）与本地 path 版 `tari_hashing 6.3.0-pre.0`；现在统一为本地 path 版 `6.3.0-pre.1`，`tari_sidechain 8.0.0` 不再依赖 `tari_hashing 6.2.0`。
   - 从差异看这是消除两套哈希实现并存的改进，但本地 `hashing/` 相对 6.2.0 的具体行为差异（代码未提供）无法核对。相关文件：`Cargo.lock`、`Cargo.toml`（`tari_hashing = { path = "hashing", ... }`）。

3. **`supply-chain/config.toml` 豁免记录疑似误改（证据支持，建议修正）**
   - `[[exemptions.which]]` 的 `version` 从 `6.3.0-pre.0` 改为 `6.3.0-pre.1`。第三方 crate `which` 不使用 Tari 的版本号，这看起来像是批量替换版本字符串时误伤了 cargo-vet 豁免条目。后果是豁免记录与实际第三方版本不匹配，可能导致 `cargo vet` 校验失效或供应链审计配置不一致。这不是恶意代码迹象，但属于供应链治理问题。
   - 相关文件：`supply-chain/config.toml`（约第 3278 行附近）。

4. **编译期依赖 `syn` 1.0.109 → 2.0.118（无运行时风险）**
   - 仅是某个 proc-macro crate 的编译期依赖更新（`Cargo.lock`），不影响运行时行为，无安全含义。

5. **恶意代码/崩溃/内存问题：提供的差异中无证据**
   - 差异仅涉及版本号与依赖声明，未见可疑代码、构建脚本改动或新增网络/执行行为。注意这只是对所给 diff 的判断，不代表对 `tari_sidechain`/`tari_jellyfish` 外部源码或未提供的仓库其他部分做了审查。

**人工复核建议**
- 审查 crates.io 上 `tari_sidechain 8.0.0` 与 `tari_jellyfish 7.0.0` 的源码/变更日志（未包含在本差异中），重点确认：Merkle 树/承诺哈希构造是否改变、序列化格式是否变化、侧链验证逻辑是否变化，并据此判断是否存在共识或跨版本兼容性风险；
- 确认本地 `hashing/` crate 与原 registry `tari_hashing 6.2.0` 的哈希行为一致性（尤其被 `tari_jellyfish`/侧链路径使用的哈希域）；
- 核对并修正 `supply-chain/config.toml` 中 `which` 的豁免版本，运行 `cargo vet` 验证供应链配置；
- 因这是 `-pre` 预发布版本，建议在正式版本前补充针对侧链路径的集成/兼容性测试。



<!-- watch-release: eyJjb2luIjogInRhcmkiLCAicHVibGlzaGVkX2F0IjogIjIwMjYtMTAtMjlUMDE6Mjg6MTdaIiwgInJlcG8iOiAidGFyaS1wcm9qZWN0L3RhcmkiLCAicmlzayI6ICLlvoXkurrlt6XlpI3moLgiLCAidGFnIjogInY2LjMuMC1wcmUuMiJ9 -->
#### v6.3.0-pre.2

- 仓库：[`tari-project/tari`](https://github.com/tari-project/tari)
- 发布日期：2026-10-29T01:28:17Z
- Release：https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.2
- 代码比较：`v6.3.0-pre.1` → `v6.3.0-pre.2`
- AI 风险级别：待人工复核

##### Release note

## What's Changed
* fix(core): check claimed difficulty on short header batches by @SWvheerden in https://github.com/tari-project/tari/pull/8160
* fix(mempool): drop encrypted transaction gossip and always ban the clear-text source by @SWvheerden in https://github.com/tari-project/tari/pull/8173
* fix(chain-storage): keep walking an orphan's ancestry above the main tip by @SWvheerden in https://github.com/tari-project/tari/pull/8174
* fix(chain-storage): output index consistency by @SWvheerden in https://github.com/tari-project/tari/pull/8175
* test(grpc,script): cover MAX_SCRIPT_BYTES and 8 MiB gRPC script rejection (#8012) by @Brayaniglesias08 in https://github.com/tari-project/tari/pull/8167
* fix(grpc): replace per-request Argon2id with constant-time Basic auth and per-IP backoff (#8013) by @Brayaniglesias08 in https://github.com/tari-project/tari/pull/8170
* fix(identity): back up corrupt identity files before regenerating (#8030) by @Brayaniglesias08 in https://github.com/tari-project/tari/pull/8164
* fix(grpc): zeroize UnblindedOutput keys on all exit paths and redact Debug (#8020) by @Brayaniglesias08 in https://github.com/tari-project/tari/pull/8166
* fix(node): log and document gRPC methods enabled by mining and second-layer flags (#8024) by @Brayaniglesias08 in https://github.com/tari-project/tari/pull/8168
* fix(mempool): only exempt height-dependent input script failures from bans by @SWvheerden in https://github.com/tari-project/tari/pull/8187
* fix(validation): consistent verdicts for re-created outputs and validator node queries after exit by @SWvheerden in https://github.com/tari-project/tari/pull/8191
* fix(deps): bump ctutils and tokio, ignore crypto-bigint 0.5 timing advisory by @Brayaniglesias08 in https://github.com/tari-project/tari/pull/8186
* fix(miner): handle stratum responses without a method field by @SWvheerden in https://github.com/tari-project/tari/pull/8192
* fix(utilities): prevent prompt CPU spin on non-TTY and handle EOF/quit cleanly by @Vallejo1921 in https://github.com/tari-project/tari/pull/8123
* fix(chain-storage): require a sorted body before treating it as the one its header commits to by @SWvheerden in https://github.com/tari-project/tari/pull/8193
* fix(libtor): bundle Tor 0.4.9.15 so the base node no longer exits on the current Tor consensus by @SWvheerden in https://github.com/tari-project/tari/pull/8194

## New Contributors
* @Brayaniglesias08 made their first contribution in https://github.com/tari-project/tari/pull/8167

**Full Changelog**: https://github.com/tari-project/tari/compare/v6.3.0-pre.1...v6.3.0-pre.2

##### 变更文件

1. `.cargo/audit.toml`
2. `Cargo.lock`
3. `Cargo.toml`
4. `applications/minotari_app_grpc/Cargo.toml`
5. `applications/minotari_app_grpc/build.rs`
6. `applications/minotari_app_grpc/src/authentication/basic_auth.rs`
7. `applications/minotari_app_grpc/src/authentication/mod.rs`
8. `applications/minotari_app_grpc/src/authentication/salted_password.rs`
9. `applications/minotari_app_grpc/src/authentication/server_interceptor.rs`
10. `applications/minotari_app_grpc/src/conversions/transaction_output.rs`
11. `applications/minotari_app_grpc/src/conversions/unblinded_output.rs`
12. `applications/minotari_app_utilities/src/identity_management.rs`
13. `applications/minotari_app_utilities/src/parse_miner_input.rs`
14. `applications/minotari_console_wallet/src/grpc/wallet_grpc_server.rs`
15. `applications/minotari_console_wallet/src/init/mod.rs`
16. `applications/minotari_ledger_wallet/comms_testing/Cargo.lock`
17. `applications/minotari_ledger_wallet/comms_testing/Cargo.toml`
18. `applications/minotari_ledger_wallet/wallet/Cargo.lock`
19. `applications/minotari_ledger_wallet/wallet/Cargo.toml`
20. `applications/minotari_merge_mining_proxy/src/run_merge_miner.rs`
21. `applications/minotari_miner/Cargo.toml`
22. `applications/minotari_miner/src/miner.rs`
23. `applications/minotari_miner/src/run_miner.rs`
24. `applications/minotari_miner/src/stratum/controller.rs`
25. `applications/minotari_miner/src/stratum/stratum_controller/controller.rs`
26. `applications/minotari_miner/tests/non_tty_exit.rs`
27. `applications/minotari_node/src/config.rs`
28. `applications/minotari_node/src/grpc/base_node_grpc_server.rs`
29. `base_layer/core/src/base_node/comms_interface/inbound_handlers.rs`
30. `base_layer/core/src/base_node/rpc/query_service.rs`
31. `base_layer/core/src/base_node/rpc/service.rs`
32. `base_layer/core/src/base_node/sync/block_sync/error.rs`
33. `base_layer/core/src/base_node/sync/block_sync/synchronizer.rs`
34. `base_layer/core/src/base_node/sync/header_sync/synchronizer.rs`
35. `base_layer/core/src/base_node/sync/horizon_state_sync/synchronizer.rs`
36. `base_layer/core/src/base_node/sync/rpc/mod.rs`
37. `base_layer/core/src/base_node/sync/rpc/sync_utxos_task.rs`
38. `base_layer/core/src/chain_storage/active_validator_node.rs`
39. `base_layer/core/src/chain_storage/async_db.rs`
40. `base_layer/core/src/chain_storage/blockchain_backend.rs`
41. `base_layer/core/src/chain_storage/blockchain_database.rs`
42. `base_layer/core/src/chain_storage/db_transaction.rs`
43. `base_layer/core/src/chain_storage/lmdb_db/cursors.rs`
44. `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs`
45. `base_layer/core/src/chain_storage/lmdb_db/validator_node_store.rs`
46. `base_layer/core/src/chain_storage/tests/blockchain_database.rs`
47. `base_layer/core/src/chain_storage/utxo_mined_info.rs`
48. `base_layer/core/src/mempool/mempool_storage.rs`
49. `base_layer/core/src/mempool/service/inbound_handlers.rs`
50. `base_layer/core/src/test_helpers/block_spec.rs`
51. `base_layer/core/src/test_helpers/blockchain.rs`
52. `base_layer/core/src/test_helpers/mod.rs`
53. `base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs`
54. `base_layer/core/src/validation/block_body/block_body_partial_validator.rs`
55. `base_layer/core/src/validation/block_body/mod.rs`
56. `base_layer/core/src/validation/block_body/test.rs`
57. `base_layer/core/src/validation/error.rs`
58. `base_layer/core/src/validation/helpers.rs`
59. `base_layer/core/tests/helpers/block_builders.rs`
60. `base_layer/core/tests/helpers/nodes.rs`
61. `base_layer/core/tests/helpers/sync.rs`
62. `base_layer/core/tests/tests/block_sync.rs`
63. `base_layer/core/tests/tests/header_sync.rs`
64. `base_layer/core/tests/tests/node_comms_interface.rs`
65. `base_layer/transaction_components/src/transaction_components/test.rs`
66. `base_layer/transaction_components/src/validation/aggregate_body/aggregate_body_internal_validator.rs`
67. `base_layer/transaction_components/src/validation/error.rs`
68. `changelog-development.md`
69. `common/config/presets/c_base_node_b_mining_allow_methods.toml`
70. `common/config/presets/c_base_node_b_non_mining_allow_methods.toml`
71. `common/src/configuration/bootstrap.rs`
72. `common/src/configuration/utils.rs`
73. `deny.toml`
74. `docs/src/API_GRPC_Explanation.md`
75. `infrastructure/libtor/Cargo.toml`
76. `infrastructure/tari_script/src/script.rs`
77. `package-lock.json`
78. `supply-chain/config.toml`

##### AI 审查

风险级别：待人工复核

说明：发行说明声称的多数共识/验证/内存池改动在所提供的 diff 中并不存在（diff 只包含 Cargo 清单与锁文件、`applications/minotari_app_grpc`、`applications/minotari_app_utilities`，且在 `identity_management.rs` 测试中途被截断），因此无法对最高影响面的改动做出定级；可见部分本身大致为 P2 级别的安全权衡与加固。以下按证据强度区分“代码支持 / 待验证 / 证据不足”。

重要发现

1. 共识与验证规则改动无法从提供的 diff 中核实（证据不足，优先级最高）
   发行说明声称修复：短头批次的 claimed difficulty 校验（#8160）、孤儿祖先回溯（#8174）、output index 一致性（#8175）、body 排序后才视为 header 承诺的 body（#8193）、mempool 加密交易 gossip 丢弃并封禁明文来源（#8173）、mempool 豁免范围收窄（#8187）、验证判定一致性（#8191）。这些均属于区块/交易接受规则层面，可能改变共识判定或对等节点封禁行为，是硬分叉/兼容性风险的典型来源。提供的 diff 中完全没有 `base_layer/core`、chain_storage、mempool 相关文件，无法确认规则是否变化、是否需要网络版本门控或协调升级。
   相关文件（未在 diff 中出现，仅按发行说明推断）：base_layer/core（共识/验证）、chain_storage、mempool。
   人工复核建议：拉取上述 PR 的实际文件差异；逐条判断是否改变“区块/交易是否被接受”的判定；若收紧校验（如 body 必须排序、difficulty 必须核实），确认旧节点与新节点是否会对同一历史/新块产生分歧，并评估 #8173/#8187 的封禁策略是否可能误封合法旧版本节点。

2. gRPC Basic 认证从每请求 Argon2id 验证改为内存中明文常量时间比较（代码支持，安全权衡，需确认部署约束）
   `applications/minotari_app_grpc/src/authentication/basic_auth.rs`、`server_interceptor.rs` 中可见：
   - `BasicAuthCredentials` 现在保存明文口令（`Zeroizing<Vec<u8>>`）并逐字节比较（`constant_time_verify_padded`），`salted_password.rs`（Argon2id PHC 哈希）被删除，`minotari_app_grpc` 的 `argon2` 依赖被移除（Cargo.toml/Cargo.lock 一致）。
   - 新增按来源 IP 的失败退避：`MAX_FAILURES_BEFORE_BACKOFF=5`、`FAILURE_WINDOW=60s`、`INITIAL_BACKOFF=50ms`、`MAX_BACKOFF=60s`、`MAX_TRACKED_PEERS=1024`（有界，配套测试断言有界性），并对接入地址做日志限速。
   风险权衡（代码支持）：
   - 单次验证从约数十毫秒（Argon2id）降到微秒级（测试 `failed_auth_completes_in_microseconds` 明确如此），暴力破解成本大幅下降，防护完全依赖按 IP 退避；跨 IP（僵尸网络、IPv6 前缀轮换）可绕过，且 `MAX_TRACKED_PEERS=1024` 的 LRU 淘汰使大量来源 IP 可冲刷跟踪表。
   - `is_loopback_ip` 对 loopback（含 IPv4-mapped IPv6）完全豁免跟踪与退避，本机任意进程可以微秒级速度无节制尝试口令。
   - 配置中必须存在明文口令且长期驻留内存（可被 core dump/交换区暴露）；旧代码 `BasicAuthCredentials::new` 只接受 PHC 哈希字符串，若既有部署在配置里放的是 PHC 哈希，新代码会把哈希串当明文口令比对，导致认证失效（失败关闭），发行说明未给迁移说明。
   代码支持：常量时间比较实现本身对越长输入做了裁剪（`bytes_len_clipped`、`get(i).unwrap_or(pad_byte)`），未发现可由超长 Authorization 头触发的 panic（原越长用户名 panic 回归测试被保留）。
   人工复核建议：确认配置解析与启动路径对“PHC 哈希配置”的兼容处理；评估默认文档是否强制绑定 localhost/防火墙 + 强口令；考虑增加全局（而非仅按 IP）速率上限，或保留慢 KDF + 校验结果缓存；确认 `ServerAuthenticationInterceptor::new` 返回 `None` 时调用方是拒绝启动还是禁用认证（避免 fail-open，此点在 diff 中未见调用方）。

3. gRPC 私钥脱敏与 zeroize（代码支持，覆盖范围待验证）
   `applications/minotari_app_grpc/build.rs` 对 5 个含私钥字段的 proto 消息 `skip_debug`，`conversions/unblinded_output.rs` 为 `UnblindedOutput`、`ImportUtxosRequest`、`CreateBurnTransactionRequest`、`RegisterValidatorNodeRequest`、`SubmitValidatorNodeExitRequest` 手写 `Debug`（`spending_key`/`script_private_key`/`sidechain_deployment_key` 打印为 `<redacted>`）；`ZeroizeOutputKeys` 的 `Drop` 在 `convert_unblinded_output` 所有退出路径（含早期错误返回）清零 spending/script 私钥，`take_sidechain_deployment_key` 解析后清零缓冲。
   待验证：发行说明称“on all exit paths”，函数内路径有测试覆盖，但 by-value `TryFrom` 只清零被传入的那一份拷贝；若调用方仍持有包含私钥的请求消息（或 tonic 反序列化缓冲、调用方 clone），副本不清零；`take_sidechain_deployment_key` 是否被全部调用点使用在提供的 diff 中看不到。
   人工复核建议：核对 wallet/gRPC 服务端所有使用这些请求类型的调用点是否走 `take_*`；确认手写 `Debug` 字段列表与 proto 保持同步（新增敏感字段目前不会被打印，但也不会出现在日志中）。

4. 依赖替换与供应链（待验证）
   Cargo.lock 中 `libtor`/`libtor-sys`/`libtor-src`（47.13.0+0.4.7.x）被移除，替换为 crates.io 上的改名包 `tari-libtor-core/-derive/-src/-sys`（49.15.2+0.4.9.15），经 autotools/cc 编译 Tor C 源码并依赖 openssl-sys。发行说明称用于修复“当前 Tor 共识导致 base node 退出”（兼容性修复，方向合理）。但 diff 只有锁文件校验和，无法证明这些新包的源码与上游 Tor 0.4.9.15 一致或确由 Tari 官方发布。另 `tokio` 1.52.3→1.54.1、`ctutils` 0.4.2→0.4.6（#8186），其对应安全修复本身不在 diff 中（证据不足）。
   人工复核建议：核对新 crate 的发布者、源码 tarball 与上游 Tor 0.4.9.15 的差异；确认构建时下载/编译 C 源的行为在 CI 中被固定与校验。

5. `cargo-audit` 新增忽略项 RUSTSEC-2026-0387（crypto-bigint 定时侧信道）（代码支持“忽略动作”，风险论断待验证）
   `.cargo/audit.toml` 新增忽略并给出理由：0.5.x 由 `elliptic-curve` 0.13 线钉住，根工作区仅经 `pgp` 用于 auto-update 的分离签名验证（无私钥/标量运算），`k256` 仅存在于被排除的 Ledger 测试工作区。理由与低风险论断在 diff 内无法验证（`tari_p2p` auto-update 代码未提供）；公钥签名验证通常不涉密，定时泄漏风险较低，但属被压制的审计告警。
   人工复核建议：核实 `tari_p2p` auto-update 路径确无私钥运算；按注释设定到期复审，避免长期压制。

6. 身份文件损坏时备份并重建节点身份（代码支持，行为变化需注意）
   `applications/minotari_app_utilities/src/identity_management.rs`：加载失败（Malformed/Io）时先用 hard-link+unlink（unix）把原文件移到 `<name>.<unix-ts>[.n].bak`（不覆盖已有备份），再生成新身份，并以 error 级日志记录备份路径与新 node_id/公钥；目录占用路径、备份失败会中止而不覆盖原文件（有测试）。Windows 用 `exists()+rename`，存在轻微 TOCTOU。行为变化：损坏身份会被重建为**新的节点 ID/公钥**，若该身份在别处被绑定（对等身份、验证节点密钥等）会造成身份漂移；发行说明未提示这一点。unix 上不支持硬链接的文件系统会以配置错误退出（fail-closed，可接受）。
   人工复核建议：确认运维文档提示身份重建的后果；确认备份文件权限保持 0600。

7. 其余发行说明条目无法核实（证据不足）
   #8167（脚本大小限制测试）、#8168（gRPC 方法日志）、#8192（stratum 无 method 字段响应）、#8123（非 TTY 提示 CPU 空转/EOF）等在可见 diff 中只有零星痕迹（如 `transaction_output.rs` 新增 8 MiB 脚本拒绝测试，属于测试代码），实现部分未提供。资源方面：可见代码中 `AuthBackoffTracker` 有界（1024）、日志限速、`expect()` 均有前置长度检查，未发现内存泄漏或新增 panic 点；但 diff 截断，不能推广到全部改动。

恶意代码迹象（仅就已提供差异）
未发现恶意或后门迹象：可见改动为认证加固、脱敏/zeroize、身份备份与测试，未见外联、混淆、凭据外传或刻意削弱校验的代码。注意该结论不覆盖未提供的共识/存储/矿工等文件。

人工复核建议（汇总）
- 优先取得并审查 #8160/#8173/#8174/#8175/#8187/#8191/#8193 的完整代码差异，判断是否存在共识规则收紧导致的分叉风险及是否需要协调升级窗口。
- 复核 gRPC 认证改造的部署约束与向后兼容（PHC 配置迁移、loopback 豁免、全局限速、`new` 返回 `None` 的调用方语义）。
- 验证 `tari-libtor-*` 新依赖的来源与 Tor 0.4.9.15 一致性，以及被忽略的 RUSTSEC-2026-0387 影响面。



<!-- watch-release: eyJjb2luIjogInRhcmkiLCAicHVibGlzaGVkX2F0IjogIjIwMjYtMTEtMTBUMTE6NTc6NTRaIiwgInJlcG8iOiAidGFyaS1wcm9qZWN0L3RhcmkiLCAicmlzayI6ICLlvoXkurrlt6XlpI3moLgiLCAidGFnIjogInY2LjMuMC1wcmUuNCJ9 -->
#### v6.3.0-pre.4

- 仓库：[`tari-project/tari`](https://github.com/tari-project/tari)
- 发布日期：2026-11-10T11:57:54Z
- Release：https://github.com/tari-project/tari/releases/tag/v6.3.0-pre.4
- 代码比较：`v6.3.0-pre.2` → `v6.3.0-pre.4`
- AI 风险级别：待人工复核

##### Release note

## What's Changed
* fix(sync): keep median timestamp windows in height order by @SWvheerden in https://github.com/tari-project/tari/pull/8195
* fix(grpc): harden auth scheme logging, credential validation, covenants, and conversions (#8021) by @Brayaniglesias08 in https://github.com/tari-project/tari/pull/8169
* fix(sync): horizon sync resume and peer handling improvements by @SWvheerden in https://github.com/tari-project/tari/pull/8201
* fix(grpc,deps): pin liblmdb-sys by rev, upgrade rcgen to 0.14, and drop argon2 rc pin (#8022) by @Brayaniglesias08 in https://github.com/tari-project/tari/pull/8183
* fix(chain-storage): read the landed key when picking a validator node activation epoch by @SWvheerden in https://github.com/tari-project/tari/pull/8203
* fix(wallet): batch scrape_wallet transactions by TRANSACTION_INPUTS_LIMIT by @Brayaniglesias08 in https://github.com/tari-project/tari/pull/8189
* fix(header-sync): do not record out-of-sequence headers as bad blocks by @SWvheerden in https://github.com/tari-project/tari/pull/8204
* fix(mempool): keep height-expired spends out of block templates by @SWvheerden in https://github.com/tari-project/tari/pull/8244
* fix(chain-storage): stop the consistency check reporting healthy databases as corrupt by @SWvheerden in https://github.com/tari-project/tari/pull/8245
* fix(chain-storage): keep orphan chain tips consistent and bound the RandomX keys gossip can select by @SWvheerden in https://github.com/tari-project/tari/pull/8246
* fix(base-node): derive the pruning target from validated headers by @SWvheerden in https://github.com/tari-project/tari/pull/8257
* fix(base-node): only disable block acceptance after a peer has proven a stronger chain by @SWvheerden in https://github.com/tari-project/tari/pull/8258
* fix(common): harden config override loading, DNS server list parsing, and ApplicationType::from_str by @ket4min-susan in https://github.com/tari-project/tari/pull/8225
* fix(comms): apply the RPC client read deadline once per request by @SWvheerden in https://github.com/tari-project/tari/pull/8261
* fix(chain-storage): make a rewind past the pruning horizon an atomic reset to genesis by @SWvheerden in https://github.com/tari-project/tari/pull/8260
* fix(utilities): minotari_app_utilities hardening batch (#8041) by @Vallejo1921 in https://github.com/tari-project/tari/pull/8149
* fix(build): emit check-cfg and warn on default testnet (#8023) by @Vallejo1921 in https://github.com/tari-project/tari/pull/8150
* fix(validation): reject headers whose kernel MMR size does not grow by @SWvheerden in https://github.com/tari-project/tari/pull/8262
* fix(chain-storage): only reset a pruned node for a chain stronger than everything it holds by @SWvheerden in https://github.com/tari-project/tari/pull/8263
* fix(mempool): remove the unused get_state method from the peer mempool RPC by @SWvheerden in https://github.com/tari-project/tari/pull/8265
* fix(common-types): split SeedWords::from_str on any whitespace by @sdbondi in https://github.com/tari-project/tari/pull/8310
* fix(metrics): reuse HTTP client, check push status codes, and set Prometheus Content-Type by @ket4min-susan in https://github.com/tari-project/tari/pull/8232
* fix(comms-dht): bound Join gossip and OnConnect peer sync admission by @SWvheerden in https://github.com/tari-project/tari/pull/8266
* fix(chain-storage): inspect seeked cursor key in get_next_activation_epoch by @sonson0910 in https://github.com/tari-project/tari/pull/8197
* fix(base-node): cache per-algorithm targets for the new-block difficulty check and bound the walk by @SWvheerden in https://github.com/tari-project/tari/pull/8318
* fix(deps): update libz-sys to 1.1.31 to mitigate RUSTSEC-2026-0418 (#8202) by @Vallejo1921 in https://github.com/tari-project/tari/pull/8255
* fix(comms): log unsupported messaging protocol negotiation at debug by @SWvheerden in https://github.com/tari-project/tari/pull/8321
* fix(libtor): preserve case-sensitivity of log destination path (#6888) by @Vallejo1921 in https://github.com/tari-project/tari/pull/8256
* fix(validation): check chain-linked timelocks at the height the body is mined at by @SWvheerden in https://github.com/tari-project/tari/pull/8319
* fix(base-node): wait for several peers before declaring initial sync by @SWvheerden in https://github.com/tari-project/tari/pull/8320
* fix(comms-dht): fix flood-ban counting, peer log spam, config docs and GetPeers clients by @SWvheerden in https://github.com/tari-project/tari/pull/8322
* fix(validation): tighten kernel burn commitment checks by @SWvheerden in https://github.com/tari-project/tari/pull/8323
* fix(mmr): validate leaf position and bounds in MerkleProof::verify and fix leaf index lookups by @cyczzhao-lab in https://github.com/tari-project/tari/pull/8294
* fix(header-sync): refresh cached chain metadata after a rewind by @SWvheerden in https://github.com/tari-project/tari/pull/8329

## New Contributors
* @ket4min-susan made their first contribution in https://github.com/tari-project/tari/pull/8225
* @sonson0910 made their first contribution in https://github.com/tari-project/tari/pull/8197
* @cyczzhao-lab made their first contribution in https://github.com/tari-project/tari/pull/8294

**Full Changelog**: https://github.com/tari-project/tari/compare/v6.3.0-pre.2...v6.3.0-pre.4

##### 变更文件

1. `.cargo/audit.toml`
2. `.github/workflows/build_binaries.json`
3. `.github/workflows/build_binaries.yml`
4. `.github/workflows/release_private_binaries.yml`
5. `Cargo.lock`
6. `Cargo.toml`
7. `SECURITY.md`
8. `applications/minotari_app_grpc/Cargo.toml`
9. `applications/minotari_app_grpc/build.rs`
10. `applications/minotari_app_grpc/src/authentication/basic_auth.rs`
11. `applications/minotari_app_grpc/src/authentication/server_interceptor.rs`
12. `applications/minotari_app_grpc/src/conversions/aggregate_body.rs`
13. `applications/minotari_app_grpc/src/conversions/peer.rs`
14. `applications/minotari_app_grpc/src/conversions/transaction_input.rs`
15. `applications/minotari_app_grpc/src/conversions/transaction_output.rs`
16. `applications/minotari_app_grpc/src/conversions/unblinded_output.rs`
17. `applications/minotari_app_grpc/src/tls/certs.rs`
18. `applications/minotari_app_utilities/Cargo.toml`
19. `applications/minotari_app_utilities/src/identity_management.rs`
20. `applications/minotari_app_utilities/src/parse_miner_input.rs`
21. `applications/minotari_console_wallet/src/automation/commands.rs`
22. `applications/minotari_ledger_wallet/comms_testing/Cargo.lock`
23. `applications/minotari_ledger_wallet/comms_testing/Cargo.toml`
24. `applications/minotari_ledger_wallet/wallet/Cargo.lock`
25. `applications/minotari_ledger_wallet/wallet/Cargo.toml`
26. `applications/minotari_node/src/commands/command/check_db.rs`
27. `applications/minotari_offline_signer/Cargo.toml`
28. `base_layer/common_types/src/grpc_authentication.rs`
29. `base_layer/common_types/src/seeds/seed_words.rs`
30. `base_layer/core/src/base_node/comms_interface/error.rs`
31. `base_layer/core/src/base_node/comms_interface/inbound_handlers.rs`
32. `base_layer/core/src/base_node/rpc/mod.rs`
33. `base_layer/core/src/base_node/rpc/query_service.rs`
34. `base_layer/core/src/base_node/rpc/service.rs`
35. `base_layer/core/src/base_node/service/service.rs`
36. `base_layer/core/src/base_node/state_machine_service/state_machine.rs`
37. `base_layer/core/src/base_node/state_machine_service/states/block_sync.rs`
38. `base_layer/core/src/base_node/state_machine_service/states/header_sync.rs`
39. `base_layer/core/src/base_node/state_machine_service/states/listening.rs`
40. `base_layer/core/src/base_node/state_machine_service/states/sync_decide.rs`
41. `base_layer/core/src/base_node/sync/ban.rs`
42. `base_layer/core/src/base_node/sync/block_sync/error.rs`
43. `base_layer/core/src/base_node/sync/block_sync/mod.rs`
44. `base_layer/core/src/base_node/sync/block_sync/synchronizer.rs`
45. `base_layer/core/src/base_node/sync/block_sync/test.rs`
46. `base_layer/core/src/base_node/sync/header_sync/error.rs`
47. `base_layer/core/src/base_node/sync/header_sync/mod.rs`
48. `base_layer/core/src/base_node/sync/header_sync/synchronizer.rs`
49. `base_layer/core/src/base_node/sync/header_sync/test.rs`
50. `base_layer/core/src/base_node/sync/header_sync/validator.rs`
51. `base_layer/core/src/base_node/sync/horizon_state_sync/error.rs`
52. `base_layer/core/src/base_node/sync/horizon_state_sync/synchronizer.rs`
53. `base_layer/core/src/base_node/sync/mock_sync_peer.rs`
54. `base_layer/core/src/base_node/sync/mod.rs`
55. `base_layer/core/src/chain_storage/async_db.rs`
56. `base_layer/core/src/chain_storage/blockchain_backend.rs`
57. `base_layer/core/src/chain_storage/blockchain_database.rs`
58. `base_layer/core/src/chain_storage/db_transaction.rs`
59. `base_layer/core/src/chain_storage/error.rs`
60. `base_layer/core/src/chain_storage/lmdb_db/helpers.rs`
61. `base_layer/core/src/chain_storage/lmdb_db/lmdb.rs`
62. `base_layer/core/src/chain_storage/lmdb_db/lmdb_db.rs`
63. `base_layer/core/src/chain_storage/lmdb_db/lmdb_tree_writer.rs`
64. `base_layer/core/src/chain_storage/lmdb_db/mod.rs`
65. `base_layer/core/src/chain_storage/lmdb_db/row_data/block_header_accumulated_data.rs`
66. `base_layer/core/src/chain_storage/lmdb_db/stats_collector.rs`
67. `base_layer/core/src/chain_storage/lmdb_db/validator_node_store.rs`
68. `base_layer/core/src/chain_storage/mod.rs`
69. `base_layer/core/src/chain_storage/tests/blockchain_database.rs`
70. `base_layer/core/src/chain_storage/tests/fixtures/reference_lmdb/data.mdb.gz`
71. `base_layer/core/src/common/rolling_vec.rs`
72. `base_layer/core/src/mempool/mempool.rs`
73. `base_layer/core/src/mempool/mempool_storage.rs`
74. `base_layer/core/src/mempool/priority/prioritized_transaction.rs`
75. `base_layer/core/src/mempool/proto/mod.rs`
76. `base_layer/core/src/mempool/proto/state_response.proto`
77. `base_layer/core/src/mempool/proto/state_response.rs`
78. `base_layer/core/src/mempool/rpc/mod.rs`
79. `base_layer/core/src/mempool/rpc/service.rs`
80. `base_layer/core/src/mempool/rpc/test.rs`
81. `base_layer/core/src/mempool/service/handle.rs`
82. `base_layer/core/src/mempool/service/inbound_handlers.rs`
83. `base_layer/core/src/mempool/test_utils/mock.rs`
84. `base_layer/core/src/mempool/unconfirmed_pool/mod.rs`
85. `base_layer/core/src/mempool/unconfirmed_pool/unconfirmed_pool.rs`
86. `base_layer/core/src/proto/decode_budget_tests.rs`
87. `base_layer/core/src/proto/mod.rs`
88. `base_layer/core/src/test_helpers/blockchain.rs`
89. `base_layer/core/src/validation/aggregate_body/aggregate_body_chain_validator.rs`
90. `base_layer/core/src/validation/difficulty_calculator.rs`
91. `base_layer/core/src/validation/error.rs`
92. `base_layer/core/src/validation/header/header_full_validator.rs`
93. `base_layer/core/src/validation/test.rs`
94. `base_layer/core/tests/helpers/nodes.rs`
95. `base_layer/core/tests/helpers/sync.rs`
96. `base_layer/core/tests/tests/block_sync.rs`
97. `base_layer/core/tests/tests/header_sync.rs`
98. `base_layer/core/tests/tests/horizon_sync.rs`
99. `base_layer/core/tests/tests/mempool.rs`
100. `base_layer/core/tests/tests/node_comms_interface.rs`
101. `base_layer/mmr/src/merkle_mountain_range.rs`
102. `base_layer/mmr/src/merkle_proof.rs`
103. `base_layer/mmr/tests/tests/merkle_mountain_range.rs`
104. `base_layer/node_components/src/blocks/block_header.rs`
105. `base_layer/p2p/src/domain_message.rs`
106. `base_layer/transaction_components/Cargo.toml`
107. `base_layer/transaction_components/src/consensus/consensus_constants.rs`
108. `base_layer/transaction_components/src/transaction_builder/builder.rs`
109. `base_layer/transaction_components/src/transaction_builder/error.rs`
110. `base_layer/transaction_components/src/transaction_components/covenants/covenant.rs`
111. `base_layer/transaction_components/src/validation/aggregate_body/aggregate_body_internal_validator.rs`
112. `base_layer/transaction_components/src/validation/aggregate_body/mod.rs`
113. `base_layer/transaction_components/src/validation/error.rs`
114. `base_layer/wallet/Cargo.toml`
115. `base_layer/wallet/src/output_manager_service/handle.rs`
116. `base_layer/wallet/src/output_manager_service/service.rs`
117. `base_layer/wallet/src/transaction_service/error.rs`
118. `base_layer/wallet/src/transaction_service/handle.rs`
119. `base_layer/wallet/src/transaction_service/service.rs`
120. `base_layer/wallet/tests/output_manager_service_tests/service.rs`
121. `base_layer/wallet_ffi/src/lib.rs`
122. `base_layer/wallet_ffi/wallet.h`
123. `changelog-development.md`
124. `common/config/presets/c_base_node_c.toml`
125. `common/config/presets/d_console_wallet.toml`
126. `common/src/configuration/bootstrap.rs`
127. `common/src/configuration/dns_name_server_list.rs`
128. `common/src/configuration/loader.rs`
129. `common/src/configuration/name_server.rs`
130. `common/tari_features/src/resolver.rs`
131. `comms/core/src/protocol/messaging/outbound.rs`
132. `comms/core/src/protocol/rpc/client/mod.rs`
133. `comms/core/src/protocol/rpc/test/smoke.rs`
134. `comms/dht/Cargo.toml`
135. `comms/dht/src/actor.rs`
136. `comms/dht/src/config.rs`
137. `comms/dht/src/connectivity/metrics.rs`
138. `comms/dht/src/connectivity/mod.rs`
139. `comms/dht/src/connectivity/test.rs`
140. `comms/dht/src/crypt.rs`
141. `comms/dht/src/dedup/dedup_cache.rs`
142. `comms/dht/src/dedup/mod.rs`
143. `comms/dht/src/dht.rs`
144. `comms/dht/src/inbound/decryption.rs`
145. `comms/dht/src/inbound/deserialize.rs`
146. `comms/dht/src/inbound/dht_handler/join_gate.rs`
147. `comms/dht/src/inbound/dht_handler/layer.rs`
148. `comms/dht/src/inbound/dht_handler/middleware.rs`
149. `comms/dht/src/inbound/dht_handler/mod.rs`
150. `comms/dht/src/inbound/dht_handler/task.rs`
151. `comms/dht/src/inbound/forward.rs`
152. `comms/dht/src/inbound/message.rs`
153. `comms/dht/src/inbound/metrics.rs`
154. `comms/dht/src/inbound/mod.rs`
155. `comms/dht/src/network_discovery/admission.rs`
156. `comms/dht/src/network_discovery/config.rs`
157. `comms/dht/src/network_discovery/discovering.rs`
158. `comms/dht/src/network_discovery/mod.rs`
159. `comms/dht/src/network_discovery/on_connect.rs`
160. `comms/dht/src/network_discovery/ready.rs`
161. `comms/dht/src/network_discovery/rebootstrap.rs`
162. `comms/dht/src/network_discovery/seed_strap.rs`
163. `comms/dht/src/network_discovery/state_machine.rs`
164. `comms/dht/src/network_discovery/test.rs`
165. `comms/dht/src/outbound/broadcast.rs`
166. `comms/dht/src/outbound/message_params.rs`
167. `comms/dht/src/proto/rpc.proto`
168. `comms/dht/src/rpc/service.rs`
169. `comms/dht/src/rpc/test.rs`
170. `comms/dht/src/test_utils/dht_actor_mock.rs`
171. `deny.toml`
172. `infrastructure/libtor/src/tor.rs`
173. `infrastructure/metrics/src/lib.rs`
174. `infrastructure/metrics/src/server/builder.rs`
175. `infrastructure/metrics/src/server/pull.rs`
176. `infrastructure/metrics/src/server/push.rs`
177. `package-lock.json`
178. `supply-chain/config.toml`

##### AI 审查

风险级别：待人工复核（偏 P1：存在多项共识/验证相关声明无法在所给 diff 中核实，且 diff 明显被截断）

重要发现：

1. **共识与验证规则变更声明大量无法核实（证据不足）**
   发行说明声称修改了 median timestamp 窗口排序、kernel MMR size 必须增长、区块体挖矿高度的 timelock 检查、kernel burn commitment 检查、`MerkleProof::verify` 的叶位置/边界校验等。这些都属于共识/验证层改动，可能造成网络内新旧版本节点对同一区块判定不一致（类似软分叉效应）。但所给 diff 中并未出现对应文件（`validation/`、`mmr/`、`chain_storage/`、`mempool/` 等多数内容缺失），diff 在 `inbound_handlers.rs` 中途被截断。
   相关文件（据发行说明）：`base_layer/core/src/validation/*`、`base_layer/mmr/*`、`base_layer/core/src/chain_storage/*`。
   建议：人工拉取完整 diff，逐项确认这些校验是“收紧且对历史区块同样适用”还是“仅对新块生效”，判断是否构成实际硬分叉/兼容性断裂；升级前在测试网验证新旧节点混跑。

2. **`.cargo/audit.toml` 新增忽略 RUSTSEC-2026-0459（SQLite 未初始化内存问题）——代码支持，但属安全权衡**
   diff 显示将该公告加入 ignore 列表，附带理由（diesel 限制 `libsqlite3-sys` 版本、攻击需本地恶意 WAL 文件）。发行说明未提及此项。注释说明合理，但这是主动抑制安全公告，且 `minotari_utils dbstats` 会打开操作员传入的路径。
   相关文件：`.cargo/audit.toml`。
   建议：确认 dbstats/其他入口不会打开不可信目录下的 SQLite+WAL 文件；跟踪 diesel 升级后及时移除该 ignore。

3. **`tari_sidechain` 从 8.0.0 跳到 9.0.0（主版本升级，发行说明未提及）**
   `Cargo.toml`/`Cargo.lock` 显示该外部 crate 主版本升级（同时 `tari_jellyfish` 7.0.0→7.1.0）。主版本号递增通常意味着不兼容 API/序列化或共识数据结构变化。diff 中未包含其源码。
   建议：人工核对 tari_sidechain 9.0.0 的变更日志，重点检查序列化格式、shard key、validator node 相关数据结构是否改变，是否影响已有链上数据。

4. **gRPC 认证：用户名含 ':' 时整体拒绝所有请求（fail-closed，代码支持，有破坏性升级风险）**
   `server_interceptor.rs` 新增 `reject_all`：配置的 gRPC 用户名含 ':' 时启动即记录错误并拒绝全部请求。这是有意的封闭式失败，但对已有部署是破坏性变更（此前该配置可能"可用"）。另注意 `ServerAuthenticationInterceptor::new` 在其他 `Err(_)`（用户名超长、密码非法 UTF-8）时返回 `None`——调用方如何处理 `None`（是否等同"无认证拦截器"）在 diff 中不可见，存在潜在认证旁路疑点，但该语义与改动前 `.ok()?` 一致，非本次引入。
   相关文件：`applications/minotari_app_grpc/src/authentication/{server_interceptor,basic_auth}.rs`。
   建议：核查所有 `ServerAuthenticationInterceptor::new(...)` 调用点对 `None` 的处理；发布说明中明确告警该配置破坏性变更。

5. **Covenant 反序列化从允许尾随字节改为严格 `borsh::from_slice`（兼容性收紧）**
   `transaction_input.rs`、`transaction_output.rs`、`unblinded_output.rs` 中 covenant 解析改为拒绝尾随字节，并附带测试。若 gRPC 提交路径与 P2P 路径的解析严格度此前不一致，此改动会拒绝过去可接受的输入；这是 API/接受面变化，需确认与 P2P 共识路径一致性，避免两路径判定分歧。
   相关文件：`applications/minotari_app_grpc/src/conversions/{transaction_input,transaction_output,unblinded_output}.rs`。
   建议：确认 P2P 网络层对 covenant 的解析同样严格；测试历史交易重放不受影响。

6. **`GrpcAuthentication` 序列化密码改为 `<redacted>` 且反序列化拒绝该占位符（破坏性配置往返）**
   `grpc_authentication.rs`：序列化输出脱敏，反序列化遇 `<redacted>` 直接报错。防止密码明文落盘是好事，但任何"读取配置→写回配置→重启"的流程会永久丢失密码并启动失败。发行说明未提及。
   相关文件：`base_layer/common_types/src/grpc_authentication.rs`。
   建议：确认无代码路径会把序列化结果写回配置文件；文档说明该行为。

7. **剪枝节点 rewind 越过剪枝高度将清空链至创世（破坏性升级行为，仅有警告文本可见）**
   `check_db.rs` 新增警告文案表明：autocorrect 若需回退过剪枝高度，链会被清到高度 0 并全量重新同步。发行说明称"原子重置到创世"。实际 reset 逻辑未在 diff 中出现。这是数据/服务连续性上的破坏性行为。
   相关文件：`applications/minotari_node/src/commands/command/check_db.rs`（实际逻辑应在 `chain_storage`，未提供）。
   建议：核对 reset-to-genesis 实现是否正确处理锁与原子性（避免半清空状态）；向运维明确升级风险。

8. **身份文件校验与 Zeroizing 改进（代码支持，方向良好）**
   `identity_management.rs` 现在校验公钥/NodeID 与私钥一致性，不一致时拒绝替换原文件（防覆盖），签名无效时仅重签名保留私钥；文件内容用 `Zeroizing` 包裹。测试覆盖较全。行为变化：此前某些损坏文件会被静默重建，现在会直接报 `ConfigError` 退出。
   建议：在发布说明中提示这一启动失败行为变化。

9. **其他依赖与杂项**
   - `liblmdb-sys` 由 tag 改为 rev 固定，commit 相同（8d88933…），无实质代码变化（代码支持）。
   - `libz-sys` 1.1.29→1.1.31、`rcgen` 0.12→0.14、`pem`/`yasna`/`rand` 小版本升级；`rcgen` 证书生成重写并有 TLS 握手集成测试，未见明显问题。
   - `SECURITY.md` 移除了 security@tari.com 邮件列表披露渠道，仅保留 GitHub 私密披露——非漏洞，但降低披露渠道冗余。
   - `verify_base_node_grpc_mining_responses` 不再调用 `get_new_block`/`submit_block` 探测（有测试佐证），意味着矿机启动时不再验证这两个方法的权限——功能回退，非安全问题。
   - `SeedWords::from_str` 改为按任意空白分隔——宽松化，属可用性修复。

恶意代码迹象：在**所提供的 diff 范围内**未发现恶意代码、后门、密钥泄露或可疑网络外传行为；新增逻辑多为防御性收紧并附带测试。但由于 diff 被截断、大量发行说明条目（sync、chain-storage、mempool、header-sync、metrics、comms-dht、common 配置解析等）对应的代码未提供，**无法据此断言这些条目的实现是否正确或无害**。

人工复核建议（优先级排序）：
1. 取得完整 diff，逐条核对所有 validation/consensus 相关改动（发现 1），确认新旧节点兼容性与是否需要网络协调升级。
2. 核对 `tari_sidechain` 9.0.0 变更（发现 3）。
3. 核查 gRPC 拦截器 `None` 返回值的所有调用点（发现 4）与配置写回路径（发现 6）。
4. 核对 rewind/reset-to-genesis 原子性（发现 7）与 SQLite 审计忽略项的实际暴露面（发现 2）。

