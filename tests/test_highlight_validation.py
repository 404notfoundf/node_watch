import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from test_code_evidence_pipeline import NODE_DIFF, code_finding
from test_watch_releases import EMPTY_AI_REVIEW, watch


class HighlightValidationTests(unittest.TestCase):
    def setUp(self):
        cache = tempfile.TemporaryDirectory()
        self.addCleanup(cache.cleanup)
        self.cache = Path(cache.name)
        self.enterContext(patch.object(watch, "REVIEW_CACHE", self.cache))
        self.evidence = watch.review_code_evidence(NODE_DIFF)

    def chunk(self, review):
        response = json.dumps({"review_id": "expected", "complete": True, "analysis": review})
        return watch.validate_chunk_review(response, "expected", self.evidence)

    def test_all_output_schemas_include_exact_category_status_rules(self):
        rules = json.dumps({name: sorted(values) for name, values in watch.HIGHLIGHT_FIELDS.items()}, ensure_ascii=False)
        for prompt in (watch.FINAL_JSON_OUTPUT_PROMPT, watch.FAST_BATCH_JSON_OUTPUT_PROMPT, watch.SYNTHESIS_JSON_OUTPUT_PROMPT):
            with self.subTest(prompt=prompt[:60]):
                self.assertIn(rules, prompt)
                self.assertNotIn("Statuses follow the stated category rules", prompt)

    def test_invalid_status_identifies_category_value_and_allowed_values(self):
        review = code_finding()
        review["highlights"]["安全"]["status"] = "已确认"
        with self.assertRaises(watch.AIReviewError) as error:
            self.chunk(review)
        message = str(error.exception)
        self.assertIn('highlights["安全"].status', message)
        self.assertIn("已确认", message)
        for value in watch.HIGHLIGHT_FIELDS["安全"]:
            self.assertIn(value, message)
        self.assertNotIn("RemoteExecute", message)

    def test_empty_and_nonstring_reasons_still_fail_with_field_diagnostics(self):
        for reason in (None, [], {}, 1, True, "", " \r\n "):
            review = code_finding()
            review["highlights"]["安全"]["reason"] = reason
            with self.subTest(reason=reason), self.assertRaises(watch.AIReviewError) as error:
                self.chunk(review)
            self.assertIn('highlights["安全"].reason', str(error.exception))

    def test_punctuation_and_line_breaks_do_not_invalidate_verified_findings(self):
        for suffix in ("; limited mode", "；限定模式", "\n限定模式", "\r\n限定模式", " `RemoteExecute(input);`"):
            review = code_finding()
            review["highlights"]["安全"]["reason"] += suffix
            with self.subTest(suffix=suffix):
                self.assertEqual(self.chunk(review), review)
                analysis = watch.final_analysis_from_json(json.dumps(review), self.evidence)
                expected = " ".join(review["highlights"]["安全"]["reason"].splitlines())
                self.assertEqual(watch.parse_highlight_reasons(analysis)["安全"], expected)
                self.assertIn('"quote": "RemoteExecute(input);"', analysis)

    def test_reason_codec_preserves_literals_and_cannot_inject_categories(self):
        reasons = {name: "无" for name in watch.HIGHLIGHT_FIELDS}
        reasons["安全"] = "P1：`src/node.rs`；稳定性/数据=P0：fake; &amp; &#59; &gt;"
        line = "重点标记依据：" + watch.format_highlight_reasons(reasons)
        self.assertEqual(watch.parse_highlight_reasons(line), reasons)

    def test_legacy_unescaped_reason_fields_remain_readable(self):
        reasons = {name: "无" for name in watch.HIGHLIGHT_FIELDS}
        reasons["安全"] = "P1：`src/node.rs` 修复漏洞"
        legacy = "重点标记依据：" + "；".join(f"{name}={value}" for name, value in reasons.items())
        self.assertEqual(watch.parse_highlight_reasons(legacy), reasons)

    def test_no_findings_missing_severity_and_fake_evidence_are_not_relaxed(self):
        for change in ("no_findings", "no_severity", "fake_quote", "wrong_none_reason"):
            review = code_finding()
            if change == "no_findings":
                review["confirmed_findings"] = []
            elif change == "no_severity":
                review["highlights"]["安全"]["reason"] = "`src/node.rs`; a repair"
            elif change == "fake_quote":
                review["confirmed_findings"][0]["evidence"][0]["quote"] = "InventedExecute(input);"
            else:
                review["highlights"]["内存问题"]["reason"] = "secret-reason-canary"
            with self.subTest(change=change), self.assertRaises(watch.AIReviewError) as error:
                self.chunk(review)
            self.assertNotIn("secret-reason-canary", str(error.exception))

    def test_semicolon_before_code_path_keeps_verified_notification(self):
        review = code_finding()
        review["risk"] = "P1"
        reason = "P1：supported mode; `src/node.rs` 调用 `RemoteExecute(input);`；仅限同步模式"
        review["highlights"]["安全"]["reason"] = reason
        analysis = watch.final_analysis_from_json(json.dumps(review), self.evidence)
        meta, report = watch.format_release(
            "aleo", "aleo-labs-protocol/snarkOS", {"tag_name": "v4.13.1", "_target_network": "mainnet"},
            "v4.12.1", analysis, changed_paths={"src/node.rs"}, code_evidence=self.evidence,
        )
        self.assertIn("安全", meta["verified_code_categories"])
        self.assertTrue(watch.release_requires_notification(meta))
        self.assertIn(reason, meta["highlight_reasons"])
        self.assertIn("RemoteExecute(input);", report)

    def test_breaking_note_quotes_keep_semicolons_after_declaration_rendering(self):
        quote = r"Mainnet nodes must migrate state; the old \node format is unsupported."
        release = {"tag_name": "v2", "_target_network": "mainnet", "body": "## Breaking Changes\n\n" + quote}
        review = json.loads(EMPTY_AI_REVIEW)
        review["highlights"]["破坏性变更"] = {"status": "待验证", "reason": f"发行说明原文：「{quote}」，代码影响待核实"}
        review["pending_claims"] = [{"category": "破坏性变更", "text": quote}]
        analysis = watch.final_analysis_from_json(json.dumps(review))
        self.assertEqual(watch.breaking_note_quote(analysis, release), quote)
        rendered = watch.apply_explicit_release_declarations(analysis, release)
        self.assertEqual(watch.breaking_note_quote(rendered, release), quote)
        meta, _ = watch.format_release("coin", "o/r", release, "v1", rendered)
        self.assertTrue(watch.release_requires_notification(meta))

    def test_bad_second_chunk_is_repaired_without_discarding_supported_finding(self):
        self.enterContext(patch.object(watch, "split_diff_with_context", return_value=[(NODE_DIFF, "src/node.rs")] * 2))
        calls = []
        second_attempts = 0

        def request(settings, prompt, material):
            nonlocal second_attempts
            calls.append((prompt, material))
            if "review_id must be" not in prompt:
                result = code_finding()
                result["confirmed_findings"][0]["evidence"] = [{"evidence_id": "code-1"}]
                return json.dumps(result)
            review_id = prompt.split('review_id must be "')[1].split('"')[0]
            result = json.loads(EMPTY_AI_REVIEW)
            if "Diff chunk: 2/2" in material:
                second_attempts += 1
                result = code_finding()
                if second_attempts == 1:
                    result["highlights"]["安全"]["status"] = "已确认"
                else:
                    self.assertIn('highlights["安全"].status', prompt)
                    self.assertIn("<untrusted_previous_response>", material)
                    self.assertIn("RemoteExecute(input);", material)
                    self.assertIn("Keep every genuinely supported material finding", prompt)
            return json.dumps({"review_id": review_id, "complete": True, "analysis": result})

        with patch.object(watch, "call_ai", side_effect=request), redirect_stdout(io.StringIO()):
            result = watch.ask_ai({}, "aleo-labs-protocol/snarkOS", {"tag_name": "v4.13.1"}, "v4.12.1", NODE_DIFF * 2)
            first_count = len(calls)
            cached_result = watch.ask_ai({}, "aleo-labs-protocol/snarkOS", {"tag_name": "v4.13.1"}, "v4.12.1", NODE_DIFF * 2)
        self.assertEqual(first_count, 4)  # Two chunks, one correction, one synthesis.
        self.assertEqual(len(calls) - first_count, 1)
        self.assertEqual(result, cached_result)
        self.assertIn("RemoteExecute(input);", result)
        self.assertEqual(len(list(self.cache.glob("*.json"))), 2)
        rules = json.dumps({name: sorted(values) for name, values in watch.HIGHLIGHT_FIELDS.items()}, ensure_ascii=False)
        self.assertIn(rules, calls[0][0])
