import json
import os
import tempfile
import unittest
from unittest.mock import patch

from test_watch_releases import EMPTY_AI_REVIEW, watch


OPERATOR_NOTE = "Fixed a mempool cache issue, highly recommended for mining pools and node operators."
ALEO_NOTE = (
    "There is no activation height. This release has no consensus change. "
    "Mainnet validators and node operators may upgrade at their convenience. "
    "Nodes on v4.12.x and v4.13.x can run on the same network."
)


def reviewed_entry(coin="aleo", risk="P3", category="兼容性", status="已确认", note="", tag="v4.13.1", extras=()):
    data = json.loads(EMPTY_AI_REVIEW)
    data["risk"] = risk
    evidence = {}
    for index, (name, state, severity, text) in enumerate([
        (category, status, risk, "指标语义及客户端调用方式改变；仅使用相关监控或脚本时需调整，不证明旧节点离网"),
        *extras,
    ]):
        path = f"src/change_{index}.rs"
        quote = f"apply_change_{index}(configuration);"
        evidence[path] = quote
        data["highlights"][name] = {"status": state, "reason": f"{severity}：`{path}` {text}"}
        data["confirmed_findings"].append({
            "category": name, "text": f"`{path}` {text}", "evidence": [{"path": path, "quote": quote}],
        })
    analysis = watch.final_analysis_from_json(json.dumps(data, ensure_ascii=False), evidence)
    return watch.format_release(
        coin, f"org/{coin}", {"tag_name": tag, "body": note, "_target_network": "mainnet"},
        "previous", analysis, changed_paths=set(evidence), code_evidence=evidence,
    )


