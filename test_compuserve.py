import json
import io
import subprocess
import sqlite3
from contextlib import closing
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from pathlib import Path
from unittest.mock import Mock, patch

import compuserve
import cis_phones
import cis_communities
import cis_magazine
import cis_storage
import cis_migrations
import cis_dynamic
import cis_discovery
import cis_library
import cis_forums
import cis_reference
import cis_store
import cis_business
import cis_billing
import cis_travel
import cis_experience
import cis_drafts
import cis_announcements
import cis_weather
import cis_timeline
import cis_features
import cis_cb
import cis_adventure_league
import smoke_test
import fake2
import feed_utils
import telnet_app
from cis_terminal import wrap_terminal_text
from cis_session import SessionState


class FirstCallContentTests(unittest.TestCase):
    def test_arc_delivers_linked_resolution_once_without_member_mail(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, 'BASE_DIR', Path(directory)), patch.object(compuserve, 'forum_threads', {}), patch.dict('os.environ', {'CIS_SIMULATION_DATE': '1988-12-15', 'CIS_SIMULATION_TIME': '12:00'}):
            self.assertTrue(cis_dynamic.ensure_forum_activity(compuserve))
            self.assertFalse(cis_dynamic.ensure_forum_activity(compuserve))
            state = cis_dynamic.load_state(compuserve)
            events = state['events']
            self.assertEqual(len(events), 4)
            self.assertEqual([e['due_tick'] - events[0]['due_tick'] for e in events], [0, 120, 360, 1320])
            self.assertFalse(cis_dynamic.process_events(compuserve))
            for event in events:
                event['due_tick'] = 0
            cis_dynamic.save_state(compuserve, state)
            self.assertTrue(cis_dynamic.process_events(compuserve))
            self.assertFalse(cis_dynamic.process_events(compuserve))
            messages = next(iter(compuserve.forum_threads.values()))
            self.assertEqual(len(messages), 5)
            self.assertTrue(all(m['parent_id'] == messages[0]['id'] for m in messages[1:]))
            self.assertIn('Test result:', messages[3]['body'])
            self.assertIn('Resolved', messages[4]['body'])
            self.assertEqual(compuserve.load_json('easyplex.json', default=[]), [])

    def test_arcs_do_not_repeat_after_catalog_is_exhausted(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, 'BASE_DIR', Path(directory)), patch.object(compuserve, 'forum_threads', {}):
            for day in range(1, len(cis_dynamic.FORUM_ARCS) + 2):
                with patch.dict('os.environ', {'CIS_SIMULATION_DATE': f'1988-12-{day:02}', 'CIS_SIMULATION_TIME': '12:00'}):
                    self.assertEqual(cis_dynamic.ensure_forum_activity(compuserve), day <= len(cis_dynamic.FORUM_ARCS))
            subjects = [m['subject'] for group in compuserve.forum_threads.values() for m in group]
            self.assertEqual(len(subjects), len(cis_dynamic.FORUM_ARCS))
            self.assertEqual(len(set(subjects)), len(subjects))

    def test_tour_routes_to_services_and_remembers_only_visited_stops(self):
        with patch.object(compuserve, 'current_user_id', 'TOUR'), patch.object(compuserve, 'current_profile', {}), patch.object(compuserve, 'save_profiles') as save, patch.object(compuserve, 'clear'), patch.object(compuserve, 'header_bar'), patch.object(compuserve, 'ansi_scroll'), patch.object(compuserve, 'text_page'), patch.object(compuserve, 'mail_read') as mail, patch.object(compuserve, 'forum_service') as forum, patch.object(compuserve, 'forum_libraries') as library, patch.object(compuserve, 'activity_center') as activity, patch('builtins.input', side_effect=['bad', '2', '3', '4', 'M', '2', 'M']):
            cis_experience.guided_tour(compuserve)
            cis_experience.guided_tour(compuserve)
            self.assertEqual(compuserve.current_profile['tour_visited'], ['2', '3', '4'])
            self.assertEqual(save.call_count, 3)
            mail.assert_not_called()
            self.assertEqual(forum.call_count, 2)
            library.assert_called_once_with('ibmhw')
            activity.assert_called_once_with()


class MagazineTests(unittest.TestCase):
    def test_tenth_article_is_selectable_and_new_topics_are_date_gated(self):
        from datetime import date
        issue = cis_magazine.ISSUES[0]
        with patch.object(compuserve, 'current_profile', {}), patch.object(compuserve, 'clear'), patch.object(compuserve, 'header_bar'), patch.object(compuserve, 'ansi_scroll'), patch.object(cis_magazine, 'read_article') as reader, patch('builtins.input', side_effect=['10', 'M']):
            cis_magazine.issue_menu(compuserve, issue)
            reader.assert_called_once_with(compuserve, issue, 9)
        self.assertTrue(cis_magazine.search('HyperCard', date(1988, 12, 1)))
        self.assertFalse(cis_magazine.search('multiuser', date(1988, 12, 22)))
        self.assertTrue(cis_magazine.search('multiuser', date(1988, 12, 29)))

    def test_expanded_issues_export_every_paragraph_and_use_valid_service_links(self):
        import re
        from datetime import date
        with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, 'BASE_DIR', Path(directory)), patch.object(cis_dynamic, 'simulation_day', return_value=date(1988, 12, 31)):
            for issue in cis_magazine.ISSUES:
                with self.subTest(issue=issue['id']):
                    path = cis_magazine.export_issue(compuserve, issue)
                    raw = path.read_bytes()
                    text = raw.decode('ascii')
                    flattened = ' '.join(text.split())
                    self.assertTrue(all(len(line) <= 72 for line in text.splitlines()))
                    self.assertNotIn(b'\n', raw.replace(b'\r\n', b''))
                    for article in issue['articles']:
                        for paragraph in article['paragraphs']:
                            self.assertIn(' '.join(paragraph.split()), flattened)
                        for link in article.get('related', []):
                            for destination in re.findall(r'GO ([A-Z0-9]+)', link):
                                self.assertIsNotNone(compuserve.resolve_go_destination(destination), link)
                        for width in (40, 80):
                            lines = [line for paragraph in cis_magazine.article_lines(issue, article) for line in wrap_terminal_text(paragraph, width)]
                            self.assertTrue(all(len(line) <= width for line in lines))

    def test_issues_are_complete_unique_and_follow_the_calendar(self):
        from datetime import date
        self.assertEqual(len(cis_magazine.ISSUES), 5)
        identifiers = []
        for issue in cis_magazine.ISSUES:
            self.assertEqual(len(issue['articles']), 10)
            for article in issue['articles']:
                identifiers.append(article['id'])
                self.assertGreaterEqual(len(' '.join(article['paragraphs']).split()), 400)
                ' '.join(article['paragraphs']).encode('ascii')
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(cis_magazine.available(date(1988, 11, 30)), [])
        for day, count in [(1, 1), (7, 1), (8, 2), (15, 3), (22, 4), (29, 5)]:
            self.assertEqual(len(cis_magazine.available(date(1988, 12, day))), count)
        self.assertIsNone(cis_magazine.find_issue('OW881229', date(1988, 12, 15)))
        self.assertEqual(cis_magazine.search('Version 1.1 deserves', date(1988, 12, 15)), [])
        self.assertTrue(cis_magazine.search('Version 1.1 deserves', date(1988, 12, 29)))

    def test_issue_navigation_saves_read_progress_without_marking_unseen_articles(self):
        issue = cis_magazine.ISSUES[2]
        profile = {}
        with patch.object(compuserve, 'current_profile', profile), patch.object(compuserve, 'save_profiles') as save, patch.object(compuserve, 'clear'), patch.object(compuserve, 'header_bar'), patch.object(compuserve, 'ansi_scroll'), patch('builtins.input', side_effect=['2', 'N', 'P', 'M', 'M']):
            cis_magazine.issue_menu(compuserve, issue)
        self.assertEqual(set(profile['magazine_read']), {issue['articles'][1]['id'], issue['articles'][2]['id']})
        self.assertEqual(profile['magazine_last'][issue['id']], issue['articles'][1]['id'])
        self.assertTrue(save.called)
        with patch.object(compuserve, 'current_profile', profile), patch.object(compuserve, 'clear'), patch.object(compuserve, 'header_bar'), patch.object(compuserve, 'ansi_scroll'), patch.object(cis_magazine, 'read_article') as reader, patch('builtins.input', side_effect=['R', 'M']):
            cis_magazine.issue_menu(compuserve, issue)
            reader.assert_called_once_with(compuserve, issue, 1)
        with patch.object(compuserve, 'current_profile', {}):
            self.assertEqual(cis_magazine.read_count(compuserve, issue), 0)

    def test_full_issue_export_and_browser_snapshot(self):
        issue = cis_magazine.ISSUES[2]
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as exports, patch.object(compuserve, 'BASE_DIR', Path(directory)), patch.dict('os.environ', {'CIS_SIMULATION_DATE': '1988-12-15', 'CIS_WEB_TERMINAL': '1', 'CIS_WEB_EXPORT_DIR': exports}):
            path = cis_magazine.export_issue(compuserve, issue)
            data = path.read_bytes()
            text = data.decode('ascii')
            self.assertTrue(all(len(line) <= 72 for line in text.splitlines()))
            self.assertIn('CONTENTS', text)
            for article in issue['articles']:
                self.assertIn(article['title'], text)
                self.assertIn(' '.join(article['paragraphs'][-1].split()), ' '.join(text.split()))
            self.assertEqual(len(list(Path(exports).glob('*.json'))), 1)
            self.assertEqual(next(Path(exports).glob('*.bin')).read_bytes(), data)
            with self.assertRaises(ValueError):
                cis_magazine.export_issue(compuserve, cis_magazine.ISSUES[-1])

    def test_news_and_go_routes_open_magazine(self):
        self.assertEqual(compuserve.resolve_go_destination('MAGAZINE'), 'magazine')
        self.assertEqual(compuserve.resolve_go_destination('WEEKLY'), 'magazine')
        self.assertEqual(compuserve.resolve_go_destination('MAG-1'), 'magazine')
        for commands in (['4', '7', 'OFF'], ['GO MAGAZINE', 'OFF']):
            with patch.object(compuserve, 'session_state', SessionState()), patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), patch.object(cis_magazine, 'service') as magazine, patch('builtins.input', side_effect=commands):
                compuserve.navigate()
                magazine.assert_called_once_with(compuserve)

    def test_latest_issue_menu_and_find_results(self):
        with patch.dict('os.environ', {'CIS_SIMULATION_DATE': '1988-12-15'}), patch.object(compuserve, 'current_profile', {}), patch.object(compuserve, 'clear'), patch.object(compuserve, 'header_bar'), patch.object(compuserve, 'ansi_scroll') as output, patch.object(cis_magazine, 'issue_menu') as reader, patch('builtins.input', side_effect=['L', 'S gravity', '1', 'M']):
            cis_magazine.service(compuserve)
            self.assertEqual(reader.call_args_list[0].args[1]['id'], 'OW881215')
            self.assertEqual(reader.call_args_list[1].args[2], 'OW881215-2')
            self.assertFalse(any('OW881229' in call.args[0] for call in output.call_args_list))
        with patch.dict('os.environ', {'CIS_SIMULATION_DATE': '1988-12-15'}), patch.object(cis_magazine, 'service') as reader:
            self.assertTrue(cis_discovery.open_result(compuserve, 'MAGAZINE OW881215 OW881215-2 DOCK64'))
            reader.assert_called_once_with(compuserve, 'OW881215', 'OW881215-2')
            self.assertFalse(cis_discovery.open_result(compuserve, 'MAGAZINE OW881229 OW881229-1 FUTURE'))

    def test_activity_uses_latest_published_issue(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, 'BASE_DIR', Path(directory)), patch.object(compuserve, 'current_profile', {}), patch.dict('os.environ', {'CIS_SIMULATION_DATE': '1988-12-15'}):
            magazines = [item for item in cis_discovery.activity_items(compuserve) if item['kind'] == 'MAGAZINE']
            self.assertEqual(len(magazines), 1)
            self.assertEqual(magazines[0]['record']['id'], 'OW881215')
            compuserve.current_profile['magazine_read'] = [a['id'] for a in magazines[0]['record']['articles']]
            self.assertFalse(any(item['kind'] == 'MAGAZINE' for item in cis_discovery.activity_items(compuserve)))


class ComputerCommunityTests(unittest.TestCase):
    def test_install_preserves_members_and_runs_once(self):
        with tempfile.TemporaryDirectory() as directory:
            original = {'member_section': [{'id': 900000, 'author': 'Member', 'subject': 'Keep this', 'body': 'Original post'}]}
            cis_storage.write_json_atomic(directory, 'forums.json', original)
            cis_storage.write_json_atomic(directory, 'library_files.json', {'member_library': [{'number': 9000, 'name': 'OWN.TXT', 'downloads': 37}]})
            self.assertTrue(cis_communities.install(directory))
            forums = cis_storage.load_json(directory, 'forums.json')
            files = cis_storage.load_json(directory, 'library_files.json')
            self.assertEqual(forums['member_section'], original['member_section'])
            self.assertEqual(files['member_library'][0]['downloads'], 37)
            for forum in cis_communities.FORUMS.values():
                for section, _ in forum['sections'].values():
                    messages = forums[section]
                    self.assertEqual(len(messages), 3)
                    self.assertTrue(all(m['parent_id'] == messages[0]['id'] for m in messages[1:]))
                    self.assertGreater(messages[0]['id'], 900000)
                self.assertEqual(len(files[forum['library']]), 4)
            # Deleted seeded posts stay deleted after installation; counts survive.
            forums['dos_basic'].pop()
            files['dos_library'][0]['downloads'] = 12
            cis_storage.write_json_atomic(directory, 'forums.json', forums)
            cis_storage.write_json_atomic(directory, 'library_files.json', files)
            self.assertFalse(cis_communities.install(directory))
            self.assertEqual(cis_storage.load_json(directory, 'forums.json'), forums)
            self.assertEqual(cis_storage.load_json(directory, 'library_files.json'), files)

    def test_install_rolls_back_and_parallel_startups_do_not_duplicate(self):
        with tempfile.TemporaryDirectory() as directory:
            cis_storage.write_json_atomic(directory, 'forums.json', {})
            cis_storage.write_json_atomic(directory, 'library_files.json', {})
            def broken(data):
                raise RuntimeError('Interrupted content installation')
            with self.assertRaises(RuntimeError):
                cis_storage.install_content_pack(directory, 'failure-test', {'forums.json': cis_communities.merge_forums, 'library_files.json': broken})
            self.assertEqual(cis_storage.load_json(directory, 'forums.json'), {})
            with ThreadPoolExecutor(max_workers=3) as pool:
                results = list(pool.map(cis_communities.install, [directory] * 3))
            self.assertEqual(results.count(True), 1)
            forums = cis_storage.load_json(directory, 'forums.json')
            self.assertEqual(sum(map(len, forums.values())), 36)

    def test_downloads_contain_complete_content_and_exact_byte_counts(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, 'BASE_DIR', Path(directory)), patch.object(compuserve, 'current_user_id', None):
            files = cis_communities.merge_files({})
            with patch.object(compuserve, 'library_files', files):
                for records in files.values():
                    for record in records:
                        expected = cis_communities.download_content(record).encode('ascii')
                        result = cis_library.materialize_download(compuserve, record, 'B')
                        self.assertEqual(result.read_bytes(), expected)
                        self.assertEqual(record['bytes'], len(expected))
                        self.assertEqual(record['downloads'], 1)
                        self.assertNotIn(b'\x1a', expected)
                        self.assertIn('RELEASE HISTORY', cis_communities.detail_lines(record))

    def test_forum_menu_and_go_routes_open_new_services(self):
        for choice, forum_id in list(compuserve.FORUM_CHOICES.items())[-4:]:
            with self.subTest(forum=forum_id), patch.object(compuserve, 'session_state', SessionState()), patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'forum_service') as service, patch.object(compuserve, 'show_logout_summary'), patch('builtins.input', side_effect=['2', choice, 'OFF']):
                compuserve.navigate()
                service.assert_called_once_with(forum_id)
            self.assertEqual(compuserve.resolve_go_destination(forum_id), forum_id)
            self.assertEqual(compuserve.resolve_go_destination(compuserve.page_names[forum_id]), forum_id)
            with patch.object(compuserve, 'library_download_screen') as library:
                compuserve.forum_libraries(forum_id)
                library.assert_called_once_with(cis_communities.LIBRARIES[forum_id])
        with patch.object(compuserve, 'session_state', SessionState()), patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), patch.object(compuserve, 'library_download_screen') as library, patch('builtins.input', side_effect=['GO DOSLIB', 'OFF']):
            compuserve.navigate()
            library.assert_called_once_with('dos_library')

    def test_library_info_and_transfer_are_accessible(self):
        files = cis_communities.merge_files({})
        number = files['dos_library'][0]['number']
        with patch.object(compuserve, 'library_files', files), patch.object(compuserve, 'clear'), patch.object(compuserve, 'header_bar'), patch.object(compuserve, 'ansi_scroll'), patch.object(compuserve, 'text_page') as page, patch.object(compuserve, 'library_transfer') as transfer, patch('builtins.input', side_effect=[f'I {number}', str(number), 'M']):
            compuserve.library_download_screen('dos_library')
        self.assertIn('RELEASE HISTORY', page.call_args.args[2])
        transfer.assert_called_once_with(files['dos_library'][0])


