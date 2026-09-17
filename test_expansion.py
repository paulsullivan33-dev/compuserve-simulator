import io
from contextlib import ExitStack
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import compuserve as app
import cis_communications as comm
import cis_hardware as hardware
import cis_library
import cis_ownership
import cis_poster
import cis_store


class ExpansionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        for name, value in [('BASE_DIR', Path(directory.name)), ('current_user_id', '70000,0001'),
                            ('current_handle', 'Alice'), ('current_profile', {}),
                            ('connection_baud', 1200), ('SCREEN_WIDTH', 80), ('library_files', {}),
                            ('profiles', {'70000,0001': {}, '70000,0002': {}})]:
            patcher = patch.object(app, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def deliver(self, *skus):
        return cis_ownership.receive_order(app, {'number': 'ORDER-' + str(skus),
            'user_id': app.current_user_id, 'items': [dict(sku=sku, quantity=1,
            name=cis_store.find_product(sku)['name']) for sku in skus]})

    def test_catalog_setup_coverage(self):
        computers = cis_store.search(category='COMPUTERS')
        self.assertEqual({p['sku'] for p in computers}, set(hardware.SPECS))
        for sku in (2010, 2011, 2012, 2013, 2014):
            self.assertTrue(cis_store.find_product(sku)['configuration'])
            self.assertTrue(any(p['category'] == 'COMPUTER ACCESSORIES' for p in cis_store.compatible_products(str(sku))[1]))

    def test_active_machine_persists_and_is_member_scoped(self):
        assets = self.deliver(2014)
        self.assertIn('Active computer', hardware.activate(app, assets[0]['id']))
        self.assertEqual((app.SCREEN_WIDTH, app.connection_baud), (40, 300))
        self.assertEqual(hardware.snapshot(app)['memory_kb'], 32)
        with patch.object(app, 'current_user_id', '70000,0002'):
            self.assertIsNone(hardware.snapshot(app))
            self.assertIn('own equipment', hardware.activate(app, assets[0]['id']))
        self.assertEqual(hardware.snapshot(app)['sku'], 2014)
        hardware.activate(app, 'OFF')
        self.assertIsNone(hardware.snapshot(app))
        self.assertEqual((app.SCREEN_WIDTH, app.connection_baud), (80, 1200))

    def test_attachments_and_modem_rate(self):
        pc, slow, fast, cable, wrong = self.deliver(2002, 1101, 1102, 1201, 2117)
        hardware.activate(app, pc['id'])
        file = {'name': 'README.TXT'}
        self.assertIn('modem', hardware.transfer_plan(app, file, 2000)['error'])
        self.assertIn('not compatible', hardware.attach(app, wrong['id']))
        hardware.attach(app, slow['id'])
        self.assertIn('1201', hardware.transfer_plan(app, file, 2000)['error'])
        hardware.attach(app, cable['id'])
        slower = hardware.transfer_plan(app, file, 2000)['seconds']
        hardware.attach(app, slow['id'], detach=True)
        hardware.attach(app, fast['id'])
        faster = hardware.transfer_plan(app, file, 2000)['seconds']
        self.assertGreater(slower, faster)
        self.assertEqual(app.connection_baud, 2400)
        cis_ownership.return_item(app, pc['id'])
        self.assertIn('unavailable', hardware.transfer_plan(app, file, 2000)['error'])

    def test_disk_capacity_platform_and_delete(self):
        laptop = self.deliver(2014)[0]
        hardware.activate(app, laptop['id'])
        file = {'name': 'NOTE.TXT'}
        hardware.record_download(app, file, 24000, 'B')
        self.assertIn('Disk full', hardware.transfer_plan(app, {'name': 'OTHER.TXT'}, 1000)['error'])
        # Replacing a file doesn't charge its size twice.
        self.assertNotIn('error', hardware.transfer_plan(app, file, 24000))
        self.assertIn('does not match', hardware.transfer_plan(app, {'name': 'DOS.ARC', 'platforms': ['DOS']}, 10)['error'])
        self.assertIn('memory', hardware.transfer_plan(app, {'name': 'NOTE.TXT', 'min_memory_kb': 64}, 10)['error'])
        hardware.remove_file(app, 'NOTE.TXT')
        self.assertEqual(hardware.snapshot(app)['used'], 0)

    def test_bundle_upgrade_and_display_prerequisites(self):
        amiga, ram = self.deliver(2008, 2115)
        hardware.activate(app, amiga['id'])
        self.assertIn('included', hardware.attach(app, ram['id']))
        pc, monitor, card = self.deliver(2002, 2105, 1804)
        hardware.activate(app, pc['id'])
        self.assertIn('1804', hardware.attach(app, monitor['id']))
        hardware.attach(app, card['id'])
        self.assertIn('Attached', hardware.attach(app, monitor['id']))
        self.assertEqual(hardware.snapshot(app)['display'], 'VGA color')

    def test_download_uses_actual_payload_and_rejects_oversize(self):
        laptop = self.deliver(2014)[0]
        hardware.activate(app, laptop['id'])
        file = dict(name='MODEMREF.TXT', bytes=999999, number=100, description='notes', downloads=0)
        payload = cis_library.download_bytes(app, file)
        destination = cis_library.materialize_download(app, file, 'B')
        self.assertEqual(destination.read_bytes(), payload)
        self.assertEqual(hardware.snapshot(app)['used'], len(payload))
        self.assertGreater(hardware.snapshot(app)['transfer_seconds'], 0)
        large = dict(name='LARGE.TXT', bytes=30000, number=101, description='large', downloads=0)
        with self.assertRaisesRegex(ValueError, 'Disk full'):
            cis_library.materialize_download(app, large, 'B')
        self.assertFalse((app.BASE_DIR / 'downloads' / 'LARGE.TXT').exists())
        self.assertEqual(large['downloads'], 0)

    def test_failed_host_write_does_not_consume_capacity(self):
        laptop = self.deliver(2014)[0]
        hardware.activate(app, laptop['id'])
        def fail():
            raise OSError('disk unavailable')
        with self.assertRaises(OSError):
            hardware.record_download(app, {'name': 'NOTE.TXT'}, 100, 'B', writer=fail)
        self.assertEqual(hardware.snapshot(app)['used'], 0)

    def test_library_ui_and_legacy_software_platform_inference(self):
        laptop = self.deliver(2014)[0]
        hardware.activate(app, laptop['id'])
        dos_file = dict(name='MEMTST.ARC', bytes=18000, number=101, description='DOS utility', downloads=0)
        app.library_files = {'ibmhw_lib1': [dos_file]}
        self.assertEqual(hardware.platforms(app, dos_file), ['DOS'])
        with patch.object(app, 'input', return_value='B'), patch.object(app, 'ansi_scroll') as output:
            app.library_transfer(dos_file)
        self.assertTrue(any('does not match' in str(call) for call in output.call_args_list))
        file = dict(name='README.TXT', text_content='Hello world', bytes=11, number=102, description='text', downloads=0)
        with patch.object(app, 'input', return_value='B'), patch.object(app, 'ansi_scroll') as output, patch.dict(app.startup_options, {'fast_mode': True}):
            app.library_transfer(file)
        self.assertTrue(any('Transfer complete' in str(call) for call in output.call_args_list))
        self.assertEqual(hardware.snapshot(app)['used'], 11)

    def test_storage_cannot_be_detached_until_files_fit(self):
        mac, drive, modem, cable = self.deliver(2004, 2106, 1101, 1203)
        hardware.activate(app, mac['id'])
        for item in (drive, modem, cable):
            hardware.attach(app, item['id'])
        hardware.record_download(app, {'name': 'BIG.TXT'}, 1000000, 'B')
        self.assertIn('Remove downloaded files', hardware.attach(app, drive['id'], detach=True))
        hardware.remove_file(app, 'BIG.TXT')
        self.assertIn('detached', hardware.attach(app, drive['id'], detach=True))

    def test_public_file_is_snapshot_with_owner_controls_and_counts(self):
        comm.save_file(app, 'tip', 'Original tip')
        number = comm.publish_file(app, 'tip', 'A useful tip')
        comm.save_file(app, 'tip', 'Private revision')
        with patch.object(app, 'current_user_id', '70000,0002'):
            comm.remove_public_file(app, number)
            record = comm.state(app)['public_files'][0]
            path = cis_library.materialize_download(app, record, 'B')
            self.assertEqual(path.read_text(), 'Original tip')
            self.assertEqual(comm.state(app)['public_files'][0]['downloads'], 1)
        comm.remove_public_file(app, number)
        self.assertFalse(comm.state(app)['public_files'])
        self.assertEqual(comm.state(app)['files'][app.current_user_id]['tip'], 'Private revision')

    def test_society_join_discussion_leave(self):
        with patch.object(comm, 'input', side_effect=['J', '3', 'L', 'M']), patch.object(app, 'ansi_scroll'), patch.object(comm, 'bulletin') as board:
            comm.society(app)
        board.assert_called_once_with(app, category_filter='CB SOCIETY')
        self.assertFalse(comm.state(app)['society'])

    def test_color_card_delivers_only_to_valid_member(self):
        self.assertIsNone(comm.send_card(app, 'NOPE', '1', 'Hello'))
        number = comm.send_card(app, '70000,0002', '1', 'Hello\x1b[2J')
        message = app.load_json('easyplex.json', default=[])[0]
        self.assertEqual(message['id'], number)
        self.assertEqual(message['card_color'], 'MAGENTA')
        self.assertIn('HAPPY BIRTHDAY', message['body'])
        self.assertNotIn('\x1b', message['body'])
        self.assertFalse(message['read'])
        with patch.object(app, 'current_user_id', '70000,0002'), patch.object(app.cis_mail, 'input', side_effect=['1', '', 'M']), patch.object(app, 'text_page') as page, patch.object(app, 'ansi_scroll'), patch.object(app, 'clear'), patch.object(app, 'header_bar'):
            app.cis_mail.read(app)
        self.assertEqual(page.call_args.kwargs['color'], 'MAGENTA')

    def test_trusted_color_renderer_resets_and_plain_text_is_available(self):
        stream = io.StringIO()
        with patch('sys.stdout', stream), patch.object(app, 'clear'), patch.object(app, 'header_bar'), patch.object(app, 'ansi_scroll'), patch.object(app, 'input', return_value=''):
            app.text_page('poster_mail', 'Card', ['Thanks'], color='GREEN')
        self.assertEqual(stream.getvalue(), '\x1b[32m\x1b[0m')

    def test_coverage_and_photo_navigation(self):
        rows = cis_poster.coverage_records(app)
        society = next(r for r in rows if r['destination'] == 'poster_communicate' and '/ 7 ' in r['label'])
        self.assertIn('working', society['status'])
        self.assertTrue(rows)
        self.assertEqual([r['label'] for r in rows if r['status'] == 'unimplemented'], [])
        with patch.object(app, 'text_page') as page:
            app.open_go_destination(app.go_map['GO PHOTOS'], ['main'])
        self.assertTrue(any('CUPCAKE' in line for line in page.call_args.args[2]))
        with patch.object(cis_poster, 'input', side_effect=['U', 'M']), patch.object(app, 'ansi_scroll') as output, patch.object(app, 'clear'), patch.object(app, 'header_bar'):
            cis_poster.directory(app, ['main'], coverage=True)
        self.assertTrue(any('No matching topics.' in str(c) for c in output.call_args_list))

    def test_poster_destinations_are_recognized_by_dispatcher(self):
        # Exercise real destination resolution, replacing only interactive services.
        with ExitStack() as mocks:
            for name in ('sports_menu', 'books_menu', 'entertainment_menu',
                         'forum_service', 'activity_center', 'live_weather_service',
                         'text_page'):
                mocks.enter_context(patch.object(app, name))
            mocks.enter_context(patch.object(app.cis_magazine, 'service'))
            mocks.enter_context(patch.object(app.cis_shareware, 'service'))
            mocks.enter_context(patch.object(app.session_state, 'remember_destination'))
            for key, screen in app.screens.items():
                if not screen.get('poster'):
                    continue
                for field in ('targets', 'related_targets'):
                    for choice, target in screen.get(field, {}).items():
                        with self.subTest(screen=key, choice=choice, field=field, target=target):
                            self.assertIn(choice, screen['options'])
                            self.assertTrue(app.open_go_destination(target, ['main']))


if __name__ == '__main__':
    unittest.main()
