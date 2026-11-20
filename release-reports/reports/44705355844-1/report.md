# 版本更新报告

## 检查批次 2026-11-20 09:45:23 UTC

### aleo

#### v4.12.0 · 正式版 · 完整评估
<!-- watch-repo: aleo-labs-protocol/snarkOS -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** ⚠️ **重大发行说明待核实：** 共识/硬分叉声明
- **处置建议：** 需人工确认 · 重点关注
- **建议理由：** 发行说明或 AI 结论存在未核实的重大项，升级前需要人工确认。 上游升级建议，发行说明原文：「All mainnet validators and node operators need to upgrade before the activation height.」

##### AI 审查

**代码已确认的发现**
1. **已确认 — 破坏性变更：** 编译期 `slipstream-plugins` 特性与 `--slipstream-config` 启动参数被整体移除（`Cargo.toml`、`cli/src/commands/start.rs`），此前使用 Slipstream 插件构建并在启动配置使用该参数的节点升级后将无法启动，需删除该参数；`history`、`history-staking-rewards` 仅保留为空别名以兼容旧构建命令，仅影响显式使用该插件功能的节点。 代码证据：{"path": "Cargo.toml", "quote": "slipstream-plugins = [ \"snarkos-node/slipstream-plugins\", \"snarkos-cli/slipstream-plugins\" ]"} 代码证据：{"path": "cli/src/commands/start.rs", "quote": "    #[cfg(feature = \"slipstream-plugins\")]\n    #[clap(long = \"slipstream-config\", value_name = \"PATH\", verbatim_doc_comment)]\n    pub slipstream_configs: Vec<PathBuf>,"} 代码证据：{"path": "Cargo.toml", "quote": "history = []\nhistory-staking-rewards = []"}
2. **已确认 — 安全：** 修复：开启 REST 的验证者/客户端节点在 broadcast 且 `check_transaction=true` 时，基线在 `node/rest/src/routes.rs` 的异步处理中内联执行 `check_transaction_basic` 重校验，可长期占用异步运行时线程；目标版本将该校验移入 `spawn_blocking` 并让验证许可随任务持有，`node/rest/src/lib.rs` 的排队信号量按并发上限封顶、满载直接返回 429，限制远程请求可堆积的等待队列。 代码证据：{"path": "node/rest/src/routes.rs", "quote": "            let res = rest.ledger.check_transaction_basic(&tx, None, &mut rand::rng()).map_err(|err| {"} 代码证据：{"path": "node/rest/src/routes.rs", "quote": "        let tx = if check_transaction {\n            let verification_slot = if tx.is_execute() {\n                rest.verification_slots.executions.acquire().await?\n            } else {\n                rest.verification_slots.deploys.acquire().await?\n            };"} 代码证据：{"path": "node/rest/src/routes.rs", "quote": "            match tokio::task::spawn_blocking(move || {"} 代码证据：{"path": "node/rest/src/routes.rs", "quote": "                let _verification_slot = verification_slot;\n                ledger.check_transaction_basic(&tx, None, &mut rand::rng()).map(|()| tx)\n            })\n            .await\n            {\n                Ok(Ok(tx)) => tx,"} 代码证据：{"path": "node/rest/src/lib.rs", "quote": "    fn new(concurrent_limit: usize) -> Self {\n        Self {\n            concurrent: Arc::new(Semaphore::new(concurrent_limit)),\n            queued: Arc::new(Semaphore::new(concurrent_limit.saturating_mul(2))),\n        }\n    }"} 代码证据：{"path": "node/rest/src/lib.rs", "quote": "        let queued = self\n            .queued\n            .clone()\n            .try_acquire_owned()\n            .map_err(|_| RestError::too_many_requests(anyhow::anyhow!(\"Too many verifications in progress\")))?;"}
3. **已确认 — 兼容性：** 对外 Prometheus 指标命名与单位口径变更：`node/metrics/src/names.rs` 中 `snarkos_tcp_tasks_total` 改为语义不同的 `snarkos_tcp_queued_inbound_messages`，并引入 `snarkos_consensus_block_lag_secs`、`snarkos_consensus_advance_to_next_block_secs` 等秒单位名称；依赖旧指标名的监控面板与告警查询需更新，仅影响监控，不影响节点运行。 代码证据：{"path": "node/metrics/src/names.rs", "quote": "    pub const BLOCK_LAG: &str = \"snarkos_consensus_block_lag_secs\";"} 代码证据：{"path": "node/metrics/src/names.rs", "quote": "    pub const TCP_TASKS: &str = \"snarkos_tcp_tasks_total\";"} 代码证据：{"path": "node/metrics/src/names.rs", "quote": "    pub const QUEUED_INBOUND_MESSAGES: &str = \"snarkos_tcp_queued_inbound_messages\";"} 代码证据：{"path": "node/metrics/src/names.rs", "quote": "    pub const ADVANCE_TO_NEXT_BLOCK_SECS: &str = \"snarkos_consensus_advance_to_next_block_secs\";"}
4. **已确认 — 稳定性/数据：** 修复：验证者 BFT 存储区分可取回传输与仅记录为 aborted 的传输 ID（`node/bft/src/helpers/storage.rs`、`node/bft/storage-service/src/memory.rs`、`node/bft/src/primary.rs`），避免证书在提案/同步中引用仅记录为 aborted 的传输后，节点在提交时无法提供所承诺的传输；仅影响验证者 BFT 运行。 代码证据：{"path": "node/bft/src/helpers/storage.rs", "quote": "    pub fn contains_retrievable_transmission(&self, transmission_id: impl Into<TransmissionID<N>>) -> bool {\n        self.transmissions.contains_retrievable_transmission(transmission_id.into())\n    }"} 代码证据：{"path": "node/bft/src/helpers/storage.rs", "quote": "    pub fn contains_aborted_transmission(&self, transmission_id: impl Into<TransmissionID<N>>) -> bool {\n        self.transmissions.contains_aborted_transmission(transmission_id.into())\n    }"} 代码证据：{"path": "node/bft/src/primary.rs", "quote": "                if self.storage.contains_retrievable_transmission(id) || self.storage.contains_aborted_transmission(id)\n                {"} 代码证据：{"path": "node/bft/storage-service/src/memory.rs", "quote": "                            if aborted_transmission_ids_lock.contains_key(&transmission_id) {\n                                aborted_transmission_ids.insert(transmission_id);\n                            } else {"}
5. **已确认 — 稳定性/数据：** 修复：`node/bft/src/helpers/storage.rs` 的 `current_round`、`current_height` 与 `gc_round` 改为 `fetch_max` 原子推进，消除并发写入导致的轮次/高度回退与 GC 更新竞态；仅影响验证者 BFT 存储并发路径。 代码证据：{"path": "node/bft/src/helpers/storage.rs", "quote": "        let previous_value = self.current_round.fetch_max(next_round, Ordering::SeqCst);"} 代码证据：{"path": "node/bft/src/helpers/storage.rs", "quote": "        let previous_gc_round = self.gc_round.fetch_max(next_gc_round, Ordering::SeqCst);"} 代码证据：{"path": "node/bft/src/helpers/storage.rs", "quote": "        self.current_height.fetch_max(next_height, Ordering::SeqCst);"}

