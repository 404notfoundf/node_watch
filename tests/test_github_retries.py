import io
import json
import os
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from test_watch_releases import watch


class GitHubRetryTests(unittest.TestCase):
    def setUp(self):
        self.request = self.enterContext(patch.object(watch.urllib.request, "urlopen"))
        self.sleep = self.enterContext(patch.object(watch.time, "sleep"))
        self.output = io.StringIO()
        self.enterContext(redirect_stdout(self.output))

    def response(self, data):
        return io.BytesIO(json.dumps(data).encode("utf-8"))

    def http_error(self, status):
        return watch.urllib.error.HTTPError("https://api.github.com/repos/o/r/releases", status, "gateway-error", None, None)

    def test_success_does_not_retry(self):
        self.request.return_value = self.response([{"tag_name": "v1"}])
        self.assertEqual(watch.github_json("repos/o/r/releases"), [{"tag_name": "v1"}])
        self.request.assert_called_once()
        self.sleep.assert_not_called()
        self.assertEqual(self.output.getvalue(), "")

    def test_release_pagination_retries_only_the_failed_page(self):
        self.request.side_effect = [
            self.response([{"tag_name": "v3"}]), self.http_error(502),
            self.response([{"tag_name": "v2"}, {"tag_name": "v1"}]), self.response([]),
        ]
        releases, previous = watch.release_window_after_running_version("o/r", "v1")
        self.assertEqual([release["tag_name"] for release in releases], ["v2", "v3"])
        self.assertEqual(previous, "v1")
        self.assertEqual([call.args[0].full_url.rsplit("page=", 1)[1] for call in self.request.call_args_list], ["1", "2", "2", "3"])
        self.sleep.assert_called_once_with(5)

    def test_transient_http_errors_retry_then_return_valid_json(self):
        for status in (408, 500, 502, 503, 504):
            with self.subTest(status=status):
                self.request.reset_mock()
                self.sleep.reset_mock()
                self.request.side_effect = [self.http_error(status), self.response({"ok": True})]
                self.assertEqual(watch.github_json("repos/o/r/releases"), {"ok": True})
                self.assertEqual(self.request.call_count, 2)
                self.sleep.assert_called_once_with(5)

    def test_backoff_is_five_ten_twenty_seconds_with_four_total_attempts(self):
        self.request.side_effect = [self.http_error(502), self.http_error(503), self.http_error(504), self.response([])]
        self.assertEqual(watch.github_json("repos/o/r/releases"), [])
        self.assertEqual(self.request.call_count, 4)
        self.assertEqual([call.args[0] for call in self.sleep.call_args_list], [5, 10, 20])
        self.assertIn("repos/o/r/releases", self.output.getvalue())
        self.assertIn("retry 3/3 after 20s", self.output.getvalue())

    def test_exhausted_http_retries_raise_the_original_last_error(self):
        errors = [self.http_error(502) for _ in range(4)]
        self.request.side_effect = errors
        with self.assertRaises(watch.urllib.error.HTTPError) as raised:
            watch.github_json("repos/o/r/releases")
        self.assertIs(raised.exception, errors[-1])
        self.assertEqual(self.request.call_count, 4)
        self.assertEqual([call.args[0] for call in self.sleep.call_args_list], [5, 10, 20])

    def test_client_permission_missing_resource_and_rate_limit_errors_fail_fast(self):
        for status in (400, 401, 403, 404, 422, 429):
            with self.subTest(status=status):
                self.request.reset_mock()
                self.sleep.reset_mock()
                error = self.http_error(status)
                self.request.side_effect = error
                with self.assertRaises(watch.urllib.error.HTTPError) as raised:
                    watch.github_json("repos/o/r/releases")
                self.assertIs(raised.exception, error)
                self.request.assert_called_once()
                self.sleep.assert_not_called()

    def test_transport_errors_retry(self):
        errors = [
            TimeoutError("timed out"), ConnectionResetError("connection reset"),
            watch.urllib.error.URLError(TimeoutError("timed out")),
            watch.urllib.error.URLError(OSError("name resolution failed")),
            watch.http.client.RemoteDisconnected("connection closed"),
            watch.http.client.IncompleteRead(b"partial", 12),
        ]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                self.request.reset_mock()
                self.sleep.reset_mock()
                self.request.side_effect = [error, self.response([])]
                self.assertEqual(watch.github_json("repos/o/r/releases"), [])
                self.assertEqual(self.request.call_count, 2)
                self.sleep.assert_called_once_with(5)

    def test_transport_retries_are_bounded_and_preserve_the_last_error(self):
        errors = [TimeoutError(f"timeout {number}") for number in range(4)]
        self.request.side_effect = errors
        with self.assertRaises(TimeoutError) as raised:
            watch.github_json("repos/o/r/releases")
        self.assertIs(raised.exception, errors[-1])
        self.assertEqual(self.request.call_count, 4)
        self.assertEqual([call.args[0] for call in self.sleep.call_args_list], [5, 10, 20])

    def test_read_timeout_retries_and_closes_the_failed_response(self):
        response = self.response([])
        self.request.side_effect = [response, self.response([])]
        with patch.object(response, "read", side_effect=TimeoutError("read timeout")):
            self.assertEqual(watch.github_json("repos/o/r/releases"), [])
        self.assertTrue(response.closed)
        self.sleep.assert_called_once_with(5)

    def test_invalid_json_is_not_hidden_by_transport_retries(self):
        self.request.return_value = io.BytesIO(b"not json")
        with self.assertRaises(json.JSONDecodeError):
            watch.github_json("repos/o/r/releases")
        self.request.assert_called_once()
        self.sleep.assert_not_called()

    def test_retried_http_error_response_is_closed(self):
        response = io.BytesIO(b"bad gateway")
        error = watch.urllib.error.HTTPError("https://api.github.com/repos/o/r/releases", 502, "Bad Gateway", None, response)
        self.request.side_effect = [error, self.response([])]
        self.assertEqual(watch.github_json("repos/o/r/releases"), [])
        self.assertTrue(response.closed)

    def test_retry_preserves_get_authentication_and_does_not_log_secrets(self):
        self.request.side_effect = [watch.urllib.error.URLError("secret-canary"), self.response([])]
        with patch.dict(os.environ, {"GH_TOKEN": "secret-canary"}):
            self.assertEqual(watch.github_json("repos/o/r/releases?per_page=100&page=2"), [])
        for call in self.request.call_args_list:
            request = call.args[0]
            self.assertEqual(request.get_method(), "GET")
            self.assertEqual(request.full_url, "https://api.github.com/repos/o/r/releases?per_page=100&page=2")
            self.assertEqual(request.get_header("Authorization"), "Bearer secret-canary")
            self.assertEqual(call.kwargs["timeout"], 30)
        self.assertNotIn("secret-canary", self.output.getvalue())


if __name__ == "__main__":
    unittest.main()