class PhoneDirectoryTests(unittest.TestCase):
    def test_search_handles_ambiguous_cities_aliases_and_accents(self):
        self.assertEqual({r['region'] for r in cis_phones.search('portland')}, {'OR', 'ME'})
        self.assertEqual(cis_phones.search('Portland, OR')[0]['numbers'], ['503-232-1072'])
        self.assertEqual(cis_phones.search('nyc')[0]['numbers'], ['212-758-4114'])
        self.assertEqual(cis_phones.search('Montréal')[0]['city'], 'Montreal')
        self.assertEqual(cis_phones.search('Saint Louis')[0]['city'], 'St. Louis')
        self.assertEqual(cis_phones.search('Ft. Worth')[0]['city'], 'Fort Worth')
        self.assertEqual(cis_phones.search('missingcity'), [])
        self.assertEqual(cis_phones.search(''), [])

    def test_geographic_coverage_and_fictional_numbers(self):
        states = set('AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY DC'.split())
        self.assertTrue(states <= {r['region'] for r in cis_phones.DIRECTORY if r['country'] == 'USA'})
        self.assertGreaterEqual(len(cis_phones.DIRECTORY), 190)
        for city in ('Chicago', 'Los Angeles', 'Houston', 'Toronto', 'Vancouver', 'Montreal', 'Calgary'):
            self.assertTrue(cis_phones.search(city), city)
        identities = [(r['city'], r['region'], r['country']) for r in cis_phones.DIRECTORY]
        self.assertEqual(len(identities), len(set(identities)))
        for row in cis_phones.DIRECTORY:
            for number in row['numbers']:
                self.assertRegex(number, r'^\d{3}-\d{3}-\d{4}$')
                if not row['historical']:
                    self.assertRegex(number, r'^\d{3}-555-01\d{2}$')

    def test_directory_search_sources_and_pagination(self):
        output = []
        replies = iter(['missingcity', 'sources', 'all', '?', '', 's', 'Chicago', 'Montreal', 'm'])
        cis_phones.run(output.append, lambda prompt: next(replies))
        transcript = '\n'.join(output)
        self.assertIn('No cities found', transcript)
        self.assertIn(cis_phones.SOURCE_URL, transcript)
        self.assertIn('Press Enter, S, or M.', transcript)
        self.assertIn('312-443-1250 [HISTORICAL]', transcript)
        self.assertIn('[FICTIONAL]', transcript)

    def test_exit_from_paged_results(self):
        read = Mock(side_effect=['ALL', 'M'])
        output = []
        cis_phones.run(output.append, read)
        self.assertEqual(read.call_count, 2)
        self.assertNotIn('Chicago, IL - USA', output)

    def test_phones_returns_to_host_before_authentication(self):
        with patch('builtins.input', side_effect=['phones', 'Chicago', 'm', 'CIS', '70000,0001']) as read, patch.object(compuserve, 'ansi_scroll') as emit, patch.object(compuserve, 'authenticate_account', return_value=False) as authenticate:
            self.assertFalse(compuserve.login_screen())
        self.assertEqual([c.args[0] for c in read.call_args_list].count('Host Name: '), 2)
        authenticate.assert_called_once_with('70000,0001')
        self.assertTrue(any('312-443-1250' in c.args[0] for c in emit.call_args_list))

    def test_default_and_invalid_host_preserve_login_behavior(self):
        for host in ('', 'unknown'):
            with self.subTest(host=host), patch('builtins.input', side_effect=[host, '70000,0001']), patch.object(compuserve, 'ansi_scroll'), patch.object(compuserve, 'authenticate_account', return_value=False) as authenticate:
                self.assertFalse(compuserve.login_screen())
                authenticate.assert_called_once_with('70000,0001')