**待核实的发行说明主张**
6. **待核实 — 硬分叉/共识：** 发行说明声明主网 V22 共识版本将于高度 22,962,000 激活并要求所有主网验证者与节点运营者在激活高度前升级，未升级节点将面临分叉风险（发行说明原文：「**Mainnet consensus version (V22) activation height: 22,962,000** — estimated Mon 2026-10-19 ~22:00 UTC (~3:00 pm PT) at current block times.」「All mainnet validators and node operators need to upgrade before the activation height.」「Validators and clients that do not upgrade in time will be at risk of forking.」）；本次 `snarkOS` 差异仅见消息层 V22 登记、指标上报与 snarkVM 版本升级，程序映射上限 31→128 的部署验证规则位于 snarkVM `v4.12.0` 依赖，目标网最终区块/交易有效性差异缺少本仓库代码证据，需在激活高度前核实并按发行说明安排升级。

##### 版本信息

发布于 2026-10-13T19:41:26Z · 比较 `v4.11.0` → `v4.12.0` · [打开 Release](https://github.com/aleo-labs-protocol/snarkOS/releases/tag/v4.12.0)


#### v4.12.1 · 正式版 · 完整评估
<!-- watch-repo: aleo-labs-protocol/snarkOS -->

- **优先摘要（P0/P1、目标网硬分叉或重大 Breaking Changes）：** 无
- **处置建议：** 可暂缓 · 不重要
- **建议理由：** 未发现需要立即处理的重大变更。

##### AI 审查

未发现需要单独报告的重大变更。

##### 版本信息

发布于 2026-10-31T19:11:51Z · 比较 `v4.12.0` → `v4.12.1` · [打开 Release](https://github.com/aleo-labs-protocol/snarkOS/releases/tag/v4.12.1)


---

评估范围：本报告不执行上游程序或测试；每个版本的差异覆盖范围以标题中的“快速预检/完整评估”标识为准。
