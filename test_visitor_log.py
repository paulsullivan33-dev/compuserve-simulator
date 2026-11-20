"""Tests for the visitor log's ``wrote`` events (compuserve.record_write
+ the cis_forums / cis_mail wiring + cis_activity rendering)."""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import Mock, patch

import cis_activity
import cis_forums
import cis_mail
import compuserve


class _LogFileMixin(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = os.path.join(self.tmp.name, "activity.log")
        self._patcher = patch.dict(
            os.environ, {"CIS_ACTIVITY_LOG": self.log, "CIS_CLIENT_IP": "9.9.9.9"}
        )
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        self.tmp.cleanup()

    def _events(self):
        with open(self.log, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]


class RecordWriteTest(_LogFileMixin):
    def _record(self, *args, **kwargs):
        with patch.object(compuserve, "current_user_id", "70000,0001"), \
             patch.object(compuserve, "current_handle", "Sysop Sam"), \
             patch.object(compuserve, "live_session_id", "sess42"):
            compuserve.record_write(*args, **kwargs)

    def test_wrote_event_carries_envelope_and_detail(self):
        self._record("forum_post", section="general", message_id=1001,
                     subject="Hello", text="First post!")
        (event,) = self._events()
        self.assertEqual(event["event"], "wrote")
        self.assertEqual(event["user_id"], "70000,0001")
        self.assertEqual(event["session_id"], "sess42")
        self.assertEqual(event["client_ip"], "9.9.9.9")
        self.assertEqual(event["detail"]["area"], "forum_post")
        self.assertEqual(event["detail"]["handle"], "Sysop Sam")
        self.assertEqual(event["detail"]["section"], "general")
        self.assertEqual(event["detail"]["message_id"], 1001)
        self.assertEqual(event["detail"]["subject"], "Hello")
        self.assertEqual(event["detail"]["text"], "First post!")
        self.assertNotIn("truncated", event["detail"])

    def test_long_text_is_capped_and_marked(self):
        self._record("mail", to="70000,0002", subject="Long", text="x" * 1500)
        (event,) = self._events()
        self.assertEqual(len(event["detail"]["text"]), compuserve._WRITE_TEXT_LIMIT)
        self.assertTrue(event["detail"]["truncated"])

    def test_record_write_never_raises_on_bad_path(self):
        with patch.dict(os.environ, {"CIS_ACTIVITY_LOG": "/nonexistent-dir-xyz/a.log"}):
            self._record("cb", channel="1", text="hello")  # must not raise


class ForumPostWriteTest(_LogFileMixin):
    def _app(self, with_recorder=True):
        app = SimpleNamespace(
            session_state=SimpleNamespace(note_action=Mock()),
            SIMULATION_DATE="11/19/26",
            current_handle="Visitor Vic",
            current_user_id="70000,0001",
            forum_threads={},
            save_json_atomic=Mock(),
            ansi_scroll=Mock(),
            cis_dynamic=SimpleNamespace(
                record_activity=Mock(),
                begin_forum_case=Mock(return_value=None),
            ),
            cis_reference=SimpleNamespace(suggest_records=Mock(return_value=[])),
        )
        if with_recorder:
            app.record_write = Mock()
        return app

    def test_post_records_the_write(self):
        app = self._app()
        cis_forums.post(app, "general", "Greetings", "Hello from 1986!")
        app.record_write.assert_called_once()
        args, kwargs = app.record_write.call_args
        self.assertEqual(args, ("forum_post",))
        self.assertEqual(kwargs["section"], "general")
        self.assertEqual(kwargs["subject"], "Greetings")
        self.assertEqual(kwargs["text"], "Hello from 1986!")
        stored = app.forum_threads["general"][0]
        self.assertEqual(kwargs["message_id"], stored["id"])

    def test_post_works_without_a_recorder(self):
        app = self._app(with_recorder=False)
        cis_forums.post(app, "general", "Greetings", "Hello!")
        self.assertEqual(len(app.forum_threads["general"]), 1)


class MailWriteTest(_LogFileMixin):
    def test_compose_records_the_write(self):
        app = SimpleNamespace(
            load_json=Mock(return_value=[]),
            save_json_atomic=Mock(),
            ansi_scroll=Mock(),
            current_user_id="70000,0001",
            current_profile={},
            profiles={"70000,0002": {"handle": "Pen Pal"}},
            SIMULATION_DATE="11/19/26",
            session_state=SimpleNamespace(note_action=Mock()),
            record_write=Mock(),
            line_editor=Mock(return_value="Meet you on CB at eight."),
            cis_drafts=SimpleNamespace(
                get_draft=Mock(return_value=None),
                save_draft=Mock(),
                delete_draft=Mock(),
            ),
        )
        with patch.object(cis_mail, "input", return_value="Dinner Friday?"):
            cis_mail.compose(app, recipient="70000,0002")
        app.record_write.assert_called_once()
        args, kwargs = app.record_write.call_args
        self.assertEqual(args, ("mail",))
        self.assertEqual(kwargs["to"], "70000,0002")
        self.assertEqual(kwargs["subject"], "Dinner Friday?")
        self.assertEqual(kwargs["text"], "Meet you on CB at eight.")


class FormatEventTest(_LogFileMixin):
    _WROTE = {
        "ts": "2026-11-19T21:44:00", "event": "wrote",
        "user_id": "71000,0034", "client_ip": "71.10.240.227",
        "detail": {"area": "forum_post", "section": "general",
                   "message_id": 1001, "subject": "Hello",
                   "text": "Line one\nLine two"},
    }

    def test_wrote_event_renders_header_and_text(self):
        lines = cis_activity.format_event(self._WROTE)
        self.assertIn("71000,0034", lines[0])
        self.assertIn("forum_post", lines[0])
        self.assertIn("subject=Hello", lines[0])
        self.assertEqual(lines[1:], ["    Line one", "    Line two"])

    def test_truncated_marker_is_shown(self):
        event = dict(self._WROTE, detail=dict(self._WROTE["detail"], truncated=True))
        lines = cis_activity.format_event(event)
        self.assertTrue(any("truncated" in line for line in lines))

    def test_other_events_stay_one_line(self):
        event = {"ts": "2026-11-19T21:44:00", "event": "login", "user_id": "1"}
        self.assertEqual(len(cis_activity.format_event(event)), 1)

    def test_cli_writes_filter(self):
        with open(self.log, "w", encoding="utf-8") as handle:
            handle.write(json.dumps({"ts": "t", "event": "login"}) + "\n")
            handle.write(json.dumps(self._WROTE) + "\n")
        out = io.StringIO()
        with redirect_stdout(out):
            cis_activity.main(["--tail", "10", "--writes"])
        text = out.getvalue()
        self.assertIn("forum_post", text)
        self.assertNotIn("login", text)


if __name__ == "__main__":
    unittest.main()