class NavigationTests(unittest.TestCase):
    def test_go_unwinds_nested_forum_and_mail_prompts(self):
        state = SessionState()
        with patch.object(compuserve, 'session_state', state), patch.object(compuserve, 'clear'), patch.object(compuserve, 'ansi_scroll'), patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), patch.object(compuserve, 'load_mail', return_value=[]), patch('builtins.input', side_effect=['GO IBMHW', '1', 'g mail', '2', 'GO TOP', 'OFF']):
            compuserve.navigate()
        self.assertEqual(state.navigation_stack, ['main'])

    def test_go_leaves_mail_draft_without_sending(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, 'BASE_DIR', Path(directory)), patch.object(compuserve, 'session_state', SessionState()), patch.object(compuserve, 'current_user_id', '70000,0001'), patch.object(compuserve, 'profiles', {'70000,0002': {}}), patch.object(compuserve, 'current_profile', {}), patch.object(compuserve, 'clear'), patch.object(compuserve, 'ansi_scroll'), patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), patch('builtins.input', side_effect=['GO MAIL', '2', '70000,0002', 'Draft test', 'Keep this line', 'GO TOP', 'OFF']):
            compuserve.navigate()
            draft = cis_drafts.get_draft(compuserve, 'mail')
            self.assertEqual(draft['lines'], ['Keep this line'])
            self.assertEqual(compuserve.load_json('easyplex.json', default=[]), [])

    def test_unknown_go_reprompts_and_game_directions_stay_local(self):
        from cis_session import read_input, navigation_prompts, GoNavigation
        with navigation_prompts(compuserve), patch.object(compuserve, 'ansi_scroll') as emit, patch('builtins.input', side_effect=['GO NONEXISTENT', 'ordinary text', 'GO NORTH', 'GO NEWS']):
            self.assertEqual(read_input('Field: '), 'ordinary text')
            self.assertTrue(emit.called)
            self.assertEqual(read_input('? ', local_go=('NORTH',)), 'GO NORTH')
            with self.assertRaises(GoNavigation):
                read_input('? ', local_go=('NORTH',))
        with patch('builtins.input', return_value='GO MAIL'):
            self.assertEqual(read_input('Outside service session: '), 'GO MAIL')

    def test_go_from_magazine_reader_to_another_direct_service(self):
        state = SessionState()
        with patch.object(compuserve, 'session_state', state), patch.object(compuserve, 'current_profile', {}), patch.object(compuserve, 'save_profiles'), patch.object(compuserve, 'clear'), patch.object(compuserve, 'ansi_scroll'), patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), patch.object(cis_discovery, 'activity_items', return_value=[]), patch.dict('os.environ', {'CIS_SIMULATION_DATE': '1988-12-15'}), patch('builtins.input', side_effect=['GO MAGAZINE', 'L', '1', 'GO NEW', 'GO TOP', 'OFF']):
            compuserve.navigate()
        self.assertEqual(state.navigation_stack, ['main'])

    def test_top_announcements_appear_once_per_session(self):
        state = SessionState()
        with patch.object(compuserve, 'session_state', state), patch.object(compuserve, 'current_user_id', '70000,0001'), patch.object(compuserve, 'clear'), patch.object(compuserve, 'ansi_scroll') as emit, patch.object(compuserve, 'mail_waiting_count', return_value=3) as mail_count, patch.object(cis_dynamic, 'announcements', return_value=['3 EasyPlex messages', 'Other member information']) as announcements:
            compuserve.show_screen('support')
            announcements.assert_not_called()
            compuserve.show_screen('main')
            state.reset_navigation()
            compuserve.show_screen('main')
            compuserve.show_screen('support')
            compuserve.show_screen('main')
            announcements.assert_called_once()
            mail_count.assert_called_once()
            shown = [call.args[0] for call in emit.call_args_list]
            self.assertEqual(shown.count('3 EasyPlex messages'), 1)
            self.assertEqual(shown.count('Other member information'), 1)
            self.assertTrue(state.top_announcements_shown)
            with patch.object(compuserve, 'session_state', SessionState()):
                compuserve.show_screen('main')
            self.assertEqual(announcements.call_count, 2)

    def test_today_in_1988_dashboard_combines_history_activity_weather_and_reference(self):
        report = {
            "location": {"name": "Chicago"},
            "current": {"weather_code": 1, "temperature_2m": 72},
            "cached": False,
        }
        original = (compuserve.current_user_id, compuserve.current_profile)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-07"}), patch.object(cis_weather, "live_weather", return_value=report):
                compuserve.current_user_id = "70000,0001"
                compuserve.current_profile = {"weather_city": "Chicago"}
                lines = compuserve.today_in_1988_lines()
                text = "\n".join(lines)
                self.assertIn("DESTRUCTIVE EARTHQUAKE", text)
                self.assertIn("CHICAGO: MAINLY CLEAR, 72 F", text)
                self.assertIn("DID YOU KNOW?", text)
                self.assertIn("READ HISTORY", text)
        finally:
            compuserve.current_user_id, compuserve.current_profile = original

    def test_offline_timeline_search_marks_exports_and_appears_in_activity(self):
        self.assertGreaterEqual(len(cis_timeline.RECORDS), 31)
        self.assertEqual(
            {int(record["date"][-2:]) for record in cis_timeline.RECORDS},
            set(range(1, 32)),
        )
        self.assertEqual({record["kind"] for record in cis_timeline.RECORDS}, {"EVENT", "CONTEXT"})
        self.assertEqual(cis_timeline.find("h1207a")["category"], "EARTH")
        self.assertTrue(any(record["id"] == "H1221A" for record in cis_timeline.search("Lockerbie")))
        original = (compuserve.current_user_id, compuserve.current_profile)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-07"}):
                compuserve.current_user_id = "70000,0001"
                compuserve.current_profile = {}
                self.assertIn("marked", cis_timeline.mark(compuserve, "H1207A").lower())
                packet = cis_timeline.export_marked(compuserve)
                packet_text = packet.read_text(encoding="ascii")
                self.assertIn("DESTRUCTIVE EARTHQUAKE", packet_text)
                self.assertIn("RELATED REFERENCE INDEX", packet_text)
                self.assertIn("A1011", packet_text)
                history = [item for item in cis_discovery.activity_items(compuserve) if item["kind"] == "HISTORY"]
                self.assertEqual({item["record"]["id"] for item in history}, {"H1207A", "H1207B"})
        finally:
            compuserve.current_user_id, compuserve.current_profile = original

    def test_timeline_and_reference_records_navigate_in_both_directions(self):
        timeline_record = cis_timeline.find("H1207A")
        database, reference_record = cis_reference.find_record("A1011")
        self.assertIn(timeline_record, cis_timeline.records_related_to("a1011"))
        output = []
        with patch("builtins.input", side_effect=["1", "BACK", "M"]), patch.object(compuserve, "clear"), patch.object(compuserve, "header_bar"), patch.object(compuserve, "ansi_scroll", side_effect=lambda line, *_: output.append(str(line))):
            compuserve.linked_record_browser("timeline", timeline_record)
        rendered = "\n".join(output)
        self.assertIn(reference_record[1], rendered)
        self.assertGreaterEqual(rendered.count(timeline_record["title"]), 2)

    def test_historical_features_save_progress_bookmark_export_and_search(self):
        self.assertEqual(len(cis_features.FEATURES), 5)
        feature = cis_features.find("f004")
        original = (compuserve.current_user_id, compuserve.current_profile)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "save_profiles"):
                compuserve.current_user_id = "70000,0001"
                compuserve.current_profile = {}
                cis_features.save_progress(compuserve, feature, 1)
                self.assertEqual(cis_features.progress(compuserve, feature), 1)
                self.assertEqual(cis_features.toggle_bookmark(compuserve, feature), "Feature bookmarked.")
                packet = cis_features.export(compuserve, feature)
                self.assertIn("TEXT BEFORE THE WEB", packet.read_text(encoding="ascii"))
                self.assertTrue(any("F004" in result for result in cis_discovery.search(compuserve, "modem")))
                notices = [item for item in cis_discovery.activity_items(compuserve) if item["kind"] == "FEATURE"]
                self.assertEqual(len(notices), 5)
        finally:
            compuserve.current_user_id, compuserve.current_profile = original

    def test_draft_center_data_appears_in_activity_and_routes_to_resume(self):
        original = (compuserve.current_user_id, compuserve.current_profile)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)):
                compuserve.current_user_id = "70000,0001"
                compuserve.current_profile = {}
                cis_drafts.save_draft(compuserve, "mail", recipient="70000,0002", subject="Test", lines=["Body"])
                drafts = cis_drafts.list_drafts(compuserve)
                self.assertEqual(drafts[0]["subject"], "Test")
                item = next(item for item in cis_discovery.activity_items(compuserve) if item["kind"] == "DRAFT")
                with patch.object(compuserve, "resume_draft_record") as resume:
                    cis_discovery.open_activity(compuserve, item)
                resume.assert_called_once_with(item["record"])
        finally:
            compuserve.current_user_id, compuserve.current_profile = original

    def test_aborted_forum_reply_is_saved_with_parent(self):
        user_id = "70000,0001"
        profile = {}
        message = {"id": 77, "author": "MEMBER", "author_user_id": "70000,0002", "subject": "Disk cable", "body": "Question", "parent_id": None}
        original = (compuserve.current_user_id, compuserve.current_profile, compuserve.profiles, compuserve.forum_threads)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "ansi_scroll"), patch("builtins.input", side_effect=["R", "My partial reply", "ABORT"]):
                compuserve.current_user_id = user_id
                compuserve.current_profile = profile
                compuserve.profiles = {user_id: profile}
                compuserve.forum_threads = {"sample": [message]}
                cis_forums.message_actions(compuserve, "sample", message)
                draft = cis_drafts.get_draft(compuserve, "forum")
                self.assertEqual(draft["parent_id"], 77)
                self.assertEqual(draft["lines"][-1], "My partial reply")
        finally:
            compuserve.current_user_id, compuserve.current_profile, compuserve.profiles, compuserve.forum_threads = original

    def test_usage_statement_records_each_session_once_and_exports(self):
        original = (compuserve.BASE_DIR, compuserve.current_user_id, compuserve.live_session_id)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)):
                compuserve.current_user_id = "70000,0001"
                compuserve.live_session_id = "usage-test"
                cis_billing.record_session(compuserve, 125, 1200, 0.42, 0.50)
                cis_billing.record_session(compuserve, 125, 1200, 0.42, 0.50)
                lines = cis_billing.statement_lines(compuserve, include_current=False)
                self.assertTrue(any("SESSIONS" in line and "1" in line for line in lines))
                self.assertTrue(any("$   0.92" in line for line in lines))
                statement = cis_billing.export_statement(compuserve)
                self.assertIn("FICTIONAL MEMBER USAGE STATEMENT", statement.read_text(encoding="ascii"))
        finally:
            compuserve.BASE_DIR, compuserve.current_user_id, compuserve.live_session_id = original

    def test_live_weather_geocodes_formats_and_uses_cache(self):
        geocode = {"results": [{"name": "Chicago", "admin1": "Illinois", "country": "United States", "latitude": 41.85, "longitude": -87.65, "timezone": "America/Chicago"}]}
        forecast = {"current": {"time": "2026-08-31T12:00", "temperature_2m": 72, "apparent_temperature": 71, "relative_humidity_2m": 50, "weather_code": 1, "wind_speed_10m": 8, "wind_direction_10m": 240, "wind_gusts_10m": 14}, "daily": {"time": ["2026-08-31"], "weather_code": [1], "temperature_2m_max": [75], "temperature_2m_min": [60], "precipitation_probability_max": [10]}}

        class Response(io.BytesIO):
            def __enter__(self): return self
            def __exit__(self, *args): self.close()

        with tempfile.TemporaryDirectory() as directory:
            opener = Mock(side_effect=[Response(json.dumps(geocode).encode()), Response(json.dumps(forecast).encode())])
            report = cis_weather.live_weather("Chicago", directory, opener=opener)
            cached = cis_weather.live_weather("chicago", directory, opener=Mock(side_effect=AssertionError("network used")))
        rendered = "\n".join(cis_weather.weather_lines(report))
        self.assertIn("TEMPERATURE 72 F", rendered)
        self.assertIn("MAINLY CLEAR", rendered)
        self.assertTrue(cached["cached"])

    def test_openalex_search_formats_and_caches_historical_results(self):
        payload = {"results": [{
            "id": "https://openalex.org/W123456",
            "doi": "https://doi.org/10.1000/test",
            "display_name": "Packet Radio Networks",
            "publication_year": 1987,
            "authorships": [{"author": {"display_name": "Grace Hopper"}}],
            "primary_location": {"source": {"display_name": "Data Communications"}},
            "abstract_inverted_index": {"Packet": [0], "radio": [1], "works": [2]},
            "cited_by_count": 12,
            "open_access": {"is_oa": True},
            "type": "article",
        }]}

        class Response(io.BytesIO):
            def __enter__(self): return self
            def __exit__(self, *args): self.close()

        with tempfile.TemporaryDirectory() as directory, patch.dict("os.environ", {}, clear=False):
            opener = Mock(return_value=Response(json.dumps(payload).encode("utf-8")))
            records = cis_reference.search_openalex_reference("BEFORE 1989 packet radio", opener=opener, base_dir=directory)
            cached = cis_reference.search_openalex_reference("BEFORE 1989 packet radio", opener=Mock(side_effect=AssertionError("network used")), base_dir=directory)
        record = records[0]
        self.assertEqual(record["id"], "OA123456")
        self.assertEqual(record["summary"], "Packet radio works")
        self.assertEqual(record["authors"], "Grace Hopper")
        self.assertTrue(record["open_access"])
        self.assertIn("publication_year%3A%3C1989", opener.call_args.args[0].full_url)
        self.assertTrue(cached[0]["cached"])
        rendered = "\n".join(cis_reference.live_article_lines(record))
        self.assertIn("DOI: 10.1000/test", rendered)
        self.assertIn("CITATIONS: 12", rendered)

    def test_sysop_announcements_schedule_target_and_track_reads(self):
        user_id = "70000,0001"
        original = (compuserve.current_user_id, compuserve.current_profile, compuserve.profiles)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15", "CIS_SIMULATION_TIME": "12:00"}):
                compuserve.current_user_id = user_id
                compuserve.current_profile = {}
                compuserve.profiles = {user_id: {}}
                active = cis_announcements.create(compuserve, "Maintenance", "Service work tonight.", "IMPORTANT", "ALL")
                cis_announcements.create(compuserve, "Future", "Not yet visible.", "NORMAL", "ALL", "12/20/88")
                cis_announcements.create(compuserve, "Private", "For another member.", "NORMAL", "70000,9999")
                visible = cis_announcements.active(compuserve, user_id, include_read=False)
                self.assertEqual([record["title"] for record in visible], ["Maintenance"])
                items = cis_discovery.activity_items(compuserve)
                notice = next(item for item in items if item["kind"] == "NOTICE")
                cis_discovery.mark_activity_seen(compuserve, notice)
                self.assertEqual(cis_announcements.active(compuserve, user_id, include_read=False), [])
                self.assertTrue(cis_announcements.expire(compuserve, active["id"]))
                self.assertNotIn("Maintenance", [record["title"] for record in cis_announcements.active(compuserve, user_id)])
        finally:
            compuserve.current_user_id, compuserve.current_profile, compuserve.profiles = original

    def test_line_editor_autosaves_each_change(self):
        snapshots = []
        with patch("builtins.input", side_effect=["first line", "REPLACE 1 revised", "DELETE 1", "ABORT"]), patch.object(compuserve, "ansi_scroll"):
            self.assertIsNone(compuserve.line_editor(on_change=lambda lines: snapshots.append(lines)))
        self.assertEqual(snapshots, [["first line"], ["revised"], []])

    def test_aborted_easyplex_composition_remains_as_a_draft(self):
        user_id, recipient = "70000,0001", "70000,0002"
        original = (compuserve.BASE_DIR, compuserve.current_user_id, compuserve.current_profile, compuserve.profiles)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "ansi_scroll"), patch("builtins.input", side_effect=[recipient, "Test subject", "Unfinished body", "ABORT"]):
                compuserve.current_user_id = user_id
                compuserve.current_profile = {}
                compuserve.profiles = {user_id: {}, recipient: {}}
                compuserve.mail_compose()
                draft = cis_drafts.get_draft(compuserve, "mail")
                self.assertEqual(draft["recipient"], recipient)
                self.assertEqual(draft["lines"], ["Unfinished body"])
                cis_drafts.delete_draft(compuserve, "mail")
                self.assertIsNone(cis_drafts.get_draft(compuserve, "mail"))
        finally:
            compuserve.BASE_DIR, compuserve.current_user_id, compuserve.current_profile, compuserve.profiles = original

    def test_activity_center_collects_and_clears_cross_service_updates(self):
        user_id = "70000,0001"
        profile = {"forum_last_read": {}, "watched_threads": [1001]}
        forums = {"ibmhw_tech": [{"id": 1001, "author": "DiskDoctor", "subject": "IRQ reply", "body": "Check IRQ 3.", "parent_id": None}]}
        original = (compuserve.current_user_id, compuserve.current_profile, compuserve.profiles, compuserve.forum_threads)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)):
                compuserve.current_user_id = user_id
                compuserve.current_profile = profile
                compuserve.profiles = {user_id: profile}
                compuserve.forum_threads = forums
                compuserve.save_json_atomic("easyplex.json", [{"id": 1, "from": "POSTMASTER", "to": user_id, "subject": "Welcome", "body": "Hello", "read": False}])
                compuserve.save_json_atomic("orders.json", [{"number": 42, "user_id": user_id, "name": "Modem", "status": "SHIPPED"}])
                state = cis_dynamic.load_state(compuserve)
                state["reservations"] = [{"confirmation": "AX1001", "user_id": user_id, "origin": "ORD", "destination": "LGA", "status": "CONFIRMED"}]
                cis_dynamic.save_state(compuserve, state)
                items = cis_discovery.activity_items(compuserve)
                self.assertEqual({item["kind"] for item in items}, {"MAIL", "FORUM", "ORDER", "TRAVEL", "HISTORY", "FEATURE", "MAGAZINE"})
                cis_discovery.mark_all_activity_seen(compuserve, items)
                self.assertEqual(cis_discovery.activity_items(compuserve), [])
                self.assertTrue(compuserve.load_json("easyplex.json")[0]["read"])
                self.assertEqual(profile["forum_last_read"]["ibmhw_tech"], 1001)
        finally:
            compuserve.current_user_id, compuserve.current_profile, compuserve.profiles, compuserve.forum_threads = original

    def test_session_navigation_tracks_recent_destinations_and_goes_back(self):
        state = SessionState()
        state.push("mail")
        state.remember_destination("mail")
        state.remember_destination("forums")
        state.remember_destination("mail")
        self.assertEqual(state.recent_destinations, ["mail", "forums"])
        self.assertEqual(state.go_back(), "mail")
        self.assertEqual(state.current_screen, "main")
        self.assertIsNone(state.go_back())

    def test_navigation_commands_resolve_and_appear_in_help(self):
        self.assertEqual(compuserve.resolve_go_destination("BACK"), "back")
        self.assertEqual(compuserve.resolve_go_destination("RECENT"), "recent")
        help_text = "\n".join(compuserve.COMMAND_HELP_LINES)
        self.assertIn("GO BACK", help_text)
        self.assertIn("GO RECENT", help_text)

    def test_live_reference_search_normalizes_wikipedia_results(self):
        payload = {
            "query": {"pages": [{
                "pageid": 123,
                "title": "Apollo program",
                "extract": "The  Apollo\nprogram &amp; its missions.",
                "fullurl": "https://en.wikipedia.org/wiki/Apollo_program",
            }]}
        }

        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.close()

        opener = Mock(return_value=Response(json.dumps(payload).encode("utf-8")))
        records = cis_reference.search_live_reference("Apollo", opener=opener)
        self.assertEqual(records[0]["id"], "W123")
        self.assertEqual(records[0]["summary"], "The Apollo program & its missions.")
        self.assertTrue(any("MODERN CONTENT" in line for line in cis_reference.live_article_lines(records[0])))
        request = opener.call_args.args[0]
        self.assertIn("gsrsearch=Apollo", request.full_url)

    def test_live_reference_reports_provider_failures(self):
        with self.assertRaises(cis_reference.LiveReferenceError):
            cis_reference.search_live_reference("Apollo", opener=Mock(side_effect=OSError("offline")))

    def test_live_reference_cache_avoids_a_second_network_request(self):
        payload = {"query": {"pages": [{"pageid": 321, "title": "Saturn V", "extract": "Launch vehicle."}]}}

        class Response(io.BytesIO):
            def __enter__(self): return self
            def __exit__(self, *args): self.close()

        with tempfile.TemporaryDirectory() as directory:
            opener = Mock(return_value=Response(json.dumps(payload).encode("utf-8")))
            first = cis_reference.search_live_reference("Saturn V", opener=opener, base_dir=directory)
            second = cis_reference.search_live_reference("saturn v", opener=Mock(side_effect=AssertionError("network used")), base_dir=directory)
        self.assertFalse(first[0]["cached"])
        self.assertTrue(second[0]["cached"])
        self.assertEqual(second[0]["id"], "W321")

    def test_marked_live_reference_is_exported(self):
        record = {"id": "W123", "title": "Apollo program", "summary": "Moon missions.", "url": "https://example.test/apollo", "source": "Wikipedia"}
        with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
            self.assertIn("marked", cis_reference.mark_live_record(compuserve, record).lower())
            packet = cis_reference.export_marked(compuserve)
            exported = packet.read_text(encoding="ascii")
        self.assertIn("RECORD W123", exported)
        self.assertIn("MODERN CONTENT", exported)

    def test_database_upgrade_is_explicit_and_refreshes_mutable_data(self):
        upgraded_forums = {"ibmhw_tech": [{"subject": "MIGRATED"}]}
        upgraded_profiles = {"70000,0001": {"handle": "MIGRATED"}}
        upgraded_library = {"ibmhw_lib1": [{"name": "MIGRATED.ARC"}]}
        original = (compuserve.forum_threads, compuserve.profiles, compuserve.library_files)
        try:
            with patch.object(compuserve, "upgrade_database", return_value=(10, None)) as upgrade, patch.object(
                compuserve,
                "load_json",
                side_effect=[upgraded_forums, upgraded_profiles, upgraded_library],
            ), patch.object(cis_dynamic, "apply_clock_state") as apply_clock:
                result = compuserve.initialize_database()
            upgrade.assert_called_once_with(compuserve.BASE_DIR, cis_migrations.CURRENT_SCHEMA_VERSION)
            apply_clock.assert_called_once_with(compuserve)
            self.assertEqual(result, (10, None))
            self.assertIs(compuserve.forum_threads, upgraded_forums)
            self.assertIs(compuserve.profiles, upgraded_profiles)
            self.assertIs(compuserve.library_files, upgraded_library)
        finally:
            compuserve.forum_threads, compuserve.profiles, compuserve.library_files = original

    def test_global_help_lists_all_personal_command_line_tools(self):
        help_text = "\n".join(compuserve.COMMAND_HELP_LINES)
        for command in ("GO CALENDAR", "GO NOTEBOOK", "GO DOWNLOADS", "GO ACHIEVEMENTS", "GO PROFILE", "GO NEW", "FIND words", "NOTE title | text"):
            self.assertIn(command, help_text)

    def test_context_help_abbreviations_command_card_and_release_smoke(self):
        self.assertEqual(compuserve.resolve_go_destination("CAL"), "calendar")
        self.assertIsNone(compuserve.resolve_go_destination("F"))
        self.assertIn("BUY", "\n".join(compuserve.HELP_TOPICS["TRADING"]))
        wrapped = [part for line in compuserve.COMMAND_HELP_LINES for part in wrap_terminal_text(line, 40)]
        self.assertTrue(all(len(line) <= 40 for line in wrapped))
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)):
                card = cis_experience.export_command_card(compuserve)
                self.assertIn("HELP FINANCE", card.read_text(encoding="ascii"))
        self.assertIn("passed", smoke_test.run())

    def test_live_sessions_and_messages_use_relational_sqlite_tables(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            cis_storage.register_session(base, "s1", "70000,0001", "BYTE RIDER", "WEB")
            sessions = cis_storage.list_sessions(base)
            self.assertEqual(sessions[0][1:4], ("70000,0001", "BYTE RIDER", "WEB"))
            message_id = cis_storage.post_live_message(base, "cb:1", "BYTE RIDER", "Hello")
            self.assertEqual(cis_storage.read_live_messages(base, "cb:1", message_id - 1)[0][2], "Hello")
            cis_storage.set_cb_presence(base, "s1", "cb:1", "BYTE RIDER", "AWAY")
            self.assertEqual(cis_storage.list_cb_presence(base, "cb:1")[0][1:3], ("BYTE RIDER", "AWAY"))
            cis_storage.remove_cb_presence(base, "s1")
            self.assertEqual(cis_storage.list_cb_presence(base, "cb:1"), [])
            self.assertTrue(cis_storage.claim_cb_ambient(base, "cb:1", 100))
            self.assertFalse(cis_storage.claim_cb_ambient(base, "cb:1", 100))
            cis_storage.unregister_session(base, "s1")
            self.assertEqual(cis_storage.list_sessions(base), [])

    def test_cb_commands_channels_scrollback_and_ignore_preferences(self):
        self.assertEqual(cis_cb.parse_command("/join Night Owls"), ("JOIN", "Night Owls"))
        self.assertEqual(cis_cb.parse_command("hello"), ("SAY", "hello"))
        self.assertIn("Member-created", cis_cb.description("Night Owls"))
        original = (compuserve.current_user_id, compuserve.current_handle, compuserve.current_profile)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "live_session_id", "cb-test"), patch.object(compuserve, "save_profiles"), patch.object(compuserve, "clear"), patch.object(compuserve, "header_bar"), patch.object(compuserve, "ansi_scroll"), patch("builtins.input", side_effect=["/status away", "/ignore Noise", "/join Night Owls", "hello", "/exit"]):
                compuserve.current_user_id = "70000,0001"
                compuserve.current_handle = "BYTE RIDER"
                compuserve.current_profile = {}
                compuserve.cb_chat("1")
                self.assertEqual(compuserve.current_profile["cb_status"], "AWAY")
                self.assertEqual(compuserve.current_profile["cb_ignored"], ["Noise"])
                history = cis_storage.recent_live_messages(Path(directory), "cb:night owls", 20)
                self.assertTrue(any(sender == "BYTE RIDER" and body == "hello" for _, sender, body, _ in history))
                self.assertEqual(cis_storage.list_cb_presence(Path(directory)), [])
        finally:
            compuserve.current_user_id, compuserve.current_handle, compuserve.current_profile = original

    def test_telnet_negotiation_is_removed(self):
        self.assertEqual(telnet_app.strip_telnet_commands(b"\xff\xfb\x01HELLO\r\n"), b"HELLO\r\n")

    def test_concurrent_live_messages_are_not_lost(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            with ThreadPoolExecutor(max_workers=8) as pool:
                ids = list(pool.map(lambda number: cis_storage.post_live_message(base, "cb:3", f"U{number}", f"M{number}"), range(24)))
            messages = cis_storage.read_live_messages(base, "cb:3", 0, 50)
            self.assertEqual(len(set(ids)), 24)
            self.assertEqual(len(messages), 24)

    def test_dynamic_content_is_stable_and_period_appropriate(self):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            first = cis_dynamic.classifieds([])
            second = cis_dynamic.classifieds([])
            quotes = cis_dynamic.market_quotes(compuserve.service_data["quotes"])
        self.assertEqual(first, second)
        self.assertEqual(cis_dynamic.simulation_day().year, 1988)
        self.assertTrue(all(item["last"] > 0 for item in quotes.values()))

    def test_simulated_cb_roster_and_responses_are_varied_contextual_and_addressable(self):
        self.assertGreaterEqual(len(cis_dynamic.HANDLES), 30)
        self.assertGreaterEqual(len(cis_dynamic.cb_presence("1")), 7)
        self.assertEqual(len(cis_dynamic.HANDLES), len(set(cis_dynamic.HANDLES)))
        original = (compuserve.current_user_id, compuserve.current_handle)
        try:
            with tempfile.TemporaryDirectory() as directory, patch.object(compuserve, "BASE_DIR", Path(directory)):
                compuserve.current_user_id = "70000,0001"
                compuserve.current_handle = "TESTER"
                first_handle, first_text = cis_dynamic.cb_response("3", "My 386 modem keeps losing carrier; what should I check?", 10, compuserve)
                self.assertIn(first_handle, ("ModemMan", "PacketPete"))
                self.assertIn("386", first_text)
                follow_handle, follow_text = cis_dynamic.cb_response("3", "I tried that; what next?", 11, compuserve)
                self.assertEqual(follow_handle, first_handle)
                self.assertNotEqual(first_text, follow_text)
                addressed_handle, addressed_text = cis_dynamic.cb_response("1", "AmigaAce, do you know anything about MIDI?", 12, compuserve)
                self.assertEqual(addressed_handle, "AmigaAce")
                self.assertIn("one more detail", addressed_text)
                info = "\n".join(cis_dynamic.cb_member_info(compuserve, "amigaace"))
                self.assertIn("AMIGA 500", info.upper())
                self.assertIn("YOUR EXCHANGES: 1", info)
                self.assertIsNone(cis_dynamic.cb_response("1", "which way", 13))
        finally:
            compuserve.current_user_id, compuserve.current_handle = original

    def test_ambient_cb_activity_varies_by_channel_and_suppresses_repeats(self):
        batch = next((cis_dynamic.cb_ambient_events("3", bucket, (), hour=20) for bucket in range(1000, 1100) if cis_dynamic.cb_ambient_events("3", bucket, (), hour=20)), None)
        self.assertTrue(batch)
        self.assertTrue(all(sender in cis_dynamic.HANDLES or sender == "SYSTEM" for sender, _ in batch))
        all_technical_lines = [line for conversation in cis_dynamic.CB_CONVERSATIONS["3"] for _, line in conversation]
        self.assertEqual(cis_dynamic.cb_ambient_events("3", 1001, all_technical_lines, hour=20), [])

    def test_daily_forum_activity_is_inserted_only_once(self):
        original_threads = compuserve.forum_threads
        try:
            with tempfile.TemporaryDirectory() as directory:
                compuserve.forum_threads = {"ibmhw_tech": [], "gamers_general": [], "hamnet_general": []}
                with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
                    self.assertTrue(cis_dynamic.ensure_forum_activity(compuserve))
                    self.assertFalse(cis_dynamic.ensure_forum_activity(compuserve))
                self.assertEqual(sum(map(len, compuserve.forum_threads.values())), 1)
        finally:
            compuserve.forum_threads = original_threads

    def test_scheduled_mail_is_delivered_once(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15", "CIS_SIMULATION_TIME": "12:00"}):
                cis_dynamic.schedule_event(compuserve, "mail", {"to": "70000,0001", "subject": "TEST", "body": "Scheduled message"}, cis_dynamic.simulation_datetime())
                self.assertTrue(cis_dynamic.process_events(compuserve))
                self.assertFalse(cis_dynamic.process_events(compuserve))
                messages = compuserve.load_json("easyplex.json", default=[])
            self.assertEqual(len(messages), 1)

    def test_cb_keyword_response_is_period_appropriate(self):
        response = cis_dynamic.cb_response("1", "Can anyone help with my modem?", 1)
        self.assertIsNotNone(response)
        self.assertTrue(any(term in response[1].lower() for term in ("baud", "modem", "data bits", "result code")))

    def test_forum_case_crosses_forum_easyplex_and_library(self):
        original_threads, original_profiles = compuserve.forum_threads, compuserve.profiles
        try:
            with tempfile.TemporaryDirectory() as directory:
                compuserve.forum_threads = {"ibmhw_tech": []}
                compuserve.profiles = {"70000,0001": {}}
                with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"), patch.object(compuserve, "current_handle", "BYTE RIDER"), patch.object(compuserve, "current_profile", compuserve.profiles["70000,0001"]), patch.object(compuserve, "ansi_scroll"), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15", "CIS_SIMULATION_TIME": "12:00"}):
                    cis_forums.post(compuserve, "ibmhw_tech", "COM2 mouse conflict", "My serial mouse and modem both stop responding.")
                    self.assertEqual(len(compuserve.forum_threads["ibmhw_tech"]), 1)
                with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15", "CIS_SIMULATION_TIME": "14:00"}):
                    self.assertTrue(cis_dynamic.process_events(compuserve))
                    mail = compuserve.load_json("easyplex.json", default=[])
                    state = cis_dynamic.load_state(compuserve)
                self.assertEqual(len(compuserve.forum_threads["ibmhw_tech"]), 2)
                self.assertEqual(compuserve.forum_threads["ibmhw_tech"][1]["author"], "DiskDoctor")
                self.assertIn("#103", compuserve.forum_threads["ibmhw_tech"][1]["body"])
                self.assertEqual(mail[0]["to"], "70000,0001")
                self.assertEqual(next(iter(state["forum_cases"].values()))["status"], "ANSWERED")
        finally:
            compuserve.forum_threads, compuserve.profiles = original_threads, original_profiles

    def test_cb_recognizes_member_from_prior_forum_case(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"), patch.object(compuserve, "current_handle", "BYTE RIDER"):
                cis_dynamic.remember_member_for_user(compuserve, "70000,0001", "DiskDoctor", "serial-port interrupts", "COM2 conflict", library_number=103)
                response = cis_dynamic.cb_response("3", "Hello, remember my problem?", app=compuserve)
            self.assertEqual(response[0], "DiskDoctor")
            self.assertIn("file #103", response[1])

    def test_member_relationship_progresses_and_schedules_milestone_mail(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0042"):
                for number in range(3):
                    memory = cis_dynamic.remember_member_for_user(compuserve, "70000,0042", "DiskDoctor", "IRQ settings", f"exchange {number}")
                summary = cis_dynamic.relationship_summary(memory)
                state = cis_dynamic.load_state(compuserve)
                milestone = [event for event in state["events"] if event["type"] == "mail" and event["payload"].get("from") == "DiskDoctor"]
                relationship_lines = cis_dynamic.relationship_lines(compuserve)
            self.assertEqual(summary["level"], "REGULAR")
            self.assertEqual(summary["interactions"], 3)
            self.assertEqual(len(milestone), 1)
            self.assertTrue(any("DiskDoctor" in line and "REGULAR" in line for line in relationship_lines))

    def test_repeated_hostile_member_exchanges_create_rivalry(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)):
                for word in ("wrong", "nonsense", "stupid"):
                    memory = cis_dynamic.remember_member_for_user(compuserve, "70000,0041", "NightOwl", "modem debate", word)
            self.assertEqual(cis_dynamic.relationship_summary(memory)["level"], "RIVAL")
            self.assertEqual(memory["friction"], 3)

    def test_existing_interaction_memory_receives_compatible_relationship_level(self):
        legacy = {"interactions": 10, "topic": "DOS memory"}
        summary = cis_dynamic.relationship_summary(legacy)
        self.assertEqual(summary["level"], "TRUSTED")
        self.assertEqual(summary["trust"], 5)

    def test_shareware_arc_advances_files_and_forum_by_simulated_day(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0021"),
                patch.object(compuserve, "forum_threads", {"ibmhw_tech": []}),
                patch.object(compuserve, "library_files", {"ibmhw_lib1": []}),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-11"}),
            ):
                compuserve.cis_shareware.ensure_arc(compuserve)
                first = next(item for item in compuserve.library_files["ibmhw_lib1"] if item["version"] == "1.0")
                self.assertEqual(first["status"], "approved")
                self.assertEqual(len(compuserve.forum_threads["ibmhw_tech"]), 2)
                with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
                    compuserve.cis_shareware.ensure_arc(compuserve)
                second = next(item for item in compuserve.library_files["ibmhw_lib1"] if item["version"] == "1.1")
                forum_count = len(compuserve.forum_threads["ibmhw_tech"])
            self.assertEqual(first["status"], "withdrawn")
            self.assertEqual(first["replacement"], 1881)
            self.assertEqual(second["status"], "approved")
            self.assertEqual(forum_count, 6)

    def test_shareware_watch_notifies_and_tester_earns_reputation(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0020"),
                patch.object(compuserve, "forum_threads", {"ibmhw_tech": []}),
                patch.object(compuserve, "library_files", {"ibmhw_lib1": []}),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-10"}),
            ):
                compuserve.cis_shareware.ensure_arc(compuserve)
                self.assertIn("active", compuserve.cis_shareware.watch(compuserve).lower())
                self.assertIn("filed", compuserve.cis_shareware.report(compuserve, "DOS 3.3 COM2 IRQ3 Hayes 1200").lower())
                with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-16"}):
                    compuserve.cis_shareware.ensure_arc(compuserve)
                state = cis_dynamic.load_state(compuserve)
                arc = state["shareware_arcs"]["TERMLINK-88"]
                notices = [event for event in state["events"] if event["type"] == "mail" and event["payload"].get("to") == "70000,0020"]
            self.assertEqual(arc["participants"]["70000,0020"]["reputation"], 10)
            self.assertIn("70000,0020", arc["reputation_awarded"])
            self.assertGreaterEqual(len(notices), 2)

    def test_trivia_score_is_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)):
                first = cis_dynamic.record_trivia_result(compuserve, "70000,0001", True)
                second = cis_dynamic.record_trivia_result(compuserve, "70000,0001", False)
            self.assertEqual(first, {"correct": 1, "attempts": 1})
            self.assertEqual(second, {"correct": 1, "attempts": 2})

    def test_weather_and_flights_are_stable_for_simulated_day(self):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            self.assertEqual(cis_dynamic.weather("CHICAGO"), cis_dynamic.weather("CHICAGO"))
            flights = cis_dynamic.flight_schedule("ORD", "LGA")
        self.assertEqual(len(flights), 4)
        self.assertTrue(any("fictional" in line.lower() for line in flights))

    def test_daily_library_file_is_added_once(self):
        original = compuserve.library_files
        try:
            with tempfile.TemporaryDirectory() as directory:
                compuserve.library_files = {"ibmhw_lib1": []}
                with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
                    self.assertTrue(cis_dynamic.ensure_library_activity(compuserve))
                    self.assertFalse(cis_dynamic.ensure_library_activity(compuserve))
                self.assertEqual(len(compuserve.library_files["ibmhw_lib1"]), 1)
        finally:
            compuserve.library_files = original

    def test_dashboard_reports_member_activity(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"), patch.object(compuserve, "current_profile", {"joined_forums": []}):
                lines = cis_dynamic.dashboard(compuserve)
            self.assertTrue(any("MEMBER 70000,0001" in line for line in lines))

    def test_global_search_finds_library_metadata(self):
        results = cis_discovery.search(compuserve, "diagnostic")
        self.assertTrue(any(line.startswith("LIB ") for line in results))

    def test_reference_databases_are_distinct_and_searchable(self):
        self.assertTrue(all(len(database["records"]) == 50 for database in cis_reference.DATABASES.values()))
        self.assertEqual(sum(len(database["records"]) for database in cis_reference.DATABASES.values()), 200)
        self.assertEqual(cis_reference.search("academic", "Armenia")[0][0], "A1004")
        self.assertEqual(cis_reference.search("medical", "blood pressure")[0][0], "M2003")
        self.assertEqual(cis_reference.search("science", "ozone")[0][0], "S3003")
        self.assertEqual(cis_reference.search("library", "COM2 modem")[0][0], "L4003")
        self.assertEqual(cis_reference.search("academic", "plate tectonics")[0][1], "PLATE TECTONICS")
        self.assertEqual(cis_reference.search("medical", "optic nerve pressure")[0][1], "GLAUCOMA")
        self.assertEqual(cis_reference.search("science", "fiber optic transmission")[0][1], "FIBER-OPTIC COMMUNICATIONS")
        self.assertEqual(cis_reference.search("library", "SCSI terminate cable")[0][1], "SCSI DEVICE PLANNING")
        warning = cis_reference.article_lines(cis_reference.search("medical", "cold")[0], "medical")
        self.assertTrue(any("NOT A DIAGNOSIS" in line for line in warning))
        self.assertTrue(cis_reference.DATA_PATH.is_file())

    def test_reference_boolean_search_and_cross_references(self):
        and_results = cis_reference.search("academic", "COMPUTER AND ELECTRONIC")
        self.assertTrue(and_results)
        self.assertTrue(all("COMPUTER" in " ".join(record).upper() and "ELECTRONIC" in " ".join(record).upper() for record in and_results))
        or_results = cis_reference.search("science", "MODEM OR OZONE")
        self.assertTrue(any("MODEM" in " ".join(record).upper() for record in or_results))
        self.assertTrue(any("OZONE" in " ".join(record).upper() for record in or_results))
        not_results = cis_reference.search("science", "COMPUTER NOT SOFTWARE")
        self.assertTrue(not_results)
        self.assertTrue(all("SOFTWARE" not in " ".join(record).upper() for record in not_results))
        database, record = cis_reference.find_record("l4003")
        self.assertEqual((database, record[1]), ("library", "SERIAL PORT ASSIGNMENTS"))
        self.assertTrue(any(line.startswith("SEE ALSO:") for line in cis_reference.article_lines(record, database)))

    def test_reference_history_marks_packet_and_subjects(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                cis_reference.record_search(compuserve, "library", "MODEM AND SERIAL", 3)
                self.assertEqual(cis_reference.search_history(compuserve)[0]["query"], "MODEM AND SERIAL")
                self.assertIn("marked", cis_reference.mark_record(compuserve, "L4003").lower())
                packet = cis_reference.export_marked(compuserve)
                self.assertTrue(packet.is_file())
                self.assertIn("SERIAL PORT ASSIGNMENTS", packet.read_text(encoding="ascii"))
                self.assertTrue(cis_reference.subject_records("library", "COMMUNICATIONS"))
                cis_reference.clear_history(compuserve)
                self.assertEqual(cis_reference.search_history(compuserve), [])

    def test_forum_post_suggests_reference_record(self):
        original_threads = compuserve.forum_threads
        try:
            with tempfile.TemporaryDirectory() as directory:
                compuserve.forum_threads = {"sample": []}
                with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"), patch.object(compuserve, "ansi_scroll") as scroll:
                    cis_forums.post(compuserve, "sample", "COM2 modem conflict", "The serial mouse stops responding.")
                rendered = "\n".join(call.args[0] for call in scroll.call_args_list)
                self.assertIn("Reference Data Bases:", rendered)
                self.assertIn("L4003", rendered)
        finally:
            compuserve.forum_threads = original_threads

    def test_reference_service_browses_and_opens_record(self):
        with patch("builtins.input", side_effect=["MODEM", "1", "", "M"]), patch.object(compuserve, "premium_service", return_value=True), patch.object(compuserve, "ansi_scroll") as scroll, patch.object(compuserve, "clear"), patch.object(compuserve, "header_bar"):
            compuserve.reference_service("1")
        rendered = "\n".join(call.args[0] for call in scroll.call_args_list)
        self.assertIn("A1002", rendered)
        self.assertIn("MODULATOR-DEMODULATOR", rendered.upper())

    def test_reference_browse_is_paginated(self):
        with patch("builtins.input", side_effect=["B", "F", "13", "", "M"]), patch.object(compuserve, "ansi_scroll") as scroll, patch.object(compuserve, "clear"), patch.object(compuserve, "header_bar"):
            compuserve.reference_service("4")
        rendered = "\n".join(call.args[0] for call in scroll.call_args_list)
        self.assertIn("PAGE 1 OF 5", rendered)
        self.assertIn("PAGE 2 OF 5", rendered)

    def test_global_find_includes_reference_records(self):
        results = cis_discovery.search(compuserve, "ozone")
        self.assertIn("REFERENCE S3003 ANTARCTIC OZONE MEASUREMENTS", results)

    def test_member_classified_can_receive_inquiry(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                number = cis_dynamic.post_classified(compuserve, "FOR SALE: 1200 baud modem")
                with patch.object(compuserve, "current_user_id", "70000,0002"):
                    result = cis_dynamic.classified_action(compuserve, number, "inquire", "Is it still available?")
                state = cis_dynamic.load_state(compuserve)
            self.assertIn("EasyPlex", result)
            self.assertEqual(state["events"][-1]["payload"]["to"], "70000,0001")

    def test_legacy_classified_without_id_is_migrated(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            with patch.object(compuserve, "BASE_DIR", directory), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
                compuserve.save_json_atomic("dynamic_state.json", {
                    "classified_day": "1988-12-15",
                    "classifieds": [{"text": "FOR SALE: EGA monitor", "status": "ACTIVE", "expires": "1988-12-30"}],
                })
                listings = cis_dynamic.active_classifieds(compuserve, [])
                state = cis_dynamic.load_state(compuserve)
            self.assertEqual(listings, ["#1 [GENERAL] FOR SALE: EGA monitor"])
            self.assertEqual(state["classifieds"][0]["id"], 1)

    def test_member_classified_survives_simulated_day_change(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
                number = cis_dynamic.post_classified(compuserve, "FOR SALE: cherished modem")
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-16"}):
                listings = cis_dynamic.active_classifieds(compuserve, [])
            self.assertTrue(any(f"#{number}" in item for item in listings))

    def test_default_events_wait_for_simulated_time(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15", "CIS_SIMULATION_TIME": "12:00"}):
                cis_dynamic.schedule_event(compuserve, "mail", {"to": "70000,0001", "subject": "LATER", "body": "Not yet"})
                self.assertFalse(cis_dynamic.process_events(compuserve))

    def test_monotonic_timeline_delivers_event_across_december_wrap(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-31", "CIS_SIMULATION_TIME": "12:00"}):
                compuserve.save_json_atomic("dynamic_state.json", {"simulation_date": "1988-12-31", "simulation_time": "12:00", "timeline_day": 0})
                cis_dynamic.schedule_event(compuserve, "mail", {"to": "70000,0001", "subject": "NEW YEAR", "body": "Visible calendar wrapped."}, cis_dynamic.simulation_datetime() + timedelta(days=1))
                self.assertFalse(cis_dynamic.process_events(compuserve))
                self.assertIn("12/01/88", cis_dynamic.manage_event(compuserve, "ADVANCE 1 DAY"))
                self.assertTrue(cis_dynamic.process_events(compuserve))
                messages = compuserve.load_json("easyplex.json", default=[])
            self.assertEqual(messages[0]["subject"], "NEW YEAR")

    def test_reservation_appears_in_dashboard_state(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                confirmation = cis_dynamic.reserve_itinerary(compuserve, "ORD", "LGA", "AA 204 ORD 0830 LGA 1120")
                state = cis_dynamic.load_state(compuserve)
            self.assertEqual(state["reservations"][0]["confirmation"], confirmation)

    def test_generated_library_document_is_readable(self):
        original = compuserve.library_files
        try:
            with tempfile.TemporaryDirectory() as directory:
                file = {"number": 1, "name": "MODEMREF.TXT", "bytes": 4096, "date": "12/15/88", "downloads": 0, "description": "Modem reference"}
                compuserve.library_files = {"test": [file]}
                with patch.object(compuserve, "BASE_DIR", Path(directory)):
                    output = cis_library.materialize_download(compuserve, file, "B")
                text = output.read_text(encoding="ascii")
            self.assertIn("ATDT", text)
        finally:
            compuserve.library_files = original

    def test_forum_thread_tree_and_watch_notification_workflow(self):
        original_threads, original_profiles = compuserve.forum_threads, compuserve.profiles
        try:
            with tempfile.TemporaryDirectory() as directory:
                compuserve.forum_threads = {"sample": [{"id": 10, "parent_id": None, "author": "DiskDoctor", "subject": "Disk question", "body": "Help"}]}
                compuserve.profiles = {"70000,0001": {"watched_threads": []}, "70000,0002": {}}
                with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"), patch.object(compuserve, "current_profile", compuserve.profiles["70000,0001"]), patch.object(compuserve, "ansi_scroll"):
                    cis_forums.set_watch(compuserve, 10, True)
                with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0002"), patch.object(compuserve, "current_profile", compuserve.profiles["70000,0002"]), patch.object(compuserve, "ansi_scroll"):
                    cis_forums.post(compuserve, "sample", "RE: Disk question", "Try another cable.", parent_id=10)
                    state = cis_dynamic.load_state(compuserve)
                tree = cis_forums.thread_lines(compuserve.forum_threads["sample"], 10)
            self.assertEqual(len(tree), 2)
            self.assertEqual(state["events"][-1]["payload"]["to"], "70000,0001")
        finally:
            compuserve.forum_threads, compuserve.profiles = original_threads, original_profiles

    def test_root_watch_receives_nested_reply_notification(self):
        original_threads, original_profiles = compuserve.forum_threads, compuserve.profiles
        try:
            with tempfile.TemporaryDirectory() as directory:
                compuserve.forum_threads = {"sample": [
                    {"id": 10, "parent_id": None, "author": "DiskDoctor", "subject": "Disk question", "body": "Help"},
                    {"id": 11, "parent_id": 10, "author": "ByteBender", "subject": "RE: Disk question", "body": "Which controller?"},
                ]}
                compuserve.profiles = {"70000,0001": {"watched_threads": [10]}, "70000,0002": {}}
                with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0002"), patch.object(compuserve, "current_profile", compuserve.profiles["70000,0002"]), patch.object(compuserve, "ansi_scroll"):
                    cis_forums.post(compuserve, "sample", "RE: Disk question", "It is an MFM controller.", parent_id=11)
                    state = cis_dynamic.load_state(compuserve)
                self.assertEqual(state["events"][-1]["payload"]["to"], "70000,0001")
                self.assertIn("THREAD #10", state["events"][-1]["payload"]["subject"])
        finally:
            compuserve.forum_threads, compuserve.profiles = original_threads, original_profiles

    def test_member_can_cancel_order_and_reservation(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                compuserve.save_json_atomic("orders.json", [{"user_id": "70000,0001", "number": 1101, "status": "RECEIVED"}])
                cis_dynamic.reserve_itinerary(compuserve, "ORD", "LGA", "AA 204 ORD 0830 LGA 1120")
                order_result = cis_dynamic.cancel_member_item(compuserve, "CANCEL ORDER 1101")
                reservation_result = cis_dynamic.cancel_member_item(compuserve, "CANCEL RES CIS1001")
            self.assertEqual(order_result, "Order cancelled.")
            self.assertEqual(reservation_result, "Reservation cancelled.")

    def test_sysop_announcement_appears_on_main_screen(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)):
                self.assertIn("posted", cis_dynamic.manage_content(compuserve, "ANN Maintenance at 11 PM"))
                lines = cis_dynamic.announcements("70000,0001", 0, compuserve)
            self.assertIn("Maintenance at 11 PM", lines)

    def test_web_terminal_never_reads_physical_console_flow_control(self):
        with (
            patch.dict("os.environ", {"CIS_WEB_TERMINAL": "1"}),
            patch.object(compuserve, "msvcrt") as console,
        ):
            self.assertIsNone(compuserve.terminal_flow_control())
        console.kbhit.assert_not_called()

    def test_simulation_is_anchored_to_1988(self):
        self.assertEqual(compuserve.SIMULATION_YEAR, 1988)
        self.assertIn(compuserve.SCREEN_WIDTH, (40, 80))
        self.assertEqual(compuserve.BAUD_RATES[1200], 12.00)

    def test_all_declared_targets_exist(self):
        for targets in compuserve.OPTION_TARGETS.values():
            for target in targets.values():
                self.assertIn(target, compuserve.screens)

    def test_main_menu_has_an_explicit_target_for_every_option(self):
        self.assertEqual(
            set(compuserve.screens["main"]["options"]),
            set(compuserve.OPTION_TARGETS["main"]),
        )

    def test_every_library_menu_target_exists(self):
        self.assertEqual(
            set(compuserve.screens["ibmhw_libs"]["options"]),
            set(compuserve.OPTION_TARGETS["ibmhw_libs"]),
        )

    def test_remaining_forum_data_is_present(self):
        sections = {
            "macdev_general", "photography_general", "hamnet_general",
            "science_general", "gamers_pc", "gamers_console",
            "gamers_reviews", "ibmhw_reviews", "ibmhw_tips",
            "ibmhw_vendors", "ibmhw_announcements", "ibmhw_rules",
        }
        for section in sections:
            self.assertTrue(compuserve.forum_threads.get(section), section)

    def test_return_to_menu_is_rendered_once(self):
        with (
            patch.object(compuserve, "ansi_scroll") as scroll,
            patch.object(compuserve, "clear"),
        ):
            compuserve.show_screen("main")
        rendered = [call.args[0] for call in scroll.call_args_list]
        self.assertEqual(
            sum("Return to previous menu" in text for text in rendered), 1
        )
        self.assertFalse(any("Connect time" in text for text in rendered))
        self.assertFalse(any("charges" in text.lower() for text in rendered))

    def test_modem_transcript_uses_result_code_not_narration(self):
        with (
            patch.object(compuserve, "connection_baud", 1200),
            patch.object(compuserve, "ansi_scroll") as scroll,
            patch.object(compuserve, "clear"),
        ):
            compuserve.modem_dial_in()
        rendered = "\n".join(call.args[0] for call in scroll.call_args_list)
        self.assertIn("CONNECT 1200", rendered)
        self.assertNotIn("Handshake complete", rendered)
        self.assertNotIn("Connecting...", rendered)

    def test_variable_modem_can_report_busy_and_quit(self):
        with (
            patch.dict(compuserve.startup_options, {"connection_mode": "variable"}),
            patch.object(compuserve.random, "choices", return_value=["BUSY"]),
            patch("builtins.input", return_value="Q"),
            patch.object(compuserve, "ansi_scroll") as scroll,
            patch.object(compuserve, "clear"),
            patch.object(compuserve, "modem_sound"),
        ):
            connected = compuserve.modem_dial_in()
        self.assertFalse(connected)
        self.assertIn("BUSY", [call.args[0] for call in scroll.call_args_list])

    def test_terminal_flow_control_pauses_until_ctrl_q(self):
        terminal = Mock()
        terminal.kbhit.return_value = True
        terminal.getwch.side_effect = ["\x13", "\x11"]
        with patch.object(compuserve, "msvcrt", terminal):
            self.assertIsNone(compuserve.terminal_flow_control())

    def test_period_menus_do_not_use_modern_shopping_labels(self):
        rendered = json.dumps(compuserve.screens)
        for modern_label in ("Online Mall", "Coupons & Deals", "Vacation Planner"):
            self.assertNotIn(modern_label, rendered)

    def test_every_forum_has_sections_with_messages(self):
        import copy
        forums = cis_communities.merge_forums(copy.deepcopy(compuserve.forum_threads))
        for forum in compuserve.FORUM_CATALOG.values():
            self.assertTrue(forum["sections"])
            for section, _ in forum["sections"].values():
                self.assertTrue(forums.get(section), section)

    def test_live_news_uses_wire_style_and_returns_to_menu(self):
        sample = {"World": [{"title": "Current headline", "summary": "Dispatch text"}]}
        with (
            patch.object(compuserve, "load_json", return_value=sample),
            patch.object(compuserve, "ansi_scroll") as scroll,
            patch.object(compuserve, "clear"),
            patch("builtins.input", return_value="M"),
        ):
            compuserve.news_section("World")
        rendered = "\n".join(call.args[0] for call in scroll.call_args_list)
        self.assertIn("NEWS WIRE - WORLD", rendered)
        self.assertIn("Current headline", rendered)

    def test_period_news_avoids_repeats_for_five_editions(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
                editions = [compuserve.cis_period_news.edition(compuserve) for _ in range(5)]
            identifiers = [story["id"] for edition in editions for story in edition]
            self.assertEqual(len(identifiers), 60)
            self.assertEqual(len(set(identifiers)), 60)
            self.assertTrue(all(story["published"].endswith("/88") for edition in editions for story in edition))

    def test_cb_has_broad_topics_and_contextual_followup(self):
        prompts = {
            "My EGA monitor flickers": "display",
            "The floppy drive has a bad sector": "disk",
            "MultiFinder runs out of memory": "mac",
            "My TNC will not send a packet": "radio",
            "The dot matrix printer ribbon is pale": "printer",
        }
        for message in prompts:
            self.assertIsNotNone(cis_dynamic.cb_response("3", message, 2))
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"), patch.object(compuserve, "current_handle", "BYTE RIDER"):
                first = cis_dynamic.cb_response("3", "My EGA monitor flickers", 2, compuserve)
                second = cis_dynamic.cb_response("3", "What should I check?", 3, compuserve)
            self.assertEqual(first[0], second[0])
            self.assertTrue(second[1].endswith("?"))

    def test_classic_help_and_off_commands_are_global(self):
        with (
            patch("builtins.input", side_effect=["H", "", "OFF"]),
            patch.object(compuserve, "ansi_scroll"),
            patch.object(compuserve, "clear"),
            patch.object(compuserve, "show_logout_summary") as logout,
        ):
            compuserve.navigate()
        logout.assert_called_once()

    def test_page_addresses_and_relative_go_are_functional(self):
        self.assertEqual(compuserve.resolve_go_destination("CIS-1"), "main")
        self.assertEqual(compuserve.resolve_go_destination("PCS-31"), "mail")
        self.assertEqual(compuserve.resolve_go_destination("4", "main"), "support")
        self.assertEqual(compuserve.resolve_go_destination("IBMHW"), "ibmhw")

    def test_terminal_output_wraps_to_selected_width(self):
        output = io.StringIO()
        with (
            patch.object(compuserve, "SCREEN_WIDTH", 40),
            patch.object(compuserve.time, "sleep"),
            patch.object(compuserve.sys, "stdout", output),
        ):
            compuserve.ansi_scroll("word " * 20, 0)
        lines = output.getvalue().splitlines()
        self.assertTrue(lines)
        self.assertTrue(all(len(line) <= 40 for line in lines))

    def test_top_menu_matches_golden_transcript(self):
        lines = compuserve.menu_lines(
            "CompuServe",
            "CIS-1",
            "CompuServe Information Service",
            compuserve.screens["main"]["options"],
            80,
        )
        lines[0] = "CompuServe|CIS-1"
        expected = (Path(__file__).parent / "testdata" / "top_menu_80.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertEqual(lines[:-1], expected)
        self.assertEqual(lines[-1], "")

    def test_schema_migration_adds_profile_defaults(self):
        migrated, changed = compuserve.migrate_data(
            "profiles.json", {"70000,0001": {"name": "Test User"}}
        )
        self.assertTrue(changed)
        self.assertEqual(migrated["70000,0001"]["name"], "Test User")
        self.assertEqual(migrated["70000,0001"]["failed_logins"], 0)
        self.assertIn("locked", migrated["70000,0001"])

    def test_linedit_supports_list_replace_delete_and_save(self):
        entries = ["first", "second", "REPLACE 2 revised", "DELETE 1", "SAVE"]
        with (
            patch("builtins.input", side_effect=entries),
            patch.object(compuserve, "ansi_scroll"),
        ):
            body = compuserve.line_editor()
        self.assertEqual(body, "revised")

    def test_time_of_day_changes_connection_rate(self):
        standard = compuserve.datetime(1988, 12, 17, 12, 0)  # Saturday
        prime = compuserve.datetime(1988, 12, 19, 12, 0)  # Monday
        with patch.object(compuserve, "connection_baud", 1200):
            self.assertEqual(compuserve.connection_rate_per_hour(standard), 12.0)
            self.assertEqual(compuserve.connection_rate_per_hour(prime), 21.0)

    def test_library_records_have_period_transfer_metadata(self):
        required = {"number", "name", "bytes", "date", "downloads", "description"}
        for screen in compuserve.OPTION_TARGETS["ibmhw_libs"].values():
            self.assertTrue(compuserve.library_files.get(screen), screen)
            for file in compuserve.library_files[screen]:
                self.assertTrue(required.issubset(file), file)

    def test_startup_configuration_changes_terminal_and_dialing(self):
        old_baud = compuserve.connection_baud
        old_width = compuserve.SCREEN_WIDTH
        old_options = dict(compuserve.startup_options)
        try:
            with tempfile.TemporaryDirectory() as directory:
                with (
                    patch.object(compuserve, "BASE_DIR", Path(directory)),
                    patch(
                        "builtins.input",
                        side_effect=["C", "2400", "40", "screen", "Y", "clean", "N", "N", "N", "N"],
                    ),
                    patch.object(compuserve, "ansi_scroll"),
                ):
                    compuserve.startup_configuration()
            self.assertEqual(compuserve.connection_baud, 2400)
            self.assertEqual(compuserve.SCREEN_WIDTH, 40)
            self.assertTrue(compuserve.startup_options["skip_dialing"])
        finally:
            compuserve.connection_baud = old_baud
            compuserve.SCREEN_WIDTH = old_width
            compuserve.startup_options.clear()
            compuserve.startup_options.update(old_options)

    def test_remaining_top_services_have_data(self):
        for key in ("quotes", "exchange", "hotels", "reference", "catalog", "classifieds"):
            self.assertTrue(compuserve.service_data.get(key), key)

    def test_password_hashes_are_salted_and_verifiable(self):
        first = compuserve.hash_password("secret")
        second = compuserve.hash_password("secret")
        self.assertNotEqual(first, second)
        self.assertTrue(compuserve.verify_password("secret", first))
        self.assertFalse(compuserve.verify_password("wrong", first))

    def test_adventure_game_can_be_completed(self):
        with (
            patch("builtins.input", side_effect=["TAKE KEY", "NORTH", "WEST", "TAKE FUSE", "EAST", "EAST", "INSTALL FUSE", "BOOT", ""]),
            patch.object(compuserve, "ansi_scroll") as scroll,
        ):
            compuserve.adventure_game()
        rendered = "\n".join(call.args[0] for call in scroll.call_args_list)
        self.assertIn("YOU HAVE WON", rendered)

    def test_megawars_ship_is_saved_between_sessions(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"), patch("builtins.input", side_effect=["TRADE", "SAVE"]), patch.object(compuserve, "ansi_scroll"):
                compuserve.megawars_game()
                state = cis_dynamic.load_state(compuserve)
            self.assertEqual(state["megawars"]["70000,0001"]["cargo"], 1)
            self.assertEqual(state["megawars"]["70000,0001"]["credits"], 80)

    def test_megawars_mission_missiles_and_progression_persist(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0099"),
                patch("builtins.input", side_effect=["MISSION", "JUMP", "MISSILE", "MISSILE", ""]),
                patch.object(compuserve, "ansi_scroll"),
                patch.object(compuserve.random, "randint", return_value=40),
            ):
                compuserve.megawars_game()
                ship = cis_dynamic.load_state(compuserve)["megawars"]["70000,0099"]
            self.assertEqual(ship["missions"], 1)
            self.assertEqual(ship["victories"], 1)
            self.assertEqual(ship["missiles"], 0)
            self.assertGreater(ship["experience"], 0)
            self.assertIsNone(ship["mission_target"])

    def test_trivia_tournament_records_perfect_round(self):
        answers = ["IBM", "MICROSOFT", "8", "AT", "5.25"]
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0098"),
                patch("builtins.input", side_effect=answers),
                patch.object(compuserve, "ansi_scroll"),
                patch.object(compuserve.random.Random, "sample", return_value=compuserve.TRIVIA_BANK[:5]),
            ):
                compuserve.trivia_tournament()
                state = cis_dynamic.load_state(compuserve)
            record = state["trivia_tournaments"]["70000,0098"]
            self.assertEqual(record["rounds"], 1)
            self.assertEqual(record["best"], 5)
            self.assertEqual(record["points"], 75)
            self.assertEqual(state["scores"]["70000,0098"], {"correct": 5, "attempts": 5})

    def test_adventure_win_updates_player_record(self):
        commands = ["TAKE KEY", "NORTH", "WEST", "TAKE FUSE", "EAST", "EAST", "INSTALL FUSE", "BOOT", ""]
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0097"),
                patch("builtins.input", side_effect=commands),
                patch.object(compuserve, "ansi_scroll"),
            ):
                compuserve.adventure_game()
                record = cis_dynamic.load_state(compuserve)["adventure_records"]["70000,0097"]
            self.assertEqual(record["wins"], 1)
            self.assertEqual(record["best_moves"], 8)

    def test_adventure_league_character_quest_and_daily_limit_persist(self):
        roller = Mock(); roller.randint.return_value = 12
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0101"),
                patch.object(cis_adventure_league.random, "Random", return_value=roller),
            ):
                self.assertIn("WELCOME", cis_adventure_league.create_character(compuserve, "Nova", "SCOUT"))
                self.assertIn("VICTORY", cis_adventure_league.undertake(compuserve, "RELAY", "SEARCH"))
                hero = cis_adventure_league.character(compuserve)
                self.assertIn("COPPER KEY", hero["inventory"])
                self.assertEqual(hero["campaign"], 2)
                self.assertIn("already complete", cis_adventure_league.undertake(compuserve, "VAULT", "SEARCH"))

    def test_adventure_league_guild_party_journal_and_world_control(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0102"),
                patch.object(compuserve, "forum_threads", {}),
            ):
                cis_adventure_league.create_character(compuserve, "Bit Ranger", "ENGINEER")
                self.assertIn("GUILD JOINED", cis_adventure_league.join_guild(compuserve, "Night Shift"))
                self.assertIn("SENT", cis_adventure_league.invite_party(compuserve, "ByteBender"))
                self.assertIn("posted", cis_adventure_league.post_journal(compuserve, "Found a strange relay."))
                self.assertTrue(compuserve.forum_threads["gamers_general"][0]["adventure_league"])
                self.assertIn("set", cis_dynamic.manage_world(compuserve, "ADVENTURE DOUBLE XP FESTIVAL"))
                self.assertEqual(cis_adventure_league.world_event(compuserve), "DOUBLE XP FESTIVAL")
                hero = cis_adventure_league.character(compuserve)
                self.assertEqual(hero["guild"], "NIGHT SHIFT")
                self.assertEqual(hero["party"], ["ByteBender"])

    def test_cross_service_story_seeds_mail_forum_and_persists_decision(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0088"),
                patch.object(compuserve, "forum_threads", {}),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}),
            ):
                self.assertTrue(compuserve.cis_story.ensure_case(compuserve))
                self.assertFalse(compuserve.cis_story.ensure_case(compuserve))
                mail = compuserve.load_json("easyplex.json", default=[])
                self.assertEqual(sum(message.get("subject") == "MEMBER RESEARCH REQUEST CHIP-88" for message in mail), 1)
                self.assertTrue(any(message.get("story_case") == "CHIP-88" for message in compuserve.forum_threads["ibmhw_hw"]))
                for source in ("NEWS", "FORUM", "REFERENCE"):
                    compuserve.cis_story.source_lines(compuserve, source)
                result = compuserve.cis_story.decide(compuserve, "REPORT")
                state = cis_dynamic.load_state(compuserve)
                case = state["story_cases"]["70000,0088"]
                self.assertIn("privately", result)
                self.assertEqual(case["decision"], "REPORT")
                self.assertEqual(case["status"], "REFERRED TO DISTRIBUTOR")
                self.assertTrue(any(message.get("subject", "").startswith("CHIP-88 CLOSED") for message in compuserve.load_json("easyplex.json", default=[])))

    def test_story_is_unavailable_before_its_simulated_date(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0087"),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-01"}),
            ):
                self.assertFalse(compuserve.cis_story.ensure_case(compuserve))
                self.assertNotIn("story_cases", cis_dynamic.load_state(compuserve))

    def test_import_does_not_depend_on_current_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [sys.executable, "-c", "import compuserve"],
                cwd=directory,
                env={"PYTHONPATH": str(compuserve.BASE_DIR)},
                capture_output=True,
                text=True,
                timeout=10,
            )
        self.assertEqual(result.returncode, 0, result.stderr)


class PersistenceTests(unittest.TestCase):
    def test_every_prior_schema_version_upgrades_to_current(self):
        for prior in range(cis_migrations.CURRENT_SCHEMA_VERSION):
            with self.subTest(prior=prior), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                cis_storage.database_status(base)
                with closing(sqlite3.connect(base / "compuserve.db")) as database:
                    database.execute("INSERT INTO metadata(key, value) VALUES ('app_schema', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(prior),))
                    database.commit()
                version, backup = cis_storage.upgrade_database(base, cis_migrations.CURRENT_SCHEMA_VERSION)
                self.assertEqual(version, cis_migrations.CURRENT_SCHEMA_VERSION)
                self.assertTrue(backup.exists())

    def test_state_repair_fixes_malformed_new_service_records(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)):
                compuserve.save_json_atomic("dynamic_state.json", {"events": [{"bad": True}], "stock_portfolios": {"U": "bad"}, "notebooks": {"U": "bad"}, "reservations": [{}]})
                self.assertTrue(cis_dynamic.repair_state(compuserve))
                self.assertEqual(cis_dynamic.validate_state(compuserve), [])

    def test_web_password_input_uses_the_relayed_input_stream(self):
        with (
            patch.dict("os.environ", {"CIS_WEB_TERMINAL": "1"}),
            patch("builtins.input", return_value="secret") as web_input,
            patch.object(compuserve.getpass, "getpass") as console_input,
        ):
            self.assertEqual(compuserve.password_input("Password: "), "secret")
        web_input.assert_called_once_with("Password: ")
        console_input.assert_not_called()

    def test_malformed_chat_data_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fake_lines.json"
            path.write_text("not json", encoding="utf-8")
            with patch.object(fake2, "INPUT_FILE", path):
                with self.assertRaises(RuntimeError):
                    fake2.append_random_chat_line()
            self.assertEqual(path.read_text(encoding="utf-8"), "not json")

    def test_easyplex_composition_is_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            entries = ["70000,0002", "Test subject", "Line one", "Line two", "SAVE"]
            with (
                patch.object(compuserve, "BASE_DIR", directory),
                patch.object(compuserve, "current_user_id", "70000,0001"),
                patch.object(compuserve, "profiles", {"70000,0002": {}}),
                patch("builtins.input", side_effect=entries),
                patch.object(compuserve, "ansi_scroll"),
            ):
                compuserve.mail_compose()
            messages = cis_storage.load_json(directory, "easyplex.json", default=[])
            self.assertEqual(messages[0]["to"], "70000,0002")
            self.assertEqual(messages[0]["body"], "Line one\nLine two")

    def test_premium_service_accumulates_separate_charge(self):
        original = compuserve.premium_charges
        try:
            compuserve.premium_charges = 0
            with (
                patch("builtins.input", return_value="Y"),
                patch.object(compuserve, "ansi_scroll"),
                patch.object(compuserve, "clear"),
                patch.object(compuserve, "header_bar"),
            ):
                compuserve.premium_service("$ MicroQuote")
            self.assertEqual(compuserve.premium_charges, 0.5)
        finally:
            compuserve.premium_charges = original

    def test_library_transfer_creates_real_file_and_updates_count(self):
        original_files = compuserve.library_files
        try:
            with tempfile.TemporaryDirectory() as directory:
                directory = Path(directory)
                file = {
                    "number": 1, "name": "TEST.TXT", "bytes": 256,
                    "date": "12/15/88", "downloads": 0, "description": "Test file",
                }
                compuserve.library_files = {"test": [file]}
                with (
                    patch.object(compuserve, "BASE_DIR", directory),
                    patch("builtins.input", return_value="B"),
                    patch.object(compuserve, "ansi_scroll"),
                ):
                    compuserve.library_transfer(file)
                downloaded = directory / "downloads" / "TEST.TXT"
                self.assertEqual(downloaded.stat().st_size, 256)
                self.assertEqual(file["downloads"], 1)
        finally:
            compuserve.library_files = original_files

    def test_backup_and_restore_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            with patch.object(compuserve, "BASE_DIR", directory):
                compuserve.save_json_atomic("profiles.json", {"before": True})
                archive = compuserve.create_data_backup()
                compuserve.save_json_atomic("profiles.json", {"after": True})
                restored = compuserve.restore_latest_backup()
            self.assertEqual(restored, archive)
            self.assertEqual(cis_storage.load_json(directory, "profiles.json"), {"before": True})

    def test_legacy_json_is_imported_once_into_sqlite(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            profiles = directory / "profiles.json"
            profiles.write_text('{"good": true}', encoding="utf-8")
            first = cis_storage.load_json(directory, "profiles.json")
            profiles.write_text('{"changed": true}', encoding="utf-8")
            second = cis_storage.load_json(directory, "profiles.json")
            self.assertEqual(first, {"good": True})
            self.assertEqual(second, {"good": True})
            self.assertTrue((directory / "compuserve.db").is_file())

    def test_transactional_upgrade_repairs_legacy_records_and_creates_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            cis_storage.write_json_atomic(directory, "dynamic_state.json", {"classifieds": [{"text": "FOR SALE: modem"}]})
            cis_storage.write_json_atomic(directory, "profiles.json", {"70000,0001": {}})
            cis_storage.write_json_atomic(directory, "forums.json", {"sample": [{"id": 1}]})
            version, backup = cis_storage.upgrade_database(directory, 8)
            state = cis_storage.load_json(directory, "dynamic_state.json")
            profiles = cis_storage.load_json(directory, "profiles.json")
            forums = cis_storage.load_json(directory, "forums.json")
            status = cis_storage.database_status(directory)
            self.assertEqual(version, 8)
            self.assertTrue(backup.is_file())
            self.assertEqual(state["classifieds"][0]["id"], 1)
            self.assertEqual(profiles["70000,0001"]["watched_threads"], [])
            self.assertIsNone(forums["sample"][0]["parent_id"])
            self.assertEqual(status["integrity"], "ok")

    def test_sysop_clock_controls_persist(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {}, clear=False):
                result = cis_dynamic.manage_event(compuserve, "SET DATE 12/20/88")
                result_time = cis_dynamic.manage_event(compuserve, "SET TIME 21:30")
                state = cis_dynamic.load_state(compuserve)
            self.assertIn("12/20/88", result)
            self.assertIn("21:30", result_time)
            self.assertEqual(state["simulation_date"], "1988-12-20")

    def test_news_refresh_failure_is_reported_without_crashing(self):
        with (
            patch.dict("sys.modules", {"news_feed": None}),
            patch.object(compuserve, "ansi_scroll") as scroll,
        ):
            result = compuserve.refresh_current_news()
        self.assertFalse(result)
        rendered = "\n".join(call.args[0] for call in scroll.call_args_list)
        self.assertIn("previous news edition preserved", rendered)

    def test_capture_writes_displayed_session_text(self):
        old_capture = compuserve.capture_path
        try:
            with tempfile.TemporaryDirectory() as directory:
                directory = Path(directory)
                with (
                    patch.object(compuserve, "BASE_DIR", directory),
                    patch.object(compuserve.time, "sleep"),
                    patch.object(compuserve.sys, "stdout", io.StringIO()),
                ):
                    compuserve.set_capture(True)
                    path = compuserve.capture_path
                    compuserve.ansi_scroll("Captured display", 0)
                    compuserve.set_capture(False)
                self.assertIn("Captured display", path.read_text(encoding="utf-8"))
        finally:
            compuserve.capture_path = old_capture

    def test_unknown_easyplex_recipient_generates_failure_notice(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            entries = ["70000,9999", "Y", "Missing user", "Test body", "SAVE"]
            with (
                patch.object(compuserve, "BASE_DIR", directory),
                patch.object(compuserve, "current_user_id", "70000,0001"),
                patch.object(compuserve, "profiles", {}),
                patch("builtins.input", side_effect=entries),
                patch.object(compuserve, "ansi_scroll"),
            ):
                compuserve.mail_compose()
            messages = cis_storage.load_json(directory, "easyplex.json", default=[])
            self.assertEqual(len(messages), 2)
            self.assertEqual(messages[1]["from"], "POSTMASTER")

    def test_legacy_account_establishes_hashed_password(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            accounts = {"70000,0001": {"last_handle": "TEST"}}
            with (
                patch.object(compuserve, "BASE_DIR", directory),
                patch.object(compuserve, "profiles", accounts),
                patch.object(compuserve.getpass, "getpass", side_effect=["secret", "secret"]),
                patch.object(compuserve, "ansi_scroll"),
            ):
                self.assertTrue(compuserve.authenticate_account("70000,0001"))
            encoded = accounts["70000,0001"]["password_hash"]
            self.assertTrue(compuserve.verify_password("secret", encoded))

    def test_three_failed_passwords_lock_account(self):
        with tempfile.TemporaryDirectory() as directory:
            accounts = {"70000,0001": {"password_hash": compuserve.hash_password("correct")}}
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "profiles", accounts),
                patch.object(compuserve.getpass, "getpass", return_value="wrong"),
                patch.object(compuserve, "ansi_scroll"),
            ):
                self.assertFalse(compuserve.authenticate_account("70000,0001"))
            self.assertTrue(accounts["70000,0001"]["locked"])

    def test_sysop_approval_changes_upload_visibility_state(self):
        files = {"library": [{"number": 42, "status": "pending"}]}
        self.assertEqual(len(compuserve.pending_uploads(files)), 1)
        self.assertTrue(compuserve.set_upload_status(files, 42, "approved"))
        self.assertEqual(files["library"][0]["status"], "approved")

    def test_sysop_can_reset_a_locked_password(self):
        accounts = {
            "70000,0001": {
                "password_hash": compuserve.hash_password("forgotten"),
                "locked": True,
            }
        }
        self.assertTrue(compuserve.reset_password(accounts, "70000,0001"))
        self.assertNotIn("password_hash", accounts["70000,0001"])
        self.assertFalse(accounts["70000,0001"]["locked"])

    def test_forum_reply_is_persisted(self):
        original_threads = compuserve.forum_threads
        try:
            with tempfile.TemporaryDirectory() as directory:
                directory = Path(directory)
                message = {"id": 1, "date": "12/01/88", "author": "OTHER", "subject": "Question", "body": "Text"}
                threads = {"sample": [message]}
                compuserve.forum_threads = threads
                with (
                    patch.object(compuserve, "BASE_DIR", directory),
                    patch.object(compuserve, "current_user_id", "70000,0001"),
                    patch.object(compuserve, "current_handle", None),
                    patch("builtins.input", side_effect=["R", "Reply text", "SAVE"]),
                    patch.object(compuserve, "ansi_scroll"),
                ):
                    compuserve.forum_message_actions("sample", message)
                saved = cis_storage.load_json(directory, "forums.json", default={})
                self.assertEqual(saved["sample"][1]["subject"], "RE: Question")
        finally:
            compuserve.forum_threads = original_threads


class BusinessTravelTests(unittest.TestCase):
    def test_flight_times_are_valid_and_travel_dates_are_bounded(self):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            flights = cis_dynamic.flight_schedule("ORD", "LGA", "12/20/88")[:3]
        for flight in flights:
            fields = flight.split()
            departure = fields[3]
            arrival = fields[5].removesuffix("+1")
            self.assertLess(int(departure[:2]), 24); self.assertLess(int(departure[2:]), 60)
            self.assertLess(int(arrival[:2]), 24); self.assertLess(int(arrival[2:]), 60)
        self.assertEqual(cis_travel.validate_travel_date("12/31/88"), "12/31/88")
        self.assertIsNone(cis_travel.validate_travel_date("12/32/88"))
        self.assertIsNone(cis_travel.validate_travel_date("01/01/89"))

    def test_company_directory_reports_and_quotes_are_expanded(self):
        self.assertGreaterEqual(len(cis_business.COMPANIES), 12)
        self.assertIn("MSFT", [item[0] for item in cis_business.directory("software")])
        quotes = cis_dynamic.market_quotes(compuserve.service_data["quotes"])
        self.assertGreaterEqual(len(quotes), 12)
        self.assertTrue(any("Microsoft" in line for line in cis_business.report("MSFT", quotes)))

    def test_finance_watchlist_persists_by_member(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                self.assertIn("added", cis_business.watchlist(compuserve, "IBM"))
                self.assertEqual(cis_business.watchlist(compuserve), ["IBM"])

    def test_market_simulator_tracks_cash_positions_and_profit_loss(self):
        quotes = {"IBM": {"last": 100.0, "change": 0.0}}
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                self.assertIn("BUY RECORDED", cis_business.trade(compuserve, "BUY", "IBM", 10, quotes))
                portfolio = cis_business._portfolio(compuserve)
                self.assertEqual(portfolio["holdings"]["IBM"]["shares"], 10)
                self.assertEqual(portfolio["cash"], 8985.0)
                self.assertIn("SELL RECORDED", cis_business.trade(compuserve, "SELL", "IBM", 4, quotes))
                portfolio = cis_business._portfolio(compuserve)
                self.assertEqual(portfolio["holdings"]["IBM"]["shares"], 6)
                self.assertLess(portfolio["realized"], 0)
                lines = cis_business.portfolio_lines(compuserve, quotes)
                self.assertTrue(any("UNREALIZED P/L" in line for line in lines))
                self.assertEqual(len(cis_business.ledger_lines(compuserve)), 2)

    def test_concurrent_market_trades_do_not_lose_positions(self):
        quotes = {"IBM": {"last": 10.0, "change": 0.0}}
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                with ThreadPoolExecutor(max_workers=8) as pool:
                    results = list(pool.map(lambda _: cis_business.trade(compuserve, "BUY", "IBM", 1, quotes), range(20)))
                self.assertTrue(all("RECORDED" in result for result in results))
                self.assertEqual(cis_business._portfolio(compuserve)["holdings"]["IBM"]["shares"], 20)

    def test_market_simulator_rejects_overselling_and_insufficient_cash(self):
        quotes = {"IBM": {"last": 100.0, "change": 0.0}}
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                self.assertIn("only 0", cis_business.trade(compuserve, "SELL", "IBM", 1, quotes))
                self.assertIn("required", cis_business.trade(compuserve, "BUY", "IBM", 9999, quotes))
                self.assertEqual(cis_business.ledger_lines(compuserve), ["No simulated trades recorded."])

    def test_limit_order_fills_and_sends_notification(self):
        quotes = {"IBM": {"last": 100.0, "change": 0.0}}
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                self.assertIn("#1 OPEN", cis_business.place_limit(compuserve, "BUY", "IBM", 2, 101.0))
                self.assertEqual(len(cis_business.process_limits(compuserve, quotes)), 1)
                self.assertEqual(cis_business._portfolio(compuserve)["holdings"]["IBM"]["shares"], 2)
                self.assertIn("[FILLED]", cis_business.limit_lines(compuserve)[0])
                events = cis_dynamic.load_state(compuserve)["events"]
                self.assertTrue(any(event["payload"]["subject"] == "LIMIT ORDER #1 FILLED" for event in events))

    def test_corporate_actions_are_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0001"),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-23"}),
            ):
                state = cis_dynamic.load_state(compuserve)
                portfolio = cis_business._portfolio(compuserve, state)
                portfolio["holdings"] = {"INTC": {"shares": 10, "average_cost": 20.0}, "AAPL": {"shares": 4, "average_cost": 40.0}}
                cis_dynamic.save_state(compuserve, state)
                cis_business.apply_corporate_actions(compuserve)
                cis_business.apply_corporate_actions(compuserve)
                portfolio = cis_business._portfolio(compuserve)
                self.assertEqual(portfolio["cash"], 10001.20)
                self.assertEqual(portfolio["holdings"]["AAPL"], {"shares": 8, "average_cost": 20.0})

    def test_chip_88_decision_changes_semiconductor_sentiment(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                ordinary = cis_dynamic.market_quotes(compuserve.service_data["quotes"])
                state = cis_dynamic.load_state(compuserve)
                state["story_cases"] = {"70000,0001": {"decision": "PUBLISH"}}
                cis_dynamic.save_state(compuserve, state)
                adjusted = cis_business.member_quotes(compuserve, compuserve.service_data["quotes"])
                self.assertEqual(adjusted["INTC"]["last"], round(ordinary["INTC"]["last"] + .80, 2))

    def test_investment_club_forecast_is_scored_at_close(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                self.assertIn("FORECAST FILED", cis_business.submit_forecast(compuserve, "INTC", "DOWN"))
                with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-23"}):
                    lines = cis_business.investment_club_lines(compuserve, cis_dynamic.market_quotes(compuserve.service_data["quotes"]))
                self.assertTrue(any("100 POINTS" in line for line in lines))
                self.assertTrue(any(event["payload"]["subject"] == "MARKET FORECAST SCORECARD" for event in cis_dynamic.load_state(compuserve)["events"]))

    def test_finance_and_travel_packets_are_written(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                quotes = cis_dynamic.market_quotes(compuserve.service_data["quotes"])
                cis_business.watchlist(compuserve, "IBM")
                finance_packet = cis_business.export_packet(compuserve, quotes)
                travel_packet = cis_travel.export_itinerary(compuserve)
                self.assertIn("BUSINESS & FINANCIAL", finance_packet.read_text(encoding="ascii"))
                self.assertIn("FICTIONAL ITINERARY", travel_packet.read_text(encoding="ascii"))

    def test_reservation_progresses_and_trip_folder_tracks_it(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                confirmation = cis_dynamic.reserve_itinerary(compuserve, "ORD", "LGA", "AA 101 ORD 0900 LGA 1200 AVAILABLE $129 COACH", "12/20/88", 2)
                state = cis_dynamic.load_state(compuserve)
                status_event = next(event for event in state["events"] if event["type"] == "reservation_status")
                status_event["due_tick"] = 0
                cis_dynamic.save_state(compuserve, state)
                self.assertTrue(cis_dynamic.process_events(compuserve))
                folder = cis_travel.trip_folder(compuserve)
                self.assertTrue(any(confirmation in line and "TICKETED" in line for line in folder))

    def test_disrupted_itinerary_can_be_rebooked(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                confirmation = cis_dynamic.reserve_itinerary(compuserve, "ORD", "LGA", "AA 101 ORD 0900 LGA 1200 DELAYED $129 COACH", "12/20/88", 1)
                self.assertIn("recorded", cis_dynamic.rebook_itinerary(compuserve, confirmation, "UA 202 ORD 1000 LGA 1300 AVAILABLE $149 COACH"))
                reservation = cis_dynamic.load_state(compuserve)["reservations"][0]
                self.assertEqual(reservation["status"], "REBOOKED")
                self.assertIn("UA 202", reservation["flight"])

    def test_weather_operations_flags_trip_and_sends_alert(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0066"),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-16", "CIS_SIMULATION_TIME": "09:00"}),
            ):
                confirmation = cis_dynamic.reserve_itinerary(compuserve, "ORD", "LGA", "UA 202 ORD 1000 LGA 1300 AVAILABLE $149 COACH", "12/17/88")
                state = cis_dynamic.load_state(compuserve)
                reservation = next(item for item in state["reservations"] if item["confirmation"] == confirmation)
                self.assertIn("ACTION REQUIRED", reservation["status"])
                self.assertEqual(state["travel_disruptions"][confirmation]["storm"], "GL-1216")
                messages = compuserve.load_json("easyplex.json", default=[])
                self.assertTrue(any(message.get("subject", "").startswith(f"ACTION REQUIRED {confirmation}") for message in messages))
                self.assertTrue(any(confirmation in line and "ACTION REQUIRED" in line for line in compuserve.cis_disruptions.member_lines(compuserve)))

    def test_weather_rail_choice_persists_and_blocks_stale_ticketing(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0065"),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-22", "CIS_SIMULATION_TIME": "09:00"}),
            ):
                confirmation = cis_dynamic.reserve_itinerary(compuserve, "BOS", "DCA", "EA 440 BOS 0900 DCA 1100 AVAILABLE $129 COACH", "12/23/88")
                result = compuserve.cis_disruptions.resolve(compuserve, confirmation, "RAIL")
                state = cis_dynamic.load_state(compuserve)
                ticket_event = next(event for event in state["events"] if event["type"] == "reservation_status" and event["payload"]["confirmation"] == confirmation)
                ticket_event["due_tick"] = 0
                cis_dynamic.save_state(compuserve, state)
                cis_dynamic.process_events(compuserve)
                reservation = next(item for item in cis_dynamic.load_state(compuserve)["reservations"] if item["confirmation"] == confirmation)
                self.assertIn("rail", result.lower())
                self.assertEqual(reservation["status"], "REBOOKED - RAIL")
                self.assertEqual(reservation["weather_resolution"], "RAIL")

    def test_global_find_discovers_companies_airports_and_hotels(self):
        self.assertTrue(any(line.startswith("COMPANY MSFT") for line in cis_discovery.search(compuserve, "Microsoft")))
        self.assertTrue(any(line.startswith("AIRPORT ORD") for line in cis_discovery.search(compuserve, "O'Hare")))
        self.assertTrue(any(line.startswith("HOTEL CHICAGO Palmer") for line in cis_discovery.search(compuserve, "Palmer")))

    def test_calendar_notebook_and_representative_are_persistent(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                self.assertIn("#1", cis_experience.add_note(compuserve, "IBM", "Review company report", "FINANCE"))
                self.assertIn("IBM", cis_experience.read_note(compuserve, 1))
                self.assertIn("sent", cis_experience.request_representative(compuserve, "FINANCE", "Explain the quote"))
                self.assertTrue(any("EASYPLEX" in line for line in cis_experience.calendar_lines(compuserve)))

    def test_market_weekends_and_sysop_world_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-17"}, clear=False):
                quotes = cis_dynamic.market_quotes(compuserve.service_data["quotes"])
                self.assertTrue(all(item["change"] == 0 for item in quotes.values()))
                self.assertIn("set", cis_dynamic.manage_world(compuserve, "WEATHER HEAVY SNOW"))
                self.assertTrue(any("HEAVY SNOW" in line for line in cis_dynamic.weather("CHICAGO")))
                self.assertIn("cleared", cis_dynamic.manage_world(compuserve, "CLEAR WEATHER"))

    def test_combined_trip_plan_and_market_challenge(self):
        plan = cis_travel.combined_plan("ORD", "LGA", "NEW YORK", 2, "12/20/88", cis_dynamic.flight_schedule)
        self.assertTrue(any("OUTBOUND" in line for line in plan))
        self.assertTrue(any("LODGING" in line for line in plan))
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                challenge = cis_business.challenge_lines(compuserve, cis_dynamic.market_quotes(compuserve.service_data["quotes"]))
                self.assertTrue(any("PRESERVE CAPITAL" in line for line in challenge))

    def test_travel_directories_and_hotel_reservation(self):
        self.assertEqual(len(cis_travel.AIRPORTS), 12)
        city, hotels = cis_travel.hotels("SFO")
        self.assertEqual(city, "SAN FRANCISCO")
        self.assertEqual(len(hotels), 3)
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0001"):
                confirmation = cis_dynamic.reserve_hotel(compuserve, city, hotels[0], 3)
                self.assertTrue(confirmation.startswith("HTL"))
                reservation = cis_dynamic.load_state(compuserve)["reservations"][0]
                self.assertEqual(reservation["nights"], 3)
                self.assertEqual(reservation["type"], "HOTEL")


class StoreTests(unittest.TestCase):
    def test_catalog_has_period_categories_and_searchable_items(self):
        self.assertEqual(len(cis_store.CATALOG), 36)
        self.assertIn("MODEMS", cis_store.categories())
        self.assertIn("SOFTWARE", cis_store.categories())
        matches = cis_store.search("smartmodem")
        self.assertTrue(matches)
        self.assertTrue(all("smartmodem" in item["name"].lower() for item in matches))

    def test_cart_checkout_persists_order_and_fulfillment_events(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0001"),
            ):
                self.assertIn("added", cis_store.add_to_cart(compuserve, 1101, 2))
                self.assertIn("added", cis_store.add_to_cart(compuserve, 1201))
                lines, subtotal, shipping = cis_store.cart_summary(compuserve)
                self.assertEqual(len(lines), 2)
                self.assertGreater(subtotal, 0)
                self.assertGreater(shipping, 0)
                order = cis_store.checkout(compuserve)
                self.assertEqual(order["number"], "CIS-1001")
                self.assertEqual(order["status"], "RECEIVED")
                self.assertEqual(len(order["items"]), 2)
                self.assertEqual(cis_store.cart_summary(compuserve)[0], [])
                stored = compuserve.load_json("orders.json", default=[])
                self.assertEqual(stored[0]["event_key"], order["event_key"])
                state = cis_dynamic.load_state(compuserve)
                status_events = [event for event in state["events"] if event["type"] == "order_status"]
                statuses = [event["payload"]["status"] for event in status_events]
                self.assertIn(statuses[0], ("PROCESSING", "BACK ORDER"))
                self.assertEqual(statuses[1], "SHIPPED")
                self.assertTrue(any(event["type"] == "mail" for event in state["events"]))

    def test_global_find_discovers_store_catalog(self):
        results = cis_discovery.search(compuserve, "smartmodem")
        self.assertTrue(any(result.startswith("STORE #") for result in results))

    def test_specials_stock_and_compatibility_are_stable_for_simulated_day(self):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-20"}):
            first = [(item["sku"], item["sale_price"]) for item in cis_store.specials()]
            second = [(item["sku"], item["sale_price"]) for item in cis_store.specials()]
            self.assertEqual(first, second)
            self.assertEqual(len(first), 4)
            system, products = cis_store.compatible_products("Macintosh Plus")
            self.assertEqual(system, "MACINTOSH PLUS")
            self.assertIn(1203, [item["sku"] for item in products])
            trs_system, trs_products = cis_store.compatible_products("TRS-80")
            self.assertEqual(trs_system, "TRS-80 MODEL I/III")
            self.assertIn(1104, [item["sku"] for item in trs_products])
            details = cis_store.product_details(cis_store.find_product(1101))
            self.assertTrue(any("OWNER REPORT" in line for line in details))

    def test_fulfillment_change_sends_easyplex_notice(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0001"),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15", "CIS_SIMULATION_TIME": "12:00"}),
            ):
                cis_store.add_to_cart(compuserve, 1503)
                order = cis_store.checkout(compuserve)
                state = cis_dynamic.load_state(compuserve)
                for event in state["events"]:
                    if event["type"] == "order_status":
                        event["due_tick"] = 0
                        break
                cis_dynamic.save_state(compuserve, state)
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-16", "CIS_SIMULATION_TIME": "12:01"}),
            ):
                self.assertTrue(cis_dynamic.process_events(compuserve))
                mail = compuserve.load_json("easyplex.json", default=[])
                self.assertTrue(any(order["number"] in message["subject"] for message in mail))

    def test_delivered_order_creates_owned_equipment_once(self):
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0033"),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15", "CIS_SIMULATION_TIME": "12:00"}),
            ):
                cis_store.add_to_cart(compuserve, 1101, 2)
                order = cis_store.checkout(compuserve)
                state = cis_dynamic.load_state(compuserve)
                delivered = next(event for event in state["events"] if event["type"] == "order_status" and event["payload"]["status"] == "DELIVERED")
                delivered["due_tick"] = 0
                cis_dynamic.save_state(compuserve, state)
                cis_dynamic.process_events(compuserve)
                items = compuserve.cis_ownership.equipment(compuserve)
                compuserve.cis_ownership.receive_order(compuserve, order)
                item_count_after_repeat = len(compuserve.cis_ownership.equipment(compuserve))
            self.assertEqual(len(items), 2)
            self.assertEqual(item_count_after_repeat, 2)
            self.assertTrue(all(item["status"] == "DELIVERED - NOT INSTALLED" for item in items))

    def test_equipment_install_warranty_review_and_classified_lifecycle(self):
        order = {"number": "CIS-2001", "user_id": "70000,0032", "items": [{"sku": 1804, "name": "VGA Display Adapter", "quantity": 1}]}
        with tempfile.TemporaryDirectory() as directory:
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0032"),
                patch.object(compuserve, "forum_threads", {"ibmhw_tech": []}),
            ):
                asset = compuserve.cis_ownership.receive_order(compuserve, order)[0]
                self.assertIn("installed", compuserve.cis_ownership.install(compuserve, asset["id"], "IBM PC AT").lower())
                self.assertIn("opened", compuserve.cis_ownership.warranty(compuserve, asset["id"], "Display rolls in one game").lower())
                self.assertIn("recorded", compuserve.cis_ownership.review(compuserve, asset["id"], "Sharp text after switch adjustment").lower())
                self.assertIn("classified", compuserve.cis_ownership.sell(compuserve, asset["id"], "225").lower())
                state = cis_dynamic.load_state(compuserve)
                stored = state["owned_equipment"]["70000,0032"][0]
            self.assertTrue(stored["support_case"].startswith("W"))
            self.assertEqual(stored["review"], "Sharp text after switch adjustment")
            self.assertIn("LISTED AS CLASSIFIED", stored["status"])
            self.assertTrue(state["classifieds"])
            self.assertTrue(compuserve.forum_threads["ibmhw_tech"])

    def test_incompatible_equipment_install_requests_support(self):
        order = {"number": "CIS-2002", "user_id": "70000,0031", "items": [{"sku": 1804, "name": "VGA Display Adapter", "quantity": 1}]}
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(compuserve, "BASE_DIR", Path(directory)), patch.object(compuserve, "current_user_id", "70000,0031"):
                asset = compuserve.cis_ownership.receive_order(compuserve, order)[0]
                result = compuserve.cis_ownership.install(compuserve, asset["id"], "Macintosh Plus")
                stored = compuserve.cis_ownership.equipment(compuserve)[0]
            self.assertIn("not listed", result)
            self.assertEqual(stored["status"], "COMPATIBILITY HELP NEEDED")


