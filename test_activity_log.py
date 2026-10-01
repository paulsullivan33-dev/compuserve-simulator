"""Tests for the telnet/sim activity log (cis_activity + event wiring)."""
import asyncio
import io
import json
import os
import tempfile
import types
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

import cis_activity
import cis_accounts
import compuserve
import telnet_app


class ActivityLogTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = os.path.join(self.tmp.name, "activity.log")
        self._patcher = patch.dict(os.environ, {"CIS_ACTIVITY_LOG": self.log})
        self._patcher.start()

    def tearDown(self):
        self._patcher.stop()
        self.tmp.cleanup()

    def _lines(self):
        with open(self.log, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def test_log_event_writes_json_line_with_fields(self):
        cis_activity.log_event(
            "login", session_id="abc123", client_ip="1.2.3.4",
            user_id="70000,0001", detail={"attempt": 2},
        )
        (event,) = self._lines()
        self.assertEqual(event["event"], "login")
        self.assertEqual(event["session_id"], "abc123")
        self.assertEqual(event["client_ip"], "1.2.3.4")
        self.assertEqual(event["user_id"], "70000,0001")
        self.assertEqual(event["detail"], {"attempt": 2})
        self.assertIn("ts", event)

    def test_log_event_omits_empty_fields(self):
        cis_activity.log_event("session_connected")
        (event,) = self._lines()
        self.assertEqual(set(event), {"ts", "event"})

    def test_log_event_never_raises_on_bad_path(self):
        with patch.dict(os.environ, {"CIS_ACTIVITY_LOG": "/nonexistent-dir-xyz/activity.log"}):
            cis_activity.log_event("login")  # must not raise

    def test_read_events_skips_corrupt_lines_and_limits(self):
        with open(self.log, "w", encoding="utf-8") as handle:
            handle.write('{"event": "a"}\n')
            handle.write("not json\n")
            handle.write('{"event": "b"}\n')
        events = cis_activity.read_events(limit=1)
        self.assertEqual([e["event"] for e in events], ["b"])

    def test_failed_passwords_log_attempts_then_lockout(self):
        app = types.SimpleNamespace(
            profiles={"70000,0001": {"password_hash": "x", "failed_logins": 0}},
            ansi_scroll=Mock(),
            password_input=Mock(return_value="wrong"),
            verify_password=Mock(return_value=False),
            save_profiles=Mock(),
            live_session_id="sess1",
        )
        # real hash so verify_password mock decides; simpler: stub verify False
        with patch.dict(os.environ, {"CIS_CLIENT_IP": "9.9.9.9"}):
            self.assertFalse(cis_accounts.authenticate(app, "70000,0001"))
        events = self._lines()
        kinds = [e["event"] for e in events]
        self.assertEqual(kinds, ["login_failed", "login_failed", "login_failed", "account_locked"])
        self.assertEqual([e["detail"]["attempt"] for e in events[:3]], [1, 2, 3])
        self.assertTrue(all(e["user_id"] == "70000,0001" for e in events))
        self.assertTrue(all(e["client_ip"] == "9.9.9.9" for e in events))
        self.assertTrue(app.profiles["70000,0001"]["locked"])

    def test_locked_account_attempt_logs_denied(self):
        app = types.SimpleNamespace(
            profiles={"70000,0001": {
                "locked": True,
                "locked_at": datetime.now(timezone.utc).isoformat(),
            }},
            ansi_scroll=Mock(),
            save_profiles=Mock(),
            live_session_id="sess1",
        )
        self.assertFalse(cis_accounts.authenticate(app, "70000,0001"))
        (event,) = self._lines()
        self.assertEqual(event["event"], "login_denied")
        self.assertEqual(event["detail"], {"reason": "locked"})

    def test_expired_lockout_unlocks_and_logs_event(self):
        app = types.SimpleNamespace(
            profiles={"70000,0001": {
                "password_hash": "x",
                "locked": True,
                "failed_logins": 3,
                "locked_at": (datetime.now(timezone.utc)
                              - timedelta(minutes=cis_accounts.LOCKOUT_MINUTES + 1)).isoformat(),
            }},
            ansi_scroll=Mock(),
            password_input=Mock(return_value="right"),
            verify_password=Mock(return_value=True),
            save_profiles=Mock(),
            live_session_id="sess1",
        )
        self.assertTrue(cis_accounts.authenticate(app, "70000,0001"))
        profile = app.profiles["70000,0001"]
        self.assertFalse(profile["locked"])
        self.assertNotIn("locked_at", profile)
        self.assertEqual(profile["failed_logins"], 0)
        events = self._lines()
        kinds = [e["event"] for e in events]
        self.assertEqual(kinds, ["account_unlocked"])
        self.assertEqual(events[0]["detail"], {"reason": "lockout_expired"})

    def test_lockout_without_timestamp_is_treated_as_expired(self):
        # Locks written before locked_at existed clear on the next attempt.
        app = types.SimpleNamespace(
            profiles={"70000,0001": {"password_hash": "x", "locked": True}},
            ansi_scroll=Mock(),
            password_input=Mock(return_value="right"),
            verify_password=Mock(return_value=True),
            save_profiles=Mock(),
            live_session_id="sess1",
        )
        self.assertTrue(cis_accounts.authenticate(app, "70000,0001"))
        self.assertFalse(app.profiles["70000,0001"]["locked"])
        (event,) = self._lines()
        self.assertEqual(event["event"], "account_unlocked")

    def test_lockout_records_timestamp(self):
        app = types.SimpleNamespace(
            profiles={"70000,0001": {"password_hash": "x", "failed_logins": 0}},
            ansi_scroll=Mock(),
            password_input=Mock(return_value="wrong"),
            verify_password=Mock(return_value=False),
            save_profiles=Mock(),
            live_session_id="sess1",
        )
        self.assertFalse(cis_accounts.authenticate(app, "70000,0001"))
        locked_at = app.profiles["70000,0001"]["locked_at"]
        parsed = datetime.fromisoformat(locked_at)
        self.assertLess(datetime.now(timezone.utc) - parsed, timedelta(minutes=1))

    def test_reject_busy_logs_event(self):
        class FakeWriter:
            def __init__(self):
                self.data = b""
                self.closed = False

            def write(self, data):
                self.data += data

            async def drain(self):
                pass

            def close(self):
                self.closed = True

            async def wait_closed(self):
                pass

        writer = FakeWriter()
        asyncio.run(telnet_app._reject_busy(writer, ("5.6.7.8", 4321)))
        self.assertIn(b"busy", writer.data)
        (event,) = self._lines()
        self.assertEqual(event["event"], "session_rejected_busy")
        self.assertEqual(event["client_ip"], "5.6.7.8")

    def test_peer_ip(self):
        self.assertEqual(telnet_app._peer_ip(("1.2.3.4", 1234)), "1.2.3.4")
        self.assertIsNone(telnet_app._peer_ip(None))

    def test_input_reason_maps_abrupt_disconnect(self):
        async def go():
            async def boom(*args, **kwargs):
                raise ConnectionResetError("client vanished")
            async def ok(*args, **kwargs):
                return "client_closed"
            with patch.object(telnet_app, "forward_telnet_input", side_effect=boom):
                self.assertEqual(
                    await telnet_app._input_reason(None, None, None, "s", None, None),
                    "client_error",
                )
            with patch.object(telnet_app, "forward_telnet_input", side_effect=ok):
                self.assertEqual(
                    await telnet_app._input_reason(None, None, None, "s", None, None),
                    "client_closed",
                )
        asyncio.run(go())


class PasswordEchoTest(unittest.TestCase):
    def test_term_selected_enables_echo_and_sends_will_echo(self):
        state = telnet_app._EchoState()
        self.assertFalse(state.enabled)  # no echo before terminal selection
        tr = telnet_app._EchoTranslator(state)
        fwd, iac = tr.feed(b"ready" + telnet_app._TERM_SELECTED_MARKER + b"menu")
        self.assertEqual(fwd, b"readymenu")
        self.assertEqual(iac, b"\xff\xfb\x01")  # IAC WILL ECHO, once
        self.assertTrue(state.enabled)

    def test_echo_translator_strips_markers_and_toggles_echo(self):
        state = telnet_app._EchoState()
        tr = telnet_app._EchoTranslator(state)
        # Password markers only flip the flag; WILL ECHO went out earlier.
        fwd, iac = tr.feed(b"hello " + telnet_app._ECHO_OFF_MARKER + b"world")
        self.assertEqual(fwd, b"hello world")
        self.assertEqual(iac, b"")
        self.assertFalse(state.enabled)  # server stops echoing the password
        fwd, iac = tr.feed(b"done" + telnet_app._ECHO_ON_MARKER)
        self.assertEqual(fwd, b"done")
        self.assertEqual(iac, b"")  # no WONT ECHO: server keeps echoing
        self.assertTrue(state.enabled)

    def test_echo_translator_handles_split_marker(self):
        state = telnet_app._EchoState()
        tr = telnet_app._EchoTranslator(state)
        fwd, iac = tr.feed(b"abc\x00[ECHO")
        self.assertEqual((fwd, iac), (b"abc", b""))
        fwd, iac = tr.feed(b"OFF]\x00def")
        self.assertEqual(fwd, b"def")
        self.assertEqual(iac, b"")
        self.assertFalse(state.enabled)

    def test_password_input_suppresses_echo_for_remote_terminal(self):
        buf = io.StringIO()
        env = {"CIS_REMOTE_TERMINAL": "1", "CIS_WEB_TERMINAL": ""}
        with patch.dict(os.environ, env), \
             patch.object(compuserve.sys, "stdout", buf), \
             patch("builtins.input", return_value="s3cret") as mock_input:
            self.assertEqual(compuserve.password_input("Password: "), "s3cret")
        mock_input.assert_called_once_with("Password: ")
        out = buf.getvalue()
        self.assertTrue(out.startswith(compuserve.ECHO_SUPPRESS_MARKER))
        self.assertTrue(out.endswith(compuserve.ECHO_RESTORE_MARKER))

    def test_password_input_uses_getpass_locally(self):
        env = {"CIS_REMOTE_TERMINAL": "", "CIS_WEB_TERMINAL": ""}
        with patch.dict(os.environ, env), \
             patch("getpass.getpass", return_value="pw") as mock_getpass:
            self.assertEqual(compuserve.password_input(), "pw")
        mock_getpass.assert_called_once_with("Password: ")


if __name__ == "__main__":
    unittest.main()