class UpgradeNotificationTests(unittest.TestCase):
    def test_low_severity_categories_do_not_force_upgrades_or_notify(self):
        for risk in ("P2", "P3"):
            for category, status in (
                ("兼容性", "已确认"), ("破坏性变更", "已确认"), ("硬分叉/共识", "已确认"),
                ("安全", "风险"), ("安全", "修复"), ("稳定性/数据", "修复"), ("内存问题", "修复"),
            ):
                with self.subTest(risk=risk, category=category, status=status):
                    meta, report = reviewed_entry(risk=risk, category=category, status=status)
                    self.assertEqual(meta["upgrade_advice"], "按需升级" if risk == "P2" else "可暂缓")
                    self.assertFalse(watch.release_requires_notification(meta))
                    self.assertNotIn("已确认的重要修复", report)
                    self.assertNotIn("必须升级", watch.issue_action_line(meta))

    def test_aleo_compatible_release_is_not_mandatory(self):
        meta, report = reviewed_entry(note=ALEO_NOTE)
        self.assertEqual(meta["upgrade_advice"], "可暂缓")
        self.assertFalse(watch.release_requires_notification(meta))
        self.assertNotIn("需要升级并核对现有配置", report)
        self.assertIn("配置", watch.issue_action_line(meta))

    def test_p2_advice_and_action_are_conditional(self):
        meta, _ = reviewed_entry(coin="xbt", risk="P2", category="稳定性/数据", status="修复")
        self.assertEqual(meta["upgrade_advice"], "按需升级")
        self.assertIn("适用", meta["upgrade_reason"])
        self.assertIn("受影响", watch.issue_action_line(meta))
        self.assertFalse(watch.release_requires_notification(meta))

    def test_strong_upstream_recommendations_are_distinct_from_ordinary_advice(self):
        for note, expected in (
            (OPERATOR_NOTE, "强烈建议升级"),
            ("We strongly recommend that node operators upgrade.", "强烈建议升级"),
            ("Upgrading is **highly recommended** for node operators.", "强烈建议升级"),
            ("We strongly advise all node operators to upgrade.", "强烈建议升级"),
            ("Node operators are strongly encouraged to upgrade.", "强烈建议升级"),
            ("强烈建议矿池和节点运营者升级。", "强烈建议升级"),
            ("高度推荐矿池升级到这个版本。", "强烈建议升级"),
            ("Node operators should upgrade.", "建议升级"),
            ("This is an important update for node operators.", "建议升级"),
            ("This highly optimized release is recommended for node operators.", "建议升级"),
        ):
            with self.subTest(note=note):
                meta, report = reviewed_entry(risk="P2", note=note)
                self.assertEqual(meta["upgrade_advice"], expected)
                self.assertEqual(meta["risk"], "P2")
                self.assertIn(expected, report)
                self.assertTrue(watch.release_requires_notification(meta))
                self.assertIn("维护窗口", watch.issue_action_line(meta))
                self.assertNotIn("必须升级", watch.issue_action_line(meta))
                expected_reminder = "上游强烈推荐（运营提醒）" if expected == "强烈建议升级" else "上游推荐（运营提醒）"
                self.assertEqual(watch.release_notification_summary(meta), expected_reminder)

    def test_strong_advice_uses_existing_scope_negation_and_prerelease_gates(self):
        for note in (
            "Testnet only. Highly recommended for node operators.",
            "Strongly recommended for wallet users only.",
            "We do not strongly recommend that node operators upgrade.",
            "We don't strongly advise node operators to upgrade.",
            "We never strongly recommend that node operators upgrade.",
            "Node operators are not strongly encouraged to upgrade.",
            "This release is not highly recommended for node operators.",
            "不强烈建议节点运营者升级。",
            "```text\nHighly recommended for node operators.\n```\n\nRoutine release.",
        ):
            with self.subTest(note=note):
                meta, _ = reviewed_entry(risk="P2", note=note)
                self.assertEqual(meta["upgrade_advice"], "按需升级")
                self.assertFalse(watch.release_requires_notification(meta))
        meta, _ = reviewed_entry(risk="P2", note=OPERATOR_NOTE, tag="v2-rc.1")
        self.assertEqual(meta["upgrade_advice"], "预发布版生产暂缓")
        self.assertFalse(watch.release_requires_notification(meta))

    def test_screenshot_batch_distinguishes_conditional_and_strong_upgrade_advice(self):
        aleo = reviewed_entry(risk="P2", note=ALEO_NOTE)
        alph = reviewed_entry(coin="alephium", risk="P2", category="稳定性/数据", status="修复", note=OPERATOR_NOTE, tag="v4.7.2")
        next_alph = watch.format_release("alephium", "org/alephium", {"tag_name": "v4.7.3"}, "v4.7.2", watch.final_analysis_from_json(EMPTY_AI_REVIEW))
        entries = {"aleo": {"org/aleo": [aleo]}, "alephium": {"org/alephium": [alph, next_alph]}}
        body = watch.issue_body(entries)
        self.assertIn("| 币种 | 版本 | 风险 | 处置结论 | 提醒说明 |", body)
        self.assertIn("| aleo | `v4.13.1` | P2 | 按需升级 | 未触发主动提醒；先核对是否受影响 |", body)
        self.assertIn("| alephium | `v4.7.2` | P2 | 强烈建议升级 | 上游强烈推荐（运营提醒） |", body)
        self.assertIn("| alephium | `v4.7.3` | P3 | 可暂缓 | 未触发主动提醒 |", body)
        self.assertIn("提醒说明：** 上游强烈推荐（运营提醒）", body)
        self.assertIn(OPERATOR_NOTE, body)
        self.assertNotIn("🚨", body)
        self.assertEqual(watch.release_keys(watch.notification_entries(entries)), [("alephium", "org/alephium", "v4.7.2")])

    def test_p1_consumer_compatibility_change_does_not_force_node_upgrade(self):
        meta, _ = reviewed_entry(risk="P1")
        self.assertEqual(meta["upgrade_advice"], "建议升级")
        self.assertTrue(watch.release_requires_notification(meta))
        self.assertIn("尽快", watch.issue_action_line(meta))

    def test_p0_still_requires_upgrade_and_notifies(self):
        meta, _ = reviewed_entry(risk="P0", category="稳定性/数据", status="风险")
        self.assertEqual(meta["upgrade_advice"], "必须升级")
        self.assertTrue(watch.release_requires_notification(meta))
        self.assertEqual(watch.release_notification_summary(meta), "代码风险警报")

    def test_combined_notification_summary_preserves_reasons_without_duplicates(self):
        meta, _ = reviewed_entry(risk="P1", category="安全", status="风险", note=OPERATOR_NOTE, extras=(
            ("稳定性/数据", "修复", "P1", "存在已确认的数据风险修复"),
        ))
        meta["breaking_note_quote"] = "An existing API endpoint was removed."
        self.assertEqual(
            watch.release_notification_summary(meta),
            "重大上游声明提醒；代码风险警报；上游强烈推荐（运营提醒）",
        )
        self.assertEqual(meta["upgrade_advice"], "强烈建议升级")
        self.assertEqual(meta["risk"], "P1")
        self.assertIn("上游推荐本身", watch.issue_action_line(meta))

    def test_p1_consensus_category_without_network_deadline_is_not_mandatory(self):
        meta, _ = reviewed_entry(risk="P1", category="硬分叉/共识")
        self.assertEqual(meta["upgrade_advice"], "建议升级")
        self.assertTrue(watch.release_requires_notification(meta))

    def test_unverified_p1_label_does_not_trigger_code_alert(self):
        meta, _ = reviewed_entry(risk="P1")
        meta["verified_finding_paths"] = []
        self.assertFalse(watch.release_requires_notification(meta))

    def test_global_p1_label_cannot_promote_p2_category_into_alert(self):
        meta, _ = reviewed_entry(risk="P2")
        meta["risk"] = "P1"
        self.assertFalse(watch.release_requires_notification(meta))

    def test_category_alert_needs_its_own_verified_code_path(self):
        meta, _ = reviewed_entry(risk="P1", category="安全", status="风险", extras=(
            ("兼容性", "已确认", "P2", "普通客户端变化"),
        ))
        meta["verified_finding_paths"] = ["src/change_1.rs"]
        self.assertFalse(watch.release_requires_notification(meta))

    def test_prerelease_keeps_severe_alert_without_recommending_production_deploy(self):
        meta, report = reviewed_entry(risk="P1", category="安全", status="风险", tag="v2-rc.1", note=OPERATOR_NOTE)
        self.assertEqual(meta["upgrade_advice"], "预发布版生产暂缓")
        self.assertTrue(watch.release_requires_notification(meta))
        self.assertIn("等待正式版", report)
        reasons = watch.release_notification_reasons(meta)
        self.assertTrue(any("P1 已确认 — 安全风险" in reason for reason in reasons))
        self.assertFalse(any("运营升级提醒" in reason for reason in reasons))

    def test_mixed_batch_shows_all_outcomes_but_only_real_trigger_reasons(self):
        aleo = reviewed_entry(note=ALEO_NOTE)
        xbt = reviewed_entry(coin="xbt", risk="P2", category="稳定性/数据", status="修复", tag="v29.5")
        alph = reviewed_entry(coin="alephium", category="稳定性/数据", status="修复", note=OPERATOR_NOTE, tag="v4.7.2")
        entries = {coin: {meta["repo"]: [(meta, report)]} for coin, (meta, report) in (
            ("aleo", aleo), ("xbt", xbt), ("alephium", alph),
        )}
        with tempfile.TemporaryDirectory() as directory, \
                patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "NOTIFY_LOGINS": "alice", "RUNNER_TEMP": directory}), \
                patch.object(watch, "set_workflow_output") as output:
            watch.prepare_batch_issue(entries)
            values = dict(call.args for call in output.call_args_list)
            body = watch.base64.b64decode(values["issue_body_base64"]).decode("utf-8")
        overview = body.split("**通知触发版本：**")[0]
        self.assertIn("| aleo | `v4.13.1` | P3 | 可暂缓 | 未触发主动提醒 |", overview)
        self.assertIn("| xbt | `v29.5` | P2 | 按需升级 | 未触发主动提醒；先核对是否受影响 |", overview)
        self.assertIn("| alephium | `v4.7.2` | P3 | 强烈建议升级 | 上游强烈推荐（运营提醒） |", overview)
        triggers = body.split("**通知触发版本：**")[1].split("\n## aleo\n")[0]
        self.assertIn(OPERATOR_NOTE, triggers)
        self.assertIn("运营升级提醒（非紧急风险警报）", triggers)
        self.assertNotIn("已确认 — 稳定性/数据修复", triggers)
        self.assertNotIn("🚨", triggers)
        self.assertIn("## aleo", body)
        self.assertIn("## xbt", body)
        self.assertIn("已确认 — 稳定性/数据修复", body)
        self.assertIn("通知对象：@alice", body)
        self.assertEqual(watch.notified_releases([{"user": {"login": "github-actions[bot]"}, "body": body}]), set(watch.release_keys(entries)))

    def test_severe_alert_does_not_include_unrelated_low_risk_categories(self):
        meta, report = reviewed_entry(risk="P1", category="安全", status="风险", extras=(
            ("兼容性", "已确认", "P2", "developer 命令仅改变调用方式"),
        ))
        body = watch.issue_body({"aleo": {meta["repo"]: [(meta, report)]}})
        triggers = body.split("**通知触发版本：**")[1].split("\n## aleo\n")[0]
        self.assertIn("安全风险", triggers)
        self.assertNotIn("developer", triggers)
        self.assertIn("developer", body.split("\n## aleo\n")[1])

    def test_low_risk_only_batch_explains_no_mentions(self):
        meta, report = reviewed_entry()
        with tempfile.TemporaryDirectory() as directory, \
                patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "NOTIFY_LOGINS": "alice", "RUNNER_TEMP": directory}), \
                patch.object(watch, "set_workflow_output") as output:
            watch.prepare_batch_issue({"aleo": {meta["repo"]: [(meta, report)]}})
            values = dict(call.args for call in output.call_args_list)
            body = watch.base64.b64decode(values["issue_body_base64"]).decode("utf-8")
        self.assertNotIn("通知对象：", body)
        self.assertIn("本轮没有达到主动提醒条件的版本", body)
        self.assertIn("## aleo", body)

    def test_target_network_upgrade_deadline_remains_first_trigger(self):
        meta, report = reviewed_entry(note=(
            "Mainnet hard fork activates at block height 123456. "
            "All node operators must upgrade before activation."
        ))
        self.assertEqual(meta["upgrade_advice"], "必须升级")
        body = watch.issue_body({"aleo": {meta["repo"]: [(meta, report)]}})
        triggers = body.split("**通知触发版本：**")[1].split("\n## aleo\n")[0]
        self.assertLess(triggers.index("硬分叉"), triggers.index("运营升级提醒"))
        self.assertIn("123456", triggers)
        self.assertEqual(watch.release_notification_summary(meta), "目标网强制升级提醒；上游推荐（运营提醒）")


if __name__ == "__main__":
    unittest.main()
