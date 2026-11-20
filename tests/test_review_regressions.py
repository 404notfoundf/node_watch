import io
import json
import os
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from test_watch_releases import EMPTY_AI_REVIEW, watch


ALEPHIUM_UPGRADE_NOTE = "Fixed a mempool cache issue, highly recommended for mining pools and node operators."
ROUTINE_DIFF = "diff --git a/src/utils.cpp b/src/utils.cpp\n+++ b/src/utils.cpp\n+return 1;\n"


class ReviewRegressionTests(unittest.TestCase):
    def setUp(self):
        cache = tempfile.TemporaryDirectory()
        self.addCleanup(cache.cleanup)
        self.enterContext(patch.object(watch, "REVIEW_CACHE", Path(cache.name)))

    def test_operator_upgrade_recommendation_notifies_without_inflating_risk(self):
        release = {"tag_name": "v4.7.2", "_target_network": "mainnet", "body": ALEPHIUM_UPGRADE_NOTE}
        meta, report = watch.format_release("alephium", "alephium/alephium", release, "v4.7.1", watch.final_analysis_from_json(EMPTY_AI_REVIEW))
        self.assertTrue(watch.release_requires_notification(meta))
        self.assertEqual(meta["risk"], "P3")
        self.assertEqual(meta["verified_finding_paths"], [])
        with tempfile.TemporaryDirectory() as directory, \
                patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "NOTIFY_LOGINS": "alice", "RUNNER_TEMP": directory}), \
                patch.object(watch, "set_workflow_output") as output:
            watch.prepare_batch_issue({"alephium": {"alephium/alephium": [(meta, report)]}})
            values = dict(call.args for call in output.call_args_list)
            body = watch.base64.b64decode(values["issue_body_base64"]).decode("utf-8")
            self.assertEqual(Path(values["issue_body_path"]).read_text(encoding="utf-8"), body)
        self.assertIn("运营升级提醒", body)
        self.assertIn("通知对象：@alice", body)
        self.assertNotIn("🚨", body)

    def test_operator_reminders_exclude_prereleases_and_wrong_scope(self):
        releases = [
            {"tag_name": "v4.7.2-rc.1", "body": ALEPHIUM_UPGRADE_NOTE},
            {"tag_name": "v4.7.2", "prerelease": True, "body": ALEPHIUM_UPGRADE_NOTE},
            {"tag_name": "v4.7.2", "body": "Testnet only. " + ALEPHIUM_UPGRADE_NOTE},
            {"tag_name": "v4.7.2", "body": "This release is not recommended for node operators."},
            {"tag_name": "v4.7.2", "body": "This update is strongly recommended for wallet users only."},
            {"tag_name": "v4.7.2", "body": "We recommend upgrading the Python toolchain."},
            {"tag_name": "v4.7.2", "body": "Routine update."},
        ]
        for release in releases:
            with self.subTest(release=release):
                release["_target_network"] = "mainnet"
                meta, _ = watch.format_release("coin", "o/r", release, "v1", watch.final_analysis_from_json(EMPTY_AI_REVIEW))
                self.assertFalse(watch.release_requires_notification(meta))

    def test_alephium_recommendation_survives_empty_p3_review(self):
        release = {"tag_name": "v4.7.2", "_target_network": "mainnet", "body": ALEPHIUM_UPGRADE_NOTE}
        mode = watch.review_mode("auto", release, ROUTINE_DIFF)
        meta, report = watch.format_release("alephium", "alephium/alephium", release, "v4.7.1", watch.final_analysis_from_json(EMPTY_AI_REVIEW), review=mode)
        issue = watch.issue_body({"alephium": {"alephium/alephium": [(meta, report)]}})
        self.assertEqual(mode, "full")
        self.assertEqual(meta["upgrade_advice"], "强烈建议升级")
        self.assertEqual(meta["importance"], "需关注")
        self.assertEqual(meta["conclusion"], "需关注")
        self.assertEqual(meta["risk"], "P3")
        self.assertEqual(meta["verified_finding_paths"], [])
        self.assertTrue(all(status == "无" for status in meta["highlight_statuses"].values()))
        self.assertIn(ALEPHIUM_UPGRADE_NOTE, report)
        self.assertIn(ALEPHIUM_UPGRADE_NOTE, issue)
        self.assertEqual(issue.count(ALEPHIUM_UPGRADE_NOTE), 2)
        self.assertIn("上游升级建议", issue)
        self.assertIn("维护窗口", watch.issue_action_line(meta))
        self.assertNotIn("可暂缓", issue)
        self.assertNotIn("不重要", report)
        self.assertTrue(watch.release_requires_notification(meta))

    def test_similar_operator_recommendations_trigger_full_review(self):
        strong_notes = (
            ALEPHIUM_UPGRADE_NOTE,
            "Highly recommended for pool operators and miners.",
            "We strongly recommend that all node operators upgrade to this version.",
            "Upgrading is highly recommended.",
            "强烈建议矿池和节点运营者升级到本版本。",
        )
        notes = (
            *strong_notes,
            "This release is recommended for mining pools.",
            "Node operators are encouraged to upgrade their nodes.",
            "We advise all users to update to the latest release.",
            "This is a recommended update for node operators.",
            "This is an important update for mining pools.",
            "Critical release for node operators.",
            "For node operators, this is a critical update.",
            "All node operators should upgrade.",
            "Validators must upgrade their nodes.",
            "Please upgrade your nodes to this release.",
            "推荐所有节点运营者更新。",
            "这是面向矿池的重要更新。",
            "矿池务必升级节点。",
        )
        for note in notes:
            with self.subTest(note=note):
                release = {"tag_name": "v2", "_target_network": "mainnet", "body": note}
                self.assertEqual(watch.review_mode("auto", release, ROUTINE_DIFF), "full")
                advice, reason = watch.upgrade_advice(watch.final_analysis_from_json(EMPTY_AI_REVIEW), release)
                self.assertEqual(advice, "强烈建议升级" if note in strong_notes else "建议升级")
                self.assertIn(note, reason)

    def test_non_operator_or_negative_recommendations_do_not_trigger(self):
        notes = (
            "This release is not recommended for mining pools and node operators.",
            "Upgrading is not highly recommended for node operators.",
            "Node operators should not upgrade to this release.",
            "No need to upgrade your nodes.",
            "An upgrade is not required for node operators.",
            "No upgrade is required for node operators.",
            "We recommend not upgrading your nodes yet.",
            "We recommend avoiding upgrading the nodes for now.",
            "This release is recommended for wallet users only. Node operators need not upgrade.",
            "矿池无需升级。",
            "暂不建议节点运营者升级。",
            "不推荐矿池升级。",
            "建议矿池暂缓升级。",
            "We recommend upgrading the Python toolchain.",
            "We recommend upgrading your dependencies.",
            "We recommend upgrading the dependencies used by node operators.",
            "Node operators should update their configuration files.",
            "This update is strongly recommended for wallet users only.",
            "This release is recommended for wallet users only; node operators are unaffected.",
            "仅钱包用户建议升级，节点运营者不受影响。",
            "Light clients should upgrade their GUI.",
            "Routine performance improvements for node operators.",
            "```text\nAll node operators should upgrade.\n```",
        )
        for note in notes:
            with self.subTest(note=note):
                release = {"tag_name": "v2", "_target_network": "mainnet", "body": note}
                self.assertEqual(watch.review_mode("auto", release, ROUTINE_DIFF), "fast")
                advice, _ = watch.upgrade_advice(watch.final_analysis_from_json(EMPTY_AI_REVIEW), release)
                self.assertEqual(advice, "可暂缓")

    def test_recommendations_respect_network_sections(self):
        cases = (
            ("Testnet node operators should upgrade. Mainnet is unaffected.", "mainnet", "可暂缓"),
            ("## Testnet\n\nAll node operators should upgrade.", "mainnet", "可暂缓"),
            ("## Testnet\nAll node operators should upgrade.\n\n## Mainnet\nRoutine update.", "mainnet", "可暂缓"),
            ("## Mainnet\n\nAll node operators should upgrade.", "mainnet", "建议升级"),
            ("## Testnet\n\nAll node operators should upgrade.", "testnet", "建议升级"),
            ("Mainnet node operators should upgrade.", "", "可暂缓"),
            (ALEPHIUM_UPGRADE_NOTE, "", "强烈建议升级"),
            ("## Testnet\n\nNo need to upgrade.\n\n## Mainnet\n\nAll node operators should upgrade.", "mainnet", "建议升级"),
        )
        for note, network, expected in cases:
            with self.subTest(note=note, network=network):
                release = {"tag_name": "v2", "_target_network": network, "body": note}
                advice, _ = watch.upgrade_advice(watch.final_analysis_from_json(EMPTY_AI_REVIEW), release)
                self.assertEqual(advice, expected)

    def test_upstream_recommendation_does_not_override_stricter_decisions(self):
        release = {"tag_name": "v2", "_target_network": "mainnet", "body": ALEPHIUM_UPGRADE_NOTE}
        base = watch.final_analysis_from_json(EMPTY_AI_REVIEW)
        for analysis, expected in (
            (base.replace("风险级别：P3", "风险级别：P0"), "必须升级"),
            (base.replace("风险级别：P3", "风险级别：待人工复核"), "需人工确认"),
            (base.replace("兼容性=无", "兼容性=待验证", 1), "需人工确认"),
            (base.replace("风险级别：P3", "风险级别：P2"), "强烈建议升级"),
        ):
            with self.subTest(expected=expected, analysis=analysis):
                advice, reason = watch.upgrade_advice(analysis, release)
                self.assertEqual(advice, expected)
                self.assertIn(ALEPHIUM_UPGRADE_NOTE, reason)

    def test_upstream_prerelease_recommendation_is_not_production_advice(self):
        release = {"tag_name": "v2-rc.1", "prerelease": True, "body": ALEPHIUM_UPGRADE_NOTE}
        meta, _ = watch.format_release("coin", "o/r", release, "v1", watch.final_analysis_from_json(EMPTY_AI_REVIEW))
        self.assertEqual(watch.review_mode("auto", release, ROUTINE_DIFF), "full")
        self.assertEqual(meta["upgrade_advice"], "预发布版生产暂缓")
        self.assertIn(ALEPHIUM_UPGRADE_NOTE, meta["upgrade_reason"])
        self.assertIn("暂缓升级", watch.issue_action_line(meta))
        self.assertFalse(watch.release_requires_notification(meta))

    def test_title_and_markdown_recommendations_are_recognized(self):
        release = {"tag_name": "v2", "name": "Important update for node operators", "body": "Routine fixes."}
        self.assertEqual(watch.review_mode("auto", release, ROUTINE_DIFF), "full")
        release = {"tag_name": "v2", "body": "**All node operators should upgrade.**"}
        advice, reason = watch.upgrade_advice(watch.final_analysis_from_json(EMPTY_AI_REVIEW), release)
        self.assertEqual(advice, "建议升级")
        self.assertIn(release["body"], reason)

    def test_title_and_section_scope_cannot_leak_to_mainnet_nodes(self):
        for release in (
            {"name": "Testnet release", "body": "All node operators should upgrade."},
            {"body": "## Wallet\n\nAll users should upgrade."},
            {"name": "Wallet release", "body": "All users should upgrade."},
        ):
            with self.subTest(release=release):
                release.update(tag_name="v2", _target_network="mainnet")
                advice, _ = watch.upgrade_advice(watch.final_analysis_from_json(EMPTY_AI_REVIEW), release)
                self.assertEqual(advice, "可暂缓")

    def test_title_quote_does_not_include_synthetic_prompt_label(self):
        release = {"tag_name": "v2", "name": "Important update for node operators", "body": "Routine fixes."}
        advice, reason = watch.upgrade_advice(watch.final_analysis_from_json(EMPTY_AI_REVIEW), release)
        self.assertEqual(advice, "建议升级")
        self.assertIn(f"发行说明原文：「{release['name']}」", reason)

    def test_upgrade_recommendation_is_retained_in_chunk_claims(self):
        self.assertIn(ALEPHIUM_UPGRADE_NOTE, watch.release_note_claims(ALEPHIUM_UPGRADE_NOTE))
        self.assertIn("UPSTREAM UPGRADE RECOMMENDATIONS", watch.SYSTEM_PROMPT)

    def test_chunk_claims_keep_markdown_network_and_operator_scope(self):
        for note, scope in (
            ("## Testnet\n\nAll node operators **should** upgrade.", "## Testnet"),
            ("## Wallet\n\nAll users should upgrade.", "## Wallet"),
            ("Release title: Testnet release\n\nAll node operators should upgrade.", "Release title: Testnet release"),
        ):
            with self.subTest(note=note):
                claims = watch.release_note_claims(note)
                self.assertIn(scope, claims)
                self.assertIn("upgrade.", claims)

    def test_explicit_review_mode_still_takes_precedence(self):
        release = {"tag_name": "v2", "body": ALEPHIUM_UPGRADE_NOTE}
        self.assertEqual(watch.review_mode("fast", release, ROUTINE_DIFF), "fast")
        self.assertEqual(watch.review_mode("full", release, ROUTINE_DIFF), "full")

    def test_main_routes_operator_recommendation_to_full_review(self):
        config = {"review": {"mode": "auto"}, "coins": {"coin": {"repo": "o/r", "running_version": "v1", "network": "mainnet"}}}
        release = {"tag_name": "v2", "body": ALEPHIUM_UPGRADE_NOTE}
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            stack.enter_context(patch.object(watch, "ROOT", Path(directory)))
            stack.enter_context(patch.object(watch, "REPORTS", Path(directory)))
            stack.enter_context(patch.object(watch, "load_config", return_value=config))
            stack.enter_context(patch.object(watch, "should_read_github_issue_history", return_value=False))
            stack.enter_context(patch.object(watch, "release_window_after_running_version", return_value=([release], "v1")))
            stack.enter_context(patch.object(watch, "release_diff", return_value=(ROUTINE_DIFF, {"src/utils.cpp"})))
            stack.enter_context(patch.object(watch, "linked_release_reference_evidence", return_value=""))
            stack.enter_context(patch.object(watch, "historical_prerelease_reviews", return_value=""))
            full = stack.enter_context(patch.object(watch, "ask_ai", return_value=watch.final_analysis_from_json(EMPTY_AI_REVIEW)))
            fast = stack.enter_context(patch.object(watch, "ask_ai_fast_batch", return_value=None))
            stack.enter_context(patch.object(watch, "set_workflow_output"))
            stack.enter_context(patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}))
            watch.main()
            self.assertEqual(full.call_count, 1)
            self.assertEqual(full.call_args.args[5], "full")
            fast.assert_not_called()
            reports = list(Path(directory).glob("*.md"))
            self.assertEqual(len(reports), 1)
            self.assertIn("建议升级", reports[0].read_text(encoding="utf-8"))

    def test_testnet_fork_cannot_override_mainnet_decision(self):
        release = {"tag_name": "v2", "_target_network": "mainnet", "body": "Testnet hard fork activates at block height 123456. All node operators must upgrade before activation. Mainnet is unaffected."}
        meta, _ = watch.format_release("coin", "o/r", release, "v1", watch.final_analysis_from_json(EMPTY_AI_REVIEW))
        self.assertEqual(meta["upgrade_advice"], "可暂缓")
        self.assertFalse(watch.release_requires_notification(meta))

    def test_target_network_fork_still_notifies(self):
        release = {"tag_name": "v2", "_target_network": "mainnet", "body": "Mainnet hard fork activates at block height 123456. All node operators must upgrade before activation."}
        meta, _ = watch.format_release("coin", "o/r", release, "v1", watch.final_analysis_from_json(EMPTY_AI_REVIEW))
        self.assertEqual(meta["upgrade_advice"], "必须升级")
        self.assertTrue(watch.release_requires_notification(meta))

    def test_two_network_notices_select_target_height(self):
        release = {"_target_network": "mainnet", "body": "Testnet hard fork activates at block height 100. All node operators must upgrade before activation.\n\nMainnet hard fork activates at block height 200. All node operators must upgrade before activation."}
        self.assertEqual(watch.explicit_hard_fork_notice(release)[0], "区块高度 200")

    def test_unspecified_network_does_not_assume_testnet_is_target(self):
        release = {"body": "Testnet hard fork activates at block height 100. All node operators must upgrade before activation."}
        self.assertIsNone(watch.explicit_hard_fork_notice(release))

    def test_unknown_network_does_not_trigger_automatic_fork_upgrade(self):
        release = {"_target_network": "mainnet", "body": "Hard fork activates at block height 100. All node operators must upgrade before activation."}
        self.assertIsNone(watch.explicit_hard_fork_notice(release))

    def test_core_path_deletions_force_full_review(self):
        for path in ("src/chain/block.cpp", "src/p2p/peer.rs", "src/storage/db.go", "src/rpc.cpp", "src/validation.cpp"):
            with self.subTest(path=path):
                diff = f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1,2 +1 @@\n-if (!CheckProofOfWork(block)) return false;\n return true;\n"
                self.assertEqual(watch.review_mode("auto", {"body": "Routine update"}, diff), "full")

    def test_truncated_provider_output_is_retried_not_accepted(self):
        response = {"choices": [{"finish_reason": "length", "message": {"content": "incomplete"}}]}
        with patch.dict(os.environ, {"AI_API_KEY": "dummy", "AI_BACKEND": "openai_compatible"}), \
                patch.object(watch.urllib.request, "urlopen", side_effect=lambda *a, **k: io.BytesIO(json.dumps(response).encode())) as request, \
                patch.object(watch.time, "sleep"):
            with self.assertRaises(watch.AIReviewError):
                watch.call_ai({"api_url": "https://invalid.example/v1", "model": "test"}, "prompt", "material")
        self.assertEqual(request.call_count, 4)

    def test_incomplete_chunk_is_never_cached(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(watch, "REVIEW_CACHE", Path(directory)), \
                patch.object(watch, "call_ai", return_value="Review stopped halfway"), patch.object(watch, "call_final_ai") as synthesize:
            with self.assertRaises(watch.AIReviewError):
                watch.ask_ai({"diff_chunk_chars": 4}, "o/r", {"tag_name": "v2"}, "v1", "abcdefghij")
            self.assertEqual(list(Path(directory).glob("*.json")), [])
            synthesize.assert_not_called()

    def finding(self, quote="RemoteExecute(input);", path="src/chain/block.cpp"):
        data = json.loads(EMPTY_AI_REVIEW)
        data["risk"] = "P1"
        data["highlights"]["安全"] = {"status": "风险", "reason": f"P1：`{path}` permits remote execution"}
        data["confirmed_findings"] = [{"category": "安全", "text": f"`{path}` executes attacker input", "evidence": [{"path": path, "quote": quote}]}]
        return json.dumps(data, ensure_ascii=False)

    def test_invented_quote_is_rejected_even_with_real_path(self):
        with self.assertRaises(watch.AIReviewError):
            watch.final_analysis_from_json(self.finding(), {"src/chain/block.cpp": "return Validate(block);"})

    def test_quote_from_wrong_file_is_rejected(self):
        with self.assertRaises(watch.AIReviewError):
            watch.final_analysis_from_json(self.finding(), {"src/other.cpp": "RemoteExecute(input);"})

    def test_matching_code_quote_is_retained(self):
        result = watch.final_analysis_from_json(self.finding(), {"src/chain/block.cpp": "RemoteExecute(input);"})
        self.assertIn("RemoteExecute(input);", result)

    def test_verified_finding_still_triggers_notification(self):
        evidence = {"src/chain/block.cpp": "RemoteExecute(input);"}
        analysis = watch.final_analysis_from_json(self.finding(), evidence)
        meta, _ = watch.format_release("coin", "o/r", {"tag_name": "v2"}, "v1", analysis, code_evidence=evidence)
        self.assertTrue(watch.release_requires_notification(meta))

    def test_comment_cannot_be_used_as_code_evidence(self):
        with self.assertRaises(watch.AIReviewError):
            watch.final_analysis_from_json(self.finding(), {"src/chain/block.cpp": "// RemoteExecute(input);\nreturn true;"})

    def test_reference_quote_is_bound_to_exact_file(self):
        references = 'Code patch for "src/one.cpp":\n@@ -1 +1 @@\n+Validate(block);\nCode patch for "src/two.cpp":\n@@ -1 +1 @@\n+RemoteExecute(input);\n'
        evidence = watch.review_code_evidence("", references)
        self.assertTrue(watch.code_quote_matches("src/two.cpp", "RemoteExecute(input);", evidence))
        self.assertFalse(watch.code_quote_matches("src/one.cpp", "RemoteExecute(input);", evidence))

    def test_reference_metadata_is_not_code_evidence(self):
        references = 'Code patch for "src/one.cpp":\n@@ -1 +1 @@\n+Validate(block);\nPR #2: RemoteExecute(input); included in target tag: yes.\n'
        evidence = watch.review_code_evidence("", references)
        self.assertFalse(watch.code_quote_matches("src/one.cpp", "RemoteExecute(input);", evidence))

    def test_fast_batch_cannot_transfer_evidence_between_versions(self):
        response = "--- REVIEW 0000000000000000 ---\n" + self.finding()
        result = watch.parse_fast_batch_response(response, {"0000000000000000"}, {"0000000000000000": {"src/chain/block.cpp": "Validate(block);"}})
        self.assertIsNone(result)

    def test_invalid_evidence_retries_then_fails_without_recording(self):
        with patch.object(watch, "call_ai", return_value=self.finding()) as request:
            with self.assertRaises(watch.AIReviewError):
                watch.call_final_ai({}, "prompt", "material", {"src/chain/block.cpp": "Validate(block);"})
        self.assertEqual(request.call_count, 2)

    def test_wrong_chunk_completion_id_is_rejected(self):
        with self.assertRaises(watch.AIReviewError):
            watch.validate_chunk_review(json.dumps({"review_id": "wrong", "complete": True, "analysis": "review"}), "expected")

    def test_false_chunk_completion_is_rejected(self):
        with self.assertRaises(watch.AIReviewError):
            watch.validate_chunk_review(json.dumps({"review_id": "expected", "complete": False, "analysis": "review"}), "expected")

    def test_invalid_cached_chunk_is_replaced_not_reused(self):
        def response(settings, prompt, material):
            review_id = prompt.split('review_id must be "')[1].split('"')[0]
            return json.dumps({"review_id": review_id, "complete": True, "analysis": json.loads(EMPTY_AI_REVIEW)})
        with patch.object(watch, "cached_chunk_review", return_value="old unvalidated prose"), \
                patch.object(watch, "call_ai", side_effect=response) as request, \
                patch.object(watch, "save_chunk_review") as save, \
                patch.object(watch, "call_final_ai", return_value="complete"):
            watch.ask_ai({"diff_chunk_chars": 4}, "o/r", {"tag_name": "v2"}, "v1", "abcdefghij")
        self.assertEqual(request.call_count, 3)
        self.assertEqual(save.call_count, 3)

    def test_deleted_code_can_support_a_baseline_fix(self):
        diff = "diff --git a/src/chain/block.cpp b/src/chain/block.cpp\n--- a/src/chain/block.cpp\n+++ b/src/chain/block.cpp\n@@ -1 +1 @@\n-RemoteExecute(input);\n+Validate(input);\n"
        result = watch.final_analysis_from_json(self.finding(), watch.review_code_evidence(diff))
        self.assertIn("RemoteExecute(input);", result)

    def test_unrelated_file_changes_remain_fast(self):
        diff = "diff --git a/docs/chain.md b/docs/chain.md\n+++ b/docs/chain.md\n+Documentation update\n"
        self.assertEqual(watch.review_mode("auto", {"body": "Routine update"}, diff), "fast")

    def test_network_is_propagated_and_failed_batches_are_not_retried(self):
        captured = []
        config = {"review": {"max_releases_per_run": 4}, "coins": {"coin": {"repo": "o/r", "running_version": "v0", "network": "mainnet"}}}
        def fail(candidates, *args):
            captured.extend(candidates)
            raise watch.AIReviewError("batch failed")
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            stack.enter_context(patch.object(watch, "REPORTS", Path(directory)))
            stack.enter_context(patch.object(watch, "load_config", return_value=config))
            stack.enter_context(patch.object(watch, "should_read_github_issue_history", return_value=False))
            stack.enter_context(patch.object(watch, "reported_releases", return_value=set()))
            stack.enter_context(patch.object(watch, "release_window_after_running_version", return_value=([{"tag_name": f"v{n}"} for n in range(1, 5)], "v0")))
            stack.enter_context(patch.object(watch, "release_diff", return_value=("", set())))
            stack.enter_context(patch.object(watch, "linked_release_reference_evidence", return_value=""))
            stack.enter_context(patch.object(watch, "historical_prerelease_reviews", return_value=""))
            batch = stack.enter_context(patch.object(watch, "review_fast_candidates", side_effect=fail))
            stack.enter_context(patch.object(watch, "set_workflow_output"))
            stack.enter_context(patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}))
            watch.main()
            self.assertEqual(batch.call_count, 1)
        self.assertEqual(len(captured), 3)
        self.assertTrue(all(candidate["release"]["_target_network"] == "mainnet" for candidate in captured))

    def test_filename_alone_is_not_notification_evidence(self):
        analysis = (
            "风险级别：P1\n重点标记：破坏性变更=无；硬分叉/共识=无；兼容性=无；内存问题=无；安全=风险；稳定性/数据=无\n"
            "重点标记依据：破坏性变更=无；硬分叉/共识=无；兼容性=无；内存问题=无；安全=P1：`src/chain/block.cpp` has RCE；稳定性/数据=无\n"
            "**代码已确认的发现**\n1. **已确认 — 安全：** `src/chain/block.cpp` calls nonexistent RemoteExecute."
        )
        meta, _ = watch.format_release("coin", "o/r", {"tag_name": "v2"}, "v1", analysis, changed_paths={"src/chain/block.cpp"})
        self.assertFalse(watch.release_requires_notification(meta))

    def test_prepared_fast_candidates_survive_next_tag_fetch_failure(self):
        config = {"review": {"max_releases_per_run": 4}, "coins": {"coin": {"repo": "o/r", "running_version": "v0"}}}
        recorded = []
        def diff(repo, previous, tag):
            if tag == "v3":
                raise RuntimeError("fetch failed")
            return "", set()
        with tempfile.TemporaryDirectory() as directory, ExitStack() as stack:
            stack.enter_context(patch.object(watch, "REPORTS", Path(directory)))
            stack.enter_context(patch.object(watch, "load_config", return_value=config))
            stack.enter_context(patch.object(watch, "should_read_github_issue_history", return_value=False))
            stack.enter_context(patch.object(watch, "reported_releases", return_value=set()))
            stack.enter_context(patch.object(watch, "release_window_after_running_version", return_value=([{"tag_name": f"v{n}"} for n in range(1, 5)], "v0")))
            stack.enter_context(patch.object(watch, "release_diff", side_effect=diff))
            stack.enter_context(patch.object(watch, "linked_release_reference_evidence", return_value=""))
            stack.enter_context(patch.object(watch, "historical_prerelease_reviews", return_value=""))
            stack.enter_context(patch.object(watch, "ask_ai_fast_batch", return_value=None))
            stack.enter_context(patch.object(watch, "ask_ai", return_value=watch.final_analysis_from_json(EMPTY_AI_REVIEW)))
            stack.enter_context(patch.object(watch, "record_review_candidate", side_effect=lambda c, *a: recorded.append(c["release"]["tag_name"])))
            stack.enter_context(patch.object(watch, "set_workflow_output"))
            stack.enter_context(patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}))
            watch.main()
        self.assertEqual(recorded, ["v1", "v2"])
