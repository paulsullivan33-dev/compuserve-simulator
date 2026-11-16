"""The optional local-model add-on (cis_llm) and the services that use it."""
import json
import os
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import cis_experience
import cis_llm
import cis_ownership

ROOT = Path(__file__).resolve().parent.parent

CONFIG = {
    "ollama_url": "http://model-host:11434/",
    "min_seconds_between_calls": 2,
    "roles": {
        "cb_chat": {"model": "tiny:1b", "max_chars": 120, "context_lines": 2,
                    "prompt": "You are {handle} on channel {channel}; talk to {member}. {unknown}"},
        "customer_service": {"model": "svc:4b", "prompt": "You are a helpful customer service representative."},
        "warranty": {"enabled": False, "model": "svc:4b", "prompt": "Vendor for {product}."},
    },
}


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class ConfigFileTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "llm_config.json"
        patcher = patch.dict(os.environ, {"CIS_LLM_CONFIG": str(self.path)})
        patcher.start()
        self.addCleanup(patcher.stop)
        cis_llm._last_call.clear()
        cis_llm._cache.update(path=None, mtime=None, config=None)
        self.addCleanup(cis_llm._last_call.clear)

    def write(self, data):
        self.path.write_text(json.dumps(data), encoding="utf-8")
        cis_llm._cache.update(path=None, mtime=None, config=None)


class OffByDefaultTests(ConfigFileTestCase):
    def test_no_file_means_no_reply_and_no_network(self):
        post = Mock()
        self.assertIsNone(cis_llm.reply("cb_chat", "hello", post=post))
        self.assertFalse(cis_llm.enabled("cb_chat"))
        post.assert_not_called()

    def test_enabled_false_turns_everything_off(self):
        self.write(dict(CONFIG, enabled=False))
        post = Mock()
        self.assertIsNone(cis_llm.reply("cb_chat", "hello", post=post))
        post.assert_not_called()

    def test_unusable_file_falls_back_silently(self):
        for bad in ({"roles": {}}, {"roles": {"cb_typo": {"model": "m", "prompt": "p"}}},
                    {"roles": {"cb_chat": {"model": "m", "prompt": " "}}}, ["not", "an", "object"]):
            self.write(bad)
            post = Mock()
            self.assertIsNone(cis_llm.reply("cb_chat", "hello", post=post))
            post.assert_not_called()
            with self.assertRaises(ValueError):
                cis_llm.load_config(self.path)

    def test_disabled_or_missing_role(self):
        self.write(CONFIG)
        post = Mock()
        self.assertIsNone(cis_llm.reply("warranty", "it smokes", post=post))
        self.assertIsNone(cis_llm.reply("representative", "fares?", post=post))
        post.assert_not_called()
        self.assertTrue(cis_llm.enabled("cb_chat"))
        self.assertFalse(cis_llm.enabled("warranty"))


class ReplyTests(ConfigFileTestCase):
    def setUp(self):
        super().setUp()
        self.write(CONFIG)
        self.clock = Clock()

    def test_request_shape_prompt_and_context(self):
        post = Mock(return_value={"message": {"content": "Hey there, nice 2400 baud!"}})
        answer = cis_llm.reply("cb_chat", "anyone on?", persona={"handle": "Sparky", "channel": "1", "member": "Paul"},
                               context=["<A> one", "<B> two", "<C> three"], post=post, clock=self.clock)
        self.assertEqual(answer, "Hey there, nice 2400 baud!")
        url, body, timeout = post.call_args[0]
        self.assertEqual(url, "http://model-host:11434/api/chat")
        self.assertEqual(timeout, 20)
        self.assertEqual(body["model"], "tiny:1b")
        self.assertFalse(body["stream"])
        self.assertFalse(body["think"])
        self.assertEqual(body["keep_alive"], "15m")
        system, user = body["messages"]
        self.assertEqual(system, {"role": "system", "content": "You are Sparky on channel 1; talk to Paul. "})
        self.assertEqual(user["content"], "Recent conversation:\n<B> two\n<C> three\n\nMessage from Paul:\nanyone on?")

    def test_rate_limit_per_role(self):
        post = Mock(return_value={"message": {"content": "First reply here."}})
        self.assertEqual(cis_llm.reply("cb_chat", "a", post=post, clock=self.clock), "First reply here.")
        self.clock.t += 1
        self.assertIsNone(cis_llm.reply("cb_chat", "b", post=post, clock=self.clock))
        self.assertEqual(cis_llm.reply("customer_service", "c", post=post, clock=self.clock), "First reply here.")
        self.clock.t += 2
        self.assertEqual(cis_llm.reply("cb_chat", "d", post=post, clock=self.clock), "First reply here.")
        self.assertEqual(post.call_count, 3)

    def test_server_errors_and_empty_answers_fall_back(self):
        for outcome in (TimeoutError(), OSError("refused"), ValueError("bad json")):
            cis_llm._last_call.clear()
            self.assertIsNone(cis_llm.reply("cb_chat", "hi", post=Mock(side_effect=outcome), clock=self.clock))
        for data in ({}, {"message": {}}, {"message": {"content": "   "}}):
            cis_llm._last_call.clear()
            self.assertIsNone(cis_llm.reply("cb_chat", "hi", post=Mock(return_value=data), clock=self.clock))
        post = Mock()
        self.assertIsNone(cis_llm.reply("cb_chat", "   ", post=post, clock=self.clock))
        post.assert_not_called()

    def test_member_text_is_capped(self):
        post = Mock(return_value={"message": {"content": "ok then, sure thing."}})
        cis_llm.reply("customer_service", "x" * 5000, post=post, clock=self.clock)
        self.assertTrue(post.call_args[0][1]["messages"][1]["content"].endswith("x" * 1000 + ""))
        self.assertLess(len(post.call_args[0][1]["messages"][1]["content"]), 1100)

    def test_edits_apply_without_restart(self):
        self.assertTrue(cis_llm.enabled("cb_chat"))
        self.path.write_text(json.dumps(dict(CONFIG, enabled=False)), encoding="utf-8")
        os.utime(self.path, (2_000_000_000, 2_000_000_000))
        self.assertFalse(cis_llm.enabled("cb_chat"))


