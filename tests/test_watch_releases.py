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

    def test_ai_error_after_retries_raises_instead_of_returning_report_text(self):
        def http_error(request, timeout):
            raise urllib.error.HTTPError(request.full_url, 503, "Unavailable", None, None)

        with patch.dict(os.environ, {"AI_API_KEY": "test-key"}), \
                patch.object(watch.urllib.request, "urlopen", side_effect=http_error) as urlopen, \
                patch.object(watch.time, "sleep") as sleep:
            with self.assertRaises(watch.AIReviewError):
                watch.ask_ai(
                    {"api_url": "https://ai.example/v1", "model": "test"},
                    "owner/repo", {"tag_name": "v1"}, "v0", "diff",
                )
        self.assertEqual(urlopen.call_count, 4)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [5, 10, 20])

    def test_ai_receives_explicit_truncation_status(self):
        captured = {}

        def urlopen(request, timeout):
            captured.update(json.loads(request.data.decode("utf-8")))
            return io.BytesIO(json.dumps({"choices": [{"message": {"content": "analysis"}}]}).encode())

        with patch.dict(os.environ, {"AI_API_KEY": "test-key"}), \
                patch.object(watch, "MAX_DIFF_CHARS", 4), \
                patch.object(watch.urllib.request, "urlopen", side_effect=urlopen):
            watch.ask_ai(
                {"api_url": "https://ai.example/v1", "model": "test"},
                "owner/repo", {"tag_name": "v1"}, "v0", "abcdef",
            )
        material = captured["messages"][1]["content"]
        self.assertIn("TRUNCATED: 2 characters were omitted", material)
        self.assertIn("<untrusted_code_diff>\nabcd\n</untrusted_code_diff>", material)
        self.assertNotIn("abcdef", material)

    def test_highlight_summary_marks_major_changes(self):
        analysis = (
            "重点标记：破坏性变更=待验证；硬分叉/共识=已确认；兼容性=待验证；"
            "内存问题=修复；安全=风险；稳定性/数据=无"
        )
        summary = watch.highlight_summary(analysis)
        self.assertIn("破坏性变更**（待验证）", summary)
        self.assertIn("硬分叉/共识**（已确认）", summary)
        self.assertIn("兼容性**（待验证）", summary)
        self.assertIn("✅ **内存问题修复**", summary)
        self.assertIn("安全**（风险）", summary)
        self.assertNotIn("稳定性/数据", summary)
        self.assertIn("重点标记", watch.SYSTEM_PROMPT)
        self.assertIn("memory leaks", watch.SYSTEM_PROMPT)
        _, report = watch.format_release(
            "coin", "owner/repo", {"tag_name": "v1"}, "v0",
            f"风险级别：P1\n{analysis}", 9,
        )
        self.assertIn(f"- **重点标记：** {summary}", report)
        self.assertIn("代码差异截断（省略 9 个字符）", report)

    def test_issue_summary_lists_all_coins_releases_and_deduplicates(self):
        def entry(coin, repo, tag):
            analysis = (
                "风险级别：P1\n重点标记：破坏性变更=无；硬分叉/共识=无；兼容性=无；"
                "内存问题=修复；安全=无；稳定性/数据=无\n1. Finding"
            )
            return watch.format_release(coin, repo, {"tag_name": tag}, "previous", analysis)

        entries = {
            "tari": {"tari-project/tari": [entry("tari", "tari-project/tari", "v6.2.0")]},
            "coin-b": {"org/coin-b": [entry("coin-b", "org/coin-b", "v1"), entry("coin-b", "org/coin-b", "v2")]},
        }
        with patch.dict(os.environ, {
            "GITHUB_REPOSITORY": "owner/watch",
            "GITHUB_REPOSITORY_OWNER": "owner",
            "GITHUB_SERVER_URL": "https://github.com",
            "GITHUB_RUN_ID": "12345",
            "NOTIFY_LOGINS": "",
        }):
            body = watch.issue_body(entries)
            title = watch.issue_title(entries)

        self.assertIn("3 个新版本", body)
        self.assertIn("2 个币种、2 个仓库", body)
        self.assertIn("**tari**", body)
        self.assertIn("**coin-b**", body)
        self.assertIn("tari-project/tari", body)
        self.assertIn("`v6.2.0`", body)
        self.assertIn("`v1`", body)
        self.assertIn("`v2`", body)
        self.assertLess(body.index("**coin-b**"), body.index("**tari**"))
        self.assertIn("内存问题修复", body)
        self.assertNotIn("1. Finding", body)
        self.assertIn("/actions/runs/12345", body)
        self.assertIn("@owner", body)
        self.assertRegex(body, r"(?m)^<!-- watch-release-keys: [A-Za-z0-9_-]+ -->$")
        self.assertNotIn("reports/", body)
        self.assertIn("upstream-release-report", body)

    def test_issue_markers_are_the_persistent_release_deduplication_state(self):
        releases = [("tari", "tari-project/tari", "v6.4.0")]
        encoded = watch.base64.urlsafe_b64encode(json.dumps(releases).encode()).decode().rstrip("=")
        issues = [
            {"author": {"login": "github-actions[bot]"}, "body": f"<!-- watch-release-keys: {encoded} -->"},
            {"author": {"login": "someone-else"}, "body": f"<!-- watch-release-keys: {encoded} -->"},
        ]
        original_reports = watch.REPORTS
        with tempfile.TemporaryDirectory() as temp_dir:
            watch.REPORTS = Path(temp_dir)
            try:
                self.assertEqual(watch.reported_releases(issues), {releases[0]})
            finally:
                watch.REPORTS = original_reports

    def test_prepare_issue_writes_summary_for_the_post_artifact_workflow_step(self):
        entry = watch.format_release(
            "tari", "tari-project/tari", {"tag_name": "v6.4.0"}, "v6.3.0",
            "风险级别：P1\n重点标记：破坏性变更=无；硬分叉/共识=无；兼容性=无；内存问题=无；安全=无；稳定性/数据=无",
        )
        entries = {"tari": {"tari-project/tari": [entry]}}
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "github-output.txt"
            with patch.dict(os.environ, {
                "GITHUB_ACTIONS": "true",
                "RUNNER_TEMP": temp_dir,
                "GITHUB_OUTPUT": str(output),
                "GITHUB_REPOSITORY": "owner/watch",
                "GITHUB_RUN_ID": "12345",
                "NOTIFY_LOGINS": "",
            }):
                watch.prepare_batch_issue(entries)
            values = dict(line.split("=", 1) for line in output.read_text(encoding="utf-8").splitlines())
            self.assertEqual(values["issue_title"], watch.issue_title(entries))
            self.assertIn("watch-release-keys", Path(values["issue_body_path"]).read_text(encoding="utf-8"))

    def test_workflow_uploads_report_before_issue_and_does_not_commit_reports(self):
        workflow = watch.yaml.safe_load((SCRIPT.parents[1] / "workflows" / "watch-releases.yml").read_text(encoding="utf-8"))
        steps = workflow["jobs"]["watch"]["steps"]
        names = [step.get("name", "") for step in steps]
        self.assertNotIn("Commit reports", names)
        self.assertLess(names.index("Upload full report"), names.index("Create release summary Issue"))
        self.assertEqual(workflow["permissions"]["contents"], "read")
        self.assertEqual(workflow["permissions"]["issues"], "write")

    def test_notify_logins_uses_configured_users_or_owner_fallback(self):
        with patch.dict(os.environ, {"NOTIFY_LOGINS": "alice, bob alice", "GITHUB_REPOSITORY_OWNER": "owner"}):
            self.assertEqual(watch.notify_logins(), ["alice", "bob"])
        with patch.dict(os.environ, {"NOTIFY_LOGINS": "", "GITHUB_REPOSITORY_OWNER": "owner"}):
            self.assertEqual(watch.notify_logins(), ["owner"])

    def test_failed_ai_review_is_not_recorded_as_processed(self):
        original_reports = watch.REPORTS
        with tempfile.TemporaryDirectory() as temp_dir:
            watch.REPORTS = Path(temp_dir)
            try:
                with patch.dict(os.environ, {"GITHUB_ACTIONS": "", "GITHUB_OUTPUT": ""}), \
                        patch.object(watch, "load_config", return_value={
                            "coins": {"tari": {"repo": "tari-project/tari", "from_release": "v2"}},
                        }), \
                        patch.object(watch, "release_window_from_start", return_value=([{"tag_name": "v2"}], "v1")), \
                        patch.object(watch, "release_diff", return_value="diff"), \
                        patch.object(watch, "ask_ai", side_effect=watch.AIReviewError("HTTP 503")), \
                        patch("builtins.print"):
                    with self.assertRaisesRegex(RuntimeError, "HTTP 503"):
                        watch.main()
                self.assertEqual(watch.reported_releases(), set())
                self.assertEqual([path for path in watch.REPORTS.glob("*.md") if path.name != "index.md"], [])
                output = Path(temp_dir) / "github-output.txt"
                with patch.dict(os.environ, {
                    "GITHUB_ACTIONS": "true",
                    "GITHUB_REPOSITORY": "owner/watch",
                    "GITHUB_OUTPUT": str(output),
                }), \
                        patch.object(watch, "load_config", return_value={
                            "coins": {"tari": {"repo": "tari-project/tari", "from_release": "v2"}},
                        }), \
                        patch.object(watch, "release_window_from_start", return_value=([{"tag_name": "v2"}], "v1")), \
                        patch.object(watch, "release_diff", return_value="diff"), \
                        patch.object(watch, "run", return_value="[]"), \
                        patch.object(watch, "ask_ai", side_effect=watch.AIReviewError("HTTP 503")), \
                        patch("builtins.print"):
                    watch.main()
                self.assertEqual(output.read_text(encoding="utf-8").strip(), "failure_count=1")
                self.assertEqual(watch.reported_releases(), set())
            finally:
                watch.REPORTS = original_reports

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
                    analysis = (
                        f"风险级别：P1\n重点标记：破坏性变更=无；硬分叉/共识=无；"
                        f"兼容性=无；内存问题=无；安全=无；稳定性/数据=无\n1. Finding for {tag}"
                    )
                    return watch.format_release(coin, repo, release, f"{tag}-previous", analysis)

                watch.append_report_batch({
                    "A 币种": {"a/node": [entry("A 币种", "a/node", "v1", "2026-11-10T00:00:00Z"), entry("A 币种", "a/node", "v2", "2026-11-11T00:00:00Z")]},
                    "B 币种": {"b/node": [entry("B 币种", "b/node", "v3", "2026-11-10T12:00:00Z")]},
                })

                report_files = [path for path in watch.REPORTS.glob("*.md") if path.name != "index.md"]
                self.assertEqual(len(report_files), 1)
                report = report_files[0].read_text(encoding="utf-8")
                index = (watch.REPORTS / "index.md").read_text(encoding="utf-8")
                self.assertIn(f"]({report_files[0].name})", index)
                self.assertLess(report.index("### A 币种"), report.index("### B 币种"))
                self.assertLess(report.index("#### v1"), report.index("#### v2"))
                self.assertNotIn("#### a/node", report)
                self.assertEqual(report.count("- 仓库：[`a/node`]"), 2)
                self.assertNotIn("变更文件", report)
                self.assertNotIn("Release note", report)
                self.assertNotIn("Notes for v", report)
                self.assertNotIn("src/one.rs", report)
                self.assertEqual(report.count("- **重点标记：** 无"), 3)
                self.assertEqual(report.count("1. Finding for v"), 3)
                self.assertIn("restart at 1 for every new release", watch.SYSTEM_PROMPT)
                self.assertEqual(watch.reported_releases(), {
                    ("A 币种", "a/node", "v1"),
                    ("A 币种", "a/node", "v2"),
                    ("B 币种", "b/node", "v3"),
                })
            finally:
                watch.REPORTS = original_reports

    def test_each_batch_gets_a_report_and_legacy_index_is_preserved(self):
        original_reports = watch.REPORTS
        with tempfile.TemporaryDirectory() as temp_dir:
            watch.REPORTS = Path(temp_dir)
            try:
                legacy_meta = {"coin": "coin", "repo": "owner/repo", "tag": "v1"}
                encoded = watch.base64.urlsafe_b64encode(
                    json.dumps(legacy_meta, sort_keys=True).encode("utf-8")
                ).decode("ascii").rstrip("=")
                legacy = watch.REPORTS / "index.md"
                legacy.write_text(
                    f"# Old report\n\n## 检查批次 2026-11-10 00:00 UTC\n\n<!-- watch-release: {encoded} -->\nOld content\n",
                    encoding="utf-8",
                )

                watch.archive_legacy_index()
                watch.update_report_index()
                for tag in ("v2", "v3"):
                    watch.append_report_batch({"coin": {"owner/repo": [(
                        {"coin": "coin", "repo": "owner/repo", "tag": tag, "published_at": "2026-11-11T00:00:00Z"},
                        f"#### {tag}\n",
                    )]}})

                report_files = [path for path in watch.REPORTS.glob("*.md") if path.name != "index.md"]
                self.assertEqual(len(report_files), 3)
                index = (watch.REPORTS / "index.md").read_text(encoding="utf-8")
                self.assertNotIn("watch-release:", index)
                self.assertIn("Old content", (watch.REPORTS / "2026-11-10T00-00Z.md").read_text(encoding="utf-8"))
                self.assertTrue(all(f"]({path.name})" in index for path in report_files))
                self.assertEqual(watch.reported_releases(), {
                    ("coin", "owner/repo", "v1"),
                    ("coin", "owner/repo", "v2"),
                    ("coin", "owner/repo", "v3"),
                })
            finally:
                watch.REPORTS = original_reports


if __name__ == "__main__":
    unittest.main()
