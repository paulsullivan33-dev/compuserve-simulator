"""Concurrent sessions must not erase each other's changes to shared documents."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import cis_accounts
import cis_forums
import cis_merge
import cis_security
import cis_storage
import compuserve

ALICE = "70000,0001"
BOB = "70000,0002"


class MergeRuleTests(unittest.TestCase):
    def test_dicts_merge_field_by_field(self):
        base = {ALICE: {"cb_status": "", "disabled": False}}
        mine = {ALICE: {"cb_status": "AWAY", "disabled": False}}
        theirs = {ALICE: {"cb_status": "", "disabled": True}, BOB: {"handle": "B"}}
        self.assertEqual(cis_merge.merge(base, mine, theirs), {
            ALICE: {"cb_status": "AWAY", "disabled": True}, BOB: {"handle": "B"}})

    def test_unchanged_copy_takes_stored_version(self):
        self.assertEqual(cis_merge.merge({"a": 1}, {"a": 1}, {"a": 2}), {"a": 2})

    def test_deleted_key_is_removed(self):
        self.assertEqual(cis_merge.merge({"a": 1, "b": 2}, {"a": 1}, {"a": 1, "b": 2, "c": 3}), {"a": 1, "c": 3})

    def test_id_lists_keep_both_sides_additions(self):
        base = [{"id": 1, "body": "x"}]
        mine = [{"id": 1, "body": "x"}, {"id": 2, "body": "mine"}]
        theirs = [{"id": 1, "body": "edited"}, {"id": 3, "body": "theirs"}]
        self.assertEqual(cis_merge.merge(base, mine, theirs), [
            {"id": 1, "body": "edited"}, {"id": 3, "body": "theirs"}, {"id": 2, "body": "mine"}])

    def test_id_collision_renumbers_this_sessions_item(self):
        base = [{"id": 1}]
        mine = [{"id": 1}, {"id": 2, "body": "mine"}]
        theirs = [{"id": 1}, {"id": 2, "body": "theirs"}]
        self.assertEqual(cis_merge.merge(base, mine, theirs), [
            {"id": 1}, {"id": 2, "body": "theirs"}, {"id": 3, "body": "mine"}])

    def test_id_list_item_deleted_here_stays_deleted(self):
        base = [{"id": 1}, {"id": 2}]
        self.assertEqual(cis_merge.merge(base, [{"id": 1}], [{"id": 1}, {"id": 2}, {"id": 3}]), [{"id": 1}, {"id": 3}])

    def test_plain_lists_merge_additions_and_removals(self):
        base = ["cb", "pets"]
        mine = ["cb", "guitar"]
        theirs = ["cb", "pets", "trains"]
        self.assertEqual(cis_merge.merge(base, mine, theirs), ["cb", "trains", "guitar"])

    def test_refresh_keeps_nested_identity(self):
        profile = {"handle": "A"}
        target = {ALICE: profile, "gone": {}}
        cis_merge.refresh_in_place(target, {ALICE: {"handle": "A2"}, BOB: {}})
        self.assertIs(target[ALICE], profile)
        self.assertEqual(target, {ALICE: {"handle": "A2"}, BOB: {}})


class ConcurrentSessionTests(unittest.TestCase):
    """This process is session A; direct storage writes play session B."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.base = Path(directory.name)
        base_dir = patch.object(compuserve, "BASE_DIR", self.base)
        base_dir.start()
        self.addCleanup(base_dir.stop)
        baselines = patch.object(compuserve, "_document_baselines", {})
        baselines.start()
        self.addCleanup(baselines.stop)
        activity = patch.object(cis_accounts, "_activity")
        activity.start()
        self.addCleanup(activity.stop)

    def load(self, filename, data):
        cis_storage.write_json_atomic(self.base, filename, data)
        loaded = compuserve.load_json(filename, default={})
        attribute = {"profiles.json": "profiles", "forums.json": "forum_threads"}[filename]
        patcher = patch.object(compuserve, attribute, loaded)
        patcher.start()
        self.addCleanup(patcher.stop)
        return loaded

    def other_session(self, filename, mutator):
        cis_storage.update_json_atomic(self.base, filename, {}, mutator)

    def stored(self, filename):
        return cis_storage.load_json(self.base, filename, default={})

    def test_saving_profiles_keeps_other_sessions_changes(self):
        profiles = self.load("profiles.json", {ALICE: {"handle": "A", "disabled": False}})
        alice = profiles[ALICE]

        def sysop_elsewhere(data):
            data[ALICE]["disabled"] = True
            data[BOB] = {"handle": "B"}
        self.other_session("profiles.json", sysop_elsewhere)

        alice["cb_status"] = "AWAY"
        compuserve.save_profiles()
        stored = self.stored("profiles.json")
        self.assertTrue(stored[ALICE]["disabled"])  # the other session's change survives
        self.assertEqual(stored[ALICE]["cb_status"], "AWAY")
        self.assertIn(BOB, stored)
        # This session now sees the merged state through the same objects.
        self.assertIs(profiles[ALICE], alice)
        self.assertTrue(alice["disabled"])
        self.assertIn(BOB, profiles)

    def test_new_accounts_get_distinct_ids_across_sessions(self):
        self.load("profiles.json", {})
        self.other_session("profiles.json", lambda data: data.update({"71000,0001": {"handle": "B"}}))
        app = compuserve
        with patch.object(compuserve, "password_input", side_effect=["secret", "secret"]), \
                patch.object(compuserve, "ansi_scroll"), patch.object(cis_accounts, "_send_welcome_mail"):
            user_id = cis_accounts.register_new_account(app)
        self.assertEqual(user_id, "71000,0002")
        stored = self.stored("profiles.json")
        self.assertEqual(stored["71000,0001"], {"handle": "B"})
        self.assertTrue(cis_security.verify_password("secret", stored[user_id]["password_hash"]))

    def test_failed_logins_add_up_across_parallel_sessions(self):
        self.load("profiles.json", {ALICE: {"password_hash": cis_security.hash_password("correct")}})
        self.other_session("profiles.json", lambda data: data[ALICE].update(failed_logins=2))
        with patch.object(compuserve, "password_input", side_effect=["wrong", "correct"]) as prompt, \
                patch.object(compuserve, "ansi_scroll"):
            self.assertFalse(cis_accounts.authenticate(compuserve, ALICE))
        self.assertEqual(prompt.call_count, 1)
        stored = self.stored("profiles.json")
        self.assertEqual(stored[ALICE]["failed_logins"], 3)
        self.assertTrue(stored[ALICE]["locked"])

    def test_forum_posts_from_two_sessions_both_survive_with_unique_ids(self):
        self.load("forums.json", {"sample": [{"id": 1001, "subject": "seed"}]})
        self.other_session("forums.json", lambda data: data["sample"].append({"id": 1002, "subject": "B's post"}))
        app = Mock(wraps=compuserve)
        app.forum_threads = compuserve.forum_threads
        app.merge_save = compuserve.merge_save
        app.SIMULATION_DATE, app.current_handle, app.current_user_id = "12/01/88", "A", ALICE
        app.ansi_scroll, app.cis_dynamic, app.cis_reference = Mock(), Mock(), Mock()
        app.cis_reference.suggest_records.return_value = []
        app.cis_dynamic.begin_forum_case.return_value = None
        cis_forums.post(app, "sample", "A's post", "body")
        stored = self.stored("forums.json")["sample"]
        self.assertEqual([(m["id"], m["subject"]) for m in stored],
                         [(1001, "seed"), (1002, "B's post"), (1003, "A's post")])
        self.assertEqual(len(compuserve.forum_threads["sample"]), 3)


if __name__ == "__main__":
    unittest.main()
