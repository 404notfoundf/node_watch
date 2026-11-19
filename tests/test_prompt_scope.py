import io
import json
import re
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from test_watch_releases import EMPTY_AI_REVIEW, watch


class PromptScopeTests(unittest.TestCase):
    def setUp(self):
        cache = tempfile.TemporaryDirectory()
        self.addCleanup(cache.cleanup)
        self.enterContext(patch.object(watch, "REVIEW_CACHE", Path(cache.name)))

    def test_global_prompts_do_not_embed_project_or_old_release_verdicts(self):
        for name, prompt in (
            ("watch.yaml", watch.load_config()["ai"]["prompt"]),
            ("system", watch.SYSTEM_PROMPT),
            ("chunk", watch.CHUNK_REVIEW_PROMPT),
            ("history", watch.HISTORICAL_REVIEW_PROMPT),
        ):
            for marker in (
                "validator_node_mr", "horizon sync", "bad_blocks", "对于本系列",
                "check-db/autocorrect", "bundled-tor startup failure", "join/peer admission",
            ):
                with self.subTest(prompt=name, marker=marker):
                    self.assertFalse(marker in prompt.lower(), f"{name} contains project-specific marker: {marker}")

    def test_both_configs_keep_general_evidence_risk_and_operator_reminder_rules(self):
        for config_path in (watch.CONFIG, watch.CONFIG.with_name("watch.example.yaml")):
            with self.subTest(config=config_path.name), patch.object(watch, "CONFIG", config_path):
                prompt = watch.load_config()["ai"]["prompt"]
                for required in ("当前仓库", "不套用其他币种", "代码", "证据", "目标网络", "P0", "P1", "P2", "P3", "原文", "运营升级提醒"):
                    self.assertTrue(required in prompt, f"{config_path.name} lacks rule: {required}")
                for forbidden in ("validator_node_mr", "horizon sync", "对于本系列", "timelock", "check-db", "Tor"):
                    self.assertFalse(forbidden in prompt, f"{config_path.name} contains: {forbidden}")

    def test_repository_prompt_override_is_local_and_keeps_other_settings(self):
        defaults = {"prompt": "GLOBAL-CUSTOM-SCOPE", "model": "shared-model", "diff_chunk_chars": 400000}
        override = {"prompt": "ALEO-LOCAL-SCOPE"}
        config = {"ai": defaults, "coins": {
            "aleo": {"repo": "aleo-labs-protocol/snarkOS", "running_version": "v1", "ai": override},
            "alephium": {"repo": "alephium/alephium", "running_version": "v1"},
            "xbt": {"repo": "bitcoinknots/bitcoin", "running_version": "v1"},
        }}
        settings = {coin: watch.ai_settings(defaults, local) for coin, _, _, _, _, local in watch.configured_repositories(config)}
        self.assertEqual(settings["aleo"]["prompt"], "ALEO-LOCAL-SCOPE")
        self.assertEqual(settings["aleo"]["model"], "shared-model")
        self.assertEqual(settings["aleo"]["diff_chunk_chars"], 400000)
        self.assertEqual(settings["alephium"]["prompt"], "GLOBAL-CUSTOM-SCOPE")
        self.assertEqual(settings["xbt"]["prompt"], "GLOBAL-CUSTOM-SCOPE")
        self.assertEqual(defaults["prompt"], "GLOBAL-CUSTOM-SCOPE")
        self.assertEqual(override, {"prompt": "ALEO-LOCAL-SCOPE"})

    def test_full_fast_and_chunk_requests_use_only_the_current_override(self):
        scopes = {
            "aleo-labs-protocol/snarkOS": "ALEO-LOCAL-SCOPE",
            "alephium/alephium": "ALPH-LOCAL-SCOPE",
            "bitcoinknots/bitcoin": "XBT-LOCAL-SCOPE",
        }
        for repo, scope in scopes.items():
            for mode, chunk_chars in (("full", 1000), ("fast", 1000), ("full", 4)):
                requests = []
                def request(settings, prompt, material):
                    requests.append(prompt)
                    review_id = re.search(r'review_id must be "([0-9a-f]+)"', prompt)
                    if review_id:
                        return json.dumps({"review_id": review_id.group(1), "complete": True, "analysis": json.loads(EMPTY_AI_REVIEW)})
                    return EMPTY_AI_REVIEW
                settings = watch.ai_settings({"prompt": "GLOBAL-CUSTOM-SCOPE"}, {"prompt": scope, "diff_chunk_chars": chunk_chars})
                with self.subTest(repo=repo, mode=mode, chunk_chars=chunk_chars), \
                        patch.object(watch, "call_ai", side_effect=request), redirect_stdout(io.StringIO()):
                    watch.ask_ai(settings, repo, {"tag_name": "v2"}, "v1", "firstsecond", mode)
                self.assertTrue(requests)
                for prompt in requests:
                    self.assertIn(scope, prompt)
                    self.assertNotIn("GLOBAL-CUSTOM-SCOPE", prompt)
                    self.assertTrue(all(other not in prompt for other in scopes.values() if other != scope))
                    if "review_id must be" not in prompt:
                        self.assertIn("EVIDENCE GATES", prompt)
                    self.assertNotIn("validator_node_mr", prompt)

    def test_fast_batch_uses_the_current_repository_prompt_and_builtin_gates(self):
        settings = watch.ai_settings({"prompt": "GLOBAL-CUSTOM-SCOPE"}, {"prompt": "ALPH-LOCAL-SCOPE"})
        candidates = [{
            "repo": "alephium/alephium", "release": {"tag_name": tag}, "previous_tag": "v0",
            "diff": "diff", "target_network": "mainnet",
        } for tag in ("v1", "v2")]
        response = "\n".join(
            f"--- REVIEW {watch.fast_batch_id(item['repo'], item['release'], item['previous_tag'])} ---\n{EMPTY_AI_REVIEW}"
            for item in candidates
        )
        with patch.object(watch, "call_ai", return_value=response) as ai:
            results = watch.ask_ai_fast_batch(settings, candidates)
        self.assertEqual(len(results), 2)
        prompt = ai.call_args.args[1]
        self.assertIn("ALPH-LOCAL-SCOPE", prompt)
        self.assertNotIn("GLOBAL-CUSTOM-SCOPE", prompt)
        self.assertIn("EVIDENCE GATES", prompt)
        self.assertNotIn("validator_node_mr", prompt)
