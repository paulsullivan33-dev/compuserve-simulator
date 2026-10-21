"""Deletion uses stable account IDs, never an editable display handle."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import cis_forums


class OwnershipTests(unittest.TestCase):
    def check_delete(self, owner, current='member-1', handle='Same Handle', sysop=False):
        message = {'id': 1, 'author': 'Same Handle'}
        if owner is not None:
            message['author_user_id'] = owner
        app = SimpleNamespace(current_user_id=current, current_handle=handle,
                              current_profile={'is_sysop': sysop},
                              forum_threads={'general': [message]},
                              save_json_atomic=Mock(), ansi_scroll=Mock())
        with patch.object(cis_forums, 'input', return_value='D'):
            cis_forums.message_actions(app, 'general', message)
        return app

    def test_matching_handle_cannot_delete_another_accounts_message(self):
        app = self.check_delete('member-2')
        self.assertEqual(len(app.forum_threads['general']), 1)
        app.save_json_atomic.assert_not_called()

    def test_owner_can_delete_after_changing_handle(self):
        self.assertEqual(self.check_delete('member-1', handle='New Handle').forum_threads['general'], [])

    def test_legacy_message_requires_sysop(self):
        self.assertEqual(len(self.check_delete(None).forum_threads['general']), 1)
        self.assertEqual(self.check_delete(None, sysop=True).forum_threads['general'], [])

    def test_anonymous_id_is_not_an_owner(self):
        self.assertEqual(len(self.check_delete(None, current=None).forum_threads['general']), 1)
