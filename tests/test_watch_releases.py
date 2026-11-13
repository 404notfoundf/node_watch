import base64
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
PUBLISH_SCRIPT = SCRIPT.with_name("publish_report_site.py")
PUBLISH_SPEC = importlib.util.spec_from_file_location("publish_report_site", PUBLISH_SCRIPT)
publish_site = importlib.util.module_from_spec(PUBLISH_SPEC)
PUBLISH_SPEC.loader.exec_module(publish_site)


class WatchReleaseTests(unittest.TestCase):
    def test_pages_report_hides_marker_and_escapes_raw_html(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_dir = root / "input"
            site_dir = root / "site"
            report_dir.mkdir()
            (report_dir / "report.md").write_text(
                "# 上游 Release 监控报告\n\n"
                "## 检查批次 2026-11-13 03:33:55 UTC\n\n"
                "### tari\n\n<!-- watch-release: secret-marker -->\n\n"
                "#### v1.0.0\n\n<script>alert(1)</script>\n",
                encoding="utf-8",
            )

            report_path = publish_site.publish_report(report_dir, site_dir, "123", "1", 180)
            rendered = (site_dir / report_path).read_text(encoding="utf-8")

        self.assertIn("<h4>v1.0.0</h4>", rendered)
        self.assertNotIn("watch-release:", rendered)
        self.assertNotIn("<script>", rendered)
        self.assertIn("&lt;script&gt;", rendered)

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

    def test_codex_cli_backend_uses_read_only_exec_and_captures_report(self):
        captured = {}
        temporary_directory = watch.tempfile.TemporaryDirectory

        def run(command, **kwargs):
            captured["command"] = command
            captured["prompt"] = kwargs["input"]
            output = Path(command[command.index("--output-last-message") + 1])
            output.write_text("Codex analysis", encoding="utf-8")
            return type("Result", (), {"returncode": 0})()

        with patch.dict(os.environ, {"AI_BACKEND": "codex_cli"}), \
                patch.object(watch.shutil, "which", return_value="codex"), \
                patch.object(watch.tempfile, "TemporaryDirectory", wraps=temporary_directory) as temp_dir, \
                patch.object(watch.subprocess, "run", side_effect=run):
            result = watch.call_ai({}, "review instructions", "release diff")

        self.assertEqual(result, "Codex analysis")
        self.assertIn("--sandbox", captured["command"])
        self.assertIn("read-only", captured["command"])
        self.assertIn("--ephemeral", captured["command"])
        self.assertIn("review instructions", captured["prompt"])
        self.assertIn("release diff", captured["prompt"])
        temp_dir.assert_called_once_with(prefix="release-watch-codex-", ignore_cleanup_errors=True)

    def test_codex_cli_failure_keeps_only_the_tail_of_stderr(self):
        with patch.dict(os.environ, {"AI_BACKEND": "codex_cli"}), \
                patch.object(watch.shutil, "which", return_value="codex"), \
                patch.object(watch.subprocess, "run", return_value=type(
                    "Result", (), {"returncode": 1, "stderr": "x" * 3000 + " failure detail"}
                )()):
            with self.assertRaises(watch.AIReviewError) as error:
                watch.call_ai({}, "review instructions", "release diff")

        self.assertIn("failure detail", str(error.exception))
        self.assertLess(len(str(error.exception)), 2100)

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

    def test_ai_reviews_all_diff_chunks_then_synthesizes_findings(self):
        captured = []

        def urlopen(request, timeout):
            captured.append(json.loads(request.data.decode("utf-8")))
            content = "analysis" if len(captured) == 4 else f"Chunk finding {len(captured)}"
            return io.BytesIO(json.dumps({"choices": [{"message": {"content": content}}]}).encode())

        with patch.dict(os.environ, {"AI_API_KEY": "test-key"}), \
                patch.object(watch.urllib.request, "urlopen", side_effect=urlopen):
            result = watch.ask_ai(
                {"api_url": "https://ai.example/v1", "model": "test", "diff_chunk_chars": 4},
                "owner/repo", {"tag_name": "v1", "body": "release notes"}, "v0", "abcdefghij",
            )
        self.assertEqual(result, "analysis")
        self.assertEqual(len(captured), 4)
        chunk_materials = [request["messages"][1]["content"] for request in captured[:3]]
        self.assertIn("Diff chunk: 1/3", chunk_materials[0])
        self.assertIn("<untrusted_code_diff_chunk>\nabcd\n</untrusted_code_diff_chunk>", chunk_materials[0])
        self.assertIn("<untrusted_code_diff_chunk>\nefgh\n</untrusted_code_diff_chunk>", chunk_materials[1])
        self.assertIn("<untrusted_code_diff_chunk>\nij\n</untrusted_code_diff_chunk>", chunk_materials[2])
        summary_material = captured[3]["messages"][1]["content"]
        self.assertIn("all 10 characters were reviewed in 3 chunks", summary_material)
        self.assertIn("release notes", summary_material)
        self.assertIn("Chunk finding 1", summary_material)
        self.assertIn("Chunk finding 2", summary_material)
        self.assertIn("Chunk finding 3", summary_material)

    def test_ai_rejects_invalid_diff_chunk_size(self):
        with self.assertRaises(watch.AIReviewError):
            watch.ask_ai({"diff_chunk_chars": 0}, "owner/repo", {"tag_name": "v1"}, "v0", "diff")

    def test_auto_review_uses_fast_for_routine_change_and_full_for_risk_signals(self):
        routine_diff = "diff --git a/docs/readme.md b/docs/readme.md\n+++ b/docs/readme.md\n+Update docs\n"
        self.assertEqual(watch.review_mode("auto", {"body": "Routine release"}, routine_diff), "fast")
        self.assertEqual(watch.review_mode("auto", {"body": "Hard fork activation"}, routine_diff), "full")
        suspicious_diff = "diff --git a/src/a.py b/src/a.py\n+++ b/src/a.py\n+subprocess.run(command)\n"
        self.assertEqual(watch.review_mode("auto", {"body": "Routine release"}, suspicious_diff), "full")

    def test_fast_review_sends_inventory_and_suspicious_hunks_not_full_diff(self):
        diff = (
            "diff --git a/src/worker.py b/src/worker.py\n+++ b/src/worker.py\n"
            "+subprocess.run(command)\n context\n"
            "diff --git a/docs/readme.md b/docs/readme.md\n+++ b/docs/readme.md\n+ordinary documentation\n"
        )
        material = watch.fast_review_material("owner/repo", {"tag_name": "v1", "body": "notes"}, "v0", diff)
        self.assertIn("src/worker.py (+1/-0, 普通路径)", material)
        self.assertIn("docs/readme.md (+1/-0, 普通路径)", material)
        self.assertIn("subprocess.run(command)", material)
        self.assertNotIn("ordinary documentation", material)
        self.assertIn("FAST PRECHECK", material)

    def test_fast_ask_ai_makes_one_request(self):
        captured = []

        def urlopen(request, timeout):
            captured.append(json.loads(request.data.decode("utf-8")))
            return io.BytesIO(json.dumps({"choices": [{"message": {"content": "analysis"}}]}).encode())

        with patch.dict(os.environ, {"AI_API_KEY": "test-key"}), \
                patch.object(watch.urllib.request, "urlopen", side_effect=urlopen):
            result = watch.ask_ai(
                {"api_url": "https://ai.example/v1", "model": "test"}, "owner/repo",
                {"tag_name": "v1", "body": "notes"}, "v0", "diff --git a/a b/a\n+++ b/a\n+change\n", "fast",
            )

        self.assertEqual(result, "analysis")
        self.assertEqual(len(captured), 1)
        self.assertIn("FAST PRECHECK", captured[0]["messages"][1]["content"])

    def test_highlight_summary_marks_major_changes(self):
        analysis = (
            "重点标记：破坏性变更=待验证；硬分叉/共识=已确认；兼容性=待验证；"
            "内存问题=修复；安全=风险；稳定性/数据=无\n"
            "重点标记依据：破坏性变更=发行说明称移除旧配置格式，但差异未覆盖配置解析；"
            "硬分叉/共识=src/consensus.rs 修改了区块验证规则；兼容性=发行说明称调整协议字段，差异未核实；"
            "内存问题=src/cache.rs 修复缓存未释放；安全=src/rpc.rs 新增未校验输入；稳定性/数据=无"
        )
        summary = watch.highlight_summary(analysis)
        self.assertIn("⚠️ **重大发行说明待核实：** 破坏性变更声明、兼容性声明", summary)
        self.assertIn("重大共识变更**（已确认）", summary)
        self.assertIn("✅ **内存问题修复**", summary)
        self.assertIn("安全**（风险）", summary)
        self.assertNotIn("稳定性/数据", summary)
        self.assertIn("⚠️", summary)
        reasons = watch.highlight_reason_summary(analysis)
        self.assertIn("**破坏性变更：** 发行说明称移除旧配置格式，但差异未覆盖配置解析", reasons)
        self.assertIn("**硬分叉/共识：** src/consensus.rs 修改了区块验证规则", reasons)
        self.assertIn("**内存问题：** src/cache.rs 修复缓存未释放", reasons)
        self.assertIn("**安全：** src/rpc.rs 新增未校验输入", reasons)
        self.assertIn("重点标记", watch.SYSTEM_PROMPT)
        self.assertIn("memory leaks", watch.SYSTEM_PROMPT)
        self.assertIn("chunk-review summaries", watch.SYSTEM_PROMPT)
        self.assertIn("Omit routine refactors", watch.SYSTEM_PROMPT)
        self.assertIn("one or two concise sentences", watch.SYSTEM_PROMPT)
        self.assertIn("minor fixes or optimizations", watch.SYSTEM_PROMPT)
        hard_fork = analysis.replace(
            "硬分叉/共识=src/consensus.rs 修改了区块验证规则",
            "硬分叉/共识=硬分叉：激活高度 123 会使旧节点拒绝新区块",
        )
        self.assertIn("硬分叉**（已确认）", watch.highlight_summary(hard_fork))
        _, report = watch.format_release(
            "coin", "owner/repo", {"tag_name": "v1"}, "v0",
            f"风险级别：P1\n{analysis}\n1. Note contains {{{{repo}}}}.",
        )
        self.assertIn(f"- **重点标记：** {summary}", report)
        self.assertIn(f"- **标记依据：** {reasons}", report)
        self.assertIn("- 审查模式：完整审查", report)
        self.assertNotIn("重点标记依据：", report)
        self.assertNotIn("省略", report)
        self.assertIn("1. Note contains {{repo}}.", report)
        self.assertNotIn("{{tag}}", report)

    def test_p3_release_without_highlights_is_marked_unimportant(self):
        meta, report = watch.format_release(
            "coin", "owner/repo", {"tag_name": "v1"}, "v0",
            "风险级别：P3\n重点标记：破坏性变更=无；硬分叉/共识=无；兼容性=无；"
            "内存问题=无；安全=无；稳定性/数据=无\n"
            "重点标记依据：破坏性变更=无；硬分叉/共识=无；兼容性=无；"
            "内存问题=无；安全=无；稳定性/数据=无\n未发现需要单独报告的重大变更。",
        )
        self.assertEqual(meta["importance"], "不重要")
        self.assertEqual(meta["conclusion"], "不重要")
        self.assertIn("- 审查结论：**不重要**", report)

    def test_issue_summary_lists_all_coins_releases_and_deduplicates(self):
        def entry(coin, repo, tag):
            analysis = (
                "风险级别：P1\n重点标记：破坏性变更=无；硬分叉/共识=无；兼容性=无；"
                "内存问题=修复；安全=无；稳定性/数据=无\n"
                "重点标记依据：破坏性变更=无；硬分叉/共识=无；兼容性=无；"
                "内存问题=src/cache.rs 修复缓存未释放；安全=无；稳定性/数据=无\n1. Finding"
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
        self.assertIn("## 需关注", body)
        self.assertIn("**tari**", body)
        self.assertIn("**coin-b**", body)
        self.assertNotIn("tari-project/tari", body)
        self.assertIn("`v6.2.0`", body)
        self.assertIn("`v1`", body)
        self.assertIn("`v2`", body)
        self.assertLess(body.index("**coin-b**"), body.index("**tari**"))
        self.assertIn("内存问题修复", body)
        self.assertIn("完整审查", body)
        self.assertIn("要点：内存问题：src/cache.rs 修复缓存未释放", body)
        self.assertNotIn("标记依据", body)
        self.assertNotIn("1. Finding", body)
        self.assertIn("/actions/runs/12345", body)
        self.assertIn("@owner", body)
        self.assertRegex(body, r"(?m)^<!-- watch-release-keys: [A-Za-z0-9_-]+ -->$")
        self.assertNotIn("reports/", body)
        self.assertIn("[在线查看完整报告]({{report_url}})", body)
        self.assertIn("[下载 Markdown 报告（保留 90 天）]({{artifact_url}})", body)

    def test_issue_markers_are_the_persistent_release_deduplication_state(self):
        releases = [("tari", "tari-project/tari", "v6.4.0")]
        encoded = watch.base64.urlsafe_b64encode(json.dumps(releases).encode()).decode().rstrip("=")
        issues = [
            {"author": {"login": "github-actions[bot]"}, "body": f"<!-- watch-release-keys: {encoded} -->"},
            {"author": {"login": "repository-owner"}, "body": f"<!-- watch-release-keys: {encoded} -->"},
        ]
        original_reports = watch.REPORTS
        with tempfile.TemporaryDirectory() as temp_dir:
            watch.REPORTS = Path(temp_dir)
            try:
                self.assertEqual(watch.reported_releases(issues), set(releases))
            finally:
                watch.REPORTS = original_reports

    def test_github_issue_history_uses_paginated_api_in_actions(self):
        first_page = [{"number": number} for number in range(100)]
        second_page = [{"number": 100}]
        calls = []

        def github_json(path):
            calls.append(path)
            return first_page if path.endswith("page=1") else second_page

        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "owner/watch", "GH_TOKEN": "token"}), \
                patch.object(watch, "github_json", side_effect=github_json), \
                patch.object(watch, "run") as run:
            self.assertEqual(watch.github_issue_history(), first_page + second_page)

        self.assertEqual(calls, [
            "repos/owner/watch/issues?state=all&per_page=100&page=1",
            "repos/owner/watch/issues?state=all&per_page=100&page=2",
        ])
        run.assert_not_called()

    def test_local_issue_history_uses_public_api_without_gh_cli(self):
        calls = []

        def github_json(path):
            calls.append(path)
            return [{"body": "issue"}]

        with patch.dict(os.environ, {"GITHUB_REPOSITORY": "", "GH_TOKEN": ""}), \
                patch.object(watch, "run", return_value="https://github.com/owner/watch.git") as run, \
                patch.object(watch, "github_json", side_effect=github_json):
            self.assertEqual(watch.github_issue_history(), [{"body": "issue"}])

        run.assert_called_once_with("git", "remote", "get-url", "origin", cwd=watch.ROOT)
        self.assertEqual(calls, ["repos/owner/watch/issues?state=all&per_page=100&page=1"])

    def test_local_codex_can_skip_online_issue_history_but_actions_cannot(self):
        with patch.dict(os.environ, {
            "GITHUB_ACTIONS": "", "AI_BACKEND": "codex_cli", "SKIP_GITHUB_ISSUE_HISTORY": "1",
        }):
            self.assertFalse(watch.should_read_github_issue_history())
        with patch.dict(os.environ, {
            "GITHUB_ACTIONS": "true", "AI_BACKEND": "codex_cli", "SKIP_GITHUB_ISSUE_HISTORY": "1",
        }):
            self.assertTrue(watch.should_read_github_issue_history())

    def test_local_codex_uses_github_issue_markers_to_skip_old_releases(self):
        old_keys = [
            ["tari", "tari-project/tari", "v6.4.0"],
            ["tari", "tari-project/tari", "v6.5.0"],
        ]
        encoded = base64.urlsafe_b64encode(
            json.dumps(old_keys, separators=(",", ":")).encode("utf-8")
        ).decode("ascii").rstrip("=")
        issues = [{
            "author": {"login": "github-actions[bot]"},
            "body": f"<!-- watch-release-keys: {encoded} -->",
        }]
        diff_calls = []
        original_reports = watch.REPORTS
        original_root = watch.ROOT

        def run(*args, cwd=None):
            if args == ("git", "remote", "get-url", "origin"):
                return "https://github.com/owner/watch.git\n"
            raise AssertionError(f"Unexpected command: {args}")

        def release_diff(repo, previous, tag):
            diff_calls.append((repo, previous, tag))
            return "new diff"

        analysis = (
            "风险级别：P1\n重点标记：破坏性变更=无；硬分叉/共识=无；兼容性=无；"
            "内存问题=无；安全=无；稳定性/数据=无\n"
            "重点标记依据：破坏性变更=无；硬分叉/共识=无；兼容性=无；"
            "内存问题=无；安全=无；稳定性/数据=无\n1. New release finding"
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            watch.ROOT = Path(temp_dir)
            watch.REPORTS = watch.ROOT / "reports"
            try:
                with patch.dict(os.environ, {
                    "AI_BACKEND": "codex_cli",
                    "GITHUB_ACTIONS": "",
                    "GITHUB_REPOSITORY": "",
                    "GITHUB_OUTPUT": "",
                }), patch.object(watch, "load_config", return_value={
                    "coins": {"tari": {"repo": "tari-project/tari", "from_release": "v6.4.0"}},
                }), patch.object(watch, "release_window_from_start", return_value=(
                    [{"tag_name": "v6.4.0"}, {"tag_name": "v6.5.0"}, {"tag_name": "v6.6.0"}], "v6.3.0",
                )), patch.object(watch, "run", side_effect=run), \
                        patch.object(watch, "github_json", return_value=issues), \
                        patch.object(watch, "release_diff", side_effect=release_diff), \
                        patch.object(watch, "ask_ai", return_value=analysis), patch("builtins.print"):
                    watch.main()

                self.assertEqual(diff_calls, [("tari-project/tari", "v6.5.0", "v6.6.0")])
                reports = list(watch.REPORTS.glob("*.md"))
                self.assertEqual(len(reports), 1)
                report = reports[0].read_text(encoding="utf-8")
                self.assertIn("#### v6.6.0", report)
                self.assertNotIn("#### v6.4.0", report)
                self.assertNotIn("#### v6.5.0", report)
            finally:
                watch.REPORTS = original_reports
                watch.ROOT = original_root

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

    def test_workflow_publishes_report_before_issue_and_does_not_commit_reports(self):
        workflow = watch.yaml.safe_load((SCRIPT.parents[1] / "workflows" / "watch-releases.yml").read_text(encoding="utf-8"))
        watch_job = workflow["jobs"]["watch"]
        publish_job = workflow["jobs"]["publish-report"]
        watch_steps = watch_job["steps"]
        publish_steps = publish_job["steps"]
        watch_names = [step.get("name", "") for step in watch_steps]
        publish_names = [step.get("name", "") for step in publish_steps]
        self.assertNotIn("Commit reports", watch_names + publish_names)
        self.assertLess(watch_names.index("Upload full report"), watch_names.index("Mark incomplete release checks"))
        self.assertLess(publish_names.index("Deploy report website"), publish_names.index("Create release summary Issue"))
        self.assertEqual(publish_job["needs"], "watch")
        self.assertEqual(watch_job["permissions"]["contents"], "read")
        self.assertEqual(watch_job["permissions"]["issues"], "read")
        self.assertEqual(publish_job["permissions"]["contents"], "write")
        self.assertEqual(publish_job["permissions"]["pages"], "write")
        self.assertEqual(publish_job["permissions"]["id-token"], "write")
        self.assertIn("actions/checkout@v7", [step.get("uses") for step in watch_steps])
        self.assertIn("actions/setup-python@v7", [step.get("uses") for step in watch_steps])
        upload = next(step for step in watch_steps if step.get("name") == "Upload full report")
        create_issue = next(step for step in publish_steps if step.get("name") == "Create release summary Issue")
        self.assertEqual(upload["id"], "upload")
        self.assertEqual(upload["with"]["retention-days"], 90)
        self.assertEqual(create_issue["env"]["ARTIFACT_URL"], "${{ needs.watch.outputs.artifact_url }}")
        self.assertEqual(create_issue["env"]["PAGE_URL"], "${{ steps.deployment.outputs.page_url }}")
        self.assertIn("actions/upload-pages-artifact@v3", [step.get("uses") for step in publish_steps])
        self.assertIn("actions/deploy-pages@v4", [step.get("uses") for step in publish_steps])

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
                        patch.object(watch, "github_json", return_value=[]), \
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
                self.assertLess(report.index("### A 币种"), report.index("### B 币种"))
                self.assertLess(report.index("#### v1"), report.index("#### v2"))
                self.assertNotIn("#### a/node", report)
                self.assertEqual(report.count("- 仓库：[`a/node`]"), 2)
                self.assertNotIn("变更文件", report)
                self.assertNotIn("Release note", report)
                self.assertNotIn("Notes for v", report)
                self.assertNotIn("src/one.rs", report)
                self.assertNotIn("<!-- watch-release:", report)
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

    def test_new_reports_do_not_create_an_index_and_record_releases(self):
        original_reports = watch.REPORTS
        with tempfile.TemporaryDirectory() as temp_dir:
            watch.REPORTS = Path(temp_dir)
            try:
                for tag in ("v1", "v2", "v3"):
                    watch.append_report_batch({"coin": {"owner/repo": [(
                        {"coin": "coin", "repo": "owner/repo", "tag": tag, "published_at": "2026-11-11T00:00:00Z"},
                        f"#### {tag}\n\n- 仓库：[`owner/repo`](https://github.com/owner/repo)\n",
                    )]}})

                report_files = [path for path in watch.REPORTS.glob("*.md") if path.name != "index.md"]
                self.assertEqual(len(report_files), 3)
                self.assertFalse((watch.REPORTS / "index.md").exists())
                self.assertEqual(watch.reported_releases(), {
                    ("coin", "owner/repo", "v1"),
                    ("coin", "owner/repo", "v2"),
                    ("coin", "owner/repo", "v3"),
                })
            finally:
                watch.REPORTS = original_reports


if __name__ == "__main__":
    unittest.main()
