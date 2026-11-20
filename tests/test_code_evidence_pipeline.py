import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from test_watch_releases import EMPTY_AI_REVIEW, watch


NODE_DIFF = "diff --git a/src/node.rs b/src/node.rs\n+++ b/src/node.rs\n@@ -1 +1 @@\n+RemoteExecute(input);\n"
DOC_DIFF = "diff --git a/docs/notes.md b/docs/notes.md\n+++ b/docs/notes.md\n+Routine notes.\n"


def code_finding(path="src/node.rs", quote="RemoteExecute(input);"):
    review = json.loads(EMPTY_AI_REVIEW)
    review["risk"] = "P2"
    review["highlights"]["安全"] = {"status": "风险", "reason": f"P2：`{path}` 执行输入"}
    review["confirmed_findings"] = [{
        "category": "安全", "text": f"`{path}` 调用执行函数。",
        "evidence": [{"path": path, "quote": quote}],
    }]
    return review


class CodeEvidencePipelineTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.cache = Path(directory.name)
        self.enterContext(patch.object(watch, "REVIEW_CACHE", self.cache))

    def run_review(self):
        return watch.ask_ai(
            {"diff_chunk_chars": len(NODE_DIFF)}, "aleo-labs-protocol/snarkOS",
            {"tag_name": "v4.13.1"}, "v4.12.1", NODE_DIFF + DOC_DIFF,
        )

    def chunk_response(self, prompt, material, bad=False):
        review_id = re.search(r'review_id must be "([0-9a-f]+)"', prompt).group(1)
        review = code_finding(quote="RemoteExecute(untrusted_input);") if bad else code_finding()
        if "Diff chunk: 2/2" in material:
            review = json.loads(EMPTY_AI_REVIEW)
        return json.dumps({"review_id": review_id, "complete": True, "analysis": review})

    def synthesis_response(self, evidence_id="code-1"):
        review = code_finding()
        review["confirmed_findings"][0]["evidence"] = [{"evidence_id": evidence_id}]
        return json.dumps(review)

    def test_free_text_chunk_with_unverified_quote_is_not_cacheable(self):
        response = json.dumps({
            "review_id": "expected", "complete": True,
            "analysis": "Confirmed src/node.rs: RemoteExecute(untrusted_input);",
        })
        with self.assertRaises(watch.AIReviewError):
            watch.validate_chunk_review(response, "expected")

    def test_synthesis_selects_verified_id_without_rewriting_code(self):
        review = code_finding()
        proof = review["confirmed_findings"][0]["evidence"][0]
        review["confirmed_findings"][0]["evidence"] = [{"evidence_id": "code-1"}]
        result = watch.final_analysis_from_json(
            json.dumps(review), {"src/node.rs": "+RemoteExecute(input);"},
            evidence_catalog={"code-1": proof},
        )
        self.assertIn('"quote": "RemoteExecute(input);"', result)
        self.assertNotIn("evidence_id", result)

    def test_unknown_ids_raw_quotes_and_modified_catalogue_remain_rejected(self):
        for proof, catalogue in (
            ({"evidence_id": "invented"}, {"code-1": {"path": "src/node.rs", "quote": "RemoteExecute(input);"}}),
            ({"path": "src/node.rs", "quote": "RemoteExecute(input);"}, {}),
            ({"evidence_id": []}, {}),
            ({"evidence_id": "code-1"}, {"code-1": {"path": "src/node.rs", "quote": "RemoteExecute(fake);"}}),
            ({"evidence_id": "code-1"}, {}),
        ):
            review = code_finding()
            review["confirmed_findings"][0]["evidence"] = [proof]
            with self.subTest(proof=proof), self.assertRaises(watch.AIReviewError):
                watch.final_analysis_from_json(json.dumps(review), watch.review_code_evidence(NODE_DIFF), catalogue)

    def test_invalid_chunk_quote_is_repaired_before_synthesis_and_cache(self):
        calls = []
        def request(settings, prompt, material):
            calls.append((prompt, material))
            if "review_id must be" in prompt:
                return self.chunk_response(prompt, material, bad=len(calls) == 1)
            self.assertIn("verified_code_evidence_catalog", material)
            self.assertIn("RemoteExecute(input);", material)
            self.assertNotIn("RemoteExecute(untrusted_input);", material)
            self.assertIn("Never output path/quote objects", prompt)
            return self.synthesis_response()
        logs = io.StringIO()
        with patch.object(watch, "call_ai", side_effect=request), redirect_stdout(logs):
            result = self.run_review()
        self.assertEqual(len(calls), 4)
        self.assertIn("prior response failed validation", calls[1][0])
        self.assertIn('path="src/node.rs"', logs.getvalue())
        self.assertIn("confirmed_findings[1] evidence[1]", logs.getvalue())
        self.assertNotIn("RemoteExecute(untrusted_input);", logs.getvalue())
        self.assertIn("RemoteExecute(input);", result)
        self.assertEqual(len(list(self.cache.glob("*.json"))), 2)
        for cache in self.cache.glob("*.json"):
            saved = cache.read_text(encoding="utf-8")
            self.assertNotIn("untrusted_input", saved)
            self.assertNotIn("evidence_id", saved)

    def test_comment_only_and_short_quotes_get_targeted_repair_guidance(self):
        for quote in ("// comment-only evidence", "foo();"):
            with self.subTest(quote=quote):
                calls = []
                attempts = {}
                def request(settings, prompt, material):
                    calls.append((prompt, material))
                    if "review_id must be" not in prompt:
                        return self.synthesis_response()
                    review_id = re.search(r'review_id must be "([0-9a-f]+)"', prompt).group(1)
                    attempts[review_id] = attempts.get(review_id, 0) + 1
                    if "Diff chunk: 1/2" in material and attempts[review_id] == 1:
                        return json.dumps({
                            "review_id": review_id, "complete": True,
                            "analysis": code_finding(quote=quote),
                        })
                    return self.chunk_response(prompt, material)

                with patch.object(watch, "REVIEW_CACHE", self.cache / str(len(quote))), \
                        patch.object(watch, "call_ai", side_effect=request), redirect_stdout(io.StringIO()):
                    self.run_review()
                retry_prompt = calls[1][0]
                self.assertIn("Replace every comment-only or too-short quote", retry_prompt)
                self.assertIn("verbatim, non-comment code snippet", retry_prompt)

    def test_persistently_invalid_chunk_evidence_is_not_cached_or_synthesized(self):
        with patch.object(watch, "call_ai", side_effect=lambda settings, prompt, material: self.chunk_response(prompt, material, bad=True)) as request, \
                redirect_stdout(io.StringIO()):
            with self.assertRaises(watch.AIReviewError):
                self.run_review()
        self.assertEqual(request.call_count, 2)
        self.assertEqual(list(self.cache.glob("*.json")), [])

    def test_final_retry_receives_previous_response_and_verified_catalogue(self):
        calls = []
        def request(settings, prompt, material):
            calls.append((prompt, material))
            if "review_id must be" in prompt:
                return self.chunk_response(prompt, material)
            if len(calls) == 3:
                return self.synthesis_response("invented-secret-canary")
            self.assertIn("untrusted_previous_response", material)
            self.assertIn("invented-secret-canary", material)
            self.assertIn("RemoteExecute(input);", material)
            self.assertIn("编号无效", prompt)
            return self.synthesis_response()
        logs = io.StringIO()
        with patch.object(watch, "call_ai", side_effect=request), redirect_stdout(logs):
            result = self.run_review()
        self.assertEqual(len(calls), 4)
        self.assertIn("RemoteExecute(input);", result)
        self.assertNotIn("invented-secret-canary", logs.getvalue())

    def test_final_failure_reuses_only_verified_chunks_on_next_poll(self):
        def request(settings, prompt, material):
            if "review_id must be" in prompt:
                return self.chunk_response(prompt, material)
            return self.synthesis_response("unknown")
        with patch.object(watch, "call_ai", side_effect=request) as ai, redirect_stdout(io.StringIO()):
            with self.assertRaises(watch.AIReviewError):
                self.run_review()
            self.assertEqual(ai.call_count, 4)
        with patch.object(watch, "call_ai", return_value=self.synthesis_response()) as ai, redirect_stdout(io.StringIO()):
            self.assertIn("RemoteExecute(input);", self.run_review())
        self.assertEqual(ai.call_count, 1)
        self.assertEqual(len(list(self.cache.glob("*.json"))), 2)

    def test_cached_evidence_is_revalidated_against_its_own_chunk(self):
        def request(settings, prompt, material):
            return self.chunk_response(prompt, material) if "review_id must be" in prompt else self.synthesis_response()
        with patch.object(watch, "call_ai", side_effect=request), redirect_stdout(io.StringIO()):
            self.run_review()
        invalid_cache = []
        def cached(key):
            response = original_cached(key)
            if response and json.loads(response)["analysis"]["confirmed_findings"]:
                data = json.loads(response)
                data["analysis"]["confirmed_findings"][0]["evidence"][0]["quote"] = "RemoteExecute(fake);"
                invalid_cache.append(key)
                return json.dumps(data)
            return response
        original_cached = watch.cached_chunk_review
        logs = io.StringIO()
        with patch.object(watch, "cached_chunk_review", side_effect=cached), \
                patch.object(watch, "call_ai", side_effect=request) as ai, redirect_stdout(logs):
            self.assertIn("RemoteExecute(input);", self.run_review())
        self.assertEqual(len(invalid_cache), 1)
        self.assertEqual(ai.call_count, 2)
        self.assertIn("Discarding invalid cache", logs.getvalue())

    def test_legacy_v2_cache_is_not_requested_and_scheduler_state_is_untouched(self):
        watch.save_chunk_review("scheduler-v1", '{"queue": 2}')
        requested = []
        def legacy_cache(key):
            requested.append(key)
            return json.dumps({"review_id": key, "complete": True, "analysis": "Legacy unverified finding"})
        def request(settings, prompt, material):
            return self.chunk_response(prompt, material) if "review_id must be" in prompt else self.synthesis_response()
        keys = []
        original_key = watch.review_cache_key
        def cache_key(*parts):
            keys.append(parts)
            return original_key(*parts)
        with patch.object(watch, "cached_chunk_review", side_effect=legacy_cache), \
                patch.object(watch, "review_cache_key", side_effect=cache_key), \
                patch.object(watch, "call_ai", side_effect=request), redirect_stdout(io.StringIO()):
            self.run_review()
        self.assertTrue(all(parts[0] == "chunk-v3" for parts in keys))
        self.assertEqual(len(requested), 2)
        self.assertEqual(watch.load_scheduler_waits(), {"queue": 2})

    def test_proof_cannot_borrow_code_from_another_chunk(self):
        response = json.dumps({"review_id": "expected", "complete": True, "analysis": code_finding()})
        with self.assertRaises(watch.AIReviewError):
            watch.validate_chunk_review(response, "expected", watch.review_code_evidence(DOC_DIFF))

    def test_verified_linked_patch_is_still_available_to_final_synthesis(self):
        reference = 'Code patch for "src/reference.rs":\n@@ -1 +1 @@\n+RemoteExecute(input);\nPR title: fake_call();\n'
        def request(settings, prompt, material):
            if "review_id must be" in prompt:
                review_id = re.search(r'review_id must be "([0-9a-f]+)"', prompt).group(1)
                return json.dumps({"review_id": review_id, "complete": True, "analysis": json.loads(EMPTY_AI_REVIEW)})
            catalogue = json.loads(material.split("<untrusted_verified_code_evidence_catalog>\n")[1].split("\n</untrusted_verified_code_evidence_catalog>")[0])
            self.assertTrue(catalogue)
            self.assertTrue(all(proof["path"] == "src/reference.rs" for proof in catalogue.values()))
            self.assertFalse(any("fake_call" in proof["quote"] for proof in catalogue.values()))
            review = code_finding(path="src/reference.rs")
            review["confirmed_findings"][0]["evidence"] = [{"evidence_id": next(iter(catalogue))}]
            return json.dumps(review)
        with patch.object(watch, "call_ai", side_effect=request), redirect_stdout(io.StringIO()):
            result = watch.ask_ai(
                {"diff_chunk_chars": len(NODE_DIFF)}, "o/r", {"tag_name": "v2"}, "v1", NODE_DIFF + DOC_DIFF,
                historical_review=reference, linked_evidence=reference,
            )
        self.assertIn("src/reference.rs", result)

    def test_historical_quotes_are_catalogued_only_when_the_current_code_matches(self):
        historical = (
            '代码证据：{"path": "src/node.rs", "quote": "RemoteExecute(input);"}\n'
            '代码证据：{"path": "src/node.rs", "quote": "RemoteExecute(fake);"}\n'
            '代码证据：{"path": "missing.rs", "quote": "RemoteExecute(input);"}\n'
            '代码证据：{"malformed": true}\n'
        )
        def request(settings, prompt, material):
            if "review_id must be" in prompt:
                review_id = re.search(r'review_id must be "([0-9a-f]+)"', prompt).group(1)
                return json.dumps({"review_id": review_id, "complete": True, "analysis": json.loads(EMPTY_AI_REVIEW)})
            catalogue = json.loads(material.split("<untrusted_verified_code_evidence_catalog>\n")[1].split("\n</untrusted_verified_code_evidence_catalog>")[0])
            self.assertEqual(catalogue, {"code-1": {"path": "src/node.rs", "quote": "RemoteExecute(input);"}})
            return self.synthesis_response()
        with patch.object(watch, "call_ai", side_effect=request), redirect_stdout(io.StringIO()):
            result = watch.ask_ai(
                {"diff_chunk_chars": len(NODE_DIFF)}, "o/r", {"tag_name": "v2"}, "v1", NODE_DIFF + DOC_DIFF,
                historical_review=historical,
            )
        self.assertIn("RemoteExecute(input);", result)

    def test_fenced_structured_chunk_preserves_quoted_multiline_code(self):
        quote = 'say("你好");\nnext_call();'
        analysis = code_finding(quote=quote)
        response = "```json\n" + json.dumps({"review_id": "expected", "complete": True, "analysis": analysis}) + "\n```"
        result = watch.validate_chunk_review(response, "expected", {"src/node.rs": '+say("你好");\n+next_call();'})
        self.assertEqual(result["confirmed_findings"][0]["evidence"][0]["quote"], quote)

    def test_single_chunk_repair_keeps_raw_source_and_identifies_bad_quote(self):
        responses = [json.dumps(code_finding(quote="RemoteExecute(fake);")), json.dumps(code_finding())]
        with patch.object(watch, "call_ai", side_effect=responses) as ai, redirect_stdout(io.StringIO()):
            result = watch.ask_ai({}, "o/r", {"tag_name": "v2"}, "v1", NODE_DIFF)
        self.assertIn("RemoteExecute(input);", result)
        self.assertEqual(ai.call_count, 2)
        repair_prompt, repair_material = ai.call_args_list[1].args[1:]
        self.assertIn('path="src/node.rs"', repair_prompt)
        self.assertIn(NODE_DIFF, repair_material)
        self.assertIn("untrusted_previous_response", repair_material)

    def test_final_transport_error_is_not_retried_as_validation_failure(self):
        with patch.object(watch, "call_ai", side_effect=watch.AIReviewError("HTTP 401")) as ai, redirect_stdout(io.StringIO()):
            with self.assertRaises(watch.AIReviewError):
                watch.call_final_ai({}, "prompt", "material", watch.review_code_evidence(NODE_DIFF))
        self.assertEqual(ai.call_count, 1)

    def test_oversized_file_fragments_keep_their_path_for_evidence_validation(self):
        diff = NODE_DIFF + " ordinary_call();\n" * 12
        calls = []
        def request(settings, prompt, material):
            calls.append(material)
            if "review_id must be" not in prompt:
                return self.synthesis_response()
            review_id = re.search(r'review_id must be "([0-9a-f]+)"', prompt).group(1)
            review = code_finding(quote="ordinary_call();") if "ordinary_call();" in material else json.loads(EMPTY_AI_REVIEW)
            return json.dumps({"review_id": review_id, "complete": True, "analysis": review})
        with patch.object(watch, "call_ai", side_effect=request), redirect_stdout(io.StringIO()):
            result = watch.ask_ai({"diff_chunk_chars": len(NODE_DIFF)}, "o/r", {"tag_name": "v2"}, "v1", diff)
        self.assertGreater(len(calls), 2)
        self.assertIn("ordinary_call();", result)

    def test_rust_attributes_and_dereference_expressions_are_code_evidence(self):
        path = "cli/src/commands/start.rs"
        evidence = watch.review_code_evidence(
            f"diff --git a/{path} b/{path}\n"
            f"+++ b/{path}\n@@ -1 +1,3 @@\n"
            "+#[tokio::main]\n+*target_ptr = start_node();\n+unsafe { *target_ptr = start_node(); }\n"
        )
        for quote in ("#[tokio::main]", "*target_ptr = start_node();", "unsafe { *target_ptr = start_node(); }"):
            with self.subTest(quote=quote):
                watch.validate_code_proof({"path": path, "quote": quote}, evidence, "test")

    def test_comment_only_block_quote_is_rejected_but_not_treated_as_rust_code(self):
        quote = "/* explanatory comment\n * still only a comment\n */"
        evidence = watch.review_code_evidence(
            "diff --git a/src/start.rs b/src/start.rs\n+++ b/src/start.rs\n@@ -1 +1,3 @@\n"
            "+/* explanatory comment\n+ * still only a comment\n+ */\n"
        )
        with self.assertRaisesRegex(watch.AIReviewError, "\u4ec5\u4e3a\u6ce8\u91ca"):
            watch.validate_code_proof({"path": "src/start.rs", "quote": quote}, evidence, "test")

    def test_rust_attribute_survives_four_chunk_review_and_cache(self):
        path, quote = "cli/src/commands/start.rs", "#[tokio::main]"
        diff = NODE_DIFF.replace("src/node.rs", path).replace("RemoteExecute(input);", quote)
        chunk_chars = len(diff)
        diff += "".join(DOC_DIFF.replace("notes.md", f"notes-{number}.md") for number in range(3))
        def request(settings, prompt, material):
            if "review_id must be" in prompt:
                review_id = re.search(r'review_id must be "([0-9a-f]+)"', prompt).group(1)
                analysis = code_finding(path, quote) if "Diff chunk: 1/4" in material else json.loads(EMPTY_AI_REVIEW)
                return json.dumps({"review_id": review_id, "complete": True, "analysis": analysis})
            analysis = code_finding(path, quote)
            analysis["confirmed_findings"][0]["evidence"] = [{"evidence_id": "code-1"}]
            return json.dumps(analysis)

        logs = io.StringIO()
        with patch.object(watch, "call_ai", side_effect=request) as ai, redirect_stdout(logs):
            for _ in range(2):
                result = watch.ask_ai(
                    {"diff_chunk_chars": chunk_chars}, "aleo-labs-protocol/snarkOS",
                    {"tag_name": "v4.12.0"}, "v4.11.0", diff,
                )
                self.assertIn(quote, result)
                self.assertIn(path, result)
        self.assertEqual(ai.call_count, 6)
        self.assertEqual(len(list(self.cache.glob("*.json"))), 4)
        self.assertIn("Reusing verified diff chunk 1/4", logs.getvalue())
        self.assertNotIn("Invalid result", logs.getvalue())

    def test_diagnostics_identify_reason_and_position_without_quote_content(self):
        for proof, evidence, reason in (
            ({"path": "missing.rs", "quote": "secret-canary-call();"}, {}, "路径不在"),
            ({"path": "src/node.rs", "quote": "foo();"}, {"src/node.rs": "+foo();"}, "引用太短"),
            ({"path": "src/node.rs", "quote": "// secret-canary"}, {"src/node.rs": "+// secret-canary"}, "仅为注释"),
            ({"path": "src/node.rs", "quote": "secret-canary-call();"}, watch.review_code_evidence(NODE_DIFF), "原文不匹配"),
        ):
            with self.subTest(reason=reason), self.assertRaises(watch.AIReviewError) as error:
                watch.validate_code_proof(proof, evidence, "finding-2 proof-3")
            self.assertIn(reason, str(error.exception))
            self.assertIn("finding-2 proof-3", str(error.exception))
            self.assertNotIn("secret-canary", str(error.exception))
