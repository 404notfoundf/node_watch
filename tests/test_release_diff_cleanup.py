import errno
import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from test_watch_releases import EMPTY_AI_REVIEW, watch


DIFF = "diff --git a/src/node.rs b/src/node.rs\n+++ b/src/node.rs\n+apply_fix();\n"
NAME_STATUS = "M\0src/node.rs\0"


class ReleaseDiffCleanupTests(unittest.TestCase):
    def setUp(self):
        fixture = tempfile.TemporaryDirectory(prefix="release-watch-test-")
        self.addCleanup(fixture.cleanup)
        self.root = Path(fixture.name)
        self.directory = MagicMock()
        self.directory.name = str(self.root / "checkout")
        self.directory.cleanup.return_value = None
        self.directory.__enter__.return_value = self.directory.name
        self.directory.__exit__.side_effect = lambda *args: self.directory.cleanup()
        self.temp = self.enterContext(patch.object(watch.tempfile, "TemporaryDirectory", return_value=self.directory))
        self.git = self.enterContext(patch.object(watch, "run", side_effect=self.git_command))
        self.sleep = self.enterContext(patch.object(watch.time, "sleep"))
        self.stdout, self.stderr = io.StringIO(), io.StringIO()
        self.enterContext(redirect_stdout(self.stdout))
        self.enterContext(redirect_stderr(self.stderr))

    def git_command(self, *args, **kwargs):
        if "--name-status" in args:
            return NAME_STATUS
        return DIFF if args[1] == "diff" else ""

    def review_diff(self):
        return watch.release_diff("aleo-labs-protocol/snarkOS", "v4.12.1", "v4.13.1")

    def cleanup_error(self):
        return OSError(errno.ENOTEMPTY, "Directory not empty", str(self.root / "checkout/.git/objects"))

    def test_fetch_disables_automatic_maintenance_and_cleans_checkout(self):
        self.assertEqual(self.review_diff(), (DIFF, {"src/node.rs"}))
        fetches = [item for item in self.git.call_args_list if item.args[1] == "fetch"]
        self.assertEqual(len(fetches), 2)
        for item in fetches:
            self.assertIn("--no-auto-maintenance", item.args)
        self.directory.cleanup.assert_called_once_with()
        self.sleep.assert_not_called()

    def test_cleanup_retries_without_repeating_git_or_losing_diff(self):
        self.directory.cleanup.side_effect = [self.cleanup_error(), self.cleanup_error(), None]
        self.assertEqual(self.review_diff(), (DIFF, {"src/node.rs"}))
        self.assertEqual(self.directory.cleanup.call_count, 3)
        self.assertEqual(self.sleep.call_args_list, [call(0.2), call(0.5)])
        self.assertEqual(self.git.call_count, 6)

    def test_persistent_cleanup_failure_is_only_a_warning(self):
        self.directory.cleanup.side_effect = self.cleanup_error()
        self.assertEqual(self.review_diff(), (DIFF, {"src/node.rs"}))
        self.assertEqual(self.directory.cleanup.call_count, 4)
        self.assertEqual(self.sleep.call_args_list, [call(0.2), call(0.5), call(1)])
        self.assertEqual(self.git.call_count, 6)
        self.assertIn("Warning: temporary Git checkout cleanup failed", self.stdout.getvalue())
        self.assertIn(self.directory.name, self.stdout.getvalue())
        self.assertNotIn("Git diff failed", self.stdout.getvalue())

    def test_cleanup_failure_does_not_replace_original_fetch_error(self):
        original = RuntimeError("fatal: original fetch failure")
        def fail_fetch(*args, **kwargs):
            if args[1] == "fetch":
                raise original
            return self.git_command(*args, **kwargs)
        self.git.side_effect = fail_fetch
        self.directory.cleanup.side_effect = self.cleanup_error()
        with self.assertRaises(RuntimeError) as caught:
            self.review_diff()
        self.assertIs(caught.exception, original)
        self.assertEqual(self.directory.cleanup.call_count, 4)
        self.assertIn("during fetch v4.12.1", self.stdout.getvalue())
        self.assertIn("Traceback", self.stderr.getvalue())
        self.assertIn("fatal: original fetch failure", self.stderr.getvalue())

    def test_diff_failure_logs_context_and_still_cleans_checkout(self):
        original = RuntimeError("fatal: original diff failure")
        def fail_diff(*args, **kwargs):
            if args[1] == "diff":
                raise original
            return self.git_command(*args, **kwargs)
        self.git.side_effect = fail_diff
        with self.assertRaises(RuntimeError) as caught:
            self.review_diff()
        self.assertIs(caught.exception, original)
        self.directory.cleanup.assert_called_once_with()
        self.assertIn("aleo-labs-protocol/snarkOS v4.12.1 -> v4.13.1 during diff", self.stdout.getvalue())
        self.assertIn("fatal: original diff failure", self.stderr.getvalue())

    def test_path_listing_failure_cannot_return_partial_diff(self):
        original = RuntimeError("fatal: path listing failure")
        def fail_listing(*args, **kwargs):
            if "--name-status" in args:
                raise original
            return self.git_command(*args, **kwargs)
        self.git.side_effect = fail_listing
        with self.assertRaises(RuntimeError) as caught:
            self.review_diff()
        self.assertIs(caught.exception, original)
        self.directory.cleanup.assert_called_once_with()
        self.assertIn("during changed-path listing", self.stdout.getvalue())

    def test_missing_baseline_does_not_create_or_clean_checkout(self):
        self.assertEqual(watch.release_diff("org/repo", None, "v1")[1], set())
        self.temp.assert_not_called()
        self.git.assert_not_called()
        self.directory.cleanup.assert_not_called()
        self.sleep.assert_not_called()

    def test_main_keeps_successful_coins_and_retries_only_failed_git_review(self):
        config = {
            "review": {"mode": "full", "max_releases_per_run": 4},
            "coins": {coin: {"repo": f"{coin}/repo", "running_version": "v0"} for coin in ("aleo", "alph")},
        }
        completed = set()
        current_repo = ""
        fail_aleo = True
        def commands(*args, **kwargs):
            nonlocal current_repo
            if args[1] == "remote":
                current_repo = args[-1]
            if args[1] == "fetch" and "aleo/repo" in current_repo and fail_aleo:
                raise RuntimeError("fatal: Aleo fetch failed")
            return self.git_command(*args, **kwargs)
        original_record = watch.record_review_candidate
        def record(candidate, analysis, entries, processed):
            original_record(candidate, analysis, entries, processed)
            completed.add((candidate["coin"], candidate["repo"], candidate["release"]["tag_name"]))
        self.git.side_effect = commands
        self.directory.cleanup.side_effect = self.cleanup_error()
        self.enterContext(patch.object(watch, "ROOT", self.root))
        self.enterContext(patch.object(watch, "REPORTS", self.root / "reports"))
        self.enterContext(patch.object(watch, "REVIEW_CACHE", self.root / "cache"))
        self.enterContext(patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}))
        self.enterContext(patch.object(watch, "load_config", return_value=config))
        self.enterContext(patch.object(watch, "should_read_github_issue_history", return_value=False))
        self.enterContext(patch.object(watch, "reported_releases", side_effect=lambda *args: set(completed)))
        self.enterContext(patch.object(watch, "release_window_after_running_version", return_value=([{"tag_name": "v1"}], "v0")))
        self.enterContext(patch.object(watch, "historical_prerelease_reviews", return_value=""))
        self.enterContext(patch.object(watch, "linked_release_reference_evidence", return_value=""))
        ai = self.enterContext(patch.object(watch, "ask_ai", return_value=watch.final_analysis_from_json(EMPTY_AI_REVIEW)))
        self.enterContext(patch.object(watch, "record_review_candidate", side_effect=record))
        output = self.enterContext(patch.object(watch, "set_workflow_output"))
        publish = self.enterContext(patch.object(watch, "prepare_batch_issue"))
        watch.main()
        self.assertEqual(completed, {("alph", "alph/repo", "v1")})
        self.assertEqual(dict(item.args for item in output.call_args_list)["failure_count"], "1")
        self.assertEqual(set(publish.call_args.args[0]), {"alph"})
        self.assertEqual(ai.call_count, 1)
        output.reset_mock()
        ai.reset_mock()
        fail_aleo = False
        watch.main()
        self.assertEqual(completed, {("aleo", "aleo/repo", "v1"), ("alph", "alph/repo", "v1")})
        self.assertEqual(dict(item.args for item in output.call_args_list)["failure_count"], "0")
        self.assertEqual(ai.call_count, 1)
        self.assertEqual(set(publish.call_args.args[0]), {"aleo"})


if __name__ == "__main__":
    unittest.main()
