"""Password reset and lockout behavior that must hold across connections."""
import os
import types
import unittest
from unittest.mock import Mock, patch

import cis_accounts
import cis_security
import cis_sysop

USER = "70000,0001"


def make_app(profiles, passwords):
    return types.SimpleNamespace(
        profiles=profiles,
        ansi_scroll=Mock(),
        password_input=Mock(side_effect=passwords),
        verify_password=cis_security.verify_password,
        hash_password=cis_security.hash_password,
        save_profiles=Mock(),
        live_session_id="sess",
    )


class AccountSecurityTests(unittest.TestCase):
    def setUp(self):
        # Keep activity events out of the real log.
        patcher = patch.object(cis_accounts, "_activity")
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_reset_account_cannot_be_claimed_without_the_temporary_password(self):
        profiles = {USER: {"password_hash": cis_security.hash_password("original")}}
        temporary = cis_sysop.reset_password(profiles, USER)
        app = make_app(profiles, ["guess1", "guess2", "guess3"])
        self.assertFalse(cis_accounts.authenticate(app, USER))
        self.assertTrue(profiles[USER]["locked"])
        self.assertTrue(cis_security.verify_password(temporary, profiles[USER]["password_hash"]))

    def test_temporary_password_forces_a_new_password(self):
        profiles = {USER: {"password_hash": cis_security.hash_password("original")}}
        temporary = cis_sysop.reset_password(profiles, USER)
        app = make_app(profiles, [temporary, "newpass", "newpass"])
        self.assertTrue(cis_accounts.authenticate(app, USER))
        profile = profiles[USER]
        self.assertNotIn("must_change_password", profile)
        self.assertTrue(cis_security.verify_password("newpass", profile["password_hash"]))
        self.assertFalse(cis_security.verify_password(temporary, profile["password_hash"]))

    def test_abandoned_forced_change_denies_login_and_keeps_flag(self):
        profiles = {USER: {"password_hash": cis_security.hash_password("original")}}
        temporary = cis_sysop.reset_password(profiles, USER)
        app = make_app(profiles, [temporary, "newpass", "different"])
        self.assertFalse(cis_accounts.authenticate(app, USER))
        self.assertTrue(profiles[USER]["must_change_password"])

    def test_remote_session_cannot_set_first_password_on_hashless_account(self):
        for transport in ("WEB", "TELNET"):
            with self.subTest(transport=transport), patch.dict(os.environ, {"CIS_TRANSPORT": transport}):
                profiles = {USER: {"last_handle": "TEST", "is_sysop": True}}
                app = make_app(profiles, ["attacker", "attacker"])
                self.assertFalse(cis_accounts.authenticate(app, USER))
                self.assertNotIn("password_hash", profiles[USER])
                app.password_input.assert_not_called()

    def test_console_can_still_establish_legacy_password(self):
        env = {k: v for k, v in os.environ.items() if k != "CIS_TRANSPORT"}
        with patch.dict(os.environ, env, clear=True):
            profiles = {USER: {"last_handle": "TEST"}}
            app = make_app(profiles, ["secret", "secret"])
            self.assertTrue(cis_accounts.authenticate(app, USER))
            self.assertTrue(cis_security.verify_password("secret", profiles[USER]["password_hash"]))

    def test_failures_persist_when_the_caller_disconnects_between_guesses(self):
        profiles = {USER: {"password_hash": cis_security.hash_password("correct")}}
        app = make_app(profiles, ["wrong1", "wrong2", EOFError()])
        with self.assertRaises(EOFError):
            cis_accounts.authenticate(app, USER)
        self.assertEqual(profiles[USER]["failed_logins"], 2)
        self.assertGreaterEqual(app.save_profiles.call_count, 2)
        # The next connection gets only the remaining guess before lockout.
        app = make_app(profiles, ["wrong3", "correct"])
        self.assertFalse(cis_accounts.authenticate(app, USER))
        self.assertTrue(profiles[USER]["locked"])
        self.assertEqual(app.password_input.call_count, 1)

    def test_success_clears_the_failure_count(self):
        profiles = {USER: {"password_hash": cis_security.hash_password("correct"), "failed_logins": 2}}
        app = make_app(profiles, ["correct"])
        self.assertTrue(cis_accounts.authenticate(app, USER))
        self.assertEqual(profiles[USER]["failed_logins"], 0)


if __name__ == "__main__":
    unittest.main()
