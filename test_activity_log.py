"""Tests for the telnet/sim activity log (cis_activity + event wiring)."""
import asyncio
import json
import os
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

import cis_activity
import cis_accounts
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
            profiles={"70000,0001": {"locked": True}},
            ansi_scroll=Mock(),
            save_profiles=Mock(),
            live_session_id="sess1",
        )
        self.assertFalse(cis_accounts.authenticate(app, "70000,0001"))
        (event,) = self._lines()
        self.assertEqual(event["event"], "login_denied")
        self.assertEqual(event["detail"], {"reason": "locked"})

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


if __name__ == "__main__":
    unittest.main()
