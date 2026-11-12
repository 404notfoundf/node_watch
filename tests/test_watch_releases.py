import io
import importlib.util
import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "watch_releases.py"
SPEC = importlib.util.spec_from_file_location("watch_releases", SCRIPT)
watch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(watch)


class WatchReleaseTests(unittest.TestCase):
    def test_report_path_cannot_escape_reports_directory(self):
        path = watch.report_path("coin/../x", "owner/repo", "v1/../2")
        self.assertEqual(path, watch.REPORTS / "coin%2F..%2Fx" / "owner--repo" / "v1%2F..%2F2.md")

    def test_release_order_starts_at_configured_release(self):
        original = watch.github_json
        pages = [
            [{"tag_name": "v3"}, {"tag_name": "v2"}],
            [{"tag_name": "v1"}],
            [],
        ]
        watch.github_json = lambda _: pages.pop(0)
        try:
            self.assertEqual([item["tag_name"] for item in watch.releases_from_start("o/r", "v2")], ["v2", "v3"])
        finally:
            watch.github_json = original

    def test_ai_retries_rate_limit_then_succeeds(self):
        calls = 0

        def urlopen(request, timeout):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise urllib.error.HTTPError(request.full_url, 429, "Too Many Requests", None, None)
            return io.BytesIO(json.dumps({"choices": [{"message": {"content": "analysis"}}]}).encode())

        with patch.dict(os.environ, {"AI_API_KEY": "test-key"}), \
                patch.object(watch.urllib.request, "urlopen", side_effect=urlopen), \
                patch.object(watch.time, "sleep") as sleep:
            result = watch.ask_ai(
                {"api_url": "https://ai.example/v1", "model": "test"},
                "owner/repo",
                {"tag_name": "v1"},
                "v0",
                "diff",
            )

        self.assertEqual(result, "analysis")
        self.assertEqual(calls, 2)
        sleep.assert_called_once_with(5)

    def test_report_groups_by_coin_and_numbers_items_per_release(self):
        original_reports = watch.REPORTS
        with tempfile.TemporaryDirectory() as temp_dir:
            watch.REPORTS = Path(temp_dir)
            try:
                def entry(coin, repo, tag, published_at):
                    release = {
                        "tag_name": tag,
                        "published_at": published_at,
                        "html_url": f"https://github.com/{repo}/releases/tag/{tag}",
                        "body": f"Notes for {tag}",
                    }
                    diff = "\n".join([
                        "diff --git a/src/one.rs b/src/one.rs",
                        "+change",
                        "diff --git a/src/two.rs b/src/two.rs",
                        "+change",
                    ])
                    analysis = f"风险级别：P1\n1. Finding for {tag}"
                    return watch.format_release(coin, repo, release, f"{tag}-previous", diff, analysis)

                watch.append_report_batch({
                    "A 币种": {"a/node": [entry("A 币种", "a/node", "v1", "2026-11-10T00:00:00Z"), entry("A 币种", "a/node", "v2", "2026-11-11T00:00:00Z")]},
                    "B 币种": {"b/node": [entry("B 币种", "b/node", "v3", "2026-11-10T12:00:00Z")]},
                })

                report = (watch.REPORTS / "index.md").read_text(encoding="utf-8")
                self.assertLess(report.index("### A 币种"), report.index("### B 币种"))
                self.assertLess(report.index("#### v1"), report.index("#### v2"))
                self.assertNotIn("#### a/node", report)
                self.assertEqual(report.count("- 仓库：[`a/node`]"), 2)
                self.assertEqual(report.count("1. `src/one.rs`"), 3)
                self.assertEqual(report.count("2. `src/two.rs`"), 3)
                self.assertEqual(report.count("1. Finding for v"), 3)
                self.assertIn("restart at 1 for every new release", watch.SYSTEM_PROMPT)
                self.assertEqual(watch.reported_releases(), {
                    ("A 币种", "a/node", "v1"),
                    ("A 币种", "a/node", "v2"),
                    ("B 币种", "b/node", "v3"),
                })
            finally:
                watch.REPORTS = original_reports


if __name__ == "__main__":
    unittest.main()