class CleanTests(unittest.TestCase):
    def test_terminal_safety(self):
        dirty = "<think>plan</think>\x1b[2J\x1b[31mHi\x07 there\r\nfriend’s “modem” — café **bold** 🙂"
        self.assertEqual(cis_llm.clean(dirty, 200), "Hi there friend's \"modem\" -- cafe bold")

    def test_speaker_prefix_and_quotes(self):
        self.assertEqual(cis_llm.clean('Sparky: "Howdy, all!"', 100, speaker="Sparky"), "Howdy, all!")
        self.assertEqual(cis_llm.clean("<Sparky> Howdy", 100, speaker="Sparky"), "Howdy")

    def test_multiline_keeps_paragraphs_and_drops_subject(self):
        text = "Subject: Re: your modem\nDear Paul,\n\nCheck the cable.\x07\n  Then the switches.\n\n\n\nRegards,\nVendor"
        self.assertEqual(cis_llm.clean(text, 500, multiline=True),
                         "Dear Paul,\n\nCheck the cable. Then the switches.\n\nRegards, Vendor")
        self.assertEqual(cis_llm.clean(text, 500), "Dear Paul, Check the cable. Then the switches. Regards, Vendor")

    def test_length_cut_prefers_sentence_end(self):
        text = "First sentence is here. Second sentence runs on and on past the limit for sure."
        self.assertEqual(cis_llm.clean(text, 40), "First sentence is here.")
        self.assertEqual(cis_llm.clean("word " * 30, 20), "word word word word...")
        self.assertIsNone(cis_llm.clean("\x1b[0m", 50))


class CheckTests(ConfigFileTestCase):
    def test_missing_and_bad_files(self):
        self.assertIn("not found", cis_llm.check(self.path)[0])
        self.write({"roles": {"nope": {"model": "m", "prompt": "p"}}})
        self.assertIn("NOT USABLE", cis_llm.check(self.path)[0])

    def test_models_found_and_missing(self):
        self.write(CONFIG)
        lines = cis_llm.check(self.path, get=lambda url: {"models": [{"name": "tiny:1b"}]})
        text = "\n".join(lines)
        self.assertIn("cb_chat           on  tiny:1b  model OK", text)
        self.assertIn("customer_service  on  svc:4b  MODEL NOT FOUND", text)
        self.assertIn("warranty          off svc:4b", text)
        self.assertIn("representative    not configured (scripted)", text)

    def test_unreachable_server(self):
        self.write(CONFIG)

        def down(url):
            raise OSError("no route")
        self.assertIn("server not reachable (OSError)", "\n".join(cis_llm.check(self.path, get=down)))


class ExampleAndPackagingTests(unittest.TestCase):
    def test_example_is_valid_and_covers_every_role(self):
        config = cis_llm.load_config(ROOT / "llm_config.example.json")
        self.assertEqual(set(config["roles"]), set(cis_llm.ROLES))
        self.assertIn("customer service representative", config["roles"]["customer_service"]["prompt"])
        self.assertIn("1980s slang", config["roles"]["cb_chat"]["prompt"])

    def test_real_config_is_local_only(self):
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        self.assertIn("llm_config.json", ignored)
        files = json.loads((ROOT / "release_assets.json").read_text(encoding="utf-8"))["files"]
        self.assertNotIn("llm_config.json", files)
        self.assertIn("llm_config.example.json", files)
        self.assertIn("cis_llm.py", files)


