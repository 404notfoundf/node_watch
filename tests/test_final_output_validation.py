import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from test_code_evidence_pipeline import NODE_DIFF, code_finding
from test_watch_releases import EMPTY_AI_REVIEW, watch


class FinalOutputValidationTests(unittest.TestCase):
    def setUp(self):
        self.evidence = watch.review_code_evidence(NODE_DIFF)

    def test_system_prompt_no_longer_requests_markdown_report_output(self):
        for old_instruction in ("output exactly these fields in Chinese", "Make each non-无 category its own Markdown numbered item", "After these fields, use **代码已确认的发现**"):
            self.assertNotIn(old_instruction, watch.SYSTEM_PROMPT)
        self.assertIn("JSON", watch.SYSTEM_PROMPT)

    def test_final_accepts_only_complete_single_json_fences(self):
        expected = watch.final_analysis_from_json(EMPTY_AI_REVIEW)
        for response in ("```json\n" + EMPTY_AI_REVIEW + "\n```", "```\n" + EMPTY_AI_REVIEW + "\n```", " \n```JSON\r\n" + EMPTY_AI_REVIEW + "\r\n```\n "):
            with self.subTest(response=response[:20]):
                self.assertEqual(watch.final_analysis_from_json(response), expected)

    def test_final_prose_truncation_multiple_objects_and_invalid_fences_stay_rejected(self):
        for response in ("Result:\n" + EMPTY_AI_REVIEW, EMPTY_AI_REVIEW + "\nextra", EMPTY_AI_REVIEW * 2, "```json\n" + EMPTY_AI_REVIEW, "```json\n" + EMPTY_AI_REVIEW[:-1] + "\n```", "```javascript\n" + EMPTY_AI_REVIEW + "\n```"):
            with self.subTest(response=response[:20]), self.assertRaises(watch.AIReviewError):
                watch.final_analysis_from_json(response)

    def test_final_parse_diagnostics_show_position_not_response(self):
        response = '{"secret-response-canary":'
        with self.assertRaises(watch.AIReviewError) as error:
            watch.final_analysis_from_json(response)
        message = str(error.exception)
        for expected in ("行", "列", "响应长度"):
            self.assertIn(expected, message)
        self.assertNotIn("secret-response-canary", message)

    def test_report_sections_and_continuous_numbering_are_generated_from_json(self):
        review = code_finding()
        review["highlights"]["兼容性"] = {"status": "待验证", "reason": "发行说明有兼容性声明，代码影响待核实"}
        review["pending_claims"] = [{"category": "兼容性", "text": "A material Release Notes claim awaiting evidence"}]
        result = watch.final_analysis_from_json(json.dumps(review), self.evidence)
        self.assertIn("**代码已确认的发现**", result)
        self.assertIn("**待核实的发行说明主张**", result)
        self.assertIn("1. **已确认 — 安全：**", result)
        self.assertIn("2. **待核实 — 兼容性：**", result)

    def test_missing_repeated_narrative_paths_are_added_from_verified_evidence(self):
        for missing in ("text", "reason", "both"):
            review = code_finding()
            if missing in ("text", "both"):
                review["confirmed_findings"][0]["text"] = "Code-supported limited-scope behavior"
            if missing in ("reason", "both"):
                review["highlights"]["安全"]["reason"] = "P2：Code-supported limited-scope behavior"
            with self.subTest(missing=missing):
                result = watch.final_analysis_from_json(json.dumps(review), self.evidence)
                self.assertIn("`src/node.rs`", watch.parse_highlight_reasons(result)["安全"])
                finding = result.split("**代码已确认的发现**")[1]
                self.assertIn("`src/node.rs`", finding)
                self.assertIn('"quote": "RemoteExecute(input);"', finding)

    def test_category_reason_can_cover_multiple_verified_findings(self):
        review = code_finding()
        review["confirmed_findings"].extend(code_finding("src/other.rs")["confirmed_findings"])
        evidence = {**self.evidence, "src/other.rs": "+RemoteExecute(input);"}
        result = watch.final_analysis_from_json(json.dumps(review), evidence)
        reason = watch.parse_highlight_reasons(result)["安全"]
        self.assertIn("`src/node.rs`", reason)
        self.assertIn("`src/other.rs`", reason)

    def test_explicitly_conflicting_narrative_paths_are_not_silently_corrected(self):
        for field in ("text", "reason"):
            review = code_finding()
            if field == "text":
                review["confirmed_findings"][0]["text"] = "`src/wrong.rs` has a problem"
            else:
                review["highlights"]["安全"]["reason"] = "P2：`src/wrong.rs` has a problem"
            with self.subTest(field=field), self.assertRaises(watch.AIReviewError) as error:
                watch.final_analysis_from_json(json.dumps(review), self.evidence)
            self.assertIn(field, str(error.exception))
            self.assertIn("src/node.rs", str(error.exception))

    def test_missing_paths_never_make_fake_code_evidence_acceptable(self):
        review = code_finding()
        review["highlights"]["安全"]["reason"] = "P2：A claim"
        review["confirmed_findings"][0]["text"] = "A claim"
        review["confirmed_findings"][0]["evidence"][0]["quote"] = "InventedExecute(input);"
        with self.assertRaises(watch.AIReviewError):
            watch.final_analysis_from_json(json.dumps(review), self.evidence)

    def test_alephium_single_chunk_final_retry_handles_fence_and_missing_path(self):
        review = code_finding()
        review["highlights"]["安全"]["reason"] = "P2：Code-supported limited-scope behavior"
        review["confirmed_findings"][0]["text"] = "Code-supported limited-scope behavior"
        repaired = "```json\n" + json.dumps(review) + "\n```"
        release = {"tag_name": "v4.7.2", "_target_network": "mainnet", "body": "Highly recommended for mining pools and node operators."}
        with patch.object(watch, "call_ai", side_effect=["not valid JSON", repaired]) as request, redirect_stdout(io.StringIO()):
            result = watch.ask_ai({}, "alephium/alephium", release, "v4.7.1", NODE_DIFF)
        self.assertEqual(request.call_count, 2)
        self.assertIn("<untrusted_previous_response>", request.call_args.args[2])
        meta, _ = watch.format_release("alephium", "alephium/alephium", release, "v4.7.1", result, changed_paths={"src/node.rs"}, code_evidence=self.evidence)
        self.assertTrue(watch.release_requires_notification(meta))
        self.assertEqual(meta["upstream_upgrade_quote"], release["body"])
