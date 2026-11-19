import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_watch_releases import EMPTY_AI_REVIEW, watch


class ReleaseSchedulerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.config = {
            "review": {"max_releases_per_run": 4},
            "coins": {coin: {"repo": f"{coin}/repo", "running_version": "v0", "network": "mainnet", "include_prereleases": False} for coin in ("A", "B", "C")},
        }
        self.releases = {"A": [f"v{n}" for n in range(1, 9)], "B": ["v1"], "C": ["v1", "v2"]}
        self.processed = set()
        self.queries, self.attempts, self.completed = [], [], []
        self.query_failures, self.diff_failures = set(), set()
        self.real_record = watch.record_review_candidate
        self.real_window = watch.release_window_after_running_version
        for name, value in (("ROOT", self.root), ("REPORTS", self.root / "reports"), ("REVIEW_CACHE", self.root / "cache")):
            self.enterContext(patch.object(watch, name, value))
        self.enterContext(patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}))
        self.enterContext(patch.object(watch, "load_config", return_value=self.config))
        self.enterContext(patch.object(watch, "should_read_github_issue_history", return_value=False))
        self.enterContext(patch.object(watch, "reported_releases", side_effect=lambda *args: set(self.processed)))
        self.discovery = self.enterContext(patch.object(watch, "release_window_after_running_version", side_effect=self.discover))
        self.enterContext(patch.object(watch, "release_diff", side_effect=self.diff))
        self.enterContext(patch.object(watch, "historical_prerelease_reviews", return_value=""))
        self.enterContext(patch.object(watch, "linked_release_reference_evidence", return_value=""))
        self.enterContext(patch.object(watch, "ask_ai_fast_batch", return_value=None))
        self.ai = self.enterContext(patch.object(watch, "ask_ai", return_value=watch.final_analysis_from_json(EMPTY_AI_REVIEW)))
        self.enterContext(patch.object(watch, "record_review_candidate", side_effect=self.record))
        self.enterContext(patch.object(watch, "set_workflow_output"))
        self.enterContext(patch.object(watch, "prepare_batch_issue"))

    def discover(self, repo, running_version, include_prereleases):
        coin = repo.split("/")[0]
        self.queries.append(coin)
        if coin in self.query_failures:
            raise ValueError("Release query failed")
        return [{"tag_name": tag, "body": "Routine release"} for tag in self.releases[coin]], running_version

    def diff(self, repo, previous, tag):
        coin = repo.split("/")[0]
        self.attempts.append((coin, previous, tag, tuple(self.queries)))
        if coin in self.diff_failures:
            raise ValueError("Diff failed")
        return "diff --git a/docs/readme.md b/docs/readme.md\n+++ b/docs/readme.md\n+Routine documentation\n", {"docs/readme.md"}

    def record(self, candidate, analysis, entries, processed):
        self.real_record(candidate, analysis, entries, processed)
        key = (candidate["coin"], candidate["repo"], candidate["release"]["tag_name"])
        self.processed.add(key)
        self.completed.append((key[0], key[2]))

    def run_round(self):
        self.queries.clear()
        self.attempts.clear()
        self.completed.clear()
        watch.main()

    def waiting_for(self, coin):
        waits = watch.load_scheduler_waits()
        return next((count for key, count in waits.items() if json.loads(key)[0] == coin), 0)

    def seed_waits(self, **counts):
        waits = {json.dumps([coin, f"{coin}/repo", "v0", "mainnet", False], separators=(",", ":")): count for coin, count in counts.items()}
        watch.save_chunk_review("scheduler-v1", json.dumps(waits))

    def test_short_queues_finish_before_large_queue(self):
        self.run_round()
        self.assertEqual(self.queries, ["A", "B", "C"])
        self.assertEqual(self.completed, [("B", "v1"), ("C", "v1"), ("C", "v2"), ("A", "v1")])
        self.assertTrue(all(queried == ("A", "B", "C") for _, _, _, queried in self.attempts))
        self.run_round()
        self.assertEqual(self.completed, [("A", f"v{n}") for n in range(2, 6)])
        self.assertEqual(len(self.attempts), 4)

    def test_processed_releases_do_not_inflate_queue_size_or_break_baseline(self):
        self.processed.update(("A", "A/repo", f"v{n}") for n in range(1, 8))
        self.run_round()
        self.assertEqual(self.completed[0], ("A", "v8"))
        self.assertEqual(self.attempts[0][1], "v7")
        self.assertEqual(len(self.attempts), 4)

    def test_waiting_coin_gets_one_protected_slot_after_three_rounds(self):
        self.releases["B"], self.releases["C"] = [], []
        for number in range(1, 5):
            self.releases["B"].append(f"v{number}")
            self.releases["C"].extend(f"v{n}" for n in range(number * 3 - 2, number * 3 + 1))
            self.run_round()
            if number <= 3:
                self.assertNotIn("A", [coin for coin, _ in self.completed])
                self.assertEqual(self.waiting_for("A"), number)
            else:
                self.assertEqual(self.completed[0], ("A", "v1"))
                self.assertEqual(sum(coin == "A" for coin, _ in self.completed), 1)
                self.assertEqual(self.waiting_for("A"), 0)
            self.assertEqual(len(self.attempts), 4)

    def test_real_release_filter_excludes_test_tags_and_github_prereleases(self):
        self.releases["A"] = ["v1-test", "v2-testnet", "v3-rc.1", "v4-pre.1", "v5-alpha.1", "v6", "v9"]
        def api(path):
            if path.endswith("page=2"):
                return []
            coin = path.removeprefix("repos/").split("/")[0]
            return [{"tag_name": tag, "body": "Routine release", "prerelease": tag == "v6"} for tag in reversed(self.releases[coin])] + [{"tag_name": "v0"}]
        def discover(repo, version, include):
            self.queries.append(repo.split("/")[0])
            return self.real_window(repo, version, include)
        self.discovery.side_effect = discover
        with patch.object(watch, "github_json", side_effect=api):
            self.run_round()
        self.assertEqual(self.completed, [("A", "v9"), ("B", "v1"), ("C", "v1"), ("C", "v2")])
        self.assertEqual(self.attempts[0][1], "v0")

    def test_enabled_prereleases_still_count_toward_limit(self):
        self.config["coins"]["A"]["include_prereleases"] = True
        self.releases = {"A": ["v1-test", "v2-rc.1", "v3-pre.1", "v4-testnet", "v5"], "B": [], "C": []}
        self.run_round()
        self.assertEqual(len(self.attempts), 4)
        self.assertEqual([tag for _, tag in self.completed], self.releases["A"][:4])

    def test_failed_coin_does_not_block_others_or_reserve_unused_slots(self):
        self.diff_failures.add("B")
        with self.assertRaises(RuntimeError):
            self.run_round()
        self.assertEqual(self.queries, ["A", "B", "C"])
        self.assertEqual(self.completed, [("C", "v1"), ("C", "v2"), ("A", "v1")])
        self.assertNotIn(("B", "B/repo", "v1"), self.processed)
        self.assertEqual(len(self.attempts), 4)
        self.assertEqual(self.waiting_for("B"), 0)

    def test_failed_query_does_not_block_discovery_or_reset_unknown_wait(self):
        self.seed_waits(A=2)
        self.query_failures.add("A")
        with self.assertRaises(RuntimeError):
            self.run_round()
        self.assertEqual(self.queries, ["A", "B", "C"])
        self.assertEqual(self.completed, [("B", "v1"), ("C", "v1"), ("C", "v2")])
        self.assertEqual(self.waiting_for("A"), 2)

    def test_multiple_protected_coins_get_oldest_first_without_exceeding_limit(self):
        self.seed_waits(A=5, B=3, C=4)
        self.config["review"]["max_releases_per_run"] = 2
        self.run_round()
        self.assertEqual(self.completed, [("A", "v1"), ("C", "v1")])
        self.assertEqual(len(self.attempts), 2)
        self.assertEqual(self.waiting_for("B"), 4)

    def test_empty_queue_resets_wait_and_running_version_change_starts_fresh(self):
        self.seed_waits(A=3, B=3)
        self.config["coins"]["A"]["running_version"] = "v1"
        self.releases["B"] = []
        self.run_round()
        self.assertEqual(self.completed[0], ("C", "v1"))
        self.assertEqual(self.waiting_for("B"), 0)
        self.assertTrue(all(json.loads(key)[2] != "v0" for key in watch.load_scheduler_waits() if json.loads(key)[0] == "A"))

    def test_invalid_wait_cache_is_ignored(self):
        for record in ([1], {"A": True}, {"A": -1}, {"A": "3"}):
            with self.subTest(record=record):
                watch.save_chunk_review("scheduler-v1", json.dumps(record))
                self.assertEqual(watch.load_scheduler_waits(), {})

    def test_failed_state_save_does_not_discard_completed_report(self):
        with patch.object(watch, "save_chunk_review", side_effect=OSError("cache unavailable")):
            with self.assertRaises(RuntimeError):
                self.run_round()
        self.assertEqual(len(self.completed), 4)
        self.assertEqual(len(list((self.root / "reports").glob("*.md"))), 1)

    def test_waits_survive_rounds_with_no_successful_report(self):
        for coin in ("B", "C", "D", "E"):
            self.config["coins"][coin] = {"repo": f"{coin}/repo", "running_version": "v0", "network": "mainnet", "include_prereleases": False}
            self.releases[coin] = ["v1"]
        self.diff_failures.update(("B", "C", "D", "E"))
        for number in range(1, 4):
            with self.assertRaises(RuntimeError):
                self.run_round()
            self.assertEqual(self.completed, [])
            self.assertEqual(self.waiting_for("A"), number)
            self.assertEqual(len(self.attempts), 4)
        self.assertEqual(list((self.root / "reports").glob("*.md")), [])
        with self.assertRaises(RuntimeError):
            self.run_round()
        self.assertEqual(self.completed, [("A", "v1")])
        self.assertEqual(self.waiting_for("A"), 0)
        self.assertEqual(len(self.attempts), 4)

    def test_failed_protected_coin_stops_its_queue_and_other_coins_continue(self):
        self.seed_waits(A=3)
        self.diff_failures.add("A")
        with self.assertRaises(RuntimeError):
            self.run_round()
        self.assertEqual([coin for coin, _, _, _ in self.attempts], ["A", "B", "C", "C"])
        self.assertEqual(self.completed, [("B", "v1"), ("C", "v1"), ("C", "v2")])
        self.assertEqual(self.waiting_for("A"), 0)

    def test_fast_batch_failure_is_isolated_to_its_coin(self):
        self.releases["B"], self.releases["C"] = ["v1", "v2"], ["v1"]
        def batch(settings, candidates):
            if candidates[0]["coin"] == "B":
                raise watch.AIReviewError("batch failed")
            return None
        with patch.object(watch, "ask_ai_fast_batch", side_effect=batch):
            with self.assertRaises(RuntimeError):
                self.run_round()
        self.assertEqual(self.completed, [("C", "v1"), ("A", "v1")])
        self.assertEqual(len(self.attempts), 4)
        self.assertFalse(any(coin == "B" for coin, _, _ in self.processed))

    def test_comparison_baseline_survives_gaps_in_processed_history(self):
        self.releases = {"A": ["v1", "v2", "v3", "v4"], "B": [], "C": []}
        self.processed.update({("A", "A/repo", "v1"), ("A", "A/repo", "v3")})
        self.run_round()
        self.assertEqual([(previous, tag) for _, previous, tag, _ in self.attempts], [("v1", "v2"), ("v3", "v4")])