class BackgroundReplyTests(ConfigFileTestCase):
    def test_reply_later_applies_only_a_usable_answer(self):
        self.write(CONFIG)
        applied = []
        with patch.object(cis_llm, "_post", return_value={"message": {"content": "Fresh answer here."}}):
            cis_llm.reply_later("customer_service", "hi", applied.append).join(5)
        self.assertEqual(applied, ["Fresh answer here."])
        cis_llm._last_call.clear()
        with patch.object(cis_llm, "_post", side_effect=TimeoutError):
            cis_llm.reply_later("customer_service", "hi", applied.append).join(5)
        self.assertEqual(applied, ["Fresh answer here."])

    def test_reply_later_is_off_without_config_and_survives_apply_errors(self):
        self.assertIsNone(cis_llm.reply_later("customer_service", "hi", Mock()))
        self.write(CONFIG)
        with patch.object(cis_llm, "_post", return_value={"message": {"content": "Fine answer."}}):
            thread = cis_llm.reply_later("customer_service", "hi", Mock(side_effect=RuntimeError("boom")))
            thread.join(5)
        self.assertFalse(thread.is_alive())


class UpdateEventPayloadTests(unittest.TestCase):
    def test_only_undelivered_events_change(self):
        import cis_dynamic
        state = {"events": [{"id": 1, "processed": False, "payload": {"body": "old", "to": "x"}},
                            {"id": 2, "processed": True, "payload": {"body": "sent"}}]}

        def update(name, default, mutate):
            self.assertEqual(name, "dynamic_state.json")
            mutate(state)
        app = types.SimpleNamespace(update_json_atomic=update)
        self.assertTrue(cis_dynamic.update_event_payload(app, 1, {"body": "new"}))
        self.assertFalse(cis_dynamic.update_event_payload(app, 2, {"body": "late"}))
        self.assertFalse(cis_dynamic.update_event_payload(app, 9, {"body": "missing"}))
        self.assertEqual(state["events"][0]["payload"], {"body": "new", "to": "x"})
        self.assertEqual(state["events"][1]["payload"], {"body": "sent"})


class ServiceHookTests(ConfigFileTestCase):
    def app(self):
        app = types.SimpleNamespace(cis_dynamic=Mock(), current_user_id="70000,0001", current_handle="Paul")
        app.cis_dynamic.schedule_event.return_value = 42
        return app

    def run_now(self):
        """Run reply_later's work synchronously so the test sees the result."""
        def start(thread_self):
            thread_self.run()
        return patch.object(cis_llm.threading.Thread, "start", start)

    def test_representative_schedules_scripted_mail_then_swaps_in_model_text(self):
        self.write({"roles": {"representative": {"model": "svc:4b", "prompt": "You are {name}, {department}."}}})
        app = self.app()
        with self.run_now(), patch.object(cis_llm, "_post",
                                          return_value={"message": {"content": "Try a weekday flight. -- Martha"}}) as post:
            result = cis_experience.request_representative(app, "travel", "cheapest fare to Denver?")
        self.assertEqual(result, "Question sent to Martha/Travel; an EasyPlex reply will follow.")
        scripted = app.cis_dynamic.schedule_event.call_args[0][2]["body"]
        self.assertIn("I reviewed your travel question.", scripted)
        self.assertEqual(post.call_args[0][1]["messages"][0]["content"], "You are Martha/Travel, Travel.")
        app.cis_dynamic.update_event_payload.assert_called_once_with(
            app, 42, {"body": "Your question: cheapest fare to Denver?\n\nTry a weekday flight. -- Martha"})

    def test_representative_without_config_sends_scripted_only(self):
        app = self.app()
        cis_experience.request_representative(app, "travel", "cheapest fare to Denver?")
        self.assertIn("I reviewed your travel question.", app.cis_dynamic.schedule_event.call_args[0][2]["body"])
        app.cis_dynamic.update_event_payload.assert_not_called()

    def test_warranty_mail_scripted_first_then_model(self):
        self.write({"roles": {"warranty": {"model": "svc:4b", "prompt": "Vendor for {product}.", "multiline": True}}})
        app = self.app()
        app.forum_threads = {}
        app.save_json_atomic = Mock()
        app.cis_dynamic.load_state.return_value = {}
        app.cis_dynamic.simulation_day.return_value = types.SimpleNamespace(strftime=lambda f: "12/01/88")
        asset = {"id": "A1", "name": "Hayes Smartmodem 2400", "sku": "HAY2400"}
        with self.run_now(), patch.object(cis_ownership, "_asset", return_value=dict(asset)), \
                patch.object(cis_llm, "_post", return_value={"message": {"content": "Check the cord.\n\nThen the switches."}}) as post:
            cis_ownership.warranty(app, "A1", "no carrier after 5 minutes")
        opening = "We received your report for Hayes Smartmodem 2400: no carrier after 5 minutes"
        self.assertEqual(app.cis_dynamic.schedule_event.call_args[0][2]["body"],
                         opening + "\n\nA vendor response and return guidance will follow.")
        self.assertEqual(post.call_args[0][1]["messages"][0]["content"], "Vendor for Hayes Smartmodem 2400.")
        app.cis_dynamic.update_event_payload.assert_called_once_with(
            app, 42, {"body": opening + "\n\nCheck the cord.\n\nThen the switches."})


if __name__ == "__main__":
    unittest.main()