class FeedTests(unittest.TestCase):
    def test_total_feed_failure_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            output = directory / "news.json"
            output.write_text('{"existing": true}', encoding="utf-8")
            with (
                patch.object(feed_utils, "BASE_DIR", directory),
                patch.object(feed_utils, "fetch_feed", side_effect=TimeoutError("timeout")),
            ):
                with self.assertRaises(RuntimeError):
                    feed_utils.build_news_file({"World": "https://example.invalid"}, "news.json")
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"existing": True})

    def test_feed_fields_are_bounded(self):
        entry = {"title": "x" * 30_000, "link": "https://example.com"}
        with patch.object(feed_utils, "fetch_feed", return_value=[entry]):
            data, failures = feed_utils.collect_news({"World": "https://example.com"})
        self.assertFalse(failures)
        self.assertEqual(len(data["World"][0]["title"]), feed_utils.MAX_FIELD_LENGTH)


class TimeCapsuleTests(unittest.TestCase):
    def test_parse_user_date_accepts_valid_entry(self):
        from datetime import date
        import cis_timecapsule
        self.assertEqual(cis_timecapsule.parse_user_date("11/09/1989"), date(1989, 11, 9))

    def test_parse_user_date_rejects_bad_form_and_range(self):
        import cis_timecapsule
        for bad in ("1989-11-09", "13/01/1990", "02/30/1990", "01/01/1970", "06/12/2026"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                cis_timecapsule.parse_user_date(bad)

    def test_surprise_date_is_deterministic_per_seed(self):
        import cis_timecapsule
        first = cis_timecapsule.surprise_date("70000,0001")
        second = cis_timecapsule.surprise_date("70000,0001")
        self.assertEqual(first, second)
        self.assertTrue(cis_timecapsule.in_range(first))

    def test_simulation_day_prefers_session_date(self):
        from datetime import date
        from cis_session import active_session, session_simulation_date
        state = SessionState()
        state.simulation_date = date(1989, 11, 9)
        with active_session(state):
            self.assertEqual(cis_dynamic.simulation_day(), date(1989, 11, 9))
            self.assertEqual(session_simulation_date(), date(1989, 11, 9))
            first = cis_dynamic.rng("period-news-0", "70000,0001").random()
            second = cis_dynamic.rng("period-news-0", "70000,0001").random()
            self.assertEqual(first, second)

    def test_simulation_day_falls_back_without_session_choice(self):
        from cis_session import active_session, session_simulation_date
        state = SessionState()
        with active_session(state):
            self.assertIsNone(session_simulation_date())
            # No session date: existing env/default behavior is preserved.
            self.assertEqual(cis_dynamic.simulation_day(), cis_dynamic.simulation_day())

    def test_no_active_session_means_no_session_date(self):
        from cis_session import session_simulation_date
        self.assertIsNone(session_simulation_date())


if __name__ == "__main__":
    unittest.main()
