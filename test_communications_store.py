import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import compuserve as app
import cis_communications as comm
import cis_store
import cis_poster
import cis_ownership


class CommunicationsStoreTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        for name, value in [('BASE_DIR', Path(directory.name)), ('current_user_id', '70000,0001'),
                            ('current_handle', 'Alice')]:
            patcher = patch.object(app, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_listing_is_opt_in_and_delete_preserves_other_data(self):
        self.assertFalse(comm.state(app).get('directory'))
        comm.save_listing(app, 'COMPUTERS', 'Macintosh enthusiast')
        record = comm.state(app)['directory'][app.current_user_id]
        self.assertEqual(set(record), {'user_id', 'handle', 'category', 'description'})
        comm.save_file(app, 'notes', 'private')
        with patch.object(comm, 'input', return_value='Y'), patch.object(app, 'ansi_scroll'):
            comm.directory(app, '4')
        self.assertFalse(comm.state(app)['directory'])
        self.assertEqual(comm.state(app)['files'][app.current_user_id]['notes'], 'private')

    def test_board_persistence_owner_deletion_and_ids(self):
        first = comm.post(app, 'HARDWARE', 'Modem help', 'Which cable?')
        with patch.object(app, 'current_user_id', '70000,0002'):
            comm.delete_post(app, first)
            self.assertEqual(len(comm.state(app)['bulletins']), 1)
        comm.delete_post(app, first)
        second = comm.post(app, 'HARDWARE', 'Solved', 'Correct cable fitted.')
        self.assertGreater(second, first)
        self.assertIsNone(comm.post(app, 'X', 'X', 'x' * (comm.LIMIT + 1)))

    def test_per_isolation_and_mail_composition(self):
        comm.save_file(app, 'letter', 'Hello\nWorld')
        with patch.object(app, 'current_user_id', '70000,0002'), patch.object(comm, 'input', return_value='M'), patch.object(app, 'ansi_scroll') as output:
            comm.personal_files(app)
            self.assertFalse(any('letter' in str(call) for call in output.call_args_list))
        with patch.object(comm, 'input', return_value='1'), patch.object(app, 'ansi_scroll'), patch.object(app.cis_mail, 'compose') as compose:
            comm.personal_files(app, use_for_mail=True)
            compose.assert_called_once_with(app, initial_lines=['Hello', 'World'])

    def test_upload_limits_and_remote_path_protection(self):
        path = app.BASE_DIR / 'letter.txt'
        path.write_text('Hello\nWorld', encoding='utf-8')
        with patch.dict('os.environ', {'CIS_WEB_TERMINAL': '0', 'CIS_REMOTE_TERMINAL': '0'}), patch.object(comm, 'input', side_effect=['L', str(path)]):
            self.assertEqual(comm.upload_text(app), 'Hello\nWorld')
        path.write_bytes(b'x' * (comm.LIMIT + 1))
        with patch.dict('os.environ', {'CIS_WEB_TERMINAL': '0', 'CIS_REMOTE_TERMINAL': '0'}), patch.object(comm, 'input', side_effect=['L', str(path)]), patch.object(app, 'ansi_scroll'):
            self.assertIsNone(comm.upload_text(app))
        with patch.dict('os.environ', {'CIS_WEB_TERMINAL': '1'}), patch.object(comm, 'input') as prompt, patch.object(app, 'line_editor', return_value='pasted'), patch.object(app, 'ansi_scroll'):
            self.assertEqual(comm.upload_text(app), 'pasted')
            prompt.assert_not_called()

    def test_per_file_sends_real_easyplex_message(self):
        comm.save_file(app, 'letter', 'Hello\nWorld')
        with (patch.object(comm, 'input', return_value='1'),
              patch.object(app.cis_mail, 'input', side_effect=['70000,0002', 'Test letter']),
              patch.object(app, 'input', return_value='SAVE'),
              patch.object(app, 'profiles', {'70000,0002': {}}),
              patch.object(app, 'current_profile', {}), patch.object(app, 'ansi_scroll')):
            comm.personal_files(app, use_for_mail=True)
        messages = app.load_json('easyplex.json', default=[])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['to'], '70000,0002')
        self.assertEqual(messages[0]['body'], 'Hello\nWorld')
        self.assertEqual(comm.state(app)['files'][app.current_user_id]['letter'], 'Hello\nWorld')

    def test_store_computer_shortcut_and_sku_compatibility(self):
        with (patch.object(app, 'input', side_effect=['PC', 'K', '2004', 'M']),
              patch.object(app, 'clear'), patch.object(app, 'header_bar'),
              patch.object(app, 'ansi_scroll') as output):
            app.comp_u_store()
        lines = '\n'.join(str(call.args[0]) for call in output.call_args_list)
        self.assertIn('Macintosh Plus - 1MB Desktop', lines)
        self.assertIn('Showing catalog guidance for MACINTOSH PLUS', lines)

    def test_poster_and_go_routes(self):
        with patch.object(comm, 'personal_files') as files:
            app.open_go_destination(app.go_map['GO PER'], ['main'])
            files.assert_called_once_with(app)
        with patch.object(comm, 'mail_upload') as upload:
            cis_poster.select(app, 'poster_mail', '3', ['main'])
            upload.assert_called_once_with(app)
        with patch.object(comm, 'bulletin') as board:
            cis_poster.select(app, 'poster_bulletin', '', ['main'])
            board.assert_called_once_with(app)

    def test_computer_accessories_checkout_and_ownership(self):
        computers = cis_store.search(category='COMPUTERS')
        self.assertEqual(len(computers), 13)
        for computer in computers:
            self.assertTrue(computer['configuration'])
            system, products = cis_store.compatible_products(str(computer['sku']))
            self.assertEqual(system, computer['system'])
            self.assertTrue(any(p['category'] == 'COMPUTER ACCESSORIES' for p in products))
        _, plus = cis_store.compatible_products('2004')
        self.assertIn(2109, {p['sku'] for p in plus})
        self.assertNotIn(2110, {p['sku'] for p in plus})
        self.assertNotIn(2107, {p['sku'] for p in cis_store.compatible_products('AMIGA 500')[1]})
        cis_store.add_to_cart(app, 2004)
        cis_store.add_to_cart(app, 2106)
        order = cis_store.checkout(app)
        self.assertEqual({i['sku'] for i in order['items']}, {2004, 2106})
        self.assertEqual(len(cis_ownership.receive_order(app, order)), 2)
        self.assertEqual(cis_ownership.receive_order(app, order), [])
        self.assertIn('installed', cis_ownership.install(app, 'EQ-0001', 'MACINTOSH PLUS'))


if __name__ == '__main__':
    unittest.main()
