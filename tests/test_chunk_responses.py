import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from test_watch_releases import EMPTY_AI_REVIEW, watch


def completed_response(prompt):
    review_id = prompt.split('review_id must be "')[1].split('"')[0]
    return json.dumps({"review_id": review_id, "complete": True, "analysis": json.loads(EMPTY_AI_REVIEW)})


class ChunkResponseTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.cache = Path(directory.name)
        self.enterContext(patch.object(watch, "REVIEW_CACHE", self.cache))
        self.enterContext(patch.object(watch, "split_diff_with_context", return_value=[("first", "src/a.rs"), ("second", "src/b.rs")]))
        self.synthesize = self.enterContext(patch.object(watch, "call_final_ai", return_value="final result"))

    def review(self):
        return watch.ask_ai({}, "aleo-labs-protocol/snarkOS", {"tag_name": "v4.13.1"}, "v4.12.1", "diff")

    def test_complete_json_fences_are_accepted(self):
        analysis = json.loads(EMPTY_AI_REVIEW)
        response = json.dumps({"review_id": "expected", "complete": True, "analysis": analysis})
        for wrapped in (response, "```json\n" + response + "\n```", "```\n" + response + "\n```", " \n```JSON\r\n" + response + "\r\n```\n "):
            with self.subTest(wrapped=wrapped):
                self.assertEqual(watch.validate_chunk_review(wrapped, "expected"), analysis)

    def test_prose_multiple_objects_and_truncated_output_remain_rejected(self):
        response = json.dumps({"review_id": "expected", "complete": True, "analysis": json.loads(EMPTY_AI_REVIEW)})
        invalid = (
            "Here is the result:\n" + response,
            response + "\nExtra explanation.",
            response + "\n" + response,
            "```json\n" + response,
            "```json\n" + response[:-1] + "\n```",
            "```json\n" + response + "\n```\nExtra explanation.",
            "```javascript\n" + response + "\n```",
        )
        for output in invalid:
            with self.subTest(output=output), self.assertRaises(watch.AIReviewError):
                watch.validate_chunk_review(output, "expected")

    def test_fences_do_not_bypass_completion_or_schema_validation(self):
        for update in ({"review_id": "wrong"}, {"complete": False}, {"complete": 1}, {"analysis": " "}, {"analysis": []}, {"extra": "field"}):
            data = {"review_id": "expected", "complete": True, "analysis": json.loads(EMPTY_AI_REVIEW), **update}
            with self.subTest(update=update), self.assertRaises(watch.AIReviewError):
                watch.validate_chunk_review("```json\n" + json.dumps(data) + "\n```", "expected")

    def test_parse_error_reports_position_without_echoing_response_content(self):
        response = json.dumps({"review_id": "expected", "complete": True, "analysis": "secret-response-canary"})[:-1]
        with self.assertRaises(watch.AIReviewError) as error:
            watch.validate_chunk_review(response, "expected")
        message = str(error.exception)
        self.assertIn("行", message)
        self.assertIn("列", message)
        self.assertIn("响应长度", message)
        self.assertNotIn("secret-response-canary", message)

    def test_failed_second_chunk_receives_a_corrective_prompt_and_completes(self):
        prompts = []
        def request(settings, prompt, material):
            prompts.append(prompt)
            response = completed_response(prompt)
            return response[:-1] if len(prompts) == 2 else response
        output = io.StringIO()
        with patch.object(watch, "call_ai", side_effect=request), redirect_stdout(output):
            self.assertEqual(self.review(), "final result")
        self.assertEqual(len(prompts), 3)
        self.assertNotEqual(prompts[1], prompts[2])
        self.assertIn("prior response failed validation", prompts[2])
        self.assertIn("attempt 2/2", output.getvalue())
        self.assertIn("Completed verified diff chunk 2/2", output.getvalue())
        self.assertEqual(len(list(self.cache.glob("*.json"))), 2)
        self.synthesize.assert_called_once()

    def test_second_chunk_failure_retains_first_chunk_for_next_run(self):
        def fail_second(settings, prompt, material):
            response = completed_response(prompt)
            return response if "Diff chunk: 1/2" in material else response[:-1]
        with patch.object(watch, "call_ai", side_effect=fail_second) as request, redirect_stdout(io.StringIO()):
            with self.assertRaises(watch.AIReviewError) as error:
                self.review()
        self.assertIn("2/2", str(error.exception))
        self.assertEqual(request.call_count, 3)
        self.assertEqual(len(list(self.cache.glob("*.json"))), 1)
        self.synthesize.assert_not_called()
        output = io.StringIO()
        with patch.object(watch, "call_ai", side_effect=lambda settings, prompt, material: completed_response(prompt)) as request, redirect_stdout(output):
            self.assertEqual(self.review(), "final result")
        self.assertEqual(request.call_count, 1)
        self.assertIn("Reusing verified diff chunk 1/2 cache", output.getvalue())
        self.assertEqual(len(list(self.cache.glob("*.json"))), 2)

    def test_verified_fenced_responses_are_reusable_from_cache(self):
        with patch.object(watch, "call_ai", side_effect=lambda settings, prompt, material: "```json\n" + completed_response(prompt) + "\n```") as request, redirect_stdout(io.StringIO()):
            self.assertEqual(self.review(), "final result")
            self.assertEqual(self.review(), "final result")
        self.assertEqual(request.call_count, 2)
        self.assertEqual(self.synthesize.call_count, 2)

    def test_transport_failure_is_not_retried_as_a_json_format_error(self):
        output = io.StringIO()
        with patch.object(watch, "call_ai", side_effect=watch.AIReviewError("HTTP 401")) as request, redirect_stdout(output):
            with self.assertRaises(watch.AIReviewError) as error:
                self.review()
        self.assertEqual(request.call_count, 1)
        self.assertIn("1/2", str(error.exception))
        self.assertIn("HTTP 401", output.getvalue())
        self.assertEqual(list(self.cache.glob("*.json")), [])
        self.synthesize.assert_not_called()
