"""Tests for cis_ntfy (best-effort ntfy session notifications)."""
import json
import os
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

import cis_ntfy


class NtfySendTest(unittest.TestCase):
    def _no_url(self):
        patcher = patch.dict(os.environ)
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("CIS_NTFY_URL", None)

    def test_send_without_url_is_silent_noop(self):
        self._no_url()
        with patch("urllib.request.urlopen") as urlopen:
            self.assertFalse(cis_ntfy.send("t", "m"))
            urlopen.assert_not_called()

    def test_send_posts_title_tags_and_body(self):
        with patch.dict(os.environ, {"CIS_NTFY_URL": "https://ntfy.sh/x"}):
            with patch("urllib.request.urlopen") as urlopen:
                resp = MagicMock()
                resp.__enter__.return_value = resp
                urlopen.return_value = resp
                self.assertTrue(
                    cis_ntfy.send("Hello", "body text", tags=("tada",))
                )
                (req,), kwargs = urlopen.call_args
                self.assertEqual(req.full_url, "https://ntfy.sh/x")
                self.assertEqual(req.data, b"body text")
                self.assertEqual(req.get_header("Title"), "Hello")
                self.assertEqual(req.get_header("Tags"), "tada")
                self.assertEqual(kwargs["timeout"], cis_ntfy.TIMEOUT_S)

    def test_send_without_tags_omits_header(self):
        with patch.dict(os.environ, {"CIS_NTFY_URL": "https://ntfy.sh/x"}):
            with patch("urllib.request.urlopen") as urlopen:
                resp = MagicMock()
                resp.__enter__.return_value = resp
                urlopen.return_value = resp
                cis_ntfy.send("Hello", "body")
                (req,), _ = urlopen.call_args
                self.assertIsNone(req.get_header("Tags"))

    def test_send_never_raises_on_network_error(self):
        with patch.dict(os.environ, {"CIS_NTFY_URL": "https://ntfy.sh/x"}):
            with patch(
                "urllib.request.urlopen", side_effect=OSError("net down")
            ):
                self.assertFalse(cis_ntfy.send("t", "m"))  # must not raise

    def test_send_async_without_url_spawns_no_thread(self):
        self._no_url()
        with patch("threading.Thread") as thread:
            cis_ntfy.send_async("t", "m")
            thread.assert_not_called()

    def test_send_async_runs_send_in_daemon_thread(self):
        with patch.dict(os.environ, {"CIS_NTFY_URL": "https://ntfy.sh/x"}):
            with patch("threading.Thread") as thread, patch.object(
                cis_ntfy, "send", return_value=True
            ) as send:
                cis_ntfy.send_async("t", "m", tags=("tada",))
                thread.assert_called_once()
                _, kwargs = thread.call_args
                self.assertTrue(kwargs["daemon"])
                self.assertEqual(kwargs["args"], ("t", "m", ("tada",)))
                kwargs["target"](*kwargs["args"])
                send.assert_called_once_with("t", "m", ("tada",))


class FormatDurationTest(unittest.TestCase):
    def test_seconds(self):
        self.assertEqual(cis_ntfy.format_duration(5), "5s")
        self.assertEqual(cis_ntfy.format_duration(59), "59s")

    def test_minutes(self):
        self.assertEqual(cis_ntfy.format_duration(60), "1m 00s")
        self.assertEqual(cis_ntfy.format_duration(187), "3m 07s")

    def test_hours(self):
        self.assertEqual(cis_ntfy.format_duration(3600), "1h 00m")
        self.assertEqual(cis_ntfy.format_duration(7500), "2h 05m")

    def test_negative_clamps_to_zero(self):
        self.assertEqual(cis_ntfy.format_duration(-3), "0s")


class RecordLogoutTest(unittest.TestCase):
    """compuserve._record_logout() writes the logout event + notifies."""

    def setUp(self):
        import compuserve  # heavy module; already imported by other tests

        self.compuserve = compuserve
        self.tmp = tempfile.TemporaryDirectory()
        self.log = os.path.join(self.tmp.name, "activity.log")
        self._env = patch.dict(
            os.environ,
            {
                "CIS_ACTIVITY_LOG": self.log,
                "CIS_CLIENT_IP": "9.9.9.9",
                "CIS_TRANSPORT": "TELNET",
            },
        )
        self._env.start()
        self._stash = {
            k: getattr(compuserve, k)
            for k in (
                "current_user_id",
                "current_handle",
                "current_profile",
                "session_start",
                "live_session_id",
            )
        }
        compuserve.current_user_id = "71000,0004"
        compuserve.current_handle = "Sysop"
        compuserve.current_profile = {"handle": "Sysop"}
        compuserve.session_start = time.time() - 125
        compuserve.live_session_id = "sess123"

    def tearDown(self):
        for key, value in self._stash.items():
            setattr(self.compuserve, key, value)
        self._env.stop()
        self.tmp.cleanup()

    def _lines(self):
        with open(self.log, encoding="utf-8") as handle:
            return [json.loads(line) for line in handle if line.strip()]

    def test_logout_event_and_ntfy(self):
        with patch.object(cis_ntfy, "send", return_value=True) as send:
            self.compuserve._record_logout()
        (event,) = self._lines()
        self.assertEqual(event["event"], "logout")
        self.assertEqual(event["user_id"], "71000,0004")
        self.assertEqual(event["client_ip"], "9.9.9.9")
        self.assertEqual(event["session_id"], "sess123")
        self.assertEqual(event["detail"]["handle"], "Sysop")
        self.assertEqual(event["detail"]["transport"], "TELNET")
        self.assertGreaterEqual(event["detail"]["duration_s"], 120)
        (title, message), kwargs = send.call_args
        self.assertEqual(title, "CompuServe logout")
        self.assertIn("71000,0004", message)
        self.assertIn("2m 05s", message)
        self.assertEqual(kwargs["tags"], ("zzz",))

    def test_logout_never_raises_with_missing_state(self):
        self.compuserve.current_profile = None
        self.compuserve.session_start = None
        with patch.object(
            cis_ntfy, "send", side_effect=RuntimeError("boom")
        ):
            self.compuserve._record_logout()  # must not raise
        (event,) = self._lines()
        self.assertEqual(event["event"], "logout")
        self.assertEqual(event["detail"]["duration_s"], 0)


if __name__ == "__main__":
    unittest.main()
