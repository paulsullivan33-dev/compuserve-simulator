import json
import io
import os
import re
import types
import importlib.util
import subprocess
import sqlite3
from contextlib import closing, redirect_stdout
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import Mock, patch
from unittest import mock

import compuserve
import cis_hamnet
import cis_nightstation
import cis_sports
import cis_veterans
import cis_roots
import cis_guitar
import cis_tradingpost
import cis_entertainment
import cis_tech
import cis_weather
import cis_crossword
import cis_books
from cis_nightstation import MAX_MOVES, NightStationGame
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
import cis_yearend
import cis_cooking
import cis_aviation
import cis_scifi
import cis_giftguide
import cis_fitness
import cis_christmas
import cis_eliza
import cis_pets
import cis_trains
import cis_photo
from cis_giftguide import (GIFT_CATALOG, _parse_recipient, catalog_vs_mall_lines, cheapest_for, gift_picker, giftguide_menu, giftguide_menu_lines, giftguide_service, hottest_lines, pick_gifts, shortages_lines, trends_lines)
from cis_christmas import (ADVENT_TREATS, CHRISTMAS_ALBUMS, CHRISTMAS_CB_LINES, CHRISTMAS_CB_TOPICS, CHRISTMAS_SONGS, christmas_cb_lines, christmas_cb_topics, christmas_menu, christmas_menu_lines, christmas_music_lines, christmas_service, christmas_treat)
import cis_travel
import cis_experience
import cis_drafts
import cis_announcements
import cis_weather
import cis_timeline
import cis_features
import cis_timecapsule
from cis_timecapsule import pack_for
import cis_cb
import cis_adventure_league
import smoke_test
import fake2
import feed_utils
import telnet_app
from cis_terminal import wrap_terminal_text
from cis_session import SessionState, active_session


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
            self.assertEqual(len(issue['articles']), 13)
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
        for commands in (['GO NEWSSIM', '7', 'OFF'], ['GO MAGAZINE', 'OFF']):
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
            # Expectations derive from the pack itself so the pack can grow.
            pack_sections = {}
            for message in cis_communities.PACK['messages']:
                pack_sections.setdefault(message['section'], []).append(message)
            for forum in cis_communities.FORUMS.values():
                for section, _ in forum['sections'].values():
                    messages = forums[section]
                    expected = pack_sections[section]
                    self.assertEqual(len(messages), len(expected))
                    installed_ids = {m['content_id']: m['id'] for m in messages}
                    for message, source in zip(messages, expected):
                        self.assertEqual(message['content_id'], source['content_id'])
                        self.assertGreater(message['id'], 900000)
                        if source['parent'] is None:
                            self.assertIsNone(message['parent_id'])
                        else:
                            self.assertEqual(message['parent_id'],
                                             installed_ids[source['parent']])
                lib = forum['library']
                expected_files = [f for f in cis_communities.PACK['files']
                                  if f['library'] == lib]
                self.assertEqual(len(files[lib]), len(expected_files))
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
            self.assertEqual(sum(map(len, forums.values())),
                             len(cis_communities.PACK['messages']))

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

        lib_forums = [item for item in compuserve.FORUM_CHOICES.items()
                      if item[1] in cis_communities.LIBRARIES]
        for choice, forum_id in lib_forums[-4:]:
            with self.subTest(forum=forum_id), patch.object(compuserve, 'session_state', SessionState()), patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'forum_service') as service, patch.object(compuserve, 'show_logout_summary'), patch('builtins.input', side_effect=['GO FORUMSSIM', choice, 'OFF']):

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

    def test_poster_menus_fit_both_terminal_widths(self):
        from cis_terminal import menu_lines
        for screen in compuserve.screens.values():
            if not screen.get('poster'):
                continue
            for width in (40, 80):
                lines = menu_lines('CompuServe', screen['page'], screen['title'],
                                   screen['options'], width, poster=True)
                self.assertTrue(all(len(line) <= width for line in lines))
                self.assertTrue(lines[0].endswith(screen['page']))
                for number in screen['options']:
                    self.assertEqual(sum(line.startswith(f'{number:>2}  ') for line in lines), 1)
        mall = compuserve.screens['poster_shopping']
        lines = menu_lines('CompuServe', 'SHOPPING', mall['title'], mall['options'], 80, poster=True)
        self.assertIn("    CompuServe's Electronic", lines)

    def test_poster_navigation_dispatches_and_returns(self):
        with patch.object(compuserve, 'session_state', SessionState()), \
             patch.object(compuserve, 'show_screen') as show, \
             patch.object(compuserve, 'show_logout_summary'), \
             patch.object(compuserve, 'games_service') as games, \
             patch('builtins.input', side_effect=['GO POSTER', '8', '7', 'M', 'M', 'OFF']):
            compuserve.navigate()
        games.assert_called_once_with('3')
        self.assertEqual([call.args[0] for call in show.call_args_list],
                         ['main', 'poster_index', 'poster_games', 'poster_games', 'poster_index', 'main'])

    def test_main_menu_has_an_explicit_target_for_every_option(self):
        self.assertEqual(
            set(compuserve.screens["main"]["options"]),
            set(compuserve.OPTION_TARGETS["main"]),
        )

    def test_photo_help_and_index_routes(self):
        with patch.object(compuserve, 'session_state', SessionState()), \
             patch.object(compuserve, 'show_screen') as show, \
             patch.object(compuserve, 'show_logout_summary'), \
             patch.object(compuserve, 'customer_support') as support, \
             patch('builtins.input', side_effect=['1', '8', '1', '2', 'M', 'GO TOP', 'OFF']):
            compuserve.navigate()
        support.assert_called_once_with('2')
        visited = [call.args[0] for call in show.call_args_list]
        self.assertIn('poster_help', visited)
        self.assertIn('poster_tour', visited)
        self.assertIn('poster_topics', visited)
        self.assertEqual(visited[-1], 'main')

    def test_quick_search_opens_related_forum_for_wired_words(self):
        import cis_poster
        with patch.object(compuserve, 'clear'), patch.object(compuserve, 'header_bar'), \
             patch.object(compuserve, 'ansi_scroll'), patch.object(compuserve, 'text_page') as page, \
             patch.object(compuserve, 'forum_service') as forum, \
             patch('builtins.input', side_effect=['S cbmnet', '1', 'M']):
            cis_poster.directory(compuserve, ['main'])
        forum.assert_called_once_with('commodore')
        self.assertIn('Opening a related existing simulation:', page.call_args.args[2])
        with patch.object(compuserve, 'text_page') as page, \
             patch.object(compuserve, 'forum_service') as forum:
            self.assertTrue(compuserve.open_go_destination(compuserve.resolve_go_destination('ASHTON'), ['main']))
        forum.assert_called_once_with('dos')
        self.assertIn('Opening a related existing simulation:', page.call_args.args[2])

    def test_quick_directory_pagination_empty_search_and_recovery(self):
        import cis_poster
        with patch.object(compuserve, 'clear'), patch.object(compuserve, 'header_bar'), \
             patch.object(compuserve, 'ansi_scroll') as output, \
             patch('builtins.input', side_effect=['F', 'B', 'S qzznoentry', '1', 'ALL', 'M']):
            cis_poster.directory(compuserve, ['main'], group='software')
        rendered = [call.args[0] for call in output.call_args_list]
        self.assertTrue(any(line.startswith('Page 2/') for line in rendered))
        self.assertIn('No matching topics.', rendered)
        self.assertIn('Huh', rendered)
        self.assertGreater(sum(line.startswith('Page 1/') for line in rendered), 2)

    def test_go_can_leave_index_search_prompt(self):
        with patch.object(compuserve, 'session_state', SessionState()), \
             patch.object(compuserve, 'show_screen') as show, \
             patch.object(compuserve, 'show_logout_summary'), \
             patch('builtins.input', side_effect=['2', '1', 'GO COMMUNICATE', 'OFF']):
            compuserve.navigate()
        self.assertEqual(show.call_args.args[0], 'poster_communicate')

    def test_photo_top_prompt_is_exact(self):
        with patch.object(compuserve, 'session_state', SessionState()), \
             patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), \
             patch('builtins.input', side_effect=['OFF']) as read:
            compuserve.navigate()
        read.assert_called_once_with('Enter choice number ! ')

    def test_photo_mail_preserves_sparse_options_and_existing_actions(self):
        import cis_poster
        self.assertEqual(list(compuserve.screens['poster_mail']['options']), ['2', '3', '4', '5', '6'])
        with patch.object(compuserve, 'mail_service') as mail, patch.object(compuserve.cis_mail, 'address_book') as book:
            for choice in ('2', '5', '6'):
                cis_poster.select(compuserve, 'poster_mail', choice, ['main', 'poster_mail'])
        self.assertEqual([call.args[0] for call in mail.call_args_list], ['2', '4'])
        book.assert_called_once_with(compuserve)

    def test_photo_communications_and_feedback_navigation(self):
        with patch.object(compuserve, 'session_state', SessionState()), patch.object(compuserve, 'show_screen') as show, \
             patch.object(compuserve, 'show_logout_summary'), patch.object(compuserve, 'ansi_scroll'), \
             patch.object(compuserve, 'customer_support') as feedback, \
             patch('builtins.input', side_effect=['3', '3', '6', 'M', 'M', '5', 'M', '6', '', 'M', 'OFF']):
            compuserve.navigate()
        visited = [call.args[0] for call in show.call_args_list]
        for key in ('poster_forums', 'poster_hardware', 'poster_subscribers', 'poster_feedback'):
            self.assertIn(key, visited)
        feedback.assert_called_once_with('4')
        self.assertEqual(compuserve.resolve_go_destination('FORUMSSIM'), 'forums')

    def test_all_shopping_photo_menus_open_and_return(self):
        expected = ['poster_mall', 'poster_cus', 'poster_softex', 'poster_order', 'poster_ebb', 'poster_other_shop']
        commands = ['6'] + [value for i in range(1, 7) for value in (str(i), 'M')] + ['OFF']
        with patch.object(compuserve, 'session_state', SessionState()), \
             patch.object(compuserve, 'show_screen') as show, patch.object(compuserve, 'show_logout_summary'), \
             patch('builtins.input', side_effect=commands):
            compuserve.navigate()
        visited = [call.args[0] for call in show.call_args_list]
        self.assertEqual(visited[2::2], expected)
        self.assertEqual(visited[-1], 'poster_shopping')
        for word, key in zip(('MALL', 'CUS-1', 'SOFTEX', 'ORD-1', 'EBB-1', 'SHO-10'), expected):
            self.assertEqual(compuserve.resolve_go_destination(word), key)

    def test_nonmember_browsing_does_not_write_or_checkout(self):
        import cis_poster
        with patch('builtins.input', return_value='modem'), \
             patch.object(compuserve, 'text_page') as page, patch.object(compuserve, 'save_json_atomic') as save, \
             patch.object(compuserve.cis_store, 'checkout') as checkout, \
             patch.object(compuserve.cis_store, 'add_to_cart') as add:
            cis_poster.select(compuserve, 'poster_cus', '2', ['main', 'poster_cus'])
        self.assertIn('BROWSING ONLY', page.call_args.args[1])
        self.assertTrue(any('modem' in line.lower() for line in page.call_args.args[2][1:]))
        save.assert_not_called()
        checkout.assert_not_called()
        add.assert_not_called()

    def test_poster_order_status_filters_member_and_guest(self):
        import cis_poster
        orders = [{'user_id': 'A', 'number': 'A-1', 'status': 'SHIPPED', 'name': 'MY ORDER'},
                  {'user_id': 'B', 'number': 'B-1', 'name': 'OTHER ORDER'}, {'name': 'OWNERLESS'}]
        for member in ('A', None):
            with patch.object(compuserve, 'current_user_id', member), \
                 patch.object(compuserve, 'load_json', return_value=orders), \
                 patch.object(compuserve, 'text_page') as page:
                cis_poster.select(compuserve, 'poster_order', '3', ['main', 'poster_order'])
            text = '\n'.join(page.call_args.args[2])
            self.assertNotIn('OTHER ORDER', text)
            self.assertNotIn('OWNERLESS', text)
            self.assertEqual('MY ORDER' in text, member == 'A')

    def test_photographed_forum_paging_returns_to_computers(self):
        for option, expected in (
            ('1', ['poster_software', 'poster_software_more']),
            ('2', ['poster_hardware', 'poster_hardware_more', 'poster_hardware_last']),
            ('4', ['poster_science', 'poster_science_more']),
        ):
            commands = ['11', option] + [''] * (len(expected) - 1) + ['B', 'F', 'M', 'OFF']
            with self.subTest(option=option), patch.object(compuserve, 'session_state', SessionState()), \
                 patch.object(compuserve, 'show_screen') as show, patch.object(compuserve, 'show_logout_summary'), \
                 patch('builtins.input', side_effect=commands):
                compuserve.navigate()
            visited = [call.args[0] for call in show.call_args_list]
            self.assertEqual(visited[2:2 + len(expected)], expected)
            self.assertEqual(visited[-3:], [expected[-2], expected[-1], 'poster_computers'])

    def test_new_photo_numbers_and_relative_addresses(self):
        self.assertEqual(list(compuserve.screens['poster_software_more']['options']), list(map(str, range(11, 17))))
        self.assertEqual(list(compuserve.screens['poster_hardware_last']['options']), list(map(str, range(15, 21))))
        self.assertNotIn('10', compuserve.screens['poster_science']['options'])
        self.assertEqual(list(compuserve.screens['poster_science_more']['options']), ['11', '12', '13', '14'])
        self.assertEqual(compuserve.resolve_go_destination('4', 'poster_software'), 'poster_software_more')
        self.assertEqual(compuserve.resolve_go_destination('8', 'poster_hardware'), 'poster_hardware_last')
        self.assertEqual(compuserve.resolve_go_destination('MAGAZINES'), 'poster_magazines')

    def test_hardware_continuation_opens_related_ibm_forum(self):
        with patch.object(compuserve, 'session_state', SessionState()), \
             patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), \
             patch.object(compuserve, 'text_page') as notice, patch.object(compuserve, 'forum_service') as forum, \
             patch('builtins.input', side_effect=['11', '2', '', '9', 'M', 'OFF']):
            compuserve.navigate()
        forum.assert_called_once_with('ibmhw')
        self.assertIn('Opening a related reconstructed simulation:', notice.call_args.args[2])

    def test_air_hotel_and_aae_photo_rendering_and_addresses(self):
        for width in (40, 80):
            for key in ('poster_air', 'poster_hotel', 'poster_aae', 'poster_gpo'):
                with patch.object(compuserve, 'SCREEN_WIDTH', width), patch.object(compuserve, 'clear'), patch.object(compuserve, 'ansi_scroll') as output:
                    compuserve.show_screen(key)
                lines = [call.args[0] for call in output.call_args_list]
                self.assertTrue(all(len(line) <= width for line in lines))
                if key == 'poster_air':
                    self.assertTrue(lines[0].startswith('TRAVELSHOPPER'))
                if key == 'poster_hotel':
                    self.assertIn('ADVANCE', lines)
                if key == 'poster_aae':
                    self.assertIn('Copyright @ 1986', [line.strip() for line in lines])
                    self.assertIn('* over 9 million words', lines)
        self.assertEqual(compuserve.resolve_go_destination('5', 'poster_air'), 'poster_hotel')
        self.assertEqual(compuserve.resolve_go_destination('AAE-1'), 'poster_aae')
        self.assertEqual(compuserve.resolve_go_destination('GPO-1'), 'poster_gpo')

    def test_go_can_leave_encyclopedia_welcome_without_opening_service(self):
        with patch.object(compuserve, 'session_state', SessionState()), \
             patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), \
             patch.object(compuserve, 'reference_service') as reference, \
             patch('builtins.input', side_effect=['GO AAE-1', 'GO TOP', 'OFF']) as read:
            compuserve.navigate()
        reference.assert_not_called()
        self.assertIn('Press <CR> for more ! ', [call.args[0] for call in read.call_args_list])

    def test_travel_photo_navigation_and_sparse_news_options(self):
        with patch.object(compuserve, 'session_state', SessionState()), \
             patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), \
             patch.object(compuserve, 'travel_service') as travel, \
             patch.object(compuserve, 'customer_support') as support, \
             patch('builtins.input', side_effect=['5', '2', '1', 'M', '3', '1', 'M', '4', '1', '5', '7', 'M', 'M', 'OFF']):
            compuserve.navigate()
        self.assertEqual([call.args[0] for call in travel.call_args_list], ['1', '2', '6', '4'])
        support.assert_called_once_with('4')
        self.assertEqual(set(compuserve.screens['poster_travel_news']['options']), {'5', '7'})

    def test_reference_photo_heading_and_encyclopedia_route(self):
        with patch.object(compuserve, 'clear'), patch.object(compuserve, 'ansi_scroll') as output:
            compuserve.show_screen('poster_reference')
        lines = [call.args[0] for call in output.call_args_list]
        heading = lines.index('EDUCATION')
        self.assertTrue(lines[heading - 2].startswith(' 5  Microsearch'))
        self.assertTrue(lines[heading + 1].startswith(' 6  Services for Educators'))
        with patch.object(compuserve, 'session_state', SessionState()), \
             patch.object(compuserve, 'show_screen'), patch.object(compuserve, 'show_logout_summary'), \
             patch.object(compuserve, 'reference_service') as reference, \
             patch('builtins.input', side_effect=['10', '1', '', 'M', 'M', 'OFF']):
            compuserve.navigate()
        reference.assert_called_once_with('1')
        self.assertEqual(compuserve.resolve_go_destination('TRAVEL'), 'poster_travel')
        self.assertEqual(compuserve.resolve_go_destination('REFERENCE'), 'poster_reference')
        self.assertEqual(compuserve.resolve_go_destination('TRAVELSIM'), 'travel')
        self.assertEqual(compuserve.resolve_go_destination('REFERENCESIM'), 'reference')

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

    def test_poster_top_has_no_added_return_menu_row(self):
        with (
            patch.object(compuserve, "ansi_scroll") as scroll,
            patch.object(compuserve, "clear"),
        ):
            compuserve.show_screen("main")
        rendered = [call.args[0] for call in scroll.call_args_list]
        self.assertEqual(
            sum("Return to previous menu" in text for text in rendered), 0
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
        screen = compuserve.screens["main"]
        lines = compuserve.menu_lines(
            "CompuServe",
            "TOP",
            screen["title"],
            screen["options"],
            80,
            poster=screen.get("poster", False),
        )
        lines[0] = "CompuServe|TOP"
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
        old_pending = compuserve.pending_simulation_date
        try:
            with tempfile.TemporaryDirectory() as directory:
                with (
                    patch.object(compuserve, "BASE_DIR", Path(directory)),
                    patch(
                        "builtins.input",
                        side_effect=["C", "2400", "40", "screen", "Y", "clean", "N", "N", "N", "N", "1"],
                    ),
                    patch.object(compuserve, "ansi_scroll"),
                    patch.object(compuserve, "clear"),
                    patch.object(compuserve, "header_bar"),
                ):
                    compuserve.startup_configuration()
            self.assertEqual(compuserve.connection_baud, 2400)
            self.assertEqual(compuserve.SCREEN_WIDTH, 40)
            self.assertTrue(compuserve.startup_options["skip_dialing"])
            # The temporal menu now runs in connection setup; "1" = Present Day.
            self.assertIsNone(compuserve.pending_simulation_date)
        finally:
            compuserve.connection_baud = old_baud
            compuserve.SCREEN_WIDTH = old_width
            compuserve.startup_options.clear()
            compuserve.startup_options.update(old_options)
            compuserve.pending_simulation_date = old_pending

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
                # Windows Python needs SystemRoot for OS initialization.
                env={**os.environ, "PYTHONPATH": str(compuserve.BASE_DIR)},
                capture_output=True,
                text=True,
                timeout=10,
            )
        self.assertEqual(result.returncode, 0, result.stderr)


class ContentPack8Tests(unittest.TestCase):
    """Pack 8: poster quick words all wired; DOS Applications Desk content."""

    def test_all_poster_words_have_targets(self):
        words = json.loads((REPO_ROOT / "poster_words.json").read_text(encoding="utf-8"))
        untargeted = [w["word"] for w in words if not w.get("target")]
        self.assertEqual(untargeted, [])

    def test_quick_word_targets_are_openable_destinations(self):
        words = json.loads((REPO_ROOT / "poster_words.json").read_text(encoding="utf-8"))
        for word in words:
            target = word["target"]
            self.assertTrue(
                target in compuserve.FORUM_CATALOG or target == "magazine",
                f"GO {word['word']} -> {target}",
            )

    def test_every_quick_screen_target_resolves_to_a_wired_word(self):
        words = {
            w["word"]: w.get("target")
            for w in json.loads((REPO_ROOT / "poster_words.json").read_text(encoding="utf-8"))
        }
        for key, screen in compuserve.screens.items():
            if not screen.get("poster"):
                continue
            for choice, target in screen.get("targets", {}).items():
                if target.startswith("quick:"):
                    self.assertIn(target[6:], words, f"{key}[{choice}]")
                    self.assertTrue(words[target[6:]], f"{key}[{choice}] -> {target}")

    def test_open_word_routes_to_target_forum(self):
        import cis_poster
        with patch.object(compuserve, "text_page") as page, \
             patch.object(compuserve, "forum_service") as forum:
            self.assertTrue(cis_poster.open_word(compuserve, "BORLAND", ["main"]))
        forum.assert_called_once_with("dos")
        self.assertIn("Opening a related existing simulation:", page.call_args.args[2])

    def test_no_poster_choice_or_word_reports_unimplemented(self):
        import cis_poster
        for key, screen in compuserve.screens.items():
            if not screen.get("poster"):
                continue
            for choice in screen.get("options", {}):
                self.assertNotEqual(
                    cis_poster.selection_status(compuserve, key, choice),
                    "unimplemented", f"{key}[{choice}]",
                )
        for record in cis_poster.records(compuserve):
            if record["word"]:
                self.assertNotIn("unimplemented", record["status"], record["word"])

    def test_pack_id_bumped_to_v5(self):
        self.assertEqual(cis_communities.PACK["id"], "computer-communities-1988-v5")

    def test_dos_forum_has_applications_desk_section(self):
        self.assertEqual(
            cis_communities.FORUMS["dos"]["sections"]["4"],
            ["dos_apps", "Applications Desk"],
        )

    def test_pack8_messages_wellformed(self):
        new = [m for m in cis_communities.PACK["messages"]
               if m["content_id"].startswith("community:37:")]
        self.assertGreater(len(new), 10)
        valid_sections = set()
        for forum in compuserve.FORUM_CATALOG.values():
            for _, (sec_id, _) in forum["sections"].items():
                valid_sections.add(sec_id)
        for message in new:
            self.assertIn(message["section"], valid_sections, message["content_id"])
            month, day, year = message["date"].split("/")
            self.assertEqual((month, year), ("12", "88"), message["content_id"])
            self.assertTrue(1 <= int(day) <= 31, message["content_id"])
            text = (message["subject"] + "\n" + message["body"]).lower()
            for bad in ("windows 95", "windows 98", "pentium", "usb",
                        "wi-fi", "wifi", "linux", "world wide web"):
                self.assertNotIn(bad, text, message["content_id"])

    def test_pack8_files_install_into_dos_library(self):
        with tempfile.TemporaryDirectory() as directory:
            base_dir = Path(directory)
            self.assertTrue(cis_communities.install(base_dir))
            files = cis_storage.load_json(base_dir, "library_files.json")
            names = {f["name"] for f in files["dos_library"]}
            for expected in ("DBASE-TIPS.TXT", "LOTUS123.TXT", "TURBOC.TXT", "ACAD-KEYS.TXT"):
                self.assertIn(expected, names)
            forums = cis_storage.load_json(base_dir, "forums.json")
            self.assertGreater(len(forums["dos_apps"]), 0)


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
            with (
                patch.object(compuserve, "BASE_DIR", Path(directory)),
                patch.object(compuserve, "current_user_id", "70000,0001"),
                patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-23"}),
            ):
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
        self.assertGreaterEqual(len(cis_store.CATALOG), 62)
        self.assertEqual(len({p['sku'] for p in cis_store.CATALOG}), len(cis_store.CATALOG))
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


class TimeCapsulePackTests(unittest.TestCase):
    def test_packs_are_loaded_for_every_featured_date(self):
        import cis_timecapsule
        self.assertEqual(cis_timecapsule.CONTENT_PACK_STATUS, "loaded")
        for when, _label in cis_timecapsule.FEATURED_DATES:
            with self.subTest(date=when.isoformat()):
                pack = cis_timecapsule.pack_for(when)
                self.assertIsNotNone(pack)
                self.assertEqual(pack["date"], when.isoformat())

    def test_pack_sections_meet_required_counts(self):
        import cis_timecapsule
        for when, _label in cis_timecapsule.FEATURED_DATES:
            pack = cis_timecapsule.pack_for(when)
            with self.subTest(date=when.isoformat()):
                self.assertTrue(8 <= len(pack["headlines"]) <= 12)
                self.assertTrue(2 <= len(pack["announcements"]) <= 4)
                self.assertTrue(4 <= len(pack["cb_topics"]) <= 6)
                self.assertTrue(0 <= len(pack["market_notes"]) <= 4)
                self.assertTrue(2 <= len(pack["on_this_day"]) <= 3)

    def test_pack_headlines_have_news_article_shape(self):
        import cis_timecapsule
        required = {"id", "category", "title", "summary", "published", "source"}
        for when, _label in cis_timecapsule.FEATURED_DATES:
            pack = cis_timecapsule.pack_for(when)
            for story in pack["headlines"]:
                with self.subTest(date=when.isoformat(), story=story.get("id")):
                    self.assertTrue(required.issubset(story))
                    for field in required:
                        self.assertTrue(story[field], f"empty {field}")

    def test_pack_for_returns_none_without_a_pack(self):
        import cis_timecapsule
        from datetime import date
        self.assertIsNone(cis_timecapsule.pack_for(None))
        self.assertIsNone(cis_timecapsule.pack_for(date(1985, 6, 15)))

    def test_pack_headlines_returns_copies(self):
        import cis_timecapsule
        from datetime import date
        pack = cis_timecapsule.pack_for(date(1981, 8, 12))
        stories = cis_timecapsule.pack_headlines(pack)
        self.assertEqual(len(stories), len(pack["headlines"]))
        self.assertIsNot(stories[0], pack["headlines"][0])
        self.assertEqual(stories[0]["title"], "IBM ENTERS PERSONAL COMPUTER MARKET")

    def test_cb_conversation_uses_pack_topics_and_given_handles(self):
        import random
        import cis_timecapsule
        from datetime import date
        pack = cis_timecapsule.pack_for(date(1986, 1, 28))
        handles = ["Alpha", "Beta", "Gamma"]
        lines = cis_timecapsule.cb_conversation(pack, random.Random(7), handles)
        self.assertEqual(len(lines), 2)
        for sender, line in lines:
            self.assertIn(sender, handles)
            self.assertIn(line, pack["cb_topics"])
        self.assertNotEqual(lines[0][0], lines[1][0])

    def test_cb_conversation_empty_without_topics_or_handles(self):
        import random
        import cis_timecapsule
        self.assertEqual(cis_timecapsule.cb_conversation({}, random.Random(1), ["A"]), [])
        self.assertEqual(cis_timecapsule.cb_conversation({"cb_topics": ["hi"]}, random.Random(1), []), [])

    def test_cb_ambient_is_deterministic_on_featured_date(self):
        from datetime import date
        from cis_session import active_session
        state = SessionState()
        state.simulation_date = date(1987, 10, 19)
        with active_session(state):
            first = cis_dynamic.cb_ambient_events("1", "bucket", hour=20)
            second = cis_dynamic.cb_ambient_events("1", "bucket", hour=20)
            self.assertEqual(first, second)


class ConnectionSetupTimeCapsuleTests(unittest.TestCase):
    """The temporal destination menu lives in connection setup, not post-login."""

    def setUp(self):
        self._old_pending = compuserve.pending_simulation_date
        compuserve.pending_simulation_date = None

    def tearDown(self):
        compuserve.pending_simulation_date = self._old_pending

    def test_post_login_menu_is_gone(self):
        self.assertFalse(hasattr(compuserve, "choose_temporal_destination"))

    def test_temporal_menu_in_connection_setup_stores_featured_date(self):
        from datetime import date
        with (
            patch("builtins.input", side_effect=["", "2", "8"]),
            patch.object(compuserve, "ansi_scroll"),
            patch.object(compuserve, "clear"),
            patch.object(compuserve, "header_bar"),
        ):
            compuserve.startup_configuration()
        self.assertEqual(compuserve.pending_simulation_date, date(1987, 12, 8))

    def test_temporal_menu_in_connection_setup_accepts_typed_date(self):
        from datetime import date
        with (
            patch("builtins.input", side_effect=["", "3", "06/12/1985"]),
            patch.object(compuserve, "ansi_scroll"),
            patch.object(compuserve, "clear"),
            patch.object(compuserve, "header_bar"),
        ):
            compuserve.startup_configuration()
        self.assertEqual(compuserve.pending_simulation_date, date(1985, 6, 12))

    def test_apply_phase_sets_session_date_and_persists_profile(self):
        from datetime import date
        from cis_session import active_session
        import cis_timecapsule
        state = SessionState()
        profile = {}
        compuserve.pending_simulation_date = date(1987, 10, 19)
        with (
            patch.object(compuserve, "session_state", state),
            patch.object(compuserve, "current_profile", profile),
            patch.object(compuserve, "current_user_id", "70000,0001"),
            patch.object(compuserve, "save_profiles"),
            patch.object(compuserve, "ansi_scroll"),
        ):
            compuserve.apply_pending_simulation_date()
        self.assertEqual(state.simulation_date, date(1987, 10, 19))
        self.assertEqual(profile["last_simulation_date"], "1987-10-19")
        self.assertIsNone(compuserve.pending_simulation_date)
        # The chosen date reaches the session exactly as the briefing sees it.
        with active_session(state):
            self.assertEqual(cis_dynamic.simulation_day(), date(1987, 10, 19))
            self.assertIsNotNone(cis_timecapsule.pack_for(date(1987, 10, 19)))

    def test_apply_phase_offers_remembered_era_shortcut(self):
        from datetime import date
        state = SessionState()
        profile = {"last_simulation_date": "1989-11-09"}
        compuserve.pending_simulation_date = None  # "Present Day" at setup
        with (
            patch.object(compuserve, "session_state", state),
            patch.object(compuserve, "current_profile", profile),
            patch.object(compuserve, "current_user_id", "70000,0001"),
            patch.object(compuserve, "save_profiles"),
            patch.object(compuserve, "ansi_scroll"),
            patch("builtins.input", side_effect=["Y"]),
        ):
            compuserve.apply_pending_simulation_date()
        self.assertEqual(state.simulation_date, date(1989, 11, 9))

    def test_apply_phase_present_day_clears_remembered_era_on_no(self):
        state = SessionState()
        profile = {"last_simulation_date": "1989-11-09"}
        compuserve.pending_simulation_date = None
        with (
            patch.object(compuserve, "session_state", state),
            patch.object(compuserve, "current_profile", profile),
            patch.object(compuserve, "current_user_id", "70000,0001"),
            patch.object(compuserve, "save_profiles"),
            patch.object(compuserve, "ansi_scroll"),
            patch("builtins.input", side_effect=["N"]),
        ):
            compuserve.apply_pending_simulation_date()
        self.assertIsNone(state.simulation_date)
        self.assertNotIn("last_simulation_date", profile)

    def test_apply_phase_surprise_resolves_per_user(self):
        from cis_session import active_session
        import cis_timecapsule
        state = SessionState()
        compuserve.pending_simulation_date = compuserve._SURPRISE_SENTINEL
        with (
            patch.object(compuserve, "session_state", state),
            patch.object(compuserve, "current_profile", {}),
            patch.object(compuserve, "current_user_id", "70000,0001"),
            patch.object(compuserve, "save_profiles"),
            patch.object(compuserve, "ansi_scroll"),
        ):
            compuserve.apply_pending_simulation_date()
        expected = cis_timecapsule.surprise_date("70000,0001")
        self.assertEqual(state.simulation_date, expected)
        with active_session(state):
            self.assertEqual(cis_dynamic.simulation_day(), expected)


if __name__ == "__main__":
    unittest.main()


# --- Feature 1: ham radio forum (cis_hamnet) ---
REPO_ROOT = Path(__file__).resolve().parent
JSON_PATH = REPO_ROOT / "computer_communities.json"

REQUIRED_FIELDS = {"content_id", "section", "date", "author", "subject", "body", "parent"}

# Anything that did not exist by December 1988 is banned from module content.
ANACHRONISMS = [
    "no-code", "no code", "FT-1000", "IC-706", "FT-817", "FT-897",
    "PSK31", "APRS", "D-STAR", "FT8", "DSTAR", "DMR ", "internet",
    "website", "web site", "WWW", "1991", "1992", "1995", "Windows 95",
    "cell phone", "smartphone", "EchoLink", "Winlink",
]


class TestSections(unittest.TestCase):
    def test_sections_shape(self):
        secs = cis_hamnet.SECTIONS
        self.assertIsInstance(secs, dict)
        self.assertEqual(set(secs.keys()), {"1", "2", "3", "4", "5", "6", "7", "8"})
        ids = []
        for key, spec in secs.items():
            self.assertIsInstance(spec, (tuple, list), f"section {key}")
            self.assertEqual(len(spec), 2, f"section {key}")
            sec_id, title = spec
            self.assertTrue(sec_id.startswith("hamnet_"), sec_id)
            self.assertTrue(title.strip(), sec_id)
            ids.append(sec_id)
        self.assertEqual(len(set(ids)), len(ids), "section ids must be unique")

    def test_section_spec_helper(self):
        spec = cis_hamnet.section_spec()
        self.assertEqual(spec, cis_hamnet.SECTIONS)


class TestSeedPosts(unittest.TestCase):
    def test_count(self):
        posts = cis_hamnet.SEED_POSTS
        self.assertGreaterEqual(len(posts), 12)
        self.assertLessEqual(len(posts), 18)

    def test_required_fields(self):
        for post in cis_hamnet.SEED_POSTS:
            self.assertEqual(set(post.keys()), REQUIRED_FIELDS,
                             f"field mismatch in {post.get('content_id')}")
            for field in ("content_id", "section", "date", "author", "subject", "body"):
                self.assertTrue(str(post[field]).strip(), f"{field} empty in {post['content_id']}")
            self.assertIsNone(post["parent"], f"parent must be null in {post['content_id']}")

    def test_unique_content_ids(self):
        ids = [p["content_id"] for p in cis_hamnet.SEED_POSTS]
        self.assertEqual(len(set(ids)), len(ids))
        for cid in ids:
            self.assertRegex(cid, r"^hamnet-1988-\d{3}$", cid)

    def test_sections_valid(self):
        valid = {sec_id for sec_id, _ in cis_hamnet.SECTIONS.values()} | {"hamnet_general"}
        for post in cis_hamnet.SEED_POSTS:
            self.assertIn(post["section"], valid, post["content_id"])

    def test_dates_december_1988(self):
        for post in cis_hamnet.SEED_POSTS:
            month, day, year = post["date"].split("/")
            self.assertEqual((month, year), ("12", "88"), post["content_id"])
            self.assertTrue(1 <= int(day) <= 31, post["content_id"])

    def test_no_anachronisms(self):
        for post in cis_hamnet.SEED_POSTS:
            text = (post["subject"] + "\n" + post["body"]).lower()
            for bad in ANACHRONISMS:
                self.assertNotIn(bad.lower(), text,
                                 f"anachronism {bad!r} in {post['content_id']}")

    def test_nets_announced_in_forum(self):
        blob = " ".join(p["subject"] + " " + p["body"] for p in cis_hamnet.SEED_POSTS).lower()
        for net in cis_hamnet.NETS:
            # Match on the name minus any leading location qualifier,
            # e.g. "DFW Packet BBS Net" matches "Weekly Packet BBS Net".
            key = net["name"].split(" ", 1)[-1].lower()
            self.assertIn(key, blob, f"net {net['name']} not announced in seed posts")


class TestBulletinsAndNets(unittest.TestCase):
    def test_bulletins(self):
        bulls = cis_hamnet.ARRL_BULLETINS
        self.assertGreaterEqual(len(bulls), 3)
        self.assertLessEqual(len(bulls), 4)
        for b in bulls:
            for field in ("number", "title", "date", "body"):
                self.assertTrue(str(b[field]).strip(), f"bulletin {field} empty")
            text = (b["title"] + "\n" + b["body"]).lower()
            for bad in ANACHRONISMS:
                self.assertNotIn(bad.lower(), text, f"anachronism {bad!r} in {b['number']}")

    def test_nets_shape(self):
        self.assertGreaterEqual(len(cis_hamnet.NETS), 1)
        for net in cis_hamnet.NETS:
            for field in ("name", "weekday", "time", "where", "net_control", "description"):
                self.assertTrue(str(net[field]).strip() or net[field] == 0, f"net {field} empty")
            self.assertIn(net["weekday"], range(7))
            text = (net["name"] + net["where"] + net["description"]).lower()
            for bad in ANACHRONISMS:
                self.assertNotIn(bad.lower(), text, f"anachronism {bad!r} in {net['name']}")

    def test_upcoming_net(self):
        # Tuesday 1988-12-13: next net should be Wednesday's Ham Net, in 1 day.
        s = cis_hamnet.upcoming_net(date(1988, 12, 13))
        self.assertIsInstance(s, str)
        self.assertIn("Next net", s)
        self.assertIn("CompuServe Ham Net", s)
        self.assertIn("Wednesday", s)
        self.assertIn("8:00 PM Central", s)
        # Saturday 1988-12-10: the packet net is tonight.
        s2 = cis_hamnet.upcoming_net(date(1988, 12, 10))
        self.assertIn("DFW Packet BBS Net", s2)
        self.assertIn("tonight", s2)
        # Default path (simulation day) returns a sane string.
        os.environ.pop("CIS_SIMULATION_DATE", None)
        s3 = cis_hamnet.upcoming_net()
        self.assertIn("Next net", s3)
        self.assertIn("Net control", s3)


class TestJsonMerge(unittest.TestCase):
    def test_json_parses(self):
        pack = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        self.assertIn("messages", pack)

    def test_merge_forums_accepts_hamnet_messages(self):
        data = {}
        result = cis_communities.merge_forums(data)
        hamnet_msgs = [m for m in cis_communities.PACK["messages"]
                       if m["content_id"].startswith("hamnet-1988-")]
        self.assertEqual(len(hamnet_msgs), len(cis_hamnet.SEED_POSTS))
        merged = [m for msgs in result.values() for m in msgs
                  if m.get("content_id", "").startswith("hamnet-1988-")]
        self.assertEqual(len(merged), len(hamnet_msgs))
        by_cid = {m["content_id"]: m for m in merged}
        for post in cis_hamnet.SEED_POSTS:
            self.assertIn(post["content_id"], by_cid)
            rec = by_cid[post["content_id"]]
            self.assertEqual(rec["author"], post["author"])
            self.assertEqual(rec["subject"], post["subject"])
            self.assertEqual(rec["body"], post["body"])
            self.assertIsNone(rec["parent_id"])
            self.assertEqual(rec["author_user_id"], "SIMULATED")
        # Idempotent: merging again must not duplicate.
        before = sum(len(v) for v in result.values())
        cis_communities.merge_forums(result)
        after = sum(len(v) for v in result.values())
        self.assertEqual(before, after)


# --- Feature 2: new time-capsule dates ---
NEW_DATES = [
    (date(1985, 7, 13), "Live Aid"),
    (date(1986, 4, 26), "Chernobyl"),
    (date(1989, 3, 24), "Exxon Valdez"),
    (date(1991, 1, 17), "Desert Storm begins"),
]


class NewFeaturedDatesTests(unittest.TestCase):
    def test_fourteen_featured_dates_in_chronological_order(self):
        featured = cis_timecapsule.FEATURED_DATES
        self.assertEqual(len(featured), 14)
        dates = [when for when, _ in featured]
        self.assertEqual(dates, sorted(dates))
        for when, label in NEW_DATES:
            self.assertIn((when, label), featured)

    def test_every_featured_date_has_valid_pack(self):
        # cis_timecapsule validates every pack at import; reaching this line
        # means the validator accepted all 14. Double-check coverage anyway.
        for when, _label in cis_timecapsule.FEATURED_DATES:
            pack = cis_timecapsule.pack_for(when)
            self.assertIsNotNone(pack, f"no pack for {when}")
            self.assertEqual(pack["date"], when.isoformat())

    def test_pack_for_resolves_each_new_date(self):
        for when, label in NEW_DATES:
            with self.subTest(date=when.isoformat()):
                pack = cis_timecapsule.pack_for(when)
                self.assertIsNotNone(pack)
                self.assertEqual(pack["label"], label)
                self.assertEqual(pack["date"], when.isoformat())
                # ISO-string lookup works too
                self.assertIs(cis_timecapsule.pack_for(when.isoformat()), pack)

    def test_new_packs_meet_section_count_rules(self):
        for when, _label in NEW_DATES:
            pack = cis_timecapsule.pack_for(when)
            with self.subTest(date=when.isoformat()):
                self.assertTrue(8 <= len(pack["headlines"]) <= 12)
                self.assertTrue(2 <= len(pack["announcements"]) <= 4)
                self.assertTrue(4 <= len(pack["cb_topics"]) <= 6)
                self.assertTrue(0 <= len(pack["market_notes"]) <= 4)
                self.assertTrue(2 <= len(pack["on_this_day"]) <= 3)

    def test_new_pack_headlines_have_full_shape(self):
        required = {"id", "category", "title", "summary", "published", "source"}
        seen_ids = set()
        for when, _label in NEW_DATES:
            pack = cis_timecapsule.pack_for(when)
            for story in pack["headlines"]:
                with self.subTest(date=when.isoformat(), story=story.get("id")):
                    self.assertTrue(required.issubset(story))
                    for field in required:
                        self.assertTrue(story[field], f"empty {field}")
                    self.assertNotIn(story["id"], seen_ids, "duplicate story id")
                    seen_ids.add(story["id"])

    def test_on_this_day_items_predate_pack_date(self):
        year_re = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")
        for when, _label in NEW_DATES:
            pack = cis_timecapsule.pack_for(when)
            for item in pack["on_this_day"]:
                with self.subTest(date=when.isoformat(), item=item["title"]):
                    for year in year_re.findall(item["title"] + " " + item["summary"]):
                        self.assertLessEqual(int(year), when.year)


class FeaturedDateMenuTests(unittest.TestCase):
    def _run_menu(self, inputs):
        import compuserve
        with patch.object(compuserve, "clear"), \
             patch.object(compuserve, "header_bar"), \
             patch.object(compuserve, "ansi_scroll") as scroll, \
             patch("builtins.input", side_effect=inputs):
            result = compuserve._featured_date_menu()
        lines = [str(call.args[0]) for call in scroll.call_args_list]
        return result, lines

    def test_menu_renders_fourteen_items_and_parses_fourteen(self):
        result, lines = self._run_menu(["14"])
        numbered = [ln for ln in lines if re.match(r"^\d+  \d\d/\d\d/\d\d\d\d  ", ln)]
        self.assertEqual(len(numbered), 14)
        self.assertTrue(numbered[0].startswith("1  04/12/1981"))
        self.assertTrue(numbered[13].startswith("14  08/06/1991"))
        self.assertIn("Live Aid", "".join(lines))
        self.assertEqual(result, date(1991, 8, 6))

    def test_menu_rejects_out_of_range_choices(self):
        for bad in ("15", "0"):
            result, lines = self._run_menu([bad, "M"])
            self.assertIsNone(result, f"menu accepted {bad!r}")
            self.assertTrue(
                any("Enter a number from the list" in ln for ln in lines),
                f"no rejection message for {bad!r}",
            )


class AnachronismScanTests(unittest.TestCase):
    def _all_text(self, pack):
        bits = list(pack["announcements"]) + list(pack["cb_topics"]) + list(pack["market_notes"])
        bits += [item["title"] + " " + item["summary"] for item in pack["on_this_day"]]
        for story in pack["headlines"]:
            bits.append(" ".join(str(story[f]) for f in ("id", "category", "title", "summary", "published", "source")))
        return "\n".join(bits)

    def test_no_internet_as_commonplace_before_1991(self):
        for when, _label in NEW_DATES:
            if when.year >= 1991:
                continue
            text = self._all_text(cis_timecapsule.pack_for(when))
            with self.subTest(date=when.isoformat()):
                self.assertNotIn("internet", text.lower())
                self.assertNotIn("website", text.lower())
                self.assertNotIn("e-mail", text.lower())

    def test_no_years_after_pack_date(self):
        year_re = re.compile(r"\b(19\d\d|20\d\d)\b")
        for when, _label in NEW_DATES:
            text = self._all_text(cis_timecapsule.pack_for(when))
            with self.subTest(date=when.isoformat()):
                for year in year_re.findall(text):
                    self.assertLessEqual(
                        int(year), when.year,
                        f"post-date year {year} in {when.isoformat()} pack",
                    )


# --- Feature 3: Night Shift Earth Station adventure ---
class FakeApp:
    """Minimal stand-in for the compuserve module: JSON files in a temp dir."""

    def __init__(self, tmpdir, user_id="TESTER"):
        self.tmpdir = Path(tmpdir)
        self.current_user_id = user_id
        self.cis_dynamic = cis_dynamic
        self.output_lines = []

    def ansi_scroll(self, text, delay=0.01):
        self.output_lines.append(str(text))
        return True

    def load_json(self, filename, default=None):
        path = self.tmpdir / filename
        if not path.exists():
            return default
        return json.loads(path.read_text())

    def save_json_atomic(self, filename, data):
        path = self.tmpdir / filename
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data))
        os.replace(tmp, path)


WIN_SCRIPT = [
    "TAKE FLASHLIGHT",
    "SOUTH", "TAKE GAS CAN", "NORTH",
    "EAST", "TAKE SCREWDRIVER", "TAKE STEEL KEY", "NORTH", "TAKE BRASS KEY",
    "SOUTH", "WEST",
    "NORTH", "UNLOCK DOOR", "WEST", "TAKE ALIGN CRANK", "EAST",
    "EAST", "UNLOCK DOOR", "EAST", "TAKE FEED CARTRIDGE", "WEST",
    "WEST", "SOUTH", "WEST", "NORTH",
    "FILL GENERATOR", "START GENERATOR",
    "SOUTH", "TAKE FUSE", "NORTH",
    "NORTH", "EAST", "NORTH", "EAST", "SOUTH",
    "USE SCREWDRIVER", "INSTALL FUSE",
    "EAST", "NORTH", "USE ALIGN CRANK",
    "SOUTH", "WEST", "NORTH",
    "LOAD FEED CARTRIDGE", "TRANSMIT",
]


def run_script(game, script):
    return [game.command(cmd) for cmd in script]


class WinPathTests(unittest.TestCase):
    def test_scripted_full_win_path_reaches_victory_with_expected_score(self):
        with tempfile.TemporaryDirectory() as directory:
            app = FakeApp(directory)
            game = NightStationGame(app)
            outputs = run_script(game, WIN_SCRIPT)
            self.assertTrue(game.won, "win script did not reach victory")
            self.assertTrue(game.over)
            self.assertIn("TRANSMISSION COMPLETE", outputs[-1])
            # 14 discoveries x10 + repairs 100 + unlocks 20 + time bonus 36
            self.assertEqual(game.score, 297, f"unexpected score {game.score}")
            self.assertEqual(game.moves, 45)
            state = cis_dynamic.load_state(app)
            mine = state[cis_nightstation.RECORDS_KEY]["TESTER"]
            self.assertEqual(mine["wins"], 1)
            self.assertEqual(mine["plays"], 1)
            self.assertEqual(mine["best_score"], 297)

    def test_win_shows_high_score_table(self):
        with tempfile.TemporaryDirectory() as directory:
            app = FakeApp(directory)
            game = NightStationGame(app)
            outputs = run_script(game, WIN_SCRIPT)
            self.assertIn("TOP NIGHT OPERATORS", outputs[-1])
            self.assertIn("TESTER", outputs[-1])


class ParserTests(unittest.TestCase):
    def test_nonsense_input_rejected_cleanly(self):
        game = NightStationGame()
        self.assertEqual(game.command("XYZZY PLUGH"), "I don't understand.")
        self.assertEqual(game.command("FROBNICATE THE MODEM"), "I don't understand.")
        self.assertFalse(game.over)
        self.assertEqual(game.moves, 0, "nonsense input should not cost time")

    def test_movement_boundaries(self):
        game = NightStationGame()
        self.assertEqual(game.command("NE"), "You can't go that way.")
        game.command("WEST")  # parking lot
        self.assertEqual(game.room, "parking")
        self.assertEqual(game.command("WEST"), "You can't go that way.")
        self.assertEqual(game.command("GO UP"), "You can't go that way.")

    def test_direction_abbreviations_and_go(self):
        game = NightStationGame()
        game.command("S")  # garage
        self.assertEqual(game.room, "garage")
        game.command("GO NORTH")
        self.assertEqual(game.room, "lobby")


class PuzzleChainTests(unittest.TestCase):
    def test_take_and_inventory(self):
        game = NightStationGame()
        self.assertEqual(game.command("TAKE FLASHLIGHT"), "Taken.")
        self.assertIn("flashlight", game.command("INVENTORY").lower())
        self.assertEqual(game.command("TAKE FLASHLIGHT"), "You already have the flashlight.")
        self.assertEqual(game.command("TAKE BANANA"), "You do not see that here.")

    def test_dark_room_needs_flashlight(self):
        game = NightStationGame()
        for cmd in ["WEST", "NORTH", "SOUTH"]:  # lobby -> parking -> generator -> storage
            game.command(cmd)
        self.assertEqual(game.room, "storage")
        self.assertIn("pitch dark", game.command("LOOK").lower())
        self.assertEqual(game.command("TAKE FUSE"), "You can't see a thing in here.")
        game2 = NightStationGame()
        game2.command("TAKE FLASHLIGHT")
        for cmd in ["WEST", "NORTH", "SOUTH"]:
            game2.command(cmd)
        self.assertEqual(game2.command("TAKE FUSE"), "Taken.")

    def test_generator_needs_fuel_before_start(self):
        game = NightStationGame()
        game.room = "generator"
        self.assertIn("empty", game.command("START GENERATOR").lower())
        game.inventory.append("GAS CAN")
        self.assertIn("+10", game.command("FILL GENERATOR"))
        self.assertTrue(game.fueled)
        self.assertIn("+20", game.command("START GENERATOR"))
        self.assertTrue(game.powered)

    def test_fuse_needs_open_panel(self):
        game = NightStationGame()
        game.room = "transmitter"
        game.inventory.append("FUSE")
        self.assertIn("screwed shut", game.command("INSTALL FUSE"))
        game.inventory.append("SCREWDRIVER")
        game.command("USE SCREWDRIVER")
        self.assertTrue(game.panel_open)
        game.command("INSTALL FUSE")
        self.assertTrue(game.fuse_installed)

    def test_dish_crank_needs_power(self):
        game = NightStationGame()
        game.room = "tower"
        game.inventory.append("ALIGN CRANK")
        self.assertIn("no main power", game.command("USE ALIGN CRANK").lower())
        self.assertFalse(game.dish_aligned)
        game.powered = True
        out = game.command("USE ALIGN CRANK")
        self.assertIn("locks onto the satellite", out)
        self.assertTrue(game.dish_aligned)

    def test_locked_doors_need_keys(self):
        game = NightStationGame()
        game.room = "operations"
        self.assertEqual(game.command("WEST"), "Locked: the maintenance shop door. (Brass Key required.)")
        self.assertEqual(game.command("UNLOCK DOOR"), "You need the brass key.")
        game.inventory.append("BRASS KEY")
        self.assertIn("swings open", game.command("UNLOCK DOOR"))
        game.command("WEST")
        self.assertEqual(game.room, "maintenance")

    def test_transmit_reports_missing_pieces(self):
        game = NightStationGame()
        game.room = "control"
        out = game.command("TRANSMIT")
        self.assertIn("refuses", out)
        for piece in ("main power", "exciter fuse", "off-azimuth", "cartridge"):
            self.assertIn(piece, out)
        self.assertFalse(game.won)

    def test_drop_and_retake(self):
        game = NightStationGame()
        game.command("TAKE FLASHLIGHT")
        self.assertEqual(game.command("DROP FLASHLIGHT"), "Dropped.")
        self.assertIn("nothing", game.command("INVENTORY"))
        self.assertEqual(game.command("TAKE FLASHLIGHT"), "Taken.")


class ClockAndQuitTests(unittest.TestCase):
    def test_score_and_time_commands(self):
        game = NightStationGame()
        out = game.command("SCORE")
        self.assertIn("SCORE:", out)
        self.assertIn("23:15", out)
        self.assertIn("405 minutes left", out)
        game.command("LOOK")
        self.assertIn("23:25", game.command("TIME"))

    def test_quit_exits_cleanly_and_records(self):
        with tempfile.TemporaryDirectory() as directory:
            app = FakeApp(directory)
            game = NightStationGame(app)
            out = game.command("QUIT")
            self.assertTrue(game.over)
            self.assertTrue(game.quit)
            self.assertFalse(game.won)
            self.assertIn("SHIFT INCOMPLETE", out)
            state = cis_dynamic.load_state(app)
            mine = state[cis_nightstation.RECORDS_KEY]["TESTER"]
            self.assertEqual(mine["plays"], 1)
            self.assertEqual(mine["wins"], 0)

    def test_clock_runs_out_loses_game(self):
        with tempfile.TemporaryDirectory() as directory:
            app = FakeApp(directory)
            game = NightStationGame(app)
            game.moves = MAX_MOVES - 1
            out = game.command("LOOK")
            self.assertTrue(game.lost)
            self.assertTrue(game.over)
            self.assertIn("FEED WINDOW HAS PASSED", out)

    def test_help_lists_verbs(self):
        out = NightStationGame().command("HELP")
        for verb in ("LOOK", "TAKE", "INVENTORY", "EXAMINE", "USE", "TRANSMIT", "QUIT"):
            self.assertIn(verb, out)


class HighScorePersistenceTests(unittest.TestCase):
    def test_high_score_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as directory:
            app = FakeApp(directory)
            first = NightStationGame(app)
            run_script(first, WIN_SCRIPT)
            self.assertTrue(first.won)
            second = NightStationGame(app)
            table = "\n".join(second.records_table())
            self.assertIn("TOP NIGHT OPERATORS", table)
            self.assertIn("TESTER", table)
            self.assertIn("297", table)
            state = cis_dynamic.load_state(app)
            self.assertEqual(len(state[cis_nightstation.HISCORE_KEY]), 1)

    def test_board_keeps_top_five_across_users(self):
        with tempfile.TemporaryDirectory() as directory:
            for user in ("OP1", "OP2", "OP3", "OP4", "OP5", "OP6"):
                app = FakeApp(directory, user_id=user)
                game = NightStationGame(app)
                game.score = 100
                game.won = True
                game.record_result()
            app = FakeApp(directory, user_id="OP7")
            table = "\n".join(NightStationGame(app).records_table())
            self.assertNotIn("OP6", table)
            self.assertIn("OP1", table)
            state = cis_dynamic.load_state(app)
            self.assertEqual(len(state[cis_nightstation.HISCORE_KEY]), 5)

    def test_offline_game_still_runs(self):
        game = NightStationGame()  # no app: in-memory, no persistence
        outputs = run_script(game, WIN_SCRIPT)
        self.assertTrue(game.won)
        self.assertIn("TRANSMISSION COMPLETE", outputs[-1])


class PlayEntryTests(unittest.TestCase):
    def test_play_quits_from_scripted_input(self):
        with tempfile.TemporaryDirectory() as directory:
            app = FakeApp(directory)
            with patch.object(cis_nightstation, "input", side_effect=["HELP", "QUIT"]):
                cis_nightstation.play(app)  # should return without raising
            state = cis_dynamic.load_state(app)
            self.assertEqual(state[cis_nightstation.RECORDS_KEY]["TESTER"]["plays"], 1)


# --- Feature 4: Sports & TV (cis_sports) ---
ANACHRONISMS = [
    "Friends", "Seinfeld", "CSI", "Survivor", "American Idol",
    "Texans", "Jaguars", "Panthers", "Ravens", "Titans",
    "Arizona Cardinals", "St. Louis Rams", "Tennessee Oilers",
    "Los Angeles Chargers", "2000", "1999", "1995", "1994",
    "20-16", "iPhone", "internet", "www.",
]


class SportsContentTests(unittest.TestCase):
    def setUp(self):
        os.environ["CIS_SIMULATION_DATE"] = "1988-12-15"

    def test_nfl_lines_non_empty(self):
        lines = cis_sports.nfl_lines()
        self.assertTrue(lines)
        self.assertTrue(all(isinstance(l, str) for l in lines))
        self.assertTrue(any(l.strip() for l in lines))

    def test_tv_lines_non_empty(self):
        lines = cis_sports.tv_lines()
        self.assertTrue(lines)
        self.assertTrue(all(isinstance(l, str) for l in lines))
        self.assertTrue(any(l.strip() for l in lines))

    def test_mlb_lines_non_empty(self):
        lines = cis_sports.mlb_lines()
        self.assertTrue(lines)
        self.assertTrue(all(isinstance(l, str) for l in lines))
        self.assertTrue(any(l.strip() for l in lines))

    def test_standings_divisions_and_teams_consistent(self):
        expected_divisions = {"AFC EAST", "AFC CENTRAL", "AFC WEST",
                              "NFC EAST", "NFC CENTRAL", "NFC WEST"}
        self.assertEqual(set(cis_sports.NFL_STANDINGS), expected_divisions)
        seen = {}
        for division, teams in cis_sports.NFL_STANDINGS.items():
            for team, wins, losses, ties, _verified in teams:
                self.assertTrue(team)
                self.assertGreaterEqual(wins, 0)
                self.assertEqual(wins + losses + ties, 16,
                                 f"{team} must have 16 games")
                self.assertNotIn(team, seen,
                                 f"{team} appears in two divisions")
                seen[team] = division

    def test_standings_division_winners(self):
        winners = {div: rows[0][0] for div, rows in cis_sports.NFL_STANDINGS.items()}
        self.assertEqual(winners["AFC EAST"], "Buffalo Bills")
        self.assertEqual(winners["AFC CENTRAL"], "Cincinnati Bengals")
        self.assertEqual(winners["AFC WEST"], "Seattle Seahawks")
        self.assertEqual(winners["NFC EAST"], "Philadelphia Eagles")
        self.assertEqual(winners["NFC CENTRAL"], "Chicago Bears")
        self.assertEqual(winners["NFC WEST"], "San Francisco 49ers")

    def test_standings_sorted_by_wins(self):
        for division, teams in cis_sports.NFL_STANDINGS.items():
            wins = [t[1] for t in teams]
            self.assertEqual(wins, sorted(wins, reverse=True),
                             f"{division} not sorted by wins")

    def test_highlight_varies_by_day_deterministically(self):
        dec1 = cis_sports.nfl_lines(date(1988, 12, 1))
        dec2 = cis_sports.nfl_lines(date(1988, 12, 2))
        highlight1 = [l for l in dec1 if l.startswith("THIS WEEK:")]
        highlight2 = [l for l in dec2 if l.startswith("THIS WEEK:")]
        self.assertEqual(len(highlight1), 1)
        self.assertNotEqual(highlight1, highlight2,
                            "highlight should rotate by day")
        again = cis_sports.nfl_lines(date(1988, 12, 1))
        self.assertEqual([l for l in again if l.startswith("THIS WEEK:")],
                         highlight1, "same day must give same highlight")

    def test_default_day_uses_simulation_day(self):
        # With env pinned to 1988-12-15, default day must match explicit day.
        self.assertEqual(cis_sports.nfl_lines(),
                         cis_sports.nfl_lines(date(1988, 12, 15)))

    def test_tv_grid_covers_all_nights_and_networks(self):
        for night in ("SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY",
                      "THURSDAY", "FRIDAY", "SATURDAY"):
            self.assertIn(night, cis_sports.TV_GRID)
            for net in ("ABC", "CBS", "FOX", "NBC"):
                self.assertIn(net, cis_sports.TV_GRID[night])
                self.assertTrue(cis_sports.TV_GRID[night][net])

    def test_tv_grid_key_placements(self):
        thursday = cis_sports.TV_GRID["THURSDAY"]["NBC"]
        self.assertIn("The Cosby Show", thursday)
        self.assertIn("Cheers", thursday)
        tuesday = cis_sports.TV_GRID["TUESDAY"]["ABC"]
        self.assertIn("Roseanne", tuesday)
        self.assertIn("Who's the Boss?", tuesday)
        sunday = cis_sports.TV_GRID["SUNDAY"]["CBS"]
        self.assertIn("60 Minutes", sunday)
        saturday = cis_sports.TV_GRID["SATURDAY"]["NBC"]
        self.assertIn("The Golden Girls", saturday)
        wednesday = cis_sports.TV_GRID["WEDNESDAY"]["NBC"]
        self.assertIn("Night Court", wednesday)

    def test_no_anachronisms(self):
        sections = (cis_sports.nfl_lines(date(1988, 12, 20))
                    + cis_sports.tv_lines(date(1988, 12, 20))
                    + cis_sports.mlb_lines(date(1988, 12, 20)))
        blob = "\n".join(sections)
        for word in ANACHRONISMS:
            self.assertNotIn(word, blob, f"anachronism: {word}")

    def test_sports_service_returns_sections(self):
        sections = cis_sports.sports_service(app=None)
        self.assertEqual([t for t, _ in sections],
                         ["NFL", "TV", "MLB", "SUPER BOWL", "WORLD SERIES", "NBA", "NHL"])
        for title, lines in sections:
            self.assertTrue(lines, f"{title} section empty")


# --- Feature 5: era-aware world ---
REPO = str(REPO_ROOT)
sys.path.insert(0, REPO)

import cis_dynamic
from cis_session import SessionState, active_session
from cis_timecapsule import pack_for


def _head_module():
    """Load cis_dynamic.py as committed at HEAD for pre/post-change comparison."""
    blob = subprocess.run(
        ["git", "-C", REPO, "show", "HEAD:cis_dynamic.py"],
        capture_output=True, text=True, check=True,
    ).stdout
    path = os.path.join(tempfile.gettempdir(), "cis_dynamic_head_f5.py")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(blob)
    spec = importlib.util.spec_from_file_location("cis_dynamic_head_f5", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _all_pack_topics():
    topics = set()
    for when, _label in (
        (date(1981, 8, 12), ""), (date(1984, 1, 24), ""),
        (date(1986, 1, 28), ""), (date(1987, 10, 19), ""),
        (date(1989, 11, 9), ""), (date(1991, 8, 6), ""),
    ):
        topics.update(pack_for(when)["cb_topics"])
    return topics


def _all_pack_announcements():
    lines = set()
    for when in (date(1981, 8, 12), date(1984, 1, 24), date(1986, 1, 28),
                 date(1987, 10, 19), date(1989, 11, 9), date(1991, 8, 6)):
        lines.update(pack_for(when)["announcements"])
    return lines


def _find_pack_batch(session_date, pack, hour=20, buckets=3000):
    """Scan deterministic buckets until cb_ambient_events emits pack content."""
    state = SessionState(simulation_date=session_date)
    with active_session(state):
        for bucket in range(buckets):
            batch = cis_dynamic.cb_ambient_events("1", bucket, (), hour=hour)
            if batch and any(line in pack["cb_topics"] for _sender, line in batch):
                return batch
    return None


class TestCbEraAwareness(unittest.TestCase):
    def test_featured_date_session_emits_pack_cb_topics(self):
        pack = pack_for(date(1986, 1, 28))
        batch = _find_pack_batch(date(1986, 1, 28), pack)
        self.assertIsNotNone(batch, "expected a pack-derived CB batch within the scan window")
        lines = [line for _sender, line in batch]
        self.assertTrue(any(line in pack["cb_topics"] for line in lines))
        self.assertTrue(all(sender in cis_dynamic.HANDLES for sender, _line in batch))

    def test_featured_date_session_cb_is_deterministic(self):
        pack = pack_for(date(1986, 1, 28))
        state = SessionState(simulation_date=date(1986, 1, 28))
        with active_session(state):
            first = cis_dynamic.cb_ambient_events("1", 42, (), hour=20)
            second = cis_dynamic.cb_ambient_events("1", 42, (), hour=20)
        self.assertEqual(first, second)

    def test_present_day_cb_has_no_pack_content(self):
        topics = _all_pack_topics()
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            for bucket in range(3000):
                batch = cis_dynamic.cb_ambient_events("1", bucket, (), hour=20)
                self.assertFalse(any(line in topics for _sender, line in batch))

    def test_present_day_cb_matches_pre_change_corpus(self):
        corpus = {line for conversations in cis_dynamic.CB_CONVERSATIONS.values()
                  for conversation in conversations for _sender, line in conversation}
        mover = re.compile(r"^\*\*\* \S+ left for channel [123] \*\*\*$")
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            for bucket in range(3000):
                for sender, line in cis_dynamic.cb_ambient_events("1", bucket, (), hour=20):
                    if sender == "SYSTEM":
                        self.assertRegex(line, mover)
                    else:
                        self.assertIn(line, corpus)

    def test_cb_ambient_path_function_unchanged_vs_head(self):
        head = _head_module()
        import inspect
        self.assertEqual(inspect.getsource(head.cb_ambient_events),
                         inspect.getsource(cis_dynamic.cb_ambient_events))

    def test_login_announcements_present_day_identical_vs_head(self):
        head = _head_module()
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            before = head.announcements("70000,0001")
            after = cis_dynamic.announcements("70000,0001")
        self.assertEqual(before, after)


class TestEraForumBulletins(unittest.TestCase):
    def test_featured_date_returns_pack_announcements(self):
        pack = pack_for(date(1986, 1, 28))
        lines = cis_dynamic.era_forum_bulletins("ibmhw", day=date(1986, 1, 28))
        self.assertEqual(lines[0], "SYSOP BULLETIN  [1986-01-28: Challenger]")
        self.assertEqual(lines[1:], pack["announcements"])

    def test_present_day_returns_1988_bulletins(self):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            lines = cis_dynamic.era_forum_bulletins("gamers")
        self.assertEqual(len(lines), 2)
        self.assertTrue(all(line in cis_dynamic.FORUM_BULLETINS_1988 for line in lines))
        self.assertFalse(any(line in _all_pack_announcements() for line in lines))

    def test_explicit_present_day_date_matches_default(self):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            defaulted = cis_dynamic.era_forum_bulletins("gamers")
            explicit = cis_dynamic.era_forum_bulletins("gamers", day=date(1988, 12, 15))
        self.assertEqual(defaulted, explicit)

    def test_featured_date_does_not_leak_1988_bulletins(self):
        lines = cis_dynamic.era_forum_bulletins("hamnet", day=date(1987, 10, 19))
        self.assertFalse(any(line in cis_dynamic.FORUM_BULLETINS_1988 for line in lines))


class TestSessionIsolation(unittest.TestCase):
    def test_two_sessions_render_their_own_era(self):
        pack_a = pack_for(date(1986, 1, 28))
        pack_b = pack_for(date(1991, 8, 6))
        with active_session(SessionState(simulation_date=date(1986, 1, 28))):
            self.assertEqual(cis_dynamic.simulation_day(), date(1986, 1, 28))
            lines_a = cis_dynamic.era_forum_bulletins("ibmhw")
            batch_a = _find_pack_batch(date(1986, 1, 28), pack_a)
        with active_session(SessionState(simulation_date=date(1991, 8, 6))):
            self.assertEqual(cis_dynamic.simulation_day(), date(1991, 8, 6))
            lines_b = cis_dynamic.era_forum_bulletins("ibmhw")
            batch_b = _find_pack_batch(date(1991, 8, 6), pack_b)
        self.assertEqual(lines_a[1:], pack_a["announcements"])
        self.assertEqual(lines_b[1:], pack_b["announcements"])
        self.assertTrue(any(line in pack_a["cb_topics"] for _s, line in batch_a))
        self.assertTrue(any(line in pack_b["cb_topics"] for _s, line in batch_b))
        # Neither session sees the other's content.
        self.assertFalse(any(line in pack_b["cb_topics"] for _s, line in batch_a))
        self.assertFalse(any(line in pack_a["cb_topics"] for _s, line in batch_b))

    def test_session_exit_restores_no_session_date(self):
        with active_session(SessionState(simulation_date=date(1986, 1, 28))):
            self.assertEqual(cis_dynamic.simulation_day(), date(1986, 1, 28))
        from cis_session import session_simulation_date
        self.assertIsNone(session_simulation_date())


# --- Content pack 2: veterans / roots / guitar forums, trading post, entertainment ---

CP2_REQUIRED_FIELDS = {"content_id", "section", "date", "author", "subject", "body", "parent"}

VETERANS_ANACHRONISMS = [
    "iraq", "afghanistan", "desert storm", "desert shield", "9/11",
    "september 11", "enduring freedom", "iraqi freedom", "va choice",
    "internet", "website", "web site", "1990", "1991", "2001",
]

ROOTS_ANACHRONISMS = [
    "1920 census", "1930 census", "1940 census", "ancestry.com", "dna test",
    "dna testing", "genetic genealogy", "internet", "website", "web site",
    "familysearch.org", "online tree",
]

GUITAR_ANACHRONISMS = [
    "line 6", "line6", "silver sky", "kemper", "axe-fx", "axefx",
    "fractal", "neural dsp", "youtube", "internet", "website",
    "reverb.com", "sweetwater.com", " helix",
]

TRADINGPOST_ANACHRONISMS = [
    "pentium", "windows 95", "windows95", "dvd", "mp3", "zip drive",
    "1990", "1991",
]

ENTERTAINMENT_ANACHRONISMS = [
    "1990", "internet", "website", "grunge", "nirvana",
]


def _check_cp2_seed_posts(testcase, module, prefix):
    """Shared quality gate for the three new forum content modules."""
    posts = module.SEED_POSTS
    testcase.assertGreaterEqual(len(posts), 12, f"{prefix}: too few seed posts")
    testcase.assertLessEqual(len(posts), 20, f"{prefix}: too many seed posts")
    valid_sections = {sec_id for sec_id, _ in module.SECTIONS.values()}
    seen = []
    for post in posts:
        testcase.assertEqual(set(post.keys()), CP2_REQUIRED_FIELDS,
                             f"field mismatch in {post.get('content_id')}")
        for field in ("content_id", "section", "date", "author", "subject", "body"):
            testcase.assertTrue(str(post[field]).strip(),
                                f"{field} empty in {post['content_id']}")
        testcase.assertIsNone(post["parent"], post["content_id"])
        testcase.assertIn(post["section"], valid_sections, post["content_id"])
        month, day, year = post["date"].split("/")
        testcase.assertEqual((month, year), ("12", "88"), post["content_id"])
        testcase.assertTrue(1 <= int(day) <= 31, post["content_id"])
        seen.append(post["content_id"])
    testcase.assertEqual(len(set(seen)), len(seen), f"{prefix}: duplicate content ids")
    for cid in seen:
        testcase.assertRegex(cid, rf"^{prefix}-1988-\d{{3}}$", cid)


def _check_no_anachronisms(testcase, posts, banned, label):
    for post in posts:
        text = (post["subject"] + "\n" + post["body"]).lower()
        for bad in banned:
            testcase.assertNotIn(bad.lower(), text,
                                 f"anachronism {bad!r} in {post['content_id']} ({label})")


def _check_sections_shape(testcase, module, prefix, expected_count):
    secs = module.SECTIONS
    testcase.assertIsInstance(secs, dict)
    testcase.assertEqual(len(secs), expected_count)
    testcase.assertEqual(set(secs.keys()), {str(i) for i in range(1, expected_count + 1)})
    ids = []
    for key, spec in secs.items():
        testcase.assertIsInstance(spec, (tuple, list), f"section {key}")
        testcase.assertEqual(len(spec), 2, f"section {key}")
        sec_id, title = spec
        testcase.assertTrue(sec_id.startswith(prefix + "_"), sec_id)
        testcase.assertTrue(title.strip(), sec_id)
        ids.append(sec_id)
    testcase.assertEqual(len(set(ids)), len(ids), "section ids must be unique")
    testcase.assertEqual(module.section_spec(), module.SECTIONS)


class VeteransForumTests(unittest.TestCase):
    def test_sections(self):
        _check_sections_shape(self, cis_veterans, "veterans", 4)

    def test_seed_posts(self):
        _check_cp2_seed_posts(self, cis_veterans, "veterans")

    def test_no_anachronisms(self):
        _check_no_anachronisms(self, cis_veterans.SEED_POSTS,
                               VETERANS_ANACHRONISMS, "veterans")

    def test_wall_dedication_era(self):
        blob = " ".join(p["subject"] + " " + p["body"]
                        for p in cis_veterans.SEED_POSTS).lower()
        self.assertIn("vietnam veterans memorial", blob)


class RootsForumTests(unittest.TestCase):
    def test_sections(self):
        _check_sections_shape(self, cis_roots, "roots", 6)

    def test_seed_posts(self):
        _check_cp2_seed_posts(self, cis_roots, "roots")

    def test_no_anachronisms(self):
        _check_no_anachronisms(self, cis_roots.SEED_POSTS,
                               ROOTS_ANACHRONISMS, "roots")

    def test_1920_census_not_listed_available(self):
        blob = " ".join(p["subject"] + " " + p["body"]
                        for p in cis_roots.SEED_POSTS)
        # A surname date range may end in 1920, but the 1920 census must
        # never be listed as an available research source.
        self.assertNotIn("1920 census", blob)

    def test_research_tips(self):
        self.assertGreaterEqual(len(cis_roots.RESEARCH_TIPS), 5)
        rendered = cis_roots.render_tips()
        self.assertIn("Soundex", rendered)
        for tip in cis_roots.RESEARCH_TIPS:
            self.assertTrue(tip["title"].strip())
            self.assertTrue(tip["body"].strip())


class GuitarForumTests(unittest.TestCase):
    def test_sections(self):
        _check_sections_shape(self, cis_guitar, "guitar", 6)

    def test_seed_posts(self):
        _check_cp2_seed_posts(self, cis_guitar, "guitar")

    def test_no_anachronisms(self):
        _check_no_anachronisms(self, cis_guitar.SEED_POSTS,
                               GUITAR_ANACHRONISMS, "guitar")

    def test_period_gear_present(self):
        blob = " ".join(p["subject"] + " " + p["body"]
                        for p in cis_guitar.SEED_POSTS)
        for gear in ("JCM800", "Tube Screamer", "Portastudio", "DX7"):
            self.assertIn(gear, blob, f"expected period gear {gear!r} in seed posts")


class TradingPostTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._old_base = cis_tradingpost.BASE_DIR
        cis_tradingpost.BASE_DIR = Path(self._tmp.name)

    def tearDown(self):
        cis_tradingpost.BASE_DIR = self._old_base

    def test_seed_ad_count_and_categories(self):
        ads = cis_tradingpost.seed_ads()
        self.assertEqual(len(ads), 15)
        cats = {ad["category"] for ad in ads}
        self.assertEqual(cats, {"FOR SALE", "WANTED", "TRADE"})
        ids = [ad["id"] for ad in ads]
        self.assertEqual(ids, [f"TP-{n:04d}" for n in range(1, 16)])
        for ad in ads:
            self.assertRegex(ad["placed"], r"^1988-12-\d{2}$")

    def test_seed_ads_no_anachronisms(self):
        for ad in cis_tradingpost.seed_ads():
            text = (ad["title"] + "\n" + ad["body"]).lower()
            for bad in TRADINGPOST_ANACHRONISMS:
                self.assertNotIn(bad, text, f"anachronism {bad!r} in {ad['id']}")

    def test_place_ad_persists_and_lists(self):
        ad = cis_tradingpost.place_ad("WANTED", "Test widget", 42.5,
                                      "tester", "A test ad body.",
                                      day=date(1988, 12, 15))
        self.assertEqual(ad["id"], "TP-0016")
        self.assertEqual(ad["placed"], "1988-12-15")
        active = cis_tradingpost.active_ads(day=date(1988, 12, 20))
        self.assertIn("Test widget", [a["title"] for a in active])
        in_cat = cis_tradingpost.ads_in_category("WANTED", day=date(1988, 12, 20))
        self.assertEqual(len(in_cat), 3)  # 2 seed + 1 placed

    def test_ad_expiry(self):
        ad = cis_tradingpost.place_ad("FOR SALE", "Expiring gizmo", 10.0,
                                      "tester", "Soon gone.",
                                      day=date(1988, 12, 1))
        self.assertFalse(cis_tradingpost.is_expired(ad, date(1988, 12, 31)))
        self.assertTrue(cis_tradingpost.is_expired(ad, date(1989, 1, 2)))
        active = cis_tradingpost.active_ads(day=date(1989, 2, 1))
        self.assertNotIn(ad["id"], [a["id"] for a in active])

    def test_category_lines_render(self):
        lines = cis_tradingpost.category_lines("FOR SALE", day=date(1988, 12, 20))
        text = "\n".join(lines)
        self.assertIn("Hayes Smartmodem 1200", text)
        self.assertIn("FOR SALE --", text)

    def test_menu_lines_cover_all_categories(self):
        sections = cis_tradingpost.tradingpost_menu_lines(day=date(1988, 12, 20))
        self.assertEqual([title for title, _ in sections],
                         ["FOR SALE", "WANTED", "TRADE"])
        for _title, lines in sections:
            self.assertTrue(lines)


class EntertainmentTests(unittest.TestCase):
    def test_service_sections(self):
        sections = cis_entertainment.entertainment_service(None)
        self.assertEqual([title for title, _ in sections],
                         ["Billboard Hot 100", "Movies", "Bowl Previews",
                          "Christmas Music"])
        for _title, lines in sections:
            self.assertTrue(lines)

    def test_christmas_music_seasonal(self):
        december = cis_entertainment.entertainment_menu_lines(date(1988, 12, 15))
        self.assertIn("Christmas Music", [t for t, _ in december])
        june = cis_entertainment.entertainment_menu_lines(date(1988, 6, 15))
        titles = [t for t, _ in june]
        self.assertNotIn("Christmas Music", titles)
        self.assertEqual(titles, ["Billboard Hot 100", "Movies", "Bowl Previews"])

    def test_chart_number_one_by_week(self):
        early = "\n".join(cis_entertainment.chart_lines(date(1988, 12, 5)))
        self.assertIn("Chicago", early)
        self.assertIn("Look Away", early)
        late = "\n".join(cis_entertainment.chart_lines(date(1988, 12, 25)))
        self.assertIn("Poison", late)
        self.assertIn("Every Rose Has Its Thorn", late)

    def test_movies_december_1988(self):
        text = "\n".join(cis_entertainment.movies_lines(date(1988, 12, 15)))
        for title in ("RAIN MAN", "TWINS", "THE NAKED GUN", "SCROOGED",
                      "WORKING GIRL", "DIE HARD", "WHO FRAMED ROGER RABBIT"):
            self.assertIn(title, text)

    def test_bowls_are_previews_not_results(self):
        text = "\n".join(cis_entertainment.bowls_lines(date(1988, 12, 15)))
        for bowl in ("FIESTA BOWL", "ORANGE BOWL", "SUGAR BOWL",
                     "ROSE BOWL", "COTTON BOWL"):
            self.assertIn(bowl, text)
        self.assertIn("Previews only", text)
        # None of the actual Jan 2, 1989 final scores may appear --
        # previews must never assert results.
        for score in ("34-21", "23-3", "13-7", "22-14", "17-3"):
            self.assertNotIn(score, text, f"result {score} leaked into previews")

    def test_no_anachronisms(self):
        texts = []
        for _title, lines in cis_entertainment.entertainment_menu_lines(date(1988, 12, 15)):
            texts.append("\n".join(lines))
        blob = "\n".join(texts).lower()
        for bad in ENTERTAINMENT_ANACHRONISMS:
            self.assertNotIn(bad, blob, f"anachronism {bad!r} in entertainment")


class ContentPack2WiringTests(unittest.TestCase):
    def test_forum_catalog_entries(self):
        for forum_id, module in (("veterans", cis_veterans),
                                 ("roots", cis_roots),
                                 ("guitar", cis_guitar)):
            self.assertIn(forum_id, compuserve.FORUM_CATALOG)
            sections = compuserve.FORUM_CATALOG[forum_id]["sections"]
            self.assertEqual(sections, module.SECTIONS)

    def test_forum_choices(self):
        self.assertEqual(compuserve.FORUM_CHOICES["11"], "veterans")
        self.assertEqual(compuserve.FORUM_CHOICES["12"], "roots")
        self.assertEqual(compuserve.FORUM_CHOICES["13"], "guitar")

    def test_screens_options(self):
        screens = json.loads((REPO_ROOT / "screens.json").read_text(encoding="utf-8"))
        self.assertEqual(screens["forums"]["options"]["11"], "Veterans Forum")
        self.assertEqual(screens["forums"]["options"]["12"], "Roots & Branches Genealogy Forum")
        self.assertEqual(screens["forums"]["options"]["13"], "Guitar & Music Forum")
        self.assertEqual(screens["news"]["options"]["9"], "Entertainment")
        self.assertEqual(screens["shopping"]["options"]["6"], "Trading Post Classifieds")

    def test_go_commands(self):
        self.assertEqual(compuserve.resolve_go_destination("VETERANS"), "veterans")
        self.assertEqual(compuserve.resolve_go_destination("ROOTS"), "roots")
        self.assertEqual(compuserve.resolve_go_destination("GUITAR"), "guitar")
        self.assertEqual(compuserve.resolve_go_destination("TRADINGPOST"), "tradingpost")
        self.assertEqual(compuserve.resolve_go_destination("ENTERTAINMENT"), "entertainment")

    def test_seed_messages_in_computer_communities(self):
        pack = json.loads((REPO_ROOT / "computer_communities.json").read_text(encoding="utf-8"))
        by_prefix = {}
        for message in pack["messages"]:
            for prefix in ("veterans", "roots", "guitar"):
                if message["content_id"].startswith(prefix + "-1988-"):
                    by_prefix.setdefault(prefix, []).append(message)
        self.assertEqual(len(by_prefix["veterans"]), len(cis_veterans.SEED_POSTS))
        self.assertEqual(len(by_prefix["roots"]), len(cis_roots.SEED_POSTS))
        self.assertEqual(len(by_prefix["guitar"]), len(cis_guitar.SEED_POSTS))
        for prefix, module in (("veterans", cis_veterans), ("roots", cis_roots),
                               ("guitar", cis_guitar)):
            valid = {sec_id for sec_id, _ in module.SECTIONS.values()}
            for message in by_prefix[prefix]:
                self.assertIn(message["section"], valid, message["content_id"])

    def test_merge_forums_installs_new_sections(self):
        merged = cis_communities.merge_forums({})
        for _sec_id, section_key in (("veterans", "veterans_stories"),
                                     ("roots", "roots_census"),
                                     ("guitar", "guitar_tabs")):
            self.assertTrue(merged.get(section_key), section_key)
            for message in merged[section_key]:
                self.assertIn("id", message)
                self.assertIn("parent_id", message)


    def test_new_forums_reachable_from_menu(self):
        for choice, forum_id in (("11", "veterans"), ("12", "roots"),
                                 ("13", "guitar")):
            with self.subTest(forum=forum_id), \
                    patch.object(compuserve, 'session_state', SessionState()), \
                    patch.object(compuserve, 'show_screen'), \
                    patch.object(compuserve, 'forum_service') as service, \
                    patch.object(compuserve, 'show_logout_summary'), \
                    patch('builtins.input', side_effect=['GO FORUMSSIM', choice, 'OFF']):
                compuserve.navigate()
                service.assert_called_once_with(forum_id)


# --- Content pack 3: tech forum, weather wire, daily crossword, books & magazines ---
"""Standalone tests for the Tech Talk forum content module (cis_tech).

Run: cd ~/workspace/compuserve-simulator && python3 /tmp/tech_tests.py
"""

# ============================================================
# STRIP-END markers below when merging into test_compuserve.py.
# The sys.path/setup imports live only in this standalone file.
# ============================================================
# ============================================================

REQUIRED_FIELDS = {
    "content_id", "section", "date", "author", "subject", "body", "parent",
}

EXPECTED_SECTIONS = {
    "1": "IBM PC & Clones",
    "2": "Macintosh",
    "3": "Amiga vs Atari ST",
    "4": "OS/2 & Operating Systems",
    "5": "Modems & Telecom",
    "6": "CD-ROM & New Tech",
}

BANNED_TERMS = [
    "windows 95", "windows 98", "pentium", "usb", "wi-fi", "wifi",
    "linux", "world wide web",
]


class TechForumTests(unittest.TestCase):
    def test_forum_identity(self):
        self.assertEqual(cis_tech.FORUM_ID, "tech")
        self.assertTrue(cis_tech.FORUM_TITLE.strip())

    def test_section_spec_shape(self):
        spec = cis_tech.section_spec()
        self.assertIsInstance(spec, dict)
        self.assertEqual(set(spec.keys()), {"1", "2", "3", "4", "5", "6"})
        ids = []
        for key, value in spec.items():
            self.assertIsInstance(value, tuple, f"section {key}")
            self.assertEqual(len(value), 2, f"section {key}")
            sec_id, title = value
            self.assertTrue(sec_id.startswith("tech_"), sec_id)
            self.assertTrue(title.strip(), sec_id)
            ids.append(sec_id)
        self.assertEqual(len(set(ids)), len(ids), "section ids must be unique")

    def test_section_spec_titles(self):
        spec = cis_tech.section_spec()
        for key, expected_title in EXPECTED_SECTIONS.items():
            self.assertEqual(spec[key][1], expected_title, f"section {key}")

    def test_section_spec_returns_tuples(self):
        # Must be {key: (id, title)} tuples even if SECTIONS ever changes shape.
        for key, value in cis_tech.section_spec().items():
            self.assertIsInstance(value, tuple, key)
            self.assertEqual(tuple(value), tuple(cis_tech.SECTIONS[key]))

    def test_seed_posts_count(self):
        self.assertEqual(len(cis_tech.SEED_POSTS), 16)
        self.assertEqual(len(cis_tech.seed_posts()), 16)

    def test_seed_posts_required_fields(self):
        for post in cis_tech.seed_posts():
            self.assertEqual(set(post.keys()), REQUIRED_FIELDS,
                             f"field mismatch in {post.get('content_id')}")
            for field in ("content_id", "section", "date", "author",
                          "subject", "body"):
                self.assertTrue(str(post[field]).strip(),
                                f"{field} empty in {post['content_id']}")
            self.assertIsNone(post["parent"],
                              f"parent must be None in {post['content_id']}")

    def test_seed_posts_unique_content_ids(self):
        ids = [p["content_id"] for p in cis_tech.seed_posts()]
        self.assertEqual(len(set(ids)), len(ids), "content_ids must be unique")
        for cid in ids:
            self.assertRegex(cid, r"^tech-1988-\d{3}$", cid)

    def test_seed_posts_sections_valid(self):
        valid = {sec_id for sec_id, _ in cis_tech.SECTIONS.values()}
        for post in cis_tech.seed_posts():
            self.assertIn(post["section"], valid, post["content_id"])

    def test_seed_posts_cover_all_sections(self):
        used = {p["section"] for p in cis_tech.seed_posts()}
        valid = {sec_id for sec_id, _ in cis_tech.SECTIONS.values()}
        self.assertEqual(used, valid, "every section should have seed posts")

    def test_seed_posts_dates_december_1988(self):
        for post in cis_tech.seed_posts():
            parts = post["date"].split("/")
            self.assertEqual(len(parts), 3, post["content_id"])
            month, day, year = parts
            self.assertEqual((month, year), ("12", "88"), post["content_id"])
            self.assertTrue(1 <= int(day) <= 31, post["content_id"])

    def test_no_anachronisms(self):
        for post in cis_tech.seed_posts():
            text = (post["subject"] + "\n" + post["body"]).lower()
            for bad in BANNED_TERMS:
                self.assertNotIn(bad, text,
                                 f"anachronism {bad!r} in {post['content_id']}")

    def test_seed_posts_return_copies(self):
        first = cis_tech.seed_posts()
        first[0]["subject"] = "MUTATED"
        self.assertNotEqual(cis_tech.seed_posts()[0]["subject"], "MUTATED")


"""Unit tests for the cis_weather Weather Wire & Ski Reports service.

Verifies weather_service(app): expected sections, non-empty content,
determinism per simulated day, day-to-day variation, and that no
anachronistic (post-1988) claims or exact historical-record assertions
appear in the output.
"""
# =======================================================================
# =======================================================================

import unittest
from unittest.mock import patch

import cis_weather


EXPECTED_TITLES = ("U.S. City Forecasts", "Ski Reports", "Weather Wire Notes", "1988 Weather Retrospective")

BANNED_TERMS = (
    "1989", "1990", "2000s", "internet", "global warming", "climate change",
    "twitter", "iphone", "facebook", "google", "open-meteo", "climate.gov",
)


class WeatherServiceSectionsTest(unittest.TestCase):
    def _sections(self, sim_date):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": sim_date}):
            return cis_weather.weather_service(app=None)

    def test_returns_expected_sections(self):
        sections = self._sections("1988-12-15")
        self.assertEqual(len(sections), 4)
        titles = [title for title, _lines in sections]
        self.assertEqual(tuple(titles), EXPECTED_TITLES)

    def test_each_section_has_non_empty_lines(self):
        for title, lines in self._sections("1988-12-15"):
            with self.subTest(title=title):
                self.assertIsInstance(lines, list)
                self.assertTrue(lines, f"section {title!r} is empty")
                non_blank = [line for line in lines if line.strip()]
                self.assertTrue(non_blank, f"section {title!r} has no content")
                self.assertTrue(all(isinstance(line, str) for line in lines))

    def test_city_forecasts_cover_expected_cities(self):
        blob = "\n".join(dict(self._sections("1988-12-15"))["U.S. City Forecasts"])
        for city in ("NEW YORK", "CHICAGO", "MIAMI", "SEATTLE", "DENVER",
                     "MINNEAPOLIS", "LOS ANGELES", "SAN FRANCISCO",
                     "BOSTON", "WASHINGTON", "ATLANTA", "DALLAS"):
            self.assertIn(city, blob)

    def test_ski_reports_cover_expected_resorts(self):
        blob = "\n".join(dict(self._sections("1988-12-15"))["Ski Reports"])
        for resort in ("VAIL", "ASPEN", "KILLINGTON", "STOWE", "MAMMOTH",
                       "SQUAW VALLEY", "PARK CITY"):
            self.assertIn(resort, blob)
        self.assertIn("Base depth", blob)

    def test_wire_notes_are_short_bullets(self):
        lines = dict(self._sections("1988-12-15"))["Weather Wire Notes"]
        bullets = [line for line in lines if line.startswith("* ")]
        self.assertGreaterEqual(len(bullets), 2)

    def test_titles_and_day_stamp_in_header_lines(self):
        sections = self._sections("1988-12-15")
        blob = "\n".join(line for _title, lines in sections for line in lines)
        self.assertIn("1988", blob)


class WeatherDeterminismTest(unittest.TestCase):
    def _call(self, sim_date):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": sim_date}):
            return cis_weather.weather_service(app=None)

    def test_deterministic_for_fixed_day(self):
        first = self._call("1988-12-15")
        second = self._call("1988-12-15")
        self.assertEqual(first, second)

    def test_days_can_vary(self):
        one = self._call("1988-12-15")
        one_flat = tuple(line for _t, lines in one for line in lines)
        varied = any(
            one_flat != tuple(line for _t, lines in self._call(f"1988-12-{d:02d}")
                              for line in lines)
            for d in (16, 17, 18, 19, 20, 21)
        )
        self.assertTrue(varied, "forecasts did not vary across simulated days")

    def test_explicit_day_parameter_matches_env_day(self):
        from datetime import date
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            via_env = cis_weather.weather_menu_lines()
        via_arg = cis_weather.weather_menu_lines(day=date(1988, 12, 15))
        self.assertEqual(via_env, via_arg)


class WeatherAnachronismTest(unittest.TestCase):
    def test_no_banned_terms(self):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            sections = cis_weather.weather_service(app=None)
        blob = "\n".join(line for _title, lines in sections for line in lines)
        lowered = blob.lower()
        for term in BANNED_TERMS:
            with self.subTest(term=term):
                self.assertNotIn(term, lowered, f"anachronism found: {term!r}")

    def test_no_exact_historical_record_claims(self):
        with patch.dict("os.environ", {"CIS_SIMULATION_DATE": "1988-12-15"}):
            sections = cis_weather.weather_service(app=None)
        blob = "\n".join(line for _title, lines in sections for line in lines)
        lowered = blob.lower()
        for phrase in ("official record", "recorded in 1988", "national weather service confirms"):
            self.assertNotIn(phrase, lowered)


class WeatherHelperFunctionsTest(unittest.TestCase):
    def test_helpers_return_line_lists(self):
        from datetime import date
        day = date(1988, 12, 15)
        for helper in (cis_weather.city_forecast_lines,
                       cis_weather.ski_report_lines,
                       cis_weather.wire_note_lines):
            lines = helper(day)
            self.assertIsInstance(lines, list)
            self.assertTrue(any(line.strip() for line in lines))


import io
import re
import unittest
from contextlib import redirect_stdout
from datetime import date
from unittest.mock import patch

import cis_crossword
from cis_crossword import (
    PUZZLES,
    check_answer,
    fill_slot,
    grid_rows,
    is_solved,
    new_state,
    play,
    puzzle_for_day,
    render_clues,
    render_grid,
    slots,
)


class GeometryTests(unittest.TestCase):
    def test_seven_puzzles_one_per_weekday(self):
        self.assertEqual(len(PUZZLES), 7)

    def test_grid_is_7x7(self):
        for puzzle in PUZZLES:
            rows = grid_rows(puzzle)
            self.assertEqual(len(rows), 7)
            for row in rows:
                self.assertEqual(len(row), 7)
                self.assertTrue(row.isalpha(), row)

    def test_slot_count(self):
        for puzzle in PUZZLES:
            across = [s for s in slots(puzzle) if s[0] == "A"]
            down = [s for s in slots(puzzle) if s[0] == "D"]
            self.assertEqual(len(across), 3)
            self.assertEqual(len(down), 14)

    def test_answer_lengths_match_slots(self):
        for puzzle in PUZZLES:
            for direction, number, answer, _clue, cells in slots(puzzle):
                self.assertEqual(len(answer), len(cells),
                                 f"{direction}{number} {answer}")

    def test_across_rows_match_grid(self):
        for puzzle in PUZZLES:
            rows = grid_rows(puzzle)
            self.assertEqual(rows[0], puzzle["across"][1][0])
            self.assertEqual(rows[3], puzzle["across"][8][0])
            self.assertEqual(rows[6], puzzle["across"][16][0])

    def test_down_words_interlock_with_across(self):
        for puzzle in PUZZLES:
            rows = grid_rows(puzzle)
            for direction, number, answer, _clue, cells in slots(puzzle):
                if direction != "D":
                    continue
                word = "".join(rows[r][c] for r, c in cells)
                self.assertEqual(word, answer,
                                 f"D{number} {answer} vs grid {word}")

    def test_all_answers_distinct_within_puzzle(self):
        for puzzle in PUZZLES:
            answers = [s[2] for s in slots(puzzle)]
            self.assertEqual(len(set(answers)), len(answers))

    def test_expected_clue_numbers(self):
        for puzzle in PUZZLES:
            across_nums = sorted(s[1] for s in slots(puzzle) if s[0] == "A")
            down_nums = sorted(s[1] for s in slots(puzzle) if s[0] == "D")
            self.assertEqual(across_nums, [1, 8, 16])
            self.assertEqual(down_nums, list(range(1, 8)) + list(range(9, 16)))


class RotationTests(unittest.TestCase):
    def test_deterministic_for_same_day(self):
        day = date(1988, 12, 25)
        self.assertIs(puzzle_for_day(day), puzzle_for_day(day))

    def test_weekday_mapping(self):
        # 1988-12-19 was a Monday -> puzzle index 0
        monday = puzzle_for_day(date(1988, 12, 19))
        self.assertEqual(monday["weekday"], "Monday")
        sunday = puzzle_for_day(date(1988, 12, 25))
        self.assertEqual(sunday["weekday"], "Sunday")

    def test_rotates_across_week(self):
        seen = {puzzle_for_day(date(1988, 12, 19 + i))["weekday"]
                for i in range(7)}
        self.assertEqual(len(seen), 7)

    def test_repeats_next_week(self):
        self.assertIs(puzzle_for_day(date(1988, 12, 19)),
                      puzzle_for_day(date(1988, 12, 26)))

    def test_default_uses_simulation_day(self):
        # Must not raise even with the lazy cis_dynamic import.
        puzzle = puzzle_for_day()
        self.assertIn(puzzle, PUZZLES)


class CheckAnswerTests(unittest.TestCase):
    def setUp(self):
        self.puzzle = puzzle_for_day(date(1988, 12, 19))  # Monday

    def test_accepts_correct(self):
        self.assertTrue(check_answer(self.puzzle, 1, "A", "RAINMAN"))

    def test_case_insensitive(self):
        self.assertTrue(check_answer(self.puzzle, 1, "A", "rainman"))
        self.assertTrue(check_answer(self.puzzle, 1, "A", "RainMan"))

    def test_direction_case_insensitive(self):
        self.assertTrue(check_answer(self.puzzle, 3, "d", "IRS"))

    def test_rejects_wrong(self):
        self.assertFalse(check_answer(self.puzzle, 1, "A", "DIEHARD"))

    def test_rejects_wrong_length(self):
        self.assertFalse(check_answer(self.puzzle, 1, "A", "RAIN"))

    def test_rejects_unknown_slot(self):
        self.assertFalse(check_answer(self.puzzle, 99, "A", "RAINMAN"))
        self.assertFalse(check_answer(self.puzzle, 8, "D", "DIEHARD"))

    def test_strips_spaces(self):
        self.assertTrue(check_answer(self.puzzle, 1, "A", "  rainman  "))


class SolvedTests(unittest.TestCase):
    def setUp(self):
        self.puzzle = puzzle_for_day(date(1988, 12, 19))
        self.state = new_state(self.puzzle)

    def test_fresh_state_not_solved(self):
        self.assertFalse(is_solved(self.state, self.puzzle))

    def test_partial_not_solved(self):
        self.assertTrue(fill_slot(self.state, self.puzzle, 1, "A", "RAINMAN"))
        self.assertFalse(is_solved(self.state, self.puzzle))

    def test_full_solve(self):
        for direction, number, answer, _clue, _cells in slots(self.puzzle):
            self.assertTrue(fill_slot(self.state, self.puzzle, number,
                                       direction, answer))
        self.assertTrue(is_solved(self.state, self.puzzle))

    def test_fill_slot_rejects_wrong(self):
        self.assertFalse(fill_slot(self.state, self.puzzle, 1, "A", "DIEHARD"))
        self.assertFalse(is_solved(self.state, self.puzzle))

    def test_wrong_fill_does_not_corrupt(self):
        fill_slot(self.state, self.puzzle, 1, "A", "DIEHARD")
        self.assertEqual(self.state["entries"][("A", 1)], [None] * 7)


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.puzzle = puzzle_for_day(date(1988, 12, 19))
        self.state = new_state(self.puzzle)

    def test_grid_has_seven_rows(self):
        text = render_grid(self.puzzle, self.state)
        row_lines = [ln for ln in text.splitlines()
                     if re.match(r" [1-7] \|", ln)]
        self.assertEqual(len(row_lines), 7)

    def test_grid_contains_clue_numbers(self):
        text = render_grid(self.puzzle, self.state)
        for number in (1, 7, 8, 9, 15, 16):
            self.assertIn(str(number), text)

    def test_grid_shows_blanks_when_empty(self):
        self.assertIn(".", render_grid(self.puzzle, self.state))

    def test_grid_shows_filled_letters(self):
        fill_slot(self.state, self.puzzle, 1, "A", "RAINMAN")
        text = render_grid(self.puzzle, self.state)
        self.assertIn("R", text)
        # the solved across word appears left to right in row 1
        row1 = [ln for ln in text.splitlines() if ln.startswith(" 1 |")][0]
        letters_only = re.sub(r"[^A-Z.]", "", row1)
        self.assertEqual(letters_only, "RAINMAN")

    def test_clues_list_all_entries(self):
        text = render_clues(self.puzzle)
        self.assertIn("ACROSS", text)
        self.assertIn("DOWN", text)
        for _d, number, _a, clue, _c in slots(self.puzzle):
            self.assertIn(clue, text)


class EraSafetyTests(unittest.TestCase):
    # Terms that did not exist (or not in this sense) in December 1988.
    BANNED = {
        "IPHONE", "GOOGLE", "INTERNET", "WEBSITE", "WEBLOG", "BLOG",
        "WIFI", "BLUETOOTH", "DVD", "MP3", "IPOD", "XBOX", "PLAYSTATION",
        "GAMEBOY", "TEXTING", "SELFIE", "EMOJI", "MEME", "PODCAST",
        "STREAMING", "NETFLIX", "FACEBOOK", "TWITTER", "YOUTUBE", "HASHTAG",
        "SMARTPHONE", "TABLET", "DRONE", "BITCOIN", "COVID", "BATMAN",
        "SEINFELD", "SIMPSONS", "FRIENDS",
    }

    def test_no_post_1988_terms(self):
        for puzzle in PUZZLES:
            for _d, number, answer, clue, _cells in slots(puzzle):
                words = set(re.findall(r"[A-Z]+", (answer + " " + clue).upper()))
                bad = words & self.BANNED
                self.assertEqual(bad, set(),
                                 f"{puzzle['weekday']} clue {number}: {bad}")

    def test_all_answers_alpha(self):
        for puzzle in PUZZLES:
            for _d, _n, answer, _c, _cells in slots(puzzle):
                self.assertTrue(answer.isalpha() and answer.isupper(), answer)


class PlayLoopTests(unittest.TestCase):
    def _run(self, inputs, day):
        puzzle = puzzle_for_day(day)

        class CaptureApp:
            def __init__(self):
                self.lines = []

            def ansi_scroll(self, text, delay=0.01):
                self.lines.append(str(text))
                return True

        app = CaptureApp()
        with patch("builtins.input", side_effect=inputs + ["QUIT"]):
            with patch("cis_crossword.puzzle_for_day", return_value=puzzle):
                play(app)
        return "\n".join(app.lines), puzzle

    def test_quit_immediately(self):
        out, _ = self._run(["QUIT"], date(1988, 12, 19))
        self.assertIn("DAILY CROSSWORD", out)
        self.assertIn("abandoned", out)

    def test_bad_input_is_robust(self):
        out, _ = self._run(["", "nonsense", "A99 ZZ", "A1", "HELP",
                            "GRID", "CLUES", "QUIT"], date(1988, 12, 19))
        self.assertIn("HELP", out)
        self.assertNotIn("Traceback", out)

    def test_wrong_guess_rejected(self):
        out, _ = self._run(["A1 DIEHARD", "QUIT"], date(1988, 12, 19))
        self.assertIn("Not quite", out)

    def test_wrong_length_message(self):
        out, _ = self._run(["A1 RAIN", "QUIT"], date(1988, 12, 19))
        self.assertIn("7 letters", out)

    def test_full_solve_congratulates(self):
        puzzle = puzzle_for_day(date(1988, 12, 19))
        commands = ["%s%d %s" % (d, n, a)
                    for d, n, a, _c, _cells in slots(puzzle)]
        out, _ = self._run(commands, date(1988, 12, 19))
        self.assertIn("CONGRATULATIONS", out)
        self.assertIn("17 moves", out)


"""Unit tests for the Books & Magazines module (cis_books)."""

import re
import unittest
from datetime import date

import cis_books


class BooksServiceTest(unittest.TestCase):
    def test_books_service_returns_expected_sections(self):
        sections = cis_books.books_service(app=None)
        self.assertIsInstance(sections, list)
        titles = [title for title, _lines in sections]
        self.assertEqual(
            titles,
            [
                "Hardcover Fiction Bestsellers",
                "Hardcover Nonfiction Bestsellers",
                "This Month's Magazines",
                "From the Review Desk",
            ],
        )

    def test_each_section_has_non_empty_lines(self):
        for title, lines in cis_books.books_service(app=None):
            self.assertIsInstance(lines, list, title)
            self.assertGreater(len(lines), 0, title)
            for line in lines:
                self.assertIsInstance(line, str, title)
        all_text = "\n".join(
            line for _title, lines in cis_books.books_service(app=None) for line in lines
        )
        self.assertIn("The Cardinal of the Kremlin", all_text)
        self.assertIn("A Brief History of Time", all_text)
        self.assertIn("TIME", all_text)

    def test_books_menu_lines_accepts_explicit_day(self):
        sections = cis_books.books_menu_lines(day=date(1988, 12, 25))
        self.assertEqual(len(sections), 4)
        # Deterministic: same day gives same editor's pick line.
        again = cis_books.books_menu_lines(day=date(1988, 12, 25))
        self.assertEqual(sections, again)


class SeedFilesTest(unittest.TestCase):
    REQUIRED_KEYS = {
        "content_id",
        "library",
        "name",
        "description",
        "date",
        "version",
        "system",
        "instructions",
        "history",
        "reviews",
        "content",
    }

    def test_seed_files_count_and_shape(self):
        files = cis_books.seed_files()
        self.assertTrue(6 <= len(files) <= 10, len(files))
        for entry in files:
            self.assertTrue(
                self.REQUIRED_KEYS.issubset(entry.keys()),
                f"missing keys in {entry.get('content_id')}",
            )
            for key in self.REQUIRED_KEYS:
                if key == "reviews":
                    # Reviews may be an empty list for freshly seeded issues;
                    # only the key's presence is required.
                    continue
                self.assertTrue(entry[key], f"empty {key} in {entry.get('content_id')}")

    def test_seed_files_unique_content_ids(self):
        files = cis_books.seed_files()
        ids = [entry["content_id"] for entry in files]
        self.assertEqual(len(ids), len(set(ids)))
        for cid in ids:
            self.assertTrue(cid.startswith("community-file:"))

    def test_seed_files_use_known_library(self):
        files = cis_books.seed_files()
        for entry in files:
            self.assertEqual(entry["library"], "dos_library")

    def test_seed_files_dates_are_december_1988(self):
        files = cis_books.seed_files()
        for entry in files:
            self.assertRegex(
                entry["date"], r"^12/\d{2}/88$", entry["content_id"]
            )
            day = int(entry["date"].split("/")[1])
            self.assertTrue(1 <= day <= 31)


class EraSafetyTest(unittest.TestCase):
    POST_1988_TITLES = [
        "The Dark Half",
        "The Russia House",
        "The Stand",  # miniseries tie-in era wording aside, listed as a guard
        "Jurassic Park",
        "The Firm",
        "Schindler's List",
    ]
    FORBIDDEN_YEAR = re.compile(r"\b(19\d{2})\b")

    def _all_output_text(self):
        texts = []
        for _title, lines in cis_books.books_service(app=None):
            texts.extend(lines)
        for entry in cis_books.seed_files():
            texts.append(str(entry["content"]))
            texts.append(str(entry["description"]))
        return "\n".join(texts)

    def test_no_year_after_1988(self):
        for match in self.FORBIDDEN_YEAR.finditer(self._all_output_text()):
            self.assertLessEqual(int(match.group(1)), 1988)

    def test_no_known_post_1988_titles(self):
        text = self._all_output_text()
        for title in self.POST_1988_TITLES:
            if title == "The Stand":
                continue  # guard placeholder; the book itself is 1978
            self.assertNotIn(title, text)

    def test_no_apostrophe_year_beyond_88(self):
        text = self._all_output_text()
        for match in re.finditer(r"'(\d{2})\b", text):
            self.assertLessEqual(int(match.group(1)), 88)

class ContentPack3WiringTests(unittest.TestCase):
    def test_forum_catalog_entries(self):
        self.assertIn("tech", compuserve.FORUM_CATALOG)
        sections = compuserve.FORUM_CATALOG["tech"]["sections"]
        self.assertEqual(sections, cis_tech.SECTIONS)

    def test_forum_choices(self):
        self.assertEqual(compuserve.FORUM_CHOICES["14"], "tech")

    def test_screens_options(self):
        screens = json.loads((REPO_ROOT / "screens.json").read_text(encoding="utf-8"))
        self.assertEqual(screens["forums"]["options"]["14"], "Tech Talk Forum")
        self.assertEqual(screens["news"]["options"]["10"], "Weather Wire")
        self.assertEqual(screens["news"]["options"]["11"], "Books & Magazines")
        self.assertEqual(screens["games"]["options"]["8"], "Daily Crossword")

    def test_go_commands(self):
        self.assertEqual(compuserve.resolve_go_destination("TECH"), "tech")
        # GO WEATHER intentionally still reaches the pre-existing live wire.
        self.assertEqual(compuserve.resolve_go_destination("WEATHER"), "weather")
        self.assertEqual(compuserve.resolve_go_destination("BOOKS"), "books")
        self.assertEqual(compuserve.resolve_go_destination("CROSSWORD"), "crossword")

    def test_seed_messages_in_computer_communities(self):
        pack = json.loads((REPO_ROOT / "computer_communities.json").read_text(encoding="utf-8"))
        tech_posts = [m for m in pack["messages"]
                      if m["content_id"].startswith("tech-1988-")]
        self.assertEqual(len(tech_posts), len(cis_tech.SEED_POSTS))
        valid = {sec_id for sec_id, _ in cis_tech.SECTIONS.values()}
        for message in tech_posts:
            self.assertIn(message["section"], valid, message["content_id"])

    def test_merge_forums_installs_new_sections(self):
        merged = cis_communities.merge_forums({})
        self.assertTrue(merged.get("tech_pc"), "tech_pc")
        for message in merged["tech_pc"]:
            self.assertIn("id", message)
            self.assertIn("parent_id", message)

    def test_seed_files_in_computer_communities(self):
        pack = json.loads((REPO_ROOT / "computer_communities.json").read_text(encoding="utf-8"))
        mag_files = [f for f in pack["files"]
                     if f["content_id"] in {e["content_id"] for e in cis_books.seed_files()}]
        self.assertEqual(len(mag_files), len(cis_books.seed_files()))
        for record in mag_files:
            self.assertTrue(record["date"].endswith("/88"), record["content_id"])

    def test_news_menu_dispatches_weather_and_books(self):
        with patch.object(compuserve, 'session_state', SessionState()), \
                patch.object(compuserve, 'show_screen'), \
                patch.object(compuserve, 'weather_menu') as weather, \
                patch.object(compuserve, 'books_menu') as books, \
                patch.object(compuserve, 'show_logout_summary'), \
                patch('builtins.input', side_effect=['GO NEWSSIM', '10', 'M', 'GO NEWSSIM', '11', 'M', 'OFF']):
            compuserve.navigate()
        weather.assert_called_once_with()
        books.assert_called_once_with()

    def test_games_menu_dispatches_crossword(self):
        with patch.object(cis_crossword, 'play') as play:
            compuserve.games_service("8")
        play.assert_called_once_with(compuserve)



# --- Content pack 4: Classic Games Arcade (cis_arcade) ---

"""Unit tests for cis_arcade (Classic Games Arcade).

Core game logic is tested through the engine classes with seeded RNGs;
no interactive I/O or real runtime files are touched.
"""
import random
import unittest
from unittest.mock import patch

import cis_arcade
from cis_arcade import (
    ARCADE_MENU, RECORDS_KEY, TUNNELS,
    WumpusGame, HamurabiGame, StarTrekGame, BlackjackGame,
    hand_value, is_blackjack, make_shoe, dealer_play, settle,
    arcade_records_lines, record_play,
)


class ArcadeFakeDynamic:
    """In-memory stand-in for app.cis_dynamic."""

    def __init__(self):
        self.state = {}

    def load_state(self, app):
        return self.state

    def save_state(self, app, state):
        self.state = state


class ArcadeFakeApp:
    def __init__(self, user_id="T100"):
        self.current_user_id = user_id
        self.cis_dynamic = ArcadeFakeDynamic()
        self.output_lines = []

    def ansi_scroll(self, text, delay=0.01):
        self.output_lines.append(str(text))
        return True


# ---------------------------------------------------------------------------
# Wumpus
# ---------------------------------------------------------------------------

class TestWumpusGraph(unittest.TestCase):
    def test_twenty_rooms_three_tunnels_each(self):
        self.assertEqual(len(TUNNELS), 20)
        for room, links in TUNNELS.items():
            self.assertEqual(len(links), 3, room)

    def test_tunnels_are_symmetric(self):
        for room, links in TUNNELS.items():
            for link in links:
                self.assertIn(room, TUNNELS[link])


class TestWumpusGame(unittest.TestCase):
    def setUp(self):
        self.game = WumpusGame(rng=random.Random(0))
        self.game.reset()

    def test_reset_places_hazards_away_from_start(self):
        self.assertNotIn(1, self.game.pits | self.game.bats)
        self.assertNotEqual(self.game.wumpus, 1)
        self.assertNotIn(self.game.wumpus, set(TUNNELS[1]))
        all_hazards = {self.game.wumpus} | self.game.pits | self.game.bats
        self.assertEqual(len(all_hazards), 5)  # wumpus + 2 pits + 2 bats, distinct
        self.assertEqual(self.game.arrows, 5)
        self.assertEqual(self.game.player, 1)

    def test_warnings_detect_adjacent_hazards(self):
        self.game.wumpus = 2
        self.game.pits = {5}
        self.game.bats = {8}
        warns = self.game.warnings(1)
        self.assertIn("I SMELL A WUMPUS!", warns)
        self.assertIn("I FEEL A DRAFT!", warns)
        self.assertIn("BATS NEARBY!", warns)

    def test_warnings_quiet_in_safe_room(self):
        self.game.wumpus = 20
        self.game.pits = {19, 18}
        self.game.bats = {17, 16}
        self.assertEqual(self.game.warnings(1), [])

    def test_move_to_neighbor(self):
        self.game.wumpus = 20
        self.game.pits = set()
        self.game.bats = set()
        result = self.game.move_to(2)
        self.assertEqual(result, "MOVED")
        self.assertEqual(self.game.player, 2)
        self.assertEqual(self.game.moves, 1)

    def test_move_to_non_neighbor_rejected(self):
        self.assertEqual(self.game.move_to(20), "NO_TUNNEL")
        self.assertEqual(self.game.player, 1)

    def test_entering_wumpus_room_kills(self):
        self.game.wumpus = 2
        self.game.pits = set()
        self.game.bats = set()
        self.assertEqual(self.game.move_to(2), "EATEN")
        self.assertFalse(self.game.alive)

    def test_entering_pit_kills(self):
        self.game.pits = {2}
        self.game.bats = set()
        self.game.wumpus = 20
        self.assertEqual(self.game.move_to(2), "PIT")
        self.assertFalse(self.game.alive)

    def test_bats_carry_player_away(self):
        self.game.bats = {2}
        self.game.pits = set()
        self.game.wumpus = 20
        result = self.game.move_to(2)
        self.assertIn(result, ("BATS", "EATEN", "PIT"))
        self.assertNotEqual(self.game.player, 2)

    def test_shooting_wumpus_wins(self):
        self.game.wumpus = 2
        self.game.pits = set()
        self.game.bats = set()
        self.assertEqual(self.game.fire([2]), "KILL")
        self.assertTrue(self.game.won)
        self.assertEqual(self.game.arrows, 4)

    def test_arrow_that_returns_kills_player(self):
        self.game.wumpus = 8  # not on the path
        self.game.pits = set()
        self.game.bats = set()
        self.assertEqual(self.game.fire([2, 1]), "SUICIDE")
        self.assertFalse(self.game.alive)

    def test_miss_consumes_arrow_and_wakes_wumpus(self):
        self.game.wumpus = 20
        self.game.pits = set()
        self.game.bats = set()
        result = self.game.fire([2, 3])
        self.assertIn(result, ("MISS", "MISS_MOVED", "EATEN"))
        self.assertEqual(self.game.arrows, 4)
        self.assertTrue(self.game.wumpus_awake)

    def test_no_arrows_no_shot(self):
        self.game.arrows = 0
        self.assertEqual(self.game.fire([2]), "NO_ARROWS")


# ---------------------------------------------------------------------------
# Hamurabi
# ---------------------------------------------------------------------------

class TestHamurabi(unittest.TestCase):
    def setUp(self):
        self.game = HamurabiGame(rng=random.Random(42))

    def test_starting_position(self):
        self.assertEqual(self.game.population, 100)
        self.assertEqual(self.game.grain, 2800)
        self.assertEqual(self.game.land, 1000)
        self.assertEqual(self.game.year, 0)

    def test_validate_rejects_impossible_orders(self):
        self.assertIsNotNone(self.game.validate(buy=100000, sell=0, feed=0, plant=0))
        self.assertIsNotNone(self.game.validate(buy=0, sell=2000, feed=0, plant=0))
        self.assertIsNotNone(self.game.validate(buy=0, sell=0, feed=999999, plant=0))
        self.assertIsNotNone(self.game.validate(buy=0, sell=0, feed=0, plant=2000))
        self.assertIsNotNone(self.game.validate(buy=-1, sell=0, feed=0, plant=0))
        self.assertIsNotNone(self.game.validate(buy=1, sell=1, feed=0, plant=0))

    def test_validate_accepts_sane_orders(self):
        self.assertIsNone(self.game.validate(buy=10, sell=0, feed=2000, plant=100))

    def test_year_resolution_feeds_and_harvests(self):
        report = self.game.play_year(buy=0, sell=0, feed=2000, plant=100)
        self.assertTrue(report["ok"])
        self.assertEqual(report["year"], 1)
        self.assertEqual(report["starved"], 0)
        # grain: 2800 - 2000 feed - 50 seed + harvest(100 * yield 1..6)
        self.assertEqual(self.game.grain, 800 - 50 + report["harvest"])
        self.assertGreater(self.game.population, 0)

    def test_total_starvation_impeaches(self):
        report = self.game.play_year(buy=0, sell=0, feed=0, plant=0)
        self.assertTrue(report["ok"])
        self.assertEqual(report["starved"], 100)
        self.assertTrue(report["impeached"])
        self.assertTrue(report["over"])

    def test_ten_years_ends_reign(self):
        game = HamurabiGame(rng=random.Random(0))
        for _ in range(40):
            if game.over:
                break
            # Conservative governor: sell land to cover any feeding shortfall,
            # keep a food reserve, plant the surplus, feed everyone.
            price = game.price
            need = 20 * game.population
            sell = 0
            if game.grain < need:
                sell = min(game.land, (need - game.grain + price - 1) // price)
            avail = game.grain + sell * price
            surplus = avail - need - int(0.75 * need)
            plant = min(10 * game.population, game.land - sell, max(0, surplus) * 2)
            feed = min(need, avail - plant // 2)
            report = game.play_year(buy=0, sell=sell, feed=feed, plant=plant)
            self.assertTrue(report["ok"])
        self.assertTrue(game.over)
        self.assertEqual(game.year, 10)
        self.assertFalse(game.impeached)

    def test_final_score_bounded(self):
        score = self.game.final_score()
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)

    def test_impeachment_epitaph(self):
        self.game.impeached = True
        self.assertIn("impeached", self.game.epitaph().lower())


# ---------------------------------------------------------------------------
# Star Trek
# ---------------------------------------------------------------------------

class TestStarTrek(unittest.TestCase):
    def setUp(self):
        self.game = StarTrekGame(rng=random.Random(7))
        self.game.new_mission(klingons=4)

    def test_mission_setup(self):
        self.assertEqual(self.game.klingons_total, 4)
        self.assertEqual(self.game.klingons_left(), 4)
        self.assertEqual(len(self.game.galaxy), 64)
        self.assertEqual(self.game.energy, 3000)
        self.assertEqual(self.game.torpedoes, 10)
        self.assertGreater(self.game.deadline, self.game.stardate)

    def test_nav_costs_energy_and_time(self):
        self.game.enterprise = (0, 0)
        for q in self.game.galaxy.values():
            q["klingons"] = []
        self.game.galaxy[(1, 1)]["klingons"] = []
        log = self.game.nav(1, 1)
        self.assertEqual(self.game.enterprise, (1, 1))
        self.assertEqual(self.game.energy, 3000 - 2 * 40)
        self.assertTrue(any("Warp" in line for line in log))

    def test_nav_rejects_bad_coordinates(self):
        log = self.game.nav(9, 9)
        self.assertTrue(any("out of range" in line for line in log))
        self.assertEqual(self.game.enterprise, self.game.enterprise)

    def test_phasers_destroy_klingon(self):
        self.game.enterprise = (0, 0)
        here = self.game.galaxy[(0, 0)]
        here["klingons"] = [50]
        here["starbase"] = False
        self.game.shields = 3000
        log = self.game.phasers(3000)
        self.assertEqual(here["klingons"], [])
        self.assertTrue(any("destroyed" in line.lower() for line in log))

    def test_phasers_need_target(self):
        self.game.enterprise = (0, 0)
        self.game.galaxy[(0, 0)]["klingons"] = []
        log = self.game.phasers(100)
        self.assertTrue(any("No Klingons" in line for line in log))

    def test_torpedo_out_of_range_fizzles(self):
        self.game.enterprise = (0, 0)
        before = self.game.torpedoes
        log = self.game.torpedo(7, 7)
        self.assertEqual(self.game.torpedoes, before - 1)
        self.assertTrue(any("fizzles" in line for line in log))

    def test_torpedo_kills_adjacent_klingon(self):
        game = StarTrekGame(rng=random.Random(1))
        game.new_mission(klingons=1)
        for q in game.galaxy.values():
            q["klingons"] = []
        game.enterprise = (3, 3)
        game.galaxy[(3, 4)]["klingons"] = [200]
        game.klingons_total = 1
        for _ in range(9):
            if game.won:
                break
            game.torpedo(3, 4)
        self.assertEqual(game.galaxy[(3, 4)]["klingons"], [])
        self.assertTrue(game.won)

    def test_shields_transfer(self):
        self.assertEqual(self.game.shields_cmd(500), ["Shields now 500; energy 2500."])
        self.assertEqual(self.game.shields_cmd(-200), ["Shields now 300; energy 2700."])

    def test_shields_reject_overdraft(self):
        self.assertTrue(any("Insufficient" in line for line in self.game.shields_cmd(99999)))
        self.assertTrue(any("Only" in line for line in self.game.shields_cmd(-1)))

    def test_dock_repairs_and_refuels(self):
        self.game.enterprise = (0, 0)
        self.game.galaxy[(0, 0)]["starbase"] = True
        self.game.galaxy[(0, 0)]["klingons"] = []
        self.game.energy = 100
        self.game.shields = 5
        self.game.torpedoes = 1
        self.game.damaged = {"PHA": 2}
        log = self.game.dock()
        self.assertEqual(self.game.energy, 3000)
        self.assertEqual(self.game.torpedoes, 10)
        self.assertEqual(self.game.damaged, {})
        self.assertTrue(any("Docked" in line for line in log))

    def test_klingon_attack_hurts(self):
        self.game.enterprise = (0, 0)
        here = self.game.galaxy[(0, 0)]
        here["klingons"] = [300]
        self.game.shields = 0
        energy_before = self.game.energy
        log = self.game._klingon_attack()
        self.assertLess(self.game.energy, energy_before)
        self.assertTrue(any("Klingon fires" in line for line in log))

    def test_victory_when_all_klingons_gone(self):
        for q in self.game.galaxy.values():
            q["klingons"] = []
        log = []
        self.game._check_victory(log)
        self.assertTrue(self.game.won)
        self.assertTrue(self.game.over)
        self.assertTrue(any("MISSION ACCOMPLISHED" in line for line in log))

    def test_scans_return_lines(self):
        srs = self.game.srs()
        lrs = self.game.lrs()
        self.assertTrue(srs[0].startswith("--- SHORT RANGE SCAN ---"))
        self.assertTrue(lrs[0].startswith("--- LONG RANGE SCAN ---"))
        self.assertEqual(len(lrs), 5)


# ---------------------------------------------------------------------------
# Blackjack
# ---------------------------------------------------------------------------

class TestBlackjackMath(unittest.TestCase):
    def test_hand_values(self):
        self.assertEqual(hand_value(["AS", "KD"]), (21, True))
        self.assertEqual(hand_value(["AS", "9H"]), (20, True))
        self.assertEqual(hand_value(["AS", "9H", "AD"]), (21, True))
        self.assertEqual(hand_value(["9H", "7D"]), (16, False))
        self.assertEqual(hand_value(["10H", "6D", "7C"]), (23, False))
        self.assertEqual(hand_value(["AC", "AC", "9H"]), (21, True))

    def test_blackjack_detection(self):
        self.assertTrue(is_blackjack(["AS", "KD"]))
        self.assertFalse(is_blackjack(["AS", "9H", "AD"]))
        self.assertFalse(is_blackjack(["10H", "7D"]))

    def test_shoe_size(self):
        self.assertEqual(len(make_shoe(4, random.Random(0))), 208)
        self.assertEqual(len(make_shoe(1, random.Random(0))), 52)

    def test_dealer_hits_to_17(self):
        shoe = ["2H", "5C"]  # pop() takes from the end
        final = dealer_play(shoe, ["10H", "6D"])
        self.assertEqual(hand_value(final)[0], 21)

    def test_dealer_stands_on_17(self):
        shoe = ["5C"]
        final = dealer_play(shoe, ["10H", "7D"])
        self.assertEqual(len(final), 2)
        self.assertEqual(shoe, ["5C"])  # untouched

    def test_settle_outcomes(self):
        self.assertEqual(settle(["AS", "KD"], ["10H", "7D"], 100), ("blackjack", 150))
        self.assertEqual(settle(["10H", "7D"], ["10H", "7D"], 100), ("push", 0))
        self.assertEqual(settle(["10H", "9D"], ["10H", "6D"], 100), ("win", 100))
        self.assertEqual(settle(["10H", "6D"], ["10H", "9D"], 100), ("lose", -100))
        self.assertEqual(settle(["10H", "6D", "9C"], ["10H", "7D"], 100), ("bust", -100))
        self.assertEqual(settle(["10H", "7D"], ["10H", "6D", "9C"], 100), ("dealer_bust", 100))
        self.assertEqual(settle(["AS", "KD"], ["AC", "QH"], 100), ("push", 0))


class TestBlackjackGame(unittest.TestCase):
    def test_play_hand_stand(self):
        game = BlackjackGame(rng=random.Random(1))
        player, dealer, outcome, delta = game.play_hand(100, ["S"])
        self.assertEqual(game.hands, 1)
        self.assertIn(outcome, ("win", "lose", "push", "blackjack", "bust", "dealer_bust"))
        self.assertEqual(game.chips, 500 + delta)

    def test_chips_run_out_records_session(self):
        app = ArcadeFakeApp()
        game = BlackjackGame(rng=random.Random(1), app=app, chips=10)
        game.chips = 0
        game._finish_session()
        rec = app.cis_dynamic.state[RECORDS_KEY]["T100"]["blackjack"]
        self.assertEqual(rec["plays"], 1)
        self.assertTrue(game._recorded)


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------

class TestRecords(unittest.TestCase):
    def test_record_play_persists_and_reports(self):
        app = ArcadeFakeApp()
        line = record_play(app, "T100", "wumpus", True, best=4, best_note="arrows left")
        self.assertIn("1 wins in 1 games", line)
        entry = app.cis_dynamic.state[RECORDS_KEY]["T100"]["wumpus"]
        self.assertEqual(entry, {"plays": 1, "wins": 1, "best": 4, "best_note": "arrows left"})

    def test_record_play_offline_without_app(self):
        self.assertIn("offline", record_play(None, "GUEST", "wumpus", True))

    def test_wumpus_win_records_once(self):
        app = ArcadeFakeApp()
        game = WumpusGame(rng=random.Random(0), app=app, user_id="T100")
        game.wumpus = 2
        game.pits = set()
        game.bats = set()
        self.assertEqual(game.fire([2]), "KILL")
        entry = app.cis_dynamic.state[RECORDS_KEY]["T100"]["wumpus"]
        self.assertEqual(entry["plays"], 1)
        self.assertEqual(entry["wins"], 1)
        self.assertEqual(entry["best"], 4)
        # further actions do not double-record
        game.fire([2])
        self.assertEqual(app.cis_dynamic.state[RECORDS_KEY]["T100"]["wumpus"]["plays"], 1)

    def test_arcade_records_lines_format(self):
        state = {RECORDS_KEY: {"T100": {
            "wumpus": {"plays": 3, "wins": 1, "best": 4, "best_note": "arrows left"},
            "hamurabi": {"plays": 2, "wins": 2, "best": 87, "best_note": "score"},
            "startrek": {"plays": 1, "wins": 0, "best": 0, "best_note": ""},
            "blackjack": {"plays": 10, "wins": 6, "best": 900, "best_note": "chips"},
        }}}
        lines = arcade_records_lines(state, "T100")
        self.assertEqual(len(lines), 6)
        self.assertTrue(lines[0].startswith("ARCADE WUMPUS"))
        self.assertIn("WINS 1", lines[0])
        self.assertIn("4 best arrows left", lines[0])
        self.assertTrue(lines[3].startswith("ARCADE BLACKJACK"))
        self.assertIn("HANDS 10", lines[3])
        self.assertTrue(lines[4].startswith("ARCADE ELIZA"))
        self.assertTrue(lines[5].startswith("ARCADE LANDER"))

    def test_arcade_records_lines_empty_state(self):
        lines = arcade_records_lines({}, "NOBODY")
        self.assertEqual(len(lines), 6)
        self.assertIn("---", lines[0])


# ---------------------------------------------------------------------------
# Submenu wiring
# ---------------------------------------------------------------------------

class TestArcadeMenu(unittest.TestCase):
    def test_menu_lists_four_games(self):
        keys = [key for key, _, _ in ARCADE_MENU]
        self.assertEqual(keys, ["1", "2", "3", "4", "5", "6"])
        names = [name for _, name, _ in ARCADE_MENU]
        self.assertEqual(names, ["HUNT THE WUMPUS", "HAMURABI", "SUPER STAR TREK",
                                 "BLACKJACK", "ELIZA", "LUNAR LANDER"])

    def test_menu_text_mentions_all_games(self):
        text = "\n".join(cis_arcade.arcade_menu_text())
        for name in ("HUNT THE WUMPUS", "HAMURABI", "SUPER STAR TREK", "BLACKJACK",
                     "ELIZA", "LUNAR LANDER"):
            self.assertIn(name, text)

    def test_play_quits_on_m(self):
        app = ArcadeFakeApp()
        with patch.object(cis_arcade, "input", return_value="M"):
            cis_arcade.play(app)  # returns without error

    def test_play_rejects_bad_choice_then_quits(self):
        app = ArcadeFakeApp()
        with patch.object(cis_arcade, "input", side_effect=["9", "M"]):
            cis_arcade.play(app)


# --- Content pack 4: Space & Astronomy forum (cis_space) ---

"""Tests for the Space & Astronomy forum content module (cis_space).

Verifies section spec shape, seed post fields, content_id prefix,
December 1988 dates, section/spec consistency, and that
computer_communities.json parses and contains the 16 space posts.
These tests are read-only: they never modify real runtime files.
"""

import json
import os
import re
import unittest

import cis_space

SPACE_REPO_DIR = os.path.dirname(os.path.abspath(__file__))
COMMUNITIES_PATH = os.path.join(SPACE_REPO_DIR, "computer_communities.json")

SPACE_EXPECTED_SECTIONS = {
    "1": ("space_shuttle", "Shuttle & Spaceflight"),
    "2": ("space_deepsky", "Deep Sky Observing"),
    "3": ("space_planets", "Planets & Probes"),
    "4": ("space_scopes", "Amateur Telescopes"),
    "5": ("space_nasa", "NASA & Space News"),
    "6": ("space_starparty", "Star Parties"),
}

SPACE_REQUIRED_FIELDS = {"content_id", "section", "date", "author", "subject", "body", "parent"}


class TestSpaceSectionSpec(unittest.TestCase):
    def test_forum_id_and_title(self):
        self.assertEqual(cis_space.FORUM_ID, "space")
        self.assertEqual(cis_space.FORUM_TITLE, "Space & Astronomy Forum")

    def test_section_spec_shape(self):
        spec = cis_space.section_spec()
        self.assertEqual(len(spec), 6)
        self.assertEqual(spec, SPACE_EXPECTED_SECTIONS)
        for key, (section_id, title) in spec.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(section_id, str)
            self.assertTrue(section_id.startswith("space_"))
            self.assertIsInstance(title, str)
            self.assertTrue(title)

    def test_sections_constant_matches_spec(self):
        self.assertEqual(cis_space.section_spec(), dict(cis_space.SECTIONS))


class TestSpaceSeedPosts(unittest.TestCase):
    def test_sixteen_seed_posts(self):
        self.assertEqual(len(cis_space.SEED_POSTS), 16)
        self.assertEqual(len(cis_space.seed_posts()), 16)

    def test_valid_fields(self):
        for post in cis_space.SEED_POSTS:
            self.assertEqual(set(post.keys()), SPACE_REQUIRED_FIELDS)
            for field in ("content_id", "section", "date", "author", "subject", "body"):
                self.assertIsInstance(post[field], str)
                self.assertTrue(post[field], msg=post["content_id"])
            self.assertIsNone(post["parent"])

    def test_content_id_prefix_and_sequence(self):
        ids = [p["content_id"] for p in cis_space.SEED_POSTS]
        self.assertEqual(len(set(ids)), 16)
        for i, cid in enumerate(ids, start=1):
            self.assertEqual(cid, "space-1988-%03d" % i)

    def test_dates_within_december_1988(self):
        for post in cis_space.SEED_POSTS:
            self.assertRegex(post["date"], r"^12/\d{2}/88$", msg=post["content_id"])
            day = int(post["date"].split("/")[1])
            self.assertGreaterEqual(day, 1)
            self.assertLessEqual(day, 31)

    def test_sections_match_spec(self):
        valid = {sid for sid, _ in cis_space.section_spec().values()}
        for post in cis_space.SEED_POSTS:
            self.assertIn(post["section"], valid, msg=post["content_id"])

    def test_all_sections_have_posts(self):
        used = {p["section"] for p in cis_space.SEED_POSTS}
        valid = {sid for sid, _ in cis_space.section_spec().values()}
        self.assertEqual(used, valid)

    def test_seed_posts_returns_copies(self):
        first = cis_space.seed_posts()
        first[0]["subject"] = "mutated"
        self.assertNotEqual(cis_space.SEED_POSTS[0]["subject"], "mutated")

    def test_varied_authors(self):
        authors = {p["author"] for p in cis_space.SEED_POSTS}
        self.assertGreaterEqual(len(authors), 8)

    def test_no_post_1988_content(self):
        banned = ["Hubble", "1990", "1991", "1992", "internet", "World Wide Web",
                  "digital camera", "digital astro", "CCD camera"]
        for post in cis_space.SEED_POSTS:
            text = post["subject"] + " " + post["body"]
            for word in banned:
                self.assertNotIn(word, text, msg=post["content_id"])


class TestSpaceInCommunitiesJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(COMMUNITIES_PATH, encoding="utf-8") as fh:
            cls.data = json.load(fh)

    def test_top_level_shape(self):
        for key in ("id", "provenance", "forums", "messages", "files"):
            self.assertIn(key, self.data)

    def test_contains_sixteen_space_posts(self):
        msgs = [m for m in self.data["messages"]
                if m["content_id"].startswith("space-")]
        self.assertEqual(len(msgs), 16)

    def test_space_messages_mirror_seed_posts(self):
        by_id = {m["content_id"]: m for m in self.data["messages"]}
        for post in cis_space.SEED_POSTS:
            stored = by_id[post["content_id"]]
            for field in SPACE_REQUIRED_FIELDS:
                self.assertEqual(stored[field], post[field],
                                 msg=(post["content_id"], field))


# --- Content pack 4: Space & Astronomy forum wiring (from WIRING-space.md) ---
class TestSpaceForumContentPack4(unittest.TestCase):
    def test_forum_catalog_wiring(self):
        entry = compuserve.FORUM_CATALOG["space"]
        self.assertEqual(entry["title"], "Space & Astronomy Forum")
        self.assertEqual(entry["sections"], cis_space.section_spec())

    def test_forum_choice_number(self):
        self.assertEqual(compuserve.FORUM_CHOICES["15"], "space")

    def test_go_space(self):
        self.assertEqual(compuserve.resolve_go_destination("SPACE"), "space")

    def test_seed_messages_in_computer_communities(self):
        pack = json.loads((REPO_ROOT / "computer_communities.json").read_text(encoding="utf-8"))
        space_posts = [m for m in pack["messages"]
                       if m["content_id"].startswith("space-1988-")]
        self.assertEqual(len(space_posts), len(cis_space.SEED_POSTS))
        valid = {sec_id for sec_id, _ in cis_space.SECTIONS.values()}
        for message in space_posts:
            self.assertIn(message["section"], valid, message["content_id"])

    def test_all_space_sections_reachable(self):
        for key, (section_id, _title) in cis_space.section_spec().items():
            self.assertIn(key, compuserve.FORUM_CATALOG["space"]["sections"])


# --- Content pack 4: four new time-capsule dates (cis_timecapsule) ---

"""Tests for content pack 4 of the time capsule (four new featured dates).

Run: python3 -m unittest test_timecapsule4
The finisher merges these tests into test_compuserve.py (see
WIRING-timecapsule.md).
"""
import json
import re
import unittest
from datetime import date

import cis_timecapsule

# The four new packs delivered by content pack 4: ISO date -> expected label.
NEW_PACKS = {
    "1981-04-12": "Columbia's first flight",
    "1987-12-08": "INF Treaty signed",
    "1989-10-17": "Loma Prieta earthquake",
    "1990-04-24": "Hubble launched",
}


def pack_text(pack):
    """Every user-visible string in a pack, lowercased, for content scans."""
    return json.dumps(pack).lower()


class TimeCapsulePack4Tests(unittest.TestCase):
    def test_fourteen_featured_dates_in_chronological_order(self):
        featured = cis_timecapsule.FEATURED_DATES
        self.assertEqual(len(featured), 14)
        dates = [when for when, _label in featured]
        self.assertEqual(dates, sorted(dates))
        self.assertEqual(len(set(dates)), 14)
        for when in dates:
            self.assertTrue(cis_timecapsule.MIN_DATE <= when <= cis_timecapsule.MAX_DATE)
        # The four new dates are present with their labels.
        lookup = {when.isoformat(): label for when, label in featured}
        for iso, label in NEW_PACKS.items():
            self.assertEqual(lookup.get(iso), label)

    def test_all_fourteen_packs_pass_strict_validation(self):
        # Re-run the loader so the file on disk is validated exactly the way
        # the import-time check validates it.
        packs = cis_timecapsule._load_packs()
        self.assertEqual(len(packs), 14)
        featured_keys = {when.isoformat() for when, _ in cis_timecapsule.FEATURED_DATES}
        self.assertEqual(set(packs), featured_keys)
        required = {"date", "label", "headlines", "announcements", "cb_topics",
                    "market_notes", "on_this_day"}
        story_fields = {"id", "category", "title", "summary", "published", "source"}
        for key, pack in packs.items():
            with self.subTest(pack=key):
                self.assertTrue(required.issubset(pack))
                self.assertEqual(pack["date"], key)
                # The four new packs carry their menu labels verbatim.
                if key in NEW_PACKS:
                    self.assertEqual(pack["label"], NEW_PACKS[key])
                self.assertTrue(8 <= len(pack["headlines"]) <= 12)
                self.assertTrue(2 <= len(pack["announcements"]) <= 4)
                self.assertTrue(4 <= len(pack["cb_topics"]) <= 6)
                self.assertTrue(0 <= len(pack["market_notes"]) <= 4)
                self.assertTrue(2 <= len(pack["on_this_day"]) <= 3)
                for story in pack["headlines"]:
                    self.assertTrue(story_fields.issubset(story))
                    for field in story_fields:
                        self.assertTrue(story[field], f"empty {field} in {story.get('id')}")

    def test_new_pack_labels_and_dates(self):
        for iso, label in NEW_PACKS.items():
            with self.subTest(pack=iso):
                pack = cis_timecapsule.pack_for(date.fromisoformat(iso))
                self.assertIsNotNone(pack)
                self.assertEqual(pack["date"], iso)
                self.assertEqual(pack["label"], label)
                self.assertEqual(pack["label"], NEW_PACKS[pack["date"]])

    def test_1981_pack_has_no_anachronisms(self):
        # The IBM PC was announced in August 1981; Challenger flew in 1986.
        pack = cis_timecapsule.pack_for(date(1981, 4, 12))
        text = pack_text(pack)
        for term in ("challenger", "ibm pc", "personal computer", "model 5150",
                     "pc-dos", "ms-dos", "mtv", "endeavour"):
            with self.subTest(term=term):
                self.assertNotIn(term, text)

    def test_1987_pack_has_no_berlin_wall_fall_claim(self):
        # The wall stood in December 1987; its fall (November 1989) must not
        # be referenced. The pack keeps the wall out entirely, and this test
        # also rejects any "the wall fell / came down" style claim.
        pack = cis_timecapsule.pack_for(date(1987, 12, 8))
        text = pack_text(pack)
        self.assertNotIn("berlin wall", text)
        self.assertIsNone(re.search(r"\bwall\b.{0,60}\b(fell|falls|falling|came down|"
                                    r"torn down|opened|crossed freely)\b", text))

    def test_1989_pack_has_no_hubble(self):
        # Hubble launched in April 1990, after the October 1989 quake.
        pack = cis_timecapsule.pack_for(date(1989, 10, 17))
        text = pack_text(pack)
        for term in ("hubble", "space telescope"):
            with self.subTest(term=term):
                self.assertNotIn(term, text)

    def test_1990_pack_has_no_desert_storm(self):
        # Desert Storm began in January 1991, after the April 1990 launch.
        pack = cis_timecapsule.pack_for(date(1990, 4, 24))
        text = pack_text(pack)
        for term in ("desert storm", "desert shield", "saddam", "kuwait", "iraq"):
            with self.subTest(term=term):
                self.assertNotIn(term, text)


# --- Content pack 4: magazine department expansion (cis_magazine) ---

"""Tests for content pack 4: new magazine departments (Worker D).

New recurring departments (News Briefs, SysOp Q&A, Letters to the Editor) are
merged into cis_magazine.ISSUES at import time from cis_magazine.py only;
magazine_issues.json must stay byte-identical to git HEAD and all original
article IDs (suffixes 1-10) must be present and unchanged.
"""
import re
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import cis_magazine

MAG_REPO_DIR = Path(__file__).resolve().parent
ISSUE_DATES = {
    'OW881201': '1988-12-01',
    'OW881208': '1988-12-08',
    'OW881215': '1988-12-15',
    'OW881222': '1988-12-22',
    'OW881229': '1988-12-29',
}
NEW_DEPARTMENTS = {'News Briefs', 'SysOp Q&A', 'Letters to the Editor'}
NEW_SUFFIXES = ('-11', '-12', '-13')


def new_articles(issue):
    return [a for a in issue['articles'] if a['id'].endswith(NEW_SUFFIXES)]


class MagazinePack4Tests(unittest.TestCase):
    def test_issue_dates_unchanged(self):
        self.assertEqual(len(cis_magazine.ISSUES), 5)
        for issue in cis_magazine.ISSUES:
            self.assertEqual(issue['date'], ISSUE_DATES[issue['id']])

    def test_source_json_untouched(self):
        committed = subprocess.run(
            ['git', 'show', 'HEAD:magazine_issues.json'],
            cwd=MAG_REPO_DIR, capture_output=True, check=True).stdout
        self.assertEqual(
            (MAG_REPO_DIR / 'magazine_issues.json').read_text(encoding='utf-8'),
            committed.decode('utf-8').replace('\r\n', '\n'),
            'magazine_issues.json must stay untouched; pack-4 content lives in cis_magazine.py')

    def test_original_article_ids_present_and_unchanged(self):
        for issue in cis_magazine.ISSUES:
            originals = issue['articles'][:10]
            self.assertEqual(
                [a['id'] for a in originals],
                [f"{issue['id']}-{n}" for n in range(1, 11)],
                'original articles keep their positions and IDs')
            self.assertEqual(len(issue['articles']), 13)

    def test_new_departments_present_in_each_issue(self):
        for issue in cis_magazine.ISSUES:
            with self.subTest(issue=issue['id']):
                added = new_articles(issue)
                self.assertEqual(len(added), 3)
                self.assertEqual(
                    {a['department'] for a in added}, NEW_DEPARTMENTS)
                self.assertEqual(
                    sorted(a['id'] for a in added),
                    [f"{issue['id']}-11", f"{issue['id']}-12", f"{issue['id']}-13"])

    def test_new_article_ids_unique_and_retrievable(self):
        identifiers = [a['id'] for i in cis_magazine.ISSUES for a in i['articles']]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        for issue in cis_magazine.ISSUES:
            day = date.fromisoformat(issue['date'])
            found = cis_magazine.find_issue(issue['id'], day)
            self.assertIsNotNone(found)
            for article in new_articles(issue):
                index = next(i for i, a in enumerate(found['articles'])
                             if a['id'] == article['id'])
                self.assertEqual(found['articles'][index]['title'], article['title'])

    def test_new_articles_meet_editorial_minimums(self):
        for issue in cis_magazine.ISSUES:
            for article in new_articles(issue):
                with self.subTest(article=article['id']):
                    body = ' '.join(article['paragraphs'])
                    self.assertGreaterEqual(len(body.split()), 400)
                    body.encode('ascii')
                    (article['title'] + article['department'] + article['author']).encode('ascii')
                    for link in article.get('related', []):
                        for destination in re.findall(r'GO ([A-Z0-9]+)', link):
                            import compuserve
                            self.assertIsNotNone(
                                compuserve.resolve_go_destination(destination), link)

    def test_publication_gating_still_works(self):
        self.assertEqual(cis_magazine.available(date(1988, 11, 30)), [])
        self.assertIsNone(cis_magazine.find_issue('OW881229', date(1988, 12, 15)))
        self.assertIsNone(cis_magazine.find_issue('OW881222', date(1988, 12, 21)))
        # New articles are not searchable before their issue's date.
        self.assertEqual(cis_magazine.search('door trivia game', date(1988, 12, 15)), [])
        self.assertTrue(cis_magazine.search('door trivia game', date(1988, 12, 22)))

    def test_new_article_text_retrievable_end_to_end(self):
        issue = cis_magazine.find_issue('OW881208', date(1988, 12, 31))
        article = next(a for a in issue['articles'] if a['id'] == 'OW881208-12')
        lines = cis_magazine.article_lines(issue, article)
        text = '\n'.join(lines)
        self.assertIn(article['title'], text)
        self.assertIn('SYSOP Q&A', text)
        self.assertIn(' '.join(article['paragraphs'][1].split()), ' '.join(text.split()))

    def test_new_article_exported_in_full_issue_download(self):
        import cis_dynamic
        import compuserve
        from cis_terminal import wrap_terminal_text
        issue = cis_magazine.find_issue('OW881215', date(1988, 12, 31))
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(compuserve, 'BASE_DIR', Path(directory)), \
                patch.object(cis_dynamic, 'simulation_day', return_value=date(1988, 12, 31)):
            path = cis_magazine.export_issue(compuserve, issue)
            raw = path.read_bytes()
            text = raw.decode('ascii')
            flattened = ' '.join(text.split())
            self.assertTrue(all(len(line) <= 72 for line in text.splitlines()))
            for article in new_articles(issue):
                self.assertIn(article['title'], text)
                for paragraph in article['paragraphs']:
                    self.assertIn(' '.join(paragraph.split()), flattened)
                for width in (40, 80):
                    wrapped = [line for line in wrap_terminal_text(paragraph, width)
                               for paragraph in [article['paragraphs'][0]]]
                    self.assertTrue(all(len(line) <= width for line in wrapped))

    def test_new_article_selectable_from_issue_menu(self):
        import compuserve
        issue = cis_magazine.ISSUES[0]
        with patch.object(compuserve, 'current_profile', {}), \
                patch.object(compuserve, 'clear'), \
                patch.object(compuserve, 'header_bar'), \
                patch.object(compuserve, 'ansi_scroll'), \
                patch.object(cis_magazine, 'read_article') as reader, \
                patch('builtins.input', side_effect=['11', 'M']):
            cis_magazine.issue_menu(compuserve, issue)
            reader.assert_called_once_with(compuserve, issue, 10)


# --- Page pause: line count resets at each user prompt ---

import cis_session


class PagePauseTests(unittest.TestCase):
    def setUp(self):
        self._saved_options = dict(compuserve.startup_options)
        self._saved_profile = compuserve.current_profile
        self._saved_count = compuserve.transmitted_line_count
        compuserve.startup_options["fast_mode"] = True
        compuserve.startup_options["page_pause"] = True
        compuserve.current_profile = {}
        compuserve.transmitted_line_count = 0
        self._token = cis_session._prompt_app.set(compuserve)

    def tearDown(self):
        cis_session._prompt_app.reset(self._token)
        compuserve.startup_options.clear()
        compuserve.startup_options.update(self._saved_options)
        compuserve.current_profile = self._saved_profile
        compuserve.transmitted_line_count = self._saved_count

    def _scroll(self, n, prompts):
        with patch("builtins.input", side_effect=lambda p="": prompts.append(p) or ""):
            for i in range(n):
                compuserve.ansi_scroll(f"line {i}", 0.01)

    def test_reset_page_pause_clears_counter(self):
        compuserve.transmitted_line_count = 42
        compuserve.reset_page_pause()
        self.assertEqual(compuserve.transmitted_line_count, 0)

    def test_pause_after_twenty_four_lines_without_prompt(self):
        prompts = []
        self._scroll(30, prompts)
        more = [p for p in prompts if p == "More ! "]
        self.assertEqual(len(more), 1)

    def test_prompt_resets_so_short_blocks_never_pause(self):
        prompts = []
        with patch("builtins.input", side_effect=lambda p="": prompts.append(p) or ""):
            for _ in range(3):
                for i in range(10):
                    compuserve.ansi_scroll(f"line {i}", 0.01)
                cis_session.read_input("Choice: ")
        more = [p for p in prompts if p == "More ! "]
        self.assertEqual(more, [])

    def test_read_input_without_app_still_works(self):
        token = cis_session._prompt_app.set(None)
        try:
            with patch("builtins.input", return_value="hello"):
                self.assertEqual(cis_session.read_input("P> "), "hello")
        finally:
            cis_session._prompt_app.reset(token)
# =====================================================================
# Content pack 5: 1988 Year in Review, Cooking/Aviation/Sci-Fi forums,
# sports expansion (Super Bowl preview, World Series recap, NBA, NHL).
# Merged from the five standalone worker test files by the finisher.
# =====================================================================

# --- 1988 Year in Review (cis_yearend) ---

YEAREND_BANNED_TERMS = (
    # "internet" intentionally excluded: the Morris worm was reported as
    # the "Internet worm" in 1988 wire copy, and the term predates 1988.
    "1989", "1990", "1991", "twitter", "iphone", "facebook",
    "google", "911", "9/11",
)


def _content_lines(sim_day):
    """All display lines emitted across yearend sections for a simulated date."""
    lines = []
    for _title, section_lines in cis_yearend.yearend_menu_lines(sim_day):
        lines.extend(section_lines)
    return lines


class PanAmDateGatingTest(unittest.TestCase):
    def test_panam_absent_dec_20(self):
        lines = cis_yearend.panam_lines(date(1988, 12, 20))
        self.assertEqual(lines, [])
        titles = [t for t, _ in cis_yearend.yearend_menu_lines(date(1988, 12, 20))]
        self.assertNotIn("Pan Am Flight 103", titles)
        blob = "\n".join(_content_lines(date(1988, 12, 20))).lower()
        self.assertNotIn("pan am", blob)
        self.assertNotIn("lockerbie", blob)

    def test_panam_present_dec_21(self):
        lines = cis_yearend.panam_lines(date(1988, 12, 21))
        self.assertTrue(lines)
        blob = "\n".join(lines).lower()
        self.assertIn("lockerbie", blob)
        self.assertIn("developing", blob)
        titles = [t for t, _ in cis_yearend.yearend_menu_lines(date(1988, 12, 21))]
        self.assertIn("Pan Am Flight 103", titles)

    def test_panam_developing_tone_dec_21(self):
        # Cause under investigation on Dec 21; a Dec 22 update appears later.
        dec21 = "\n".join(cis_yearend.panam_lines(date(1988, 12, 21))).lower()
        self.assertIn("under investigation", dec21)
        self.assertNotIn("december 22", dec21)
        dec22 = "\n".join(cis_yearend.panam_lines(date(1988, 12, 22))).lower()
        self.assertIn("december 22", dec22)


class ArmeniaDateGatingTest(unittest.TestCase):
    def test_armenia_absent_dec_6(self):
        self.assertEqual(cis_yearend.disaster_lines(date(1988, 12, 6)), [])
        titles = [t for t, _ in cis_yearend.yearend_menu_lines(date(1988, 12, 6))]
        self.assertNotIn("Armenia Earthquake", titles)

    def test_armenia_present_dec_7(self):
        lines = cis_yearend.disaster_lines(date(1988, 12, 7))
        self.assertTrue(lines)
        blob = "\n".join(lines).lower()
        self.assertIn("spitak", blob)


class YearEndMenuContentTest(unittest.TestCase):
    def test_menu_sections_non_empty(self):
        sections = cis_yearend.yearend_menu_lines(date(1988, 12, 15))
        self.assertTrue(sections)
        for title, lines in sections:
            with self.subTest(title=title):
                self.assertTrue(lines, f"section {title!r} is empty")
                self.assertTrue(all(isinstance(line, str) for line in lines))
                self.assertTrue(any(line.strip() for line in lines))

    def test_election_section(self):
        blob = "\n".join(cis_yearend.election_lines(date(1988, 12, 1)))
        self.assertIn("Bush", blob)
        self.assertIn("Dukakis", blob)
        self.assertIn("November 8, 1988", blob)
        self.assertIn("426", blob)

    def test_bestof_covers_four_areas(self):
        blob = "\n".join(cis_yearend.bestof_lines(date(1988, 12, 31)))
        for expected in ("MOVIES", "MUSIC", "SPORTS", "TECHNOLOGY"):
            self.assertIn(expected, blob)

    def test_no_post_1988_references(self):
        for sim_day in (date(1988, 12, 1), date(1988, 12, 15),
                        date(1988, 12, 31)):
            blob = "\n".join(_content_lines(sim_day)).lower()
            for bad in YEAREND_BANNED_TERMS:
                self.assertNotIn(
                    bad, blob,
                    f"anachronism {bad!r} on {sim_day}")

    def test_default_day_resolves_from_environment(self):
        with patch.dict(os.environ, {"CIS_SIMULATION_DATE": "1988-12-21"}):
            titles = [t for t, _ in cis_yearend.yearend_menu_lines()]
            self.assertIn("Pan Am Flight 103", titles)
        with patch.dict(os.environ, {"CIS_SIMULATION_DATE": "1988-12-10"}):
            titles = [t for t, _ in cis_yearend.yearend_menu_lines()]
            self.assertNotIn("Pan Am Flight 103", titles)

    def test_yearend_service_signature(self):
        sections = cis_yearend.yearend_service(app=None)
        self.assertTrue(sections)
        self.assertEqual(sections[0][0], "Election '88")

    def test_display_lines_fit_80_column_screen(self):
        for sim_day in (date(1988, 12, 1), date(1988, 12, 15),
                        date(1988, 12, 31)):
            for title, lines in cis_yearend.yearend_menu_lines(sim_day):
                for line in lines:
                    with self.subTest(day=sim_day, title=title):
                        self.assertLessEqual(
                            len(line), 78, f"overlong line: {line!r}")


class YearEndNewsWiringTest(unittest.TestCase):
    def test_go_yearinreview_present(self):
        go_map = json.loads((REPO_ROOT / "go_commands.json").read_text())
        self.assertIn("GO YEARINREVIEW", go_map)

    def test_news_menu_option_12(self):
        screens = json.loads((REPO_ROOT / "screens.json").read_text())
        self.assertIn("12", screens["news"]["options"])

    def test_news_choice_12_wired(self):
        # compuserve.yearend_menu drives the cis_yearend submenu.
        self.assertTrue(callable(compuserve.yearend_menu))
        sections = cis_yearend.yearend_service(app=None)
        self.assertTrue(sections)


# --- Cooking Forum (cis_cooking) ---

# Anything that did not exist by December 1988 is banned from post
# subject/body text (the module docstring's "period rules" section is
# exempt because it only names them to forbid them).
COOKING_BANNED_TERMS = [
    "INTERNET", "AIR FRYER", "INSTANT POT", "YOUTUBE", "WEBSITE",
    "BLOG", "EMAIL", "SMARTPHONE", "GOOGLE", "WIFI", "BLUETOOTH",
    "SOUS VIDE", "DIGITAL", "ONLINE", "NETFLIX", "FACEBOOK",
    "TWITTER", "IPHONE", "IPAD", "STREAMING",
]

COOKING_EXPECTED_SECTIONS = {
    "1": ("cooking_recipes", "Recipes"),
    "2": ("cooking_baking", "Holiday Baking"),
    "3": ("cooking_castiron", "Cast Iron & Cookware"),
    "4": ("cooking_microwave", "Microwave Cooking"),
    "5": ("cooking_canning", "Canning & Preserving"),
    "6": ("cooking_restaurants", "Restaurant Talk"),
}


class CookingSectionSpecTests(unittest.TestCase):
    def test_module_identity(self):
        self.assertEqual(cis_cooking.FORUM_ID, "cooking")
        self.assertEqual(cis_cooking.FORUM_TITLE, "Cooking Forum")

    def test_section_spec_shape(self):
        spec = cis_cooking.section_spec()
        self.assertIsInstance(spec, dict)
        self.assertEqual(len(spec), 6)
        self.assertEqual(set(spec.keys()), {"1", "2", "3", "4", "5", "6"})
        for key, entry in spec.items():
            self.assertIsInstance(entry, (tuple, list))
            self.assertEqual(len(entry), 2)
            section_id, title = entry
            self.assertTrue(section_id.startswith("cooking_"), key)
            self.assertTrue(title.strip(), key)

    def test_section_spec_matches_expected(self):
        spec = cis_cooking.section_spec()
        for key, expected in COOKING_EXPECTED_SECTIONS.items():
            self.assertEqual(tuple(spec[key]), expected)

    def test_seed_post_sections_covered(self):
        section_ids = {entry[0] for entry in cis_cooking.section_spec().values()}
        used = {post["section"] for post in cis_cooking.SEED_POSTS}
        self.assertEqual(used, section_ids)

    def test_wired_into_forum_catalog(self):
        entry = compuserve.FORUM_CATALOG["cooking"]
        self.assertEqual(entry["title"], "Cooking Forum")
        self.assertEqual(compuserve.FORUM_CHOICES["16"], "cooking")


class CookingSeedPostTests(unittest.TestCase):
    def test_sixteen_seed_posts(self):
        self.assertEqual(len(cis_cooking.SEED_POSTS), 16)

    def test_content_id_format(self):
        for post in cis_cooking.SEED_POSTS:
            self.assertRegex(post["content_id"], r"^cooking-1988-\d{3}$")

    def test_content_ids_sequential_and_unique(self):
        ids = [post["content_id"] for post in cis_cooking.SEED_POSTS]
        self.assertEqual(len(set(ids)), 16)
        expected = [f"cooking-1988-{n:03d}" for n in range(1, 17)]
        self.assertEqual(sorted(ids), expected)

    def test_dates_all_december_1988(self):
        for post in cis_cooking.SEED_POSTS:
            self.assertRegex(post["date"], r"^12/\d{2}/88$", post["content_id"])
            day = int(post["date"].split("/")[1])
            self.assertGreaterEqual(day, 1)
            self.assertLessEqual(day, 31)

    def test_required_fields_present(self):
        for post in cis_cooking.SEED_POSTS:
            for field in ("content_id", "section", "date", "author",
                          "subject", "body"):
                self.assertTrue(post[field], f"{field} in {post['content_id']}")
            self.assertIsNone(post["parent"], post["content_id"])

    def test_varied_authors(self):
        authors = {post["author"] for post in cis_cooking.SEED_POSTS}
        self.assertGreaterEqual(len(authors), 10)

    def test_no_anachronisms(self):
        for post in cis_cooking.SEED_POSTS:
            text = (post["subject"] + "\n" + post["body"]).lower()
            for bad in COOKING_BANNED_TERMS:
                self.assertNotIn(
                    bad.lower(), text,
                    f"anachronism {bad!r} in {post['content_id']} (cooking)")

    def test_holiday_baking_flavor(self):
        blob = " ".join(p["subject"] + " " + p["body"]
                        for p in cis_cooking.SEED_POSTS).lower()
        for keyword in ("christmas", "fruitcake", "cookie", "fudge"):
            self.assertIn(keyword, blob)

    def test_seed_posts_returns_copies(self):
        copies = cis_cooking.seed_posts()
        self.assertEqual(len(copies), 16)
        copies[0]["subject"] = "MUTATED"
        self.assertNotEqual(cis_cooking.SEED_POSTS[0]["subject"], "MUTATED")


class CookingGoCommandTests(unittest.TestCase):
    def test_go_cooking_mapped(self):
        go_map = json.loads((REPO_ROOT / "go_commands.json").read_text())
        self.assertEqual(go_map.get("GO COOKING"), "cooking")

    def test_go_cooking_resolves(self):
        self.assertEqual(compuserve.resolve_go_destination("COOKING"), "cooking")


# --- Aviation Forum (cis_aviation) ---

# Post-1988 terms that must never appear in the December 1988 seed posts.
AVIATION_ANACHRONISMS = [
    "garmin", "g1000", "internet", "foreflight", "website", "www.",
    "gps", "ipad", "flightaware", "youtube", "mp3", "glass cockpit",
    "1990", "1991",
]

AVIATION_REQUIRED_FIELDS = {"content_id", "section", "date", "author",
                            "subject", "body", "parent"}


class AviationForumTests(unittest.TestCase):
    def test_forum_identity(self):
        self.assertEqual(cis_aviation.FORUM_ID, "aviation")
        self.assertEqual(cis_aviation.FORUM_TITLE, "Aviation Forum")

    def test_section_spec_shape(self):
        secs = cis_aviation.SECTIONS
        self.assertIsInstance(secs, dict)
        self.assertEqual(len(secs), 6)
        self.assertEqual(set(secs.keys()), {"1", "2", "3", "4", "5", "6"})
        ids = []
        for key, spec in secs.items():
            self.assertIsInstance(spec, (tuple, list), f"section {key}")
            self.assertEqual(len(spec), 2, f"section {key}")
            sec_id, title = spec
            self.assertTrue(sec_id.startswith("aviation_"), sec_id)
            self.assertTrue(title.strip(), sec_id)
            ids.append(sec_id)
        self.assertEqual(len(set(ids)), len(ids), "section ids must be unique")
        self.assertEqual(cis_aviation.section_spec(), cis_aviation.SECTIONS)
        titles = [t for _, t in secs.values()]
        for expected in ("Private Pilots", "IFR Training",
                         "Aircraft Ownership", "Flight Simulator",
                         "Trip Reports", "Hangar Talk"):
            self.assertIn(expected, titles)

    def test_seed_post_count(self):
        self.assertEqual(len(cis_aviation.SEED_POSTS), 16)
        self.assertEqual(len(cis_aviation.seed_posts()), 16)

    def test_seed_post_fields_dates_ids(self):
        valid_sections = {sec_id for sec_id, _ in
                          cis_aviation.SECTIONS.values()}
        seen = []
        for post in cis_aviation.SEED_POSTS:
            self.assertEqual(set(post.keys()), AVIATION_REQUIRED_FIELDS,
                             f"field mismatch in {post.get('content_id')}")
            for field in ("content_id", "section", "date", "author",
                          "subject", "body"):
                self.assertTrue(str(post[field]).strip(),
                                f"{field} empty in {post['content_id']}")
            self.assertIsNone(post["parent"], post["content_id"])
            self.assertIn(post["section"], valid_sections,
                          post["content_id"])
            month, day, year = post["date"].split("/")
            self.assertEqual((month, year), ("12", "88"),
                             post["content_id"])
            self.assertTrue(1 <= int(day) <= 20, post["content_id"])
            seen.append(post["content_id"])
        self.assertEqual(len(set(seen)), len(seen), "duplicate content ids")
        for cid in seen:
            self.assertRegex(cid, r"^aviation-1988-\d{3}$", cid)

    def test_no_anachronisms(self):
        for post in cis_aviation.SEED_POSTS:
            text = (post["subject"] + "\n" + post["body"]).lower()
            for bad in AVIATION_ANACHRONISMS:
                self.assertNotIn(bad, text,
                                 f"anachronism {bad!r} in "
                                 f"{post['content_id']}")

    def test_go_aviation_present(self):
        go_map = json.loads((REPO_ROOT / "go_commands.json").read_text())
        self.assertIn("GO AVIATION", go_map)
        self.assertEqual(go_map["GO AVIATION"], "aviation")

    def test_go_aviation_resolves(self):
        self.assertEqual(compuserve.resolve_go_destination("AVIATION"), "aviation")

    def test_wired_into_forum_catalog(self):
        entry = compuserve.FORUM_CATALOG["aviation"]
        self.assertEqual(entry["title"], "Aviation Forum")
        self.assertEqual(entry["sections"], cis_aviation.section_spec())

    def test_forum_choice_number(self):
        self.assertEqual(compuserve.FORUM_CHOICES["17"], "aviation")
        self.assertEqual(compuserve.FORUM_CHOICES["16"], "cooking")


# --- Comics & Sci-Fi Forum (cis_scifi) ---

# Terms that must never appear in 1988-era content (case-insensitive).
SCIFI_BANNED_TERMS = [
    "INTERNET",
    "SEASON 3",
    "SEASON THREE",
    "DVD",
    "BLU-RAY",
    "YOUTUBE",
    "NETFLIX",
    "STREAMING",
    "HTTP://",
    "MEASURE OF A MAN",
    "TIM BURTON",
    "BATMAN FILM",
    "1989 BATMAN",
    "WATCHMEN FILM",
    "DEEP SPACE NINE",
    "VOYAGER",
    "FIREFLY",
    "BABYLON 5",
    "X-FILES",
    "THE MATRIX",
    "SEQUEL TRILOGY",
]

SCIFI_REQUIRED_FIELDS = {
    "content_id", "section", "date", "author", "subject", "body", "parent",
}

scifi = cis_scifi  # worker D alias, kept for readability


class SciFiForumTests(unittest.TestCase):
    def test_forum_constants(self):
        self.assertEqual(scifi.FORUM_ID, "scifi")
        self.assertEqual(scifi.FORUM_TITLE, "Comics & Sci-Fi Forum")

    def test_section_spec_has_six_sections(self):
        spec = scifi.section_spec()
        self.assertEqual(len(spec), 6)

    def test_section_spec_shape(self):
        spec = scifi.section_spec()
        self.assertEqual(sorted(spec.keys()), ["1", "2", "3", "4", "5", "6"])
        for key, value in spec.items():
            self.assertIsInstance(value, tuple)
            self.assertEqual(len(value), 2)
            section_id, title = value
            self.assertTrue(section_id.startswith("scifi_"))
            self.assertTrue(isinstance(title, str) and title.strip())
        titles = [v[1] for v in spec.values()]
        self.assertEqual(
            titles,
            ["Comic Books", "Star Trek", "Doctor Who",
             "Movies & TV", "Books", "Conventions"],
        )

    def test_sixteen_seed_posts(self):
        self.assertEqual(len(scifi.SEED_POSTS), 16)

    def test_seed_post_fields(self):
        section_ids = {v[0] for v in scifi.SECTIONS.values()}
        for post in scifi.SEED_POSTS:
            self.assertTrue(
                SCIFI_REQUIRED_FIELDS.issubset(post.keys()),
                f"post {post.get('content_id')} missing fields",
            )
            self.assertIn(post["section"], section_ids)
            self.assertTrue(post["author"].strip())
            self.assertTrue(post["subject"].strip())
            self.assertTrue(post["body"].strip())
            self.assertIsNone(post["parent"])

    def test_content_id_prefix_and_unique(self):
        ids = [p["content_id"] for p in scifi.SEED_POSTS]
        self.assertEqual(len(ids), len(set(ids)))
        for i, content_id in enumerate(ids, start=1):
            self.assertEqual(content_id, f"scifi-1988-{i:03d}")

    def test_all_dates_december_1988(self):
        for post in scifi.SEED_POSTS:
            month, day, year = post["date"].split("/")
            self.assertEqual(month, "12", f"{post['content_id']} month")
            self.assertEqual(year, "88", f"{post['content_id']} year")
            self.assertTrue(1 <= int(day) <= 20, f"{post['content_id']} day")

    def test_no_post1988_terms(self):
        for post in scifi.SEED_POSTS:
            text = (post["subject"] + " " + post["body"]).upper()
            for term in SCIFI_BANNED_TERMS:
                self.assertNotIn(
                    term, text,
                    f"banned term {term!r} in {post['content_id']}",
                )

    def test_go_scifi_in_go_commands(self):
        commands = json.loads((REPO_ROOT / "go_commands.json").read_text())
        self.assertIn("GO SCIFI", commands)
        self.assertEqual(commands["GO SCIFI"], "scifi")

    def test_go_scifi_resolves(self):
        self.assertEqual(compuserve.resolve_go_destination("SCIFI"), "scifi")

    def test_wired_into_forum_catalog(self):
        entry = compuserve.FORUM_CATALOG["scifi"]
        self.assertEqual(entry["title"], "Comics & Sci-Fi Forum")
        self.assertEqual(compuserve.FORUM_CHOICES["18"], "scifi")

    def test_seed_posts_are_copies(self):
        first = scifi.seed_posts()[0]
        first["body"] = "mutated"
        self.assertNotEqual(scifi.SEED_POSTS[0]["body"], "mutated")


# --- Sports expansion (cis_sports) ---


class SuperBowlPreviewTests(unittest.TestCase):
    def setUp(self):
        os.environ["CIS_SIMULATION_DATE"] = "1988-12-15"

    def test_preview_non_empty(self):
        lines = cis_sports.super_bowl_preview_lines()
        self.assertTrue(lines)
        self.assertTrue(all(isinstance(l, str) for l in lines))
        self.assertTrue(any(l.strip() for l in lines))

    def test_preview_identifies_as_preview_only(self):
        blob = "\n".join(cis_sports.super_bowl_preview_lines())
        self.assertIn("PREVIEW", blob)
        self.assertIn("has not been played", blob)

    def test_preview_facts(self):
        blob = "\n".join(cis_sports.super_bowl_preview_lines())
        self.assertIn("49ers", blob)
        self.assertIn("Bengals", blob)
        self.assertIn("January 22, 1989", blob)
        self.assertIn("Joe Robbie Stadium", blob)
        self.assertIn("Miami", blob)
        self.assertIn("10-6", blob)
        self.assertIn("12-4", blob)
        self.assertIn("Super Bowl XVI", blob)

    def test_preview_key_players(self):
        blob = "\n".join(cis_sports.super_bowl_preview_lines())
        for name in ("Joe Montana", "Jerry Rice", "Roger Craig",
                     "Boomer Esiason", "Ickey Woods"):
            self.assertIn(name, blob)
        self.assertIn("1988 NFL MVP", blob)

    def test_preview_never_states_result(self):
        # The game is in the future; no result may be stated or implied.
        blob = "\n".join(cis_sports.super_bowl_preview_lines(date(1988, 12, 31)))
        for forbidden in ("20-16", "49ers won", "Bengals won", "champions",
                          "defeated the Bengals", "defeated the 49ers",
                          "Super Bowl MVP"):
            self.assertNotIn(forbidden, blob)

    def test_preview_storyline_rotates_deterministically(self):
        first = cis_sports.super_bowl_preview_lines(date(1988, 12, 1))
        second = cis_sports.super_bowl_preview_lines(date(1988, 12, 2))
        h1 = [l for l in first if l.startswith("STORYLINE:")]
        h2 = [l for l in second if l.startswith("STORYLINE:")]
        self.assertEqual(len(h1), 1)
        self.assertNotEqual(h1, h2)
        again = cis_sports.super_bowl_preview_lines(date(1988, 12, 1))
        self.assertEqual([l for l in again if l.startswith("STORYLINE:")], h1)

    def test_preview_default_day_uses_simulation_day(self):
        self.assertEqual(cis_sports.super_bowl_preview_lines(),
                         cis_sports.super_bowl_preview_lines(date(1988, 12, 15)))

    def test_preview_records_are_verified(self):
        nfc_name, nfc_w, nfc_l, nfc_v = cis_sports.SB_PREVIEW["nfc_team"]
        afc_name, afc_w, afc_l, afc_v = cis_sports.SB_PREVIEW["afc_team"]
        self.assertEqual((nfc_name, nfc_w, nfc_l), ("San Francisco 49ers", 10, 6))
        self.assertEqual((afc_name, afc_w, afc_l), ("Cincinnati Bengals", 12, 4))
        self.assertTrue(nfc_v and afc_v)


class WorldSeriesTests(unittest.TestCase):
    def setUp(self):
        os.environ["CIS_SIMULATION_DATE"] = "1988-12-15"

    def test_recap_non_empty(self):
        lines = cis_sports.world_series_lines()
        self.assertTrue(lines)
        self.assertTrue(all(isinstance(l, str) for l in lines))

    def test_recap_facts(self):
        blob = "\n".join(cis_sports.world_series_lines())
        self.assertIn("Dodgers", blob)
        self.assertIn("Athletics", blob)
        self.assertIn("4", blob)
        self.assertIn("Gibson", blob)
        self.assertIn("Eckersley", blob)
        self.assertIn("Hershiser", blob)
        self.assertIn("MVP", blob)
        self.assertIn("59", blob)

    def test_recap_no_future_claims(self):
        # Recap must not claim anything that happened after December 1988.
        blob = "\n".join(cis_sports.world_series_lines())
        self.assertNotIn("1989", blob)

    def test_recap_default_day_matches_simulation_day(self):
        self.assertEqual(cis_sports.world_series_lines(),
                         cis_sports.world_series_lines(date(1988, 12, 15)))


class NBAStandingsTests(unittest.TestCase):
    def setUp(self):
        os.environ["CIS_SIMULATION_DATE"] = "1988-12-15"

    def test_lines_non_empty(self):
        lines = cis_sports.nba_lines()
        self.assertTrue(lines)
        self.assertTrue(all(isinstance(l, str) for l in lines))
        self.assertTrue(any(l.strip() for l in lines))

    def test_division_structure(self):
        self.assertEqual(set(cis_sports.NBA_STANDINGS),
                         {"ATLANTIC", "CENTRAL", "MIDWEST", "PACIFIC"})
        total = sum(len(teams) for teams in cis_sports.NBA_STANDINGS.values())
        self.assertEqual(total, 25, "1988-89 NBA had 25 teams")

    def test_expansion_team_placement(self):
        atlantic = [t[0] for t in cis_sports.NBA_STANDINGS["ATLANTIC"]]
        midwest = [t[0] for t in cis_sports.NBA_STANDINGS["MIDWEST"]]
        pacific = [t[0] for t in cis_sports.NBA_STANDINGS["PACIFIC"]]
        self.assertIn("Charlotte Hornets", atlantic)
        self.assertIn("Miami Heat", midwest)
        self.assertIn("Sacramento Kings", pacific)

    def test_all_records_verified(self):
        for division, teams in cis_sports.NBA_STANDINGS.items():
            for name, wins, losses, verified in teams:
                self.assertTrue(name)
                self.assertGreaterEqual(wins, 0)
                self.assertGreaterEqual(losses, 0)
                self.assertTrue(verified, f"{name} should be verified")

    def test_no_duplicate_teams(self):
        seen = set()
        for teams in cis_sports.NBA_STANDINGS.values():
            for name, _w, _l, _v in teams:
                self.assertNotIn(name, seen, f"{name} in two divisions")
                seen.add(name)

    def test_lines_sorted_by_win_pct(self):
        # Sorted by winning percentage, matching the source standings table.
        for division, teams in cis_sports.NBA_STANDINGS.items():
            pcts = [w / (w + l) for _n, w, l, _v in teams]
            self.assertEqual(pcts, sorted(pcts, reverse=True),
                             f"{division} not sorted by win pct")

    def test_lakers_defending_champions_mentioned(self):
        blob = "\n".join(cis_sports.nba_lines())
        self.assertIn("Defending champions: Los Angeles Lakers", blob)

    def test_default_day_matches_simulation_day(self):
        self.assertEqual(cis_sports.nba_lines(),
                         cis_sports.nba_lines(date(1988, 12, 15)))


class NHLStandingsTests(unittest.TestCase):
    def setUp(self):
        os.environ["CIS_SIMULATION_DATE"] = "1988-12-15"

    def test_lines_non_empty(self):
        lines = cis_sports.nhl_lines()
        self.assertTrue(lines)
        self.assertTrue(all(isinstance(l, str) for l in lines))
        self.assertTrue(any(l.strip() for l in lines))

    def test_division_structure(self):
        self.assertEqual(set(cis_sports.NHL_STANDINGS),
                         {"ADAMS", "PATRICK", "NORRIS", "SMYTHE"})
        total = sum(len(teams) for teams in cis_sports.NHL_STANDINGS.values())
        self.assertEqual(total, 21, "1988-89 NHL had 21 teams")

    def test_all_records_verified(self):
        for division, teams in cis_sports.NHL_STANDINGS.items():
            for name, wins, losses, ties, verified in teams:
                self.assertTrue(name)
                self.assertGreaterEqual(wins, 0)
                self.assertGreaterEqual(losses, 0)
                self.assertGreaterEqual(ties, 0)
                self.assertTrue(verified, f"{name} should be verified")

    def test_points_math(self):
        # pts = 2*W + T; spot-check leaders as of Dec 15, 1988.
        leaders = {div: rows[0] for div, rows in cis_sports.NHL_STANDINGS.items()}
        self.assertEqual(leaders["SMYTHE"][:4], ("Calgary Flames", 22, 5, 5))
        self.assertEqual(leaders["ADAMS"][:4], ("Montreal Canadiens", 19, 10, 6))
        self.assertEqual(leaders["PATRICK"][:4], ("Pittsburgh Penguins", 18, 11, 2))
        self.assertEqual(leaders["NORRIS"][:4], ("Detroit Red Wings", 17, 9, 4))
        for division, rows in cis_sports.NHL_STANDINGS.items():
            pts = [2 * w + t for _n, w, _l, t, _v in rows]
            self.assertEqual(pts, sorted(pts, reverse=True),
                             f"{division} not sorted by points")

    def test_no_duplicate_teams(self):
        seen = set()
        for teams in cis_sports.NHL_STANDINGS.values():
            for name, _w, _l, _t, _v in teams:
                self.assertNotIn(name, seen, f"{name} in two divisions")
                seen.add(name)

    def test_lines_show_points(self):
        blob = "\n".join(cis_sports.nhl_lines())
        self.assertIn("49 pts", blob)  # Calgary led the league
        self.assertIn("2 for a win, 1 for a tie", blob)

    def test_default_day_matches_simulation_day(self):
        self.assertEqual(cis_sports.nhl_lines(),
                         cis_sports.nhl_lines(date(1988, 12, 15)))

    def test_highlights_rotate_deterministically(self):
        first = cis_sports.nhl_lines(date(1988, 12, 3))
        second = cis_sports.nhl_lines(date(1988, 12, 4))
        h1 = [l for l in first if l.startswith("AROUND THE LEAGUE:")]
        h2 = [l for l in second if l.startswith("AROUND THE LEAGUE:")]
        self.assertEqual(len(h1), 1)
        self.assertNotEqual(h1, h2)


class SportsMenuWiringTests(unittest.TestCase):
    def setUp(self):
        os.environ["CIS_SIMULATION_DATE"] = "1988-12-15"

    def test_menu_includes_all_four_new_sections(self):
        titles = [title for title, _lines in cis_sports.sports_menu_lines()]
        self.assertEqual(titles, ["NFL", "TV", "MLB", "SUPER BOWL",
                                  "WORLD SERIES", "NBA", "NHL"])

    def test_menu_sections_are_line_lists(self):
        for title, lines in cis_sports.sports_menu_lines():
            self.assertTrue(lines, f"{title} section empty")
            self.assertTrue(all(isinstance(l, str) for l in lines),
                            f"{title} has non-string lines")

    def test_service_returns_sections(self):
        sections = cis_sports.sports_service(object())
        self.assertEqual(len(sections), 7)


# --- Content-pack reinstall: bumping the pack id must re-run the merge ---

import copy
import cis_communities
import cis_storage


class CommunityPackInstallTests(unittest.TestCase):
    def _message_count(self, base_dir):
        data = cis_storage.load_json(base_dir, "forums.json", default={})
        return sum(len(messages) for messages in data.values())

    def test_pack_id_bump_remerges_new_messages_without_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            base_dir = Path(tmp)
            self.assertTrue(cis_communities.install(base_dir))
            # Same pack id installs only once.
            self.assertFalse(cis_communities.install(base_dir))
            before = self._message_count(base_dir)
            self.assertGreater(before, 0)
            # Simulate a pack update: new id plus one new seed message.
            new_pack = copy.deepcopy(cis_communities.PACK)
            new_pack["id"] = "computer-communities-1988-v2-test"
            new_pack["messages"] = list(new_pack["messages"]) + [{
                "content_id": "test-forum-1988-999",
                "section": "cooking_recipes",
                "date": "1988-12-01",
                "author": "Test Cook",
                "subject": "regression test post",
                "body": "This post verifies pack updates merge.",
                "parent": None,
            }]
            with patch.object(cis_communities, "PACK", new_pack):
                self.assertTrue(cis_communities.install(base_dir))
                # Reinstalling the bumped pack is a no-op again.
                self.assertFalse(cis_communities.install(base_dir))
            data = cis_storage.load_json(base_dir, "forums.json", default={})
            self.assertEqual(self._message_count(base_dir), before + 1)
            subjects = [m["subject"] for m in data.get("cooking_recipes", [])]
            self.assertIn("regression test post", subjects)


# =======================================================================
# Content pack 6: giftguide (merged from test_pack6_*.py)
# =======================================================================



class GiftGuideFakeApp:
    """Minimal stand-in for the compuserve app object."""

    def __init__(self):
        self.output_lines = []
        self.pages = []

    def ansi_scroll(self, text, delay=0.01):
        self.output_lines.append(str(text))
        return True

    def clear(self):
        return True

    def header_bar(self, service):
        self.output_lines.append(f"[header:{service}]")
        return True

    def text_page(self, service, title, lines):
        self.pages.append((service, title, list(lines)))
        return True

    @property
    def output(self):
        return "\n".join(self.output_lines)


# ---------------------------------------------------------------------------
# Catalog integrity
# ---------------------------------------------------------------------------
class TestCatalogIntegrity(unittest.TestCase):
    def test_every_gift_has_price_flag(self):
        for gift in GIFT_CATALOG:
            note = gift.price_note
            self.assertTrue(
                "VERIFIED" in note
                or "by most accounts" in note
                or "est." in note,
                f"{gift.name}: price_note missing flag: {note!r}",
            )

    def test_every_gift_has_valid_recipients(self):
        for gift in GIFT_CATALOG:
            self.assertTrue(gift.recipients, gift.name)
            for recipient in gift.recipients:
                self.assertIn(recipient, ("kid", "teen", "adult"), gift.name)

    def test_prices_positive(self):
        for gift in GIFT_CATALOG:
            self.assertGreater(gift.price, 0, gift.name)

    def test_catalog_covers_all_recipients(self):
        for recipient in ("kid", "teen", "adult"):
            self.assertTrue(
                any(recipient in g.recipients for g in GIFT_CATALOG),
                recipient,
            )


# ---------------------------------------------------------------------------
# Pure picker logic
# ---------------------------------------------------------------------------
class TestPickGifts(unittest.TestCase):
    def test_kid_budget_50(self):
        picks = pick_gifts(50, "kid")
        self.assertTrue(picks)
        for gift in picks:
            self.assertIn("kid", gift.recipients)
            self.assertLessEqual(gift.price, 50)

    def test_sorted_priciest_first(self):
        picks = pick_gifts(200, "adult")
        prices = [g.price for g in picks]
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_max_five_results(self):
        self.assertLessEqual(len(pick_gifts(10000, "kid")), 5)

    def test_adult_big_budget_includes_camcorder(self):
        picks = pick_gifts(1000, "adult")
        self.assertTrue(any("Camcorder" in g.name for g in picks))

    def test_tiny_budget_returns_nothing(self):
        self.assertEqual(pick_gifts(0.50, "kid"), [])

    def test_unknown_recipient_returns_nothing(self):
        self.assertEqual(pick_gifts(500, "grandparent"), [])

    def test_nonpositive_budget_returns_nothing(self):
        self.assertEqual(pick_gifts(0, "teen"), [])
        self.assertEqual(pick_gifts(-10, "teen"), [])

    def test_recipient_case_insensitive(self):
        self.assertEqual(pick_gifts(50, "Kid"), pick_gifts(50, "kid"))

    def test_teen_budget_100_gets_nes_or_games(self):
        picks = pick_gifts(100, "teen")
        names = " ".join(g.name for g in picks)
        self.assertTrue(
            "Nintendo" in names or "Mario" in names or "Zelda" in names,
            names,
        )

    def test_cheapest_for_sorted_ascending(self):
        cheapest = cheapest_for("kid")
        self.assertEqual(len(cheapest), 3)
        prices = [g.price for g in cheapest]
        self.assertEqual(prices, sorted(prices))
        self.assertTrue(all("kid" in g.recipients for g in cheapest))

    def test_parse_recipient(self):
        self.assertEqual(_parse_recipient("1"), "kid")
        self.assertEqual(_parse_recipient("kid"), "kid")
        self.assertEqual(_parse_recipient("2"), "teen")
        self.assertEqual(_parse_recipient("Teenager"), "teen")
        self.assertEqual(_parse_recipient("3"), "adult")
        self.assertIsNone(_parse_recipient("bogus"))
        self.assertIsNone(_parse_recipient(""))


# ---------------------------------------------------------------------------
# Content sections
# ---------------------------------------------------------------------------
class TestContentSections(unittest.TestCase):
    def _all_lines(self, day=None):
        lines = []
        for title, section in giftguide_menu_lines(day):
            lines.extend(section)
        return lines, [t for t, _ in giftguide_menu_lines(day)]

    def test_four_sections(self):
        sections = giftguide_menu_lines()
        self.assertEqual(len(sections), 4)

    def test_no_post_1988_references(self):
        lines, _ = self._all_lines()
        text = "\n".join(lines)
        for banned in ("1989", "1990", "Game Boy", "Super Nintendo"):
            self.assertNotIn(banned, text, f"post-1988 leak: {banned}")

    def test_hottest_mentions_verified_items(self):
        text = "\n".join(hottest_lines())
        self.assertIn("NINTENDO ENTERTAINMENT SYSTEM", text)
        self.assertIn("CABBAGE PATCH KIDS", text)
        self.assertIn("TEENAGE MUTANT NINJA TURTLES", text)
        self.assertIn("VERIFIED", text)

    def test_catalog_section_mentions_wish_book(self):
        text = "\n".join(catalog_vs_mall_lines())
        self.assertIn("WISH BOOK", text)
        self.assertIn("Service Merchandise", text)

    def test_trends_has_turtle_power(self):
        text = "\n".join(trends_lines())
        self.assertIn("TURTLE POWER", text)

    def test_shortages_countdown_before_christmas(self):
        text = "\n".join(shortages_lines(date(1988, 12, 20)))
        self.assertIn("5 shopping days until Christmas", text)

    def test_shortages_countdown_christmas_eve(self):
        text = "\n".join(shortages_lines(date(1988, 12, 24)))
        self.assertIn("1 shopping day until Christmas", text)

    def test_shortages_countdown_christmas_day(self):
        text = "\n".join(shortages_lines(date(1988, 12, 25)))
        self.assertIn("Christmas Day is here", text)

    def test_shortages_after_christmas(self):
        text = "\n".join(shortages_lines(date(1988, 12, 26)))
        self.assertIn("clearance season", text)

    def test_service_entry_matches_menu_lines(self):
        app = GiftGuideFakeApp()
        sections = giftguide_service(app)
        self.assertEqual(
            [t for t, _ in sections],
            [t for t, _ in giftguide_menu_lines()],
        )

    def test_day_param_accepted_everywhere(self):
        day = date(1988, 12, 10)
        hottest_lines(day)
        catalog_vs_mall_lines(day)
        shortages_lines(day)
        trends_lines(day)
        giftguide_menu_lines(day)
        pick_gifts(50, "kid", day)


# ---------------------------------------------------------------------------
# Interactive gift picker
# ---------------------------------------------------------------------------
class TestGiftPickerInteractive(unittest.TestCase):
    def run_picker(self, app, inputs, day=None):
        with patch("builtins.input", side_effect=inputs):
            with redirect_stdout(io.StringIO()) as captured:
                gift_picker(app, day)
        return captured.getvalue()

    def test_happy_path_kid(self):
        app = GiftGuideFakeApp()
        leftover = self.run_picker(app, ["50", "1", ""])
        self.assertEqual(leftover, "", "interactive output must not use print()")
        self.assertIn("GIFT PICKER", app.output)
        self.assertIn("Kid (ages 5-8)", app.output)

    def test_happy_path_teen_budget_100(self):
        app = GiftGuideFakeApp()
        self.run_picker(app, ["100", "2", ""])
        self.assertIn("Teen", app.output)
        # A $100 teen budget should surface Nintendo-flavored picks.
        self.assertTrue(
            "Nintendo" in app.output
            or "Mario" in app.output
            or "Zelda" in app.output,
            app.output,
        )

    def test_invalid_budget_reprompts(self):
        app = GiftGuideFakeApp()
        self.run_picker(app, ["abc", "25", "3", ""])
        self.assertIn("Enter a dollar amount", app.output)
        self.assertIn("Adult", app.output)

    def test_zero_budget_reprompts(self):
        app = GiftGuideFakeApp()
        self.run_picker(app, ["0", "30", "1", ""])
        self.assertIn("more than zero", app.output)

    def test_blank_budget_cancels(self):
        app = GiftGuideFakeApp()
        self.run_picker(app, [""])
        self.assertIn("cancelled", app.output.lower())
        self.assertNotIn("GIFT PICKER --", app.output)

    def test_invalid_recipient_reprompts(self):
        app = GiftGuideFakeApp()
        self.run_picker(app, ["60", "9", "2", ""])
        self.assertIn("Pick 1, 2, or 3.", app.output)
        self.assertIn("Teen", app.output)

    def test_too_small_budget_shows_stretch_picks(self):
        app = GiftGuideFakeApp()
        self.run_picker(app, ["2", "1", ""])
        self.assertIn("come closest", app.output)

    def test_no_bare_print_in_picker(self):
        app = GiftGuideFakeApp()
        leftover = self.run_picker(app, ["75", "3", ""])
        self.assertEqual(leftover, "")


# ---------------------------------------------------------------------------
# Guide menu
# ---------------------------------------------------------------------------
class TestGiftGuideMenu(unittest.TestCase):
    def run_menu(self, app, inputs, day=None):
        with patch("builtins.input", side_effect=inputs):
            with redirect_stdout(io.StringIO()) as captured:
                giftguide_menu(app, day)
        return captured.getvalue()

    def test_menu_lists_sections_and_exits(self):
        app = GiftGuideFakeApp()
        leftover = self.run_menu(app, ["M"])
        self.assertEqual(leftover, "")
        self.assertIn("1988 HOLIDAY SHOPPING GUIDE", app.output)
        self.assertIn("Gift Picker (interactive)", app.output)

    def test_menu_opens_reading_section(self):
        app = GiftGuideFakeApp()
        self.run_menu(app, ["1", "M"])
        self.assertEqual(len(app.pages), 1)
        service, title, lines = app.pages[0]
        self.assertEqual(service, "news")
        self.assertIn("HOTTEST GIFTS", title)
        self.assertTrue(lines)

    def test_menu_invalid_choice_then_exit(self):
        app = GiftGuideFakeApp()
        self.run_menu(app, ["99", "M"])
        self.assertIn("Enter a number from the list", app.output)

    def test_menu_runs_gift_picker(self):
        app = GiftGuideFakeApp()
        # 5 = Gift Picker; blank budget cancels; M exits menu.
        self.run_menu(app, ["5", "", "M"])
        self.assertIn("THE 1988 GIFT PICKER", app.output)

    def test_menu_date_sensitive_shortages(self):
        app = GiftGuideFakeApp()
        self.run_menu(app, ["3", "M"], day=date(1988, 12, 20))
        service, title, lines = app.pages[0]
        self.assertIn("5 shopping days until Christmas", "\n".join(lines))


if __name__ == "__main__":
    unittest.main()


# =======================================================================
# Content pack 6: fitness (merged from test_pack6_*.py)
# =======================================================================

PACK6_REPO_ROOT = Path(__file__).resolve().parent
PACK6_COMMUNITIES_PATH = PACK6_REPO_ROOT / "computer_communities.json"

FITNESS_EXPECTED_SECTIONS = {
    "1": ("fitness_aerobics", "Aerobics"),
    "2": ("fitness_running", "Running"),
    "3": ("fitness_weights", "Weight Training"),
    "4": ("fitness_nutrition", "Nutrition"),
    "5": ("fitness_injuries", "Sports Medicine/Injuries"),
    "6": ("fitness_mindbody", "Mind & Body"),
}

FITNESS_EXPECTED_IDS = [f"fitness-1988-{n:03d}" for n in range(1, 17)]

FITNESS_DATE_RE = re.compile(r"^12/(0[1-9]|[12][0-9]|3[01])/88$")


def load_messages():
    with open(PACK6_COMMUNITIES_PATH, encoding="ascii") as f:
        return json.load(f)["messages"]


class TestSectionSpec(unittest.TestCase):
    def test_six_sections_with_right_keys(self):
        spec = cis_fitness.section_spec()
        self.assertEqual(spec, FITNESS_EXPECTED_SECTIONS)

    def test_section_keys_prefixed(self):
        for _num, (key, _name) in cis_fitness.section_spec().items():
            self.assertTrue(key.startswith("fitness_"), key)

    def test_module_identity(self):
        self.assertEqual(cis_fitness.FORUM_ID, "fitness")
        self.assertEqual(cis_fitness.FORUM_TITLE, "Health & Fitness Forum")


class TestFitnessSeedPosts(unittest.TestCase):
    def test_sixteen_seed_posts(self):
        self.assertEqual(len(cis_fitness.SEED_POSTS), 16)

    def test_content_ids_sequential(self):
        ids = [p["content_id"] for p in cis_fitness.SEED_POSTS]
        self.assertEqual(ids, FITNESS_EXPECTED_IDS)

    def test_post_shape(self):
        required = {"content_id", "section", "date", "author",
                    "subject", "body", "parent"}
        valid_sections = {key for key, _ in cis_fitness.SECTIONS.values()}
        for post in cis_fitness.SEED_POSTS:
            self.assertEqual(set(post.keys()), required, post["content_id"])
            self.assertIsNone(post["parent"], post["content_id"])
            self.assertIn(post["section"], valid_sections, post["content_id"])
            self.assertTrue(post["author"].strip(), post["content_id"])
            self.assertTrue(post["subject"].strip(), post["content_id"])
            self.assertGreater(len(post["body"]), 80, post["content_id"])

    def test_dates_in_december_1988(self):
        for post in cis_fitness.SEED_POSTS:
            self.assertRegex(post["date"], FITNESS_DATE_RE, post["content_id"])

    def test_no_post_1988_references(self):
        for post in cis_fitness.SEED_POSTS:
            text = (post["subject"] + " " + post["body"]).lower()
            self.assertNotIn("1990", text, post["content_id"])
            self.assertNotIn("internet", text, post["content_id"])
            self.assertNotIn("website", text, post["content_id"])

    def test_seed_posts_returns_copies(self):
        first = cis_fitness.seed_posts()
        first[0]["subject"] = "MUTATED"
        self.assertNotEqual(cis_fitness.SEED_POSTS[0]["subject"], "MUTATED")


class TestJsonSeeding(unittest.TestCase):
    def test_all_seed_ids_in_communities_json(self):
        ids = {m["content_id"] for m in load_messages()}
        for content_id in FITNESS_EXPECTED_IDS:
            self.assertIn(content_id, ids, f"{content_id} missing")

    def test_json_entries_match_module(self):
        by_id = {m["content_id"]: m for m in load_messages()}
        for post in cis_fitness.seed_posts():
            entry = by_id[post["content_id"]]
            for field in ("section", "date", "author", "subject", "body"):
                self.assertEqual(entry[field], post[field],
                                 f"{post['content_id']}.{field} mismatch")
            self.assertIsNone(entry["parent"])

    def test_no_duplicate_content_ids(self):
        ids = [m["content_id"] for m in load_messages()]
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()


# =======================================================================
# Content pack 6: movies (merged from test_pack6_*.py)
# =======================================================================

MOVIES_EXPECTED = {
    "RAIN MAN": "Released Dec 16, 1988",
    "TWINS": "Released Dec 9, 1988",
    "SCROOGED": "Released Nov 23, 1988",
    "THE NAKED GUN": "Released Dec 2, 1988",
    "WORKING GIRL": "Released Dec 21, 1988",
}

MOVIES_VALID_RATINGS = {"****1/2", "****", "***1/2", "***", "**1/2", "**", "*1/2", "*"}


class MenuFakeApp:
    """Minimal fake app capturing ansi_scroll output, like ArcadeFakeApp."""

    def __init__(self):
        self.output_lines = []

    def ansi_scroll(self, text, delay=0.01):
        self.output_lines.append(str(text))
        return True


def review_by_title(title):
    for entry in cis_entertainment.MOVIE_REVIEWS:
        if entry[0] == title:
            return entry
    return None


class TestMovieReviewsPresent(unittest.TestCase):
    def test_all_five_films_present(self):
        titles = [entry[0] for entry in cis_entertainment.MOVIE_REVIEWS]
        for title in MOVIES_EXPECTED:
            self.assertIn(title, titles, f"{title} missing from MOVIE_REVIEWS")

    def test_release_dates_correct(self):
        for title, expected_date in MOVIES_EXPECTED.items():
            entry = review_by_title(title)
            self.assertIsNotNone(entry, f"{title} not found")
            self.assertEqual(entry[1], expected_date, f"{title} release date")

    def test_review_tuple_structure(self):
        for title in MOVIES_EXPECTED:
            entry = review_by_title(title)
            self.assertIsNotNone(entry)
            self.assertEqual(len(entry), 4, f"{title} tuple shape")
            t, released, stars, blurb = entry
            self.assertTrue(t.strip(), f"{title} title empty")
            self.assertTrue(released.strip(), f"{title} release line empty")
            self.assertTrue(blurb.strip(), f"{title} review text empty")
            self.assertGreater(len(blurb), 80, f"{title} review text too short")
            self.assertIn(stars, MOVIES_VALID_RATINGS, f"{title} bad star rating")

    def test_no_post_december_1988_releases(self):
        # Scrooged (Nov 1988, in theaters through December) is the only
        # permitted pre-December entry; nothing may be dated after Dec 1988.
        for t, released, _stars, _blurb in cis_entertainment.MOVIE_REVIEWS:
            self.assertNotIn("1989", released, t)
            self.assertNotIn("1990", released, t)


class TestMoviesLines(unittest.TestCase):
    def test_movies_lines_lists_all_five(self):
        lines = cis_entertainment.movies_lines(date(1988, 12, 15))
        text = "\n".join(lines)
        for title in MOVIES_EXPECTED:
            self.assertIn(title, text, f"{title} missing from movies_lines")
            self.assertIn(MOVIES_EXPECTED[title], text, f"{title} date missing")
        # each review's blurb makes it into the rendered lines
        for title in MOVIES_EXPECTED:
            entry = review_by_title(title)
            self.assertIn(entry[3], text, f"{title} blurb missing")

    def test_movies_lines_date_aware_rotation(self):
        # rotation by week changes lead review but keeps all five present
        early = cis_entertainment.movies_lines(date(1988, 12, 2))
        late = cis_entertainment.movies_lines(date(1988, 12, 28))
        for lines in (early, late):
            text = "\n".join(lines)
            for title in MOVIES_EXPECTED:
                self.assertIn(title, text)


class TestMenuWiring(unittest.TestCase):
    def test_entertainment_menu_sections_include_movies(self):
        sections = cis_entertainment.entertainment_menu_lines(date(1988, 12, 15))
        names = [name for name, _lines in sections]
        self.assertIn("Movies", names)

    def test_menu_rendered_via_fake_app(self):
        # Mirror compuserve.py's entertainment_menu: list sections via
        # ansi_scroll, then render the Movies section the same way.
        app = MenuFakeApp()
        sections = cis_entertainment.entertainment_menu_lines(date(1988, 12, 15))
        app.ansi_scroll("ENTERTAINMENT", 0.01)
        for index, (title, _lines) in enumerate(sections, 1):
            app.ansi_scroll(f"{index}  {title}", 0.01)
        menu_text = "\n".join(app.output_lines)
        self.assertIn("ENTERTAINMENT", menu_text)
        self.assertIn("Movies", menu_text)

        movies_lines = dict(sections)["Movies"]
        app2 = MenuFakeApp()
        for line in movies_lines:
            app2.ansi_scroll(line, 0.01)
        rendered = "\n".join(app2.output_lines)
        for title, released in MOVIES_EXPECTED.items():
            self.assertIn(title, rendered, f"{title} not rendered")
            self.assertIn(released, rendered, f"{title} date not rendered")


if __name__ == "__main__":
    unittest.main()


# =======================================================================
# Content pack 6: christmas (merged from test_pack6_*.py)
# =======================================================================



class ChristmasFakeApp:
    """Minimal fake app: captures ansi_scroll, records other calls."""

    def __init__(self):
        self.output_lines = []
        self.cleared = 0
        self.headers = []
        self.pages = []

    def ansi_scroll(self, text, delay=0.01):
        self.output_lines.append(str(text))
        return True

    def clear(self):
        self.cleared += 1

    def header_bar(self, screen_key):
        self.headers.append(screen_key)

    def text_page(self, screen_key, title, lines):
        self.pages.append((screen_key, title, list(lines)))


class TestAdventCalendar(unittest.TestCase):
    def test_twenty_five_treats_defined(self):
        self.assertEqual(len(ADVENT_TREATS), 25)

    def test_december_days_each_yield_a_treat(self):
        for day in range(1, 26):
            lines = christmas_treat(date(1988, 12, day))
            self.assertTrue(lines, f"Dec {day} returned no treat")
            text = "\n".join(lines)
            self.assertIn(f"DECEMBER {day}", text)
            title, kind, body = ADVENT_TREATS[day - 1]
            self.assertIn(title, text)
            self.assertIn(kind, text)

    def test_december_treats_are_distinct(self):
        treats = [tuple(christmas_treat(date(1988, 12, d)))
                  for d in range(1, 26)]
        self.assertEqual(len(set(treats)), 25,
                         "advent treats must all be distinct")

    def test_treat_kinds_cover_trivia_fiction_tips(self):
        kinds = {kind for _t, kind, _b in ADVENT_TREATS}
        self.assertIn("TRIVIA", kinds)
        self.assertIn("TINY FICTION", kinds)
        self.assertIn("HOLIDAY TIP", kinds)

    def test_november_yields_offseason_message(self):
        lines = christmas_treat(date(1988, 11, 15))
        text = "\n".join(lines).lower()
        self.assertIn("hasn't arrived yet", text)
        self.assertIn("december 1", text)

    def test_january_yields_offseason_message(self):
        lines = christmas_treat(date(1989, 1, 5))
        text = "\n".join(lines).lower()
        self.assertIn("hasn't arrived yet", text)

    def test_december_26_notes_calendar_closed(self):
        lines = christmas_treat(date(1988, 12, 26))
        text = "\n".join(lines).lower()
        self.assertIn("closed for the year", text)

    def test_default_day_resolves(self):
        lines = christmas_treat()
        self.assertTrue(lines)


class TestHolidayCBTopics(unittest.TestCase):
    def test_topics_nonempty_in_december(self):
        topics = christmas_cb_topics(date(1988, 12, 15))
        self.assertTrue(topics)
        self.assertEqual(topics, CHRISTMAS_CB_TOPICS)

    def test_topics_empty_outside_december(self):
        self.assertEqual(christmas_cb_topics(date(1988, 11, 15)), {})
        self.assertEqual(christmas_cb_topics(date(1989, 1, 5)), {})

    def test_topic_shape_matches_cb_topics(self):
        for key, topic in CHRISTMAS_CB_TOPICS.items():
            self.assertEqual(set(topic.keys()),
                             {"keywords", "handles", "responses", "followups"},
                             key)
            for field in ("keywords", "handles", "responses", "followups"):
                self.assertTrue(topic[field], f"{key}.{field} empty")
                for value in topic[field]:
                    self.assertIsInstance(value, str)

    def test_topic_handles_are_known_cb_handles(self):
        from cis_dynamic import HANDLES
        for key, topic in CHRISTMAS_CB_TOPICS.items():
            for handle in topic["handles"]:
                self.assertIn(handle, HANDLES, f"{key}: {handle}")

    def test_ambient_lines_present(self):
        self.assertTrue(CHRISTMAS_CB_LINES)
        for line in CHRISTMAS_CB_LINES:
            self.assertIsInstance(line, str)

    def test_cb_lines_browsable(self):
        lines = christmas_cb_lines(date(1988, 12, 15))
        text = "\n".join(lines)
        for key in CHRISTMAS_CB_TOPICS:
            self.assertIn(key.upper(), text)


class TestChristmasMusic(unittest.TestCase):
    def test_albums_present_with_verified_items(self):
        self.assertTrue(CHRISTMAS_ALBUMS)
        by_title = {a["title"]: a for a in CHRISTMAS_ALBUMS}
        very_special = by_title["A Very Special Christmas"]
        self.assertEqual(very_special["year"], 1987)
        self.assertIn("VERIFIED", very_special["note"])
        fresh_aire = by_title["A Fresh Aire Christmas"]
        self.assertEqual(fresh_aire["year"], 1988)
        self.assertIn("VERIFIED", fresh_aire["note"])

    def test_songs_present_with_verified_items(self):
        self.assertTrue(CHRISTMAS_SONGS)
        by_title = {s["title"]: s for s in CHRISTMAS_SONGS}
        hollis = by_title["Christmas in Hollis"]
        self.assertEqual(hollis["artist"], "Run-D.M.C.")
        self.assertEqual(hollis["year"], 1987)
        self.assertIn("VERIFIED", hollis["note"])

    def test_nothing_after_december_1988(self):
        for album in CHRISTMAS_ALBUMS:
            self.assertLessEqual(album["year"], 1988, album["title"])
        for song in CHRISTMAS_SONGS:
            self.assertLessEqual(song["year"], 1988, song["title"])

    def test_music_lines_render(self):
        lines = christmas_music_lines(date(1988, 12, 15))
        text = "\n".join(lines)
        self.assertIn("A Very Special Christmas", text)
        self.assertIn("A Fresh Aire Christmas", text)
        self.assertIn("Christmas in Hollis", text)


class TestMenuAndService(unittest.TestCase):
    def test_menu_lines_three_sections(self):
        sections = christmas_menu_lines(date(1988, 12, 15))
        self.assertEqual(len(sections), 3)
        titles = [title for title, _lines in sections]
        self.assertEqual(titles,
                         ["Advent Calendar", "Holiday CB Topics",
                          "Christmas Music"])
        for _title, lines in sections:
            self.assertTrue(lines)

    def test_service_returns_sections(self):
        app = ChristmasFakeApp()
        sections = christmas_service(app)
        self.assertEqual(len(sections), 3)

    def _run_menu(self, inputs):
        app = ChristmasFakeApp()
        buf = io.StringIO()
        with mock.patch("builtins.input", side_effect=inputs):
            with redirect_stdout(buf):
                christmas_menu(app, date(1988, 12, 15))
        return app, buf.getvalue()

    def test_menu_advent_browse_and_exit(self):
        app, printed = self._run_menu(["1", "M", "M"])
        self.assertEqual(printed, "", "menu must not use bare print()")
        self.assertTrue(app.output_lines)
        self.assertTrue(app.pages, "advent browse should show a text page")
        self.assertIn("ADVENT", app.pages[0][1])

    def test_menu_topics_and_music_sections(self):
        app, printed = self._run_menu(["2", "3", "M"])
        self.assertEqual(printed, "")
        titles = [title for _key, title, _lines in app.pages]
        self.assertIn("HOLIDAY CB TOPICS", titles)
        self.assertIn("CHRISTMAS MUSIC", titles)

    def test_menu_rejects_bad_choice(self):
        app, _printed = self._run_menu(["9", "M"])
        self.assertIn("Enter 1-3, or M.", app.output_lines)

    def test_menu_uses_header_and_clear(self):
        app, _printed = self._run_menu(["M"])
        self.assertTrue(app.cleared)
        self.assertIn("news", app.headers)


class TestModuleHygiene(unittest.TestCase):
    def test_no_hardcoded_absolute_paths(self):
        import inspect
        source = inspect.getsource(cis_christmas)
        self.assertNotIn("/home/", source)
        self.assertNotIn("/root/", source)

    def test_repo_root_derived_from_file(self):
        from pathlib import Path
        self.assertEqual(
            cis_christmas.REPO_ROOT,
            Path(cis_christmas.__file__).resolve().parent)


if __name__ == "__main__":
    unittest.main()


# =======================================================================
# Content pack 6: weather (merged from test_pack6_*.py)
# =======================================================================

class Pack6FakeApp:
    """Minimal stand-in for the app: captures ansi_scroll output."""

    def __init__(self):
        self.output_lines = []

    def ansi_scroll(self, text, delay=0.01):
        self.output_lines.append(str(text))
        return True


class TestRetrospectiveExists(unittest.TestCase):
    def test_weather_menu_lists_retrospective_section(self):
        titles = [title for title, _ in cis_weather.weather_menu_lines()]
        self.assertIn("1988 Weather Retrospective", titles)

    def test_weather_service_exposes_retrospective(self):
        sections = cis_weather.weather_service(Pack6FakeApp())
        titles = [title for title, _ in sections]
        self.assertIn("1988 Weather Retrospective", titles)

    def test_menu_rendering_shows_new_section(self):
        # Mimics weather_menu(): numbered sections scrolled via the app.
        app = Pack6FakeApp()
        sections = cis_weather.weather_service(app)
        app.ansi_scroll("WEATHER WIRE", 0.01)
        for index, (title, _lines) in enumerate(sections, 1):
            app.ansi_scroll(f"{index}  {title}", 0.01)
        shown = "\n".join(app.output_lines)
        self.assertIn("4  1988 Weather Retrospective", shown)


class TestGilbertVerifiedFacts(unittest.TestCase):
    def setUp(self):
        self.text = "\n".join(cis_weather.retrospective_lines()).upper()

    def test_minimum_pressure_888mb(self):
        self.assertIn("888 MB", self.text)

    def test_peak_winds_185mph(self):
        self.assertIn("185 MPH", self.text)

    def test_category_5(self):
        self.assertIn("CATEGORY 5", self.text)

    def test_formed_september_8(self):
        self.assertIn("SEPT  8", self.text)

    def test_jamaica_landfall_september_12(self):
        self.assertIn("SEPT 12", self.text)
        self.assertIn("JAMAICA", self.text)

    def test_yucatan_landfall_september_14(self):
        self.assertIn("SEPT 14", self.text)
        self.assertIn("YUCATAN", self.text)

    def test_northeast_mexico_landfall_september_16(self):
        self.assertIn("SEPT 16", self.text)
        self.assertIn("LA PESCA", self.text)

    def test_most_intense_on_record(self):
        self.assertIn("MOST INTENSE", self.text)

    def test_estimated_figures_marked(self):
        lines = cis_weather.retrospective_lines()
        gilbert = lines[lines.index("STORM OF THE SEASON: HURRICANE GILBERT"):]
        tail = "\n".join(gilbert)
        self.assertIn("(est.)", tail)


class TestDroughtVerifiedFacts(unittest.TestCase):
    def setUp(self):
        self.text = "\n".join(cis_weather.retrospective_lines()).upper()

    def test_drought_section_present(self):
        self.assertIn("DROUGHT OF 1988", self.text)

    def test_mississippi_barge_traffic(self):
        self.assertIn("MISSISSIPPI", self.text)
        self.assertIn("BARGE", self.text)

    def test_hansen_june_23_testimony(self):
        self.assertIn("JUNE 23", self.text)
        self.assertIn("HANSEN", self.text)

    def test_yellowstone_acreage(self):
        self.assertIn("800,000 ACRES", self.text)

    def test_yellowstone_firefighters(self):
        self.assertIn("25,000 FIREFIGHTERS", self.text)

    def test_yellowstone_snow_end(self):
        self.assertIn("SEPTEMBER 11", self.text)

    def test_losses_marked_estimated(self):
        lines = cis_weather.retrospective_lines()
        drought = lines[lines.index("THE LONG HOT SUMMER: DROUGHT OF 1988"):]
        self.assertIn("(est.)", "\n".join(drought))


class TestNoFutureDates(unittest.TestCase):
    def test_no_dates_after_december_1988(self):
        text = "\n".join(cis_weather.retrospective_lines())
        for year in range(1989, 2001):
            self.assertNotIn(str(year), text, f"post-1988 year leaked: {year}")

    def test_no_anachronistic_decades(self):
        text = "\n".join(cis_weather.retrospective_lines()).upper()
        self.assertNotIn("WILMA", text)  # 2005 storm, unknowable in 1988


class TestRetrospectiveShape(unittest.TestCase):
    def test_lines_are_non_empty_strings(self):
        lines = cis_weather.retrospective_lines()
        self.assertTrue(lines)
        self.assertTrue(all(isinstance(line, str) for line in lines))

    def test_terminal_line_width(self):
        # Wire terminal pages wrap badly past 80 columns.
        for line in cis_weather.retrospective_lines():
            self.assertLessEqual(len(line), 76, f"line too long: {line!r}")

    def test_sub_article_functions_return_lines(self):
        self.assertTrue(cis_weather.gilbert_retrospective_lines())
        self.assertTrue(cis_weather.drought_retrospective_lines())

    def test_retrospective_accepts_explicit_day(self):
        from datetime import date
        lines = cis_weather.retrospective_lines(date(1988, 12, 15))
        self.assertIn("WEATHER WIRE SPECIAL -- 1988 WEATHER RETROSPECTIVE", lines)


if __name__ == "__main__":
    unittest.main()

# ---------------------------------------------------------------------------
# Content pack 7: pack7_test_eliza
# ---------------------------------------------------------------------------
"""Standalone tests for the cis_eliza Eliza engine (content pack 7).

Run with:
    cd ~/workspace/compuserve-simulator && PYTHONPATH=. python3 /tmp/pack7_test_eliza.py -v
"""




import cis_eliza


class ElizaEngineTests(unittest.TestCase):
    # -- API contract --------------------------------------------------------

    def test_new_state_is_json_serializable(self):
        state = cis_eliza.new_state()
        self.assertIsInstance(state, dict)
        json.dumps(state)  # must not raise

    def test_respond_returns_reply_and_new_state(self):
        reply, new_state = cis_eliza.respond("hello", cis_eliza.new_state())
        self.assertIsInstance(reply, str)
        self.assertTrue(reply)
        self.assertIsInstance(new_state, dict)
        json.dumps(new_state)  # must not raise

    def test_respond_does_not_mutate_input_state(self):
        state = cis_eliza.new_state()
        snapshot = json.dumps(state)
        cis_eliza.respond("I am sad", state)
        self.assertEqual(json.dumps(state), snapshot)

    def test_state_stays_serializable_across_turns(self):
        state = cis_eliza.new_state()
        for line in ["hello", "I am sad", "My dog is cute", "why do you ask",
                     "xyzzy", "plugh", "qwerty", "bye"]:
            _reply, state = cis_eliza.respond(line, state)
            json.dumps(state)  # must not raise every turn

    # -- quit detection ------------------------------------------------------

    def test_is_quit_words(self):
        for text in ["bye", "Bye", "BYE!", "I think I should quit now",
                     "EXIT", "exit.", "goodbye", "Goodbye, Eliza.",
                     "  quit  "]:
            self.assertTrue(cis_eliza.is_quit(text), text)

    def test_is_quit_rejects_non_words(self):
        for text in ["", "quiet", "goodbyes", "exiting", "byebye",
                     "hello there", "I am quite happy"]:
            self.assertFalse(cis_eliza.is_quit(text), text)

    def test_quit_respond_gives_goodbye(self):
        reply, _state = cis_eliza.respond("bye", cis_eliza.new_state())
        self.assertIn("goodbye", reply.lower())

    # -- pronoun reflection --------------------------------------------------

    def test_i_am_reflects_to_you_are(self):
        reply, _state = cis_eliza.respond("I am sad", cis_eliza.new_state())
        self.assertIn("you are", reply.lower())
        self.assertIn("sad", reply.lower())

    def test_contraction_reflection(self):
        reply, _state = cis_eliza.respond("I'm worried", cis_eliza.new_state())
        self.assertIn("you are", reply.lower())
        self.assertIn("worried", reply.lower())

    def test_my_reflects_to_your(self):
        reply, _state = cis_eliza.respond("My dog is cute", cis_eliza.new_state())
        self.assertIn("your dog is cute", reply.lower())

    def test_you_are_reflects_to_i_am(self):
        reply, _state = cis_eliza.respond("You are clever", cis_eliza.new_state())
        self.assertIn("i am clever", reply.lower())

    # -- structural input/output pairs ---------------------------------------

    def test_hello_greeting(self):
        reply, _state = cis_eliza.respond("hello", cis_eliza.new_state())
        self.assertIn("how do you do", reply.lower())

    def test_want_rule(self):
        reply, _state = cis_eliza.respond("I want a new car", cis_eliza.new_state())
        self.assertEqual(reply, "What would you do if you got a new car?")

    def test_because_rule(self):
        reply, _state = cis_eliza.respond("because my dog ran away",
                                          cis_eliza.new_state())
        self.assertEqual(reply, "Is that the real reason?")

    def test_keyword_rank_i_am_beats_sad(self):
        # "I am sad" hits the higher-ranked I AM keyword, not SAD.
        reply, _state = cis_eliza.respond("I am sad", cis_eliza.new_state())
        self.assertIn("you are", reply.lower())

    def test_no_match_fallback_is_neutral(self):
        reply, _state = cis_eliza.respond("xyzzy plugh", cis_eliza.new_state())
        self.assertIn(reply, cis_eliza.NOTHING_MATCHED)

    # -- round-robin rule selection (deterministic) ----------------------------

    def test_round_robin_cycles_rules(self):
        state = cis_eliza.new_state()
        reply1, state = cis_eliza.respond("I am sad", state)
        reply2, state = cis_eliza.respond("I am sad", state)
        self.assertNotEqual(reply1, reply2)
        self.assertEqual(reply1, "Why do you say you are sad?")
        self.assertEqual(reply2, "How long have you been sad?")

    def test_round_robin_wraps_around(self):
        state = cis_eliza.new_state()
        replies = []
        for _ in range(5):  # I AM has 4 rules for "* I AM *"
            reply, state = cis_eliza.respond("I am sad", state)
            replies.append(reply)
        self.assertEqual(replies[0], replies[4])

    def test_deterministic_replay(self):
        def run():
            state = cis_eliza.new_state()
            out = []
            for line in ["hello", "I am sad", "My dog is cute", "why?",
                         "xyzzy", "plugh", "qwerty"]:
                reply, state = cis_eliza.respond(line, state)
                out.append(reply)
            return out

        self.assertEqual(run(), run())

    # -- memory queue --------------------------------------------------------

    def test_memory_callback_fires(self):
        state = cis_eliza.new_state()
        _r, state = cis_eliza.respond("My dog is cute", state)
        self.assertEqual(len(state["memory"]), 1)
        # Feed inputs that match no keyword; the memory callback fires
        # deterministically on a regular cadence.
        seen_callback = False
        for word in ["xyzzy", "plugh", "qwerty", "blorp", "snarf", "zizzle"]:
            reply, state = cis_eliza.respond(word, state)
            if "earlier you mentioned" in reply.lower():
                seen_callback = True
                self.assertIn("your dog is cute", reply.lower())
                break
        self.assertTrue(seen_callback, "memory callback never fired")

    def test_memory_item_consumed_once(self):
        state = cis_eliza.new_state()
        _r, state = cis_eliza.respond("My dog is cute", state)
        callbacks = 0
        for word in ["xyzzy", "plugh", "qwerty", "blorp", "snarf",
                     "zizzle", "wobble", "frotz", "gloop"]:
            reply, state = cis_eliza.respond(word, state)
            if "earlier you mentioned" in reply.lower():
                callbacks += 1
        self.assertEqual(callbacks, 1)
        self.assertEqual(state["memory"], [])

    def test_no_memory_callback_when_queue_empty(self):
        state = cis_eliza.new_state()
        for word in ["xyzzy", "plugh", "qwerty", "blorp", "snarf", "zizzle"]:
            reply, state = cis_eliza.respond(word, state)
            self.assertNotIn("earlier you mentioned", reply.lower())

# ---------------------------------------------------------------------------
# Content pack 7: pack7_test_arcade
# ---------------------------------------------------------------------------
"""Standalone tests for content pack 7 arcade additions: ELIZA + LUNAR LANDER.

Run: cd ~/workspace/compuserve-simulator && PYTHONPATH=. python3 /tmp/pack7_test_arcade.py -v
"""




import cis_arcade
from cis_arcade import RECORDS_KEY


# ---------------------------------------------------------------------------
# Fakes (mirror the ArcadeFakeApp / ArcadeFakeDynamic pattern in
# test_compuserve.py)
# ---------------------------------------------------------------------------

class FakeDynamic:
    """In-memory stand-in for app.cis_dynamic."""

    def __init__(self):
        self.state = {}

    def load_state(self, app):
        return self.state

    def save_state(self, app, state):
        self.state = state


class Pack7ArcadeFakeApp:
    def __init__(self, user_id="T100"):
        self.current_user_id = user_id
        self.cis_dynamic = FakeDynamic()
        self.output_lines = []

    def ansi_scroll(self, text, delay=0.01):
        self.output_lines.append(str(text))
        return True

    def output(self):
        return "\n".join(self.output_lines)


class FakeEliza:
    """Stub for the cis_eliza engine contract (built by Worker A)."""

    @staticmethod
    def new_state():
        return {"turns": 0}

    @staticmethod
    def is_quit(line):
        return line.strip().lower() in ("bye", "goodbye", "quit", "exit")

    @staticmethod
    def respond(line, state):
        state["turns"] += 1
        return ("Tell me more about that.", state)


# A scripted suicide-burn sequence for CADET / MARE TRANQUILLITATIS
# (alt 1500, vel 25, fuel 1200): free-fall, then full burn, then feathering.
# Verified to touch down at 5.0 ft/s (safe: <= 8.0).
SAFE_BURNS = (
    [0] * 12
    + [40] * 16
    + [0, 40, 0, 40, 0, 40, 0, 40, 0, 40, 0, 40, 0, 40, 0, 40]
)


class ArcadeElizaLanderTests(unittest.TestCase):
    def setUp(self):
        self._saved_eliza = sys.modules.get("cis_eliza")
        sys.modules["cis_eliza"] = FakeEliza

    def tearDown(self):
        if self._saved_eliza is None:
            sys.modules.pop("cis_eliza", None)
        else:
            sys.modules["cis_eliza"] = self._saved_eliza

    # -- menu ----------------------------------------------------------

    def test_menu_lists_six_games(self):
        keys = [key for key, _name, _blurb in cis_arcade.ARCADE_MENU]
        self.assertEqual(keys, ["1", "2", "3", "4", "5", "6"])
        names = [name for _key, name, _blurb in cis_arcade.ARCADE_MENU]
        self.assertIn("ELIZA", names)
        self.assertIn("LUNAR LANDER", names)

    def test_menu_text_shows_new_games(self):
        text = "\n".join(cis_arcade.arcade_menu_text())
        self.assertIn("ELIZA", text)
        self.assertIn("LUNAR LANDER", text)

    def test_play_prompt_says_pick_1_to_6(self):
        app = Pack7ArcadeFakeApp()
        with mock.patch.object(cis_arcade, "input", side_effect=["9", "M"]):
            cis_arcade.play(app)
        self.assertIn("Pick 1-6, or M to return.", app.output())

    def test_menu_choice_5_dispatches_to_eliza(self):
        app = Pack7ArcadeFakeApp()
        with mock.patch.object(cis_arcade, "play_eliza") as mock_eliza, \
             mock.patch.object(cis_arcade, "input", side_effect=["5", "M"]):
            cis_arcade.play(app)
        mock_eliza.assert_called_once_with(app, "T100")

    def test_menu_choice_6_dispatches_to_lander(self):
        app = Pack7ArcadeFakeApp()
        with mock.patch.object(cis_arcade, "play_lander") as mock_lander, \
             mock.patch.object(cis_arcade, "input", side_effect=["6", "M"]):
            cis_arcade.play(app)
        mock_lander.assert_called_once_with(app, "T100")

    # -- ELIZA ---------------------------------------------------------

    def test_eliza_session_ends_on_bye_and_records_session(self):
        app = Pack7ArcadeFakeApp()
        script = ["hello there", "tell me about my mother", "bye"]
        with mock.patch.object(cis_arcade, "input", side_effect=script):
            cis_arcade.play_eliza(app, "U1")
        out = app.output()
        self.assertIn("*** ELIZA ***", out)
        self.assertIn("ELIZA: Tell me more about that.", out)
        self.assertIn("ELIZA: Goodbye.", out)
        entry = app.cis_dynamic.state[RECORDS_KEY]["U1"]["eliza"]
        self.assertEqual(entry["eliza_sessions"], 1)
        self.assertEqual(entry["plays"], 1)
        self.assertIn("ARCADE LOG: ELIZA -- 1 session on file.", out)

    def test_eliza_quit_is_case_insensitive(self):
        app = Pack7ArcadeFakeApp()
        with mock.patch.object(cis_arcade, "input", side_effect=["BYE"]):
            cis_arcade.play_eliza(app, "U1")
        entry = app.cis_dynamic.state[RECORDS_KEY]["U1"]["eliza"]
        self.assertEqual(entry["eliza_sessions"], 1)
        self.assertIn("ELIZA: Goodbye.", app.output())

    def test_eliza_sessions_accumulate(self):
        app = Pack7ArcadeFakeApp()
        with mock.patch.object(cis_arcade, "input", side_effect=["bye"]):
            cis_arcade.play_eliza(app, "U1")
        with mock.patch.object(cis_arcade, "input", side_effect=["bye"]):
            cis_arcade.play_eliza(app, "U1")
        entry = app.cis_dynamic.state[RECORDS_KEY]["U1"]["eliza"]
        self.assertEqual(entry["eliza_sessions"], 2)

    def test_eliza_missing_module_is_graceful(self):
        app = Pack7ArcadeFakeApp()
        with mock.patch.dict(sys.modules, {"cis_eliza": None}):
            cis_arcade.play_eliza(app, "U1")
        self.assertIn("not installed", app.output())
        self.assertNotIn("U1", app.cis_dynamic.state.get(RECORDS_KEY, {}))

    # -- LUNAR LANDER engine -------------------------------------------

    def test_lander_engine_safe_burn_sequence_lands(self):
        game = cis_arcade.LanderGame(altitude=1500.0, velocity=25.0,
                                     fuel=1200.0)
        outcome = "flying"
        for burn in SAFE_BURNS:
            outcome = game.step(burn)
            if outcome != "flying":
                break
        self.assertEqual(outcome, "landed")
        self.assertLessEqual(game.landing_velocity,
                             cis_arcade.LANDER_SAFE_VELOCITY)

    def test_lander_engine_zero_burn_crashes(self):
        game = cis_arcade.LanderGame(altitude=1500.0, velocity=25.0,
                                     fuel=1200.0)
        outcome = "flying"
        for _ in range(200):
            outcome = game.step(0)
            if outcome != "flying":
                break
        self.assertEqual(outcome, "crashed")
        self.assertGreater(game.landing_velocity,
                           cis_arcade.LANDER_SAFE_VELOCITY)

    def test_lander_engine_burn_clamped_to_fuel(self):
        game = cis_arcade.LanderGame(fuel=10.0)
        game.step(40)
        self.assertEqual(game.fuel, 0.0)

    def test_lander_grades(self):
        self.assertIn("FEATHER-SOFT", cis_arcade.lander_grade(2.0))
        self.assertIn("Eagle", cis_arcade.lander_grade(5.0))
        self.assertIn("hard landing", cis_arcade.lander_grade(7.9))

    # -- LUNAR LANDER interactive --------------------------------------

    def _lander_script(self, burns, difficulty="1", site="1"):
        return [difficulty, site] + [str(b) for b in burns]

    def test_lander_interactive_safe_landing_records(self):
        app = Pack7ArcadeFakeApp()
        with mock.patch.object(cis_arcade, "input",
                               side_effect=self._lander_script(SAFE_BURNS)):
            cis_arcade.play_lander(app, "U1")
        out = app.output()
        self.assertIn("TOUCHDOWN AT 5.0 FT/S!", out)
        self.assertIn("Eagle has landed", out)
        entry = app.cis_dynamic.state[RECORDS_KEY]["U1"]["lander"]
        self.assertEqual(entry["lander_landings"], 1)
        self.assertAlmostEqual(entry["lander_best_velocity"], 5.0)
        self.assertIn("1 soft landing", out)

    def test_lander_interactive_crash_records_no_landing(self):
        app = Pack7ArcadeFakeApp()
        with mock.patch.object(cis_arcade, "input",
                               side_effect=self._lander_script([0] * 60)):
            cis_arcade.play_lander(app, "U1")
        out = app.output()
        self.assertIn("NEW CRATER", out)
        entry = app.cis_dynamic.state[RECORDS_KEY]["U1"]["lander"]
        self.assertEqual(entry.get("lander_landings", 0), 0)
        self.assertNotIn("lander_best_velocity", entry)
        self.assertEqual(entry["plays"], 1)

    def test_lander_invalid_burn_reprompts(self):
        app = Pack7ArcadeFakeApp()
        script = self._lander_script(["abc", "99"] + [0] * 60)
        with mock.patch.object(cis_arcade, "input", side_effect=script):
            cis_arcade.play_lander(app, "U1")
        self.assertIn("?REDO", app.output())

    def test_lander_best_velocity_tracks_softest(self):
        app = Pack7ArcadeFakeApp()
        cis_arcade.record_lander_result(app, "U1", True, 5.0)
        cis_arcade.record_lander_result(app, "U1", True, 3.2)
        cis_arcade.record_lander_result(app, "U1", True, 7.5)
        cis_arcade.record_lander_result(app, "U1", False, 40.0)
        entry = app.cis_dynamic.state[RECORDS_KEY]["U1"]["lander"]
        self.assertEqual(entry["lander_landings"], 3)
        self.assertAlmostEqual(entry["lander_best_velocity"], 3.2)
        self.assertEqual(entry["plays"], 4)

    def test_lander_abort_on_bad_menu_pick_then_quit(self):
        app = Pack7ArcadeFakeApp()
        with mock.patch.object(cis_arcade, "input",
                               side_effect=["9", "1", "1"] + ["0"] * 60):
            cis_arcade.play_lander(app, "U1")
        self.assertIn("?REDO -- PICK 1 OR 2.", app.output())

    # -- records display -----------------------------------------------

    def test_records_lines_cover_both_new_games(self):
        state = {
            RECORDS_KEY: {
                "U1": {
                    "eliza": {"plays": 2, "wins": 0, "best": 0,
                              "best_note": "", "eliza_sessions": 2},
                    "lander": {"plays": 3, "wins": 2, "best": 0,
                               "best_note": "", "lander_landings": 2,
                               "lander_best_velocity": 4.2},
                }
            }
        }
        lines = cis_arcade.arcade_records_lines(state, "U1")
        self.assertEqual(len(lines), 6)
        eliza_line = next(l for l in lines if "ELIZA" in l)
        lander_line = next(l for l in lines if "LANDER" in l)
        self.assertIn("SESSIONS 2", eliza_line)
        self.assertIn("BEST ---", eliza_line)
        self.assertIn("LANDINGS 2", lander_line)
        self.assertIn("4.2 softest touchdown ft/s", lander_line)

    def test_records_lines_empty_state(self):
        lines = cis_arcade.arcade_records_lines({}, "NOBODY")
        self.assertEqual(len(lines), 6)
        self.assertTrue(all("BEST ---" in l for l in lines[-2:]))

# ---------------------------------------------------------------------------
# Content pack 7: pack7_test_cb
# ---------------------------------------------------------------------------
"""Standalone tests for Worker C: Eliza CB responder (content pack 7).

Run: cd ~/workspace/compuserve-simulator && PYTHONPATH=. python3 /tmp/pack7_test_cb.py -v
"""







class FakeElizaEngine(types.ModuleType):
    """Stand-in for Worker A's cis_eliza module, honoring the exact contract."""

    def new_state(self):
        return {"turns": 0, "last_topic": None}

    def is_quit(self, text):
        lowered = text.lower()
        return any(word in lowered for word in ("bye", "goodbye", "quit", "exit"))

    def respond(self, text, state):
        state = dict(state)
        state["turns"] += 1
        if self.is_quit(text):
            return "Goodbye. I am glad we could talk. Please come back anytime.", state
        lowered = text.lower()
        if "worried about" in lowered:
            topic = lowered.split("worried about", 1)[1].strip(" .!")
            topic = re.sub(r"\bmy\b", "your", topic)
            state["last_topic"] = topic
            reply = f"Why do you say you are worried about {topic}?"
        elif "i am" in lowered:
            reply = "How long have you felt that way?"
        else:
            reply = "Please go on."
        if state["turns"] > 1 and state.get("last_topic"):
            reply += f" Earlier you mentioned {state['last_topic']}."
        return reply, state


sys.modules["cis_eliza"] = FakeElizaEngine("cis_eliza")

import compuserve  # noqa: E402
import cis_cb  # noqa: E402
from compuserve import eliza_cb_reply, personality_line, get_channel_personality  # noqa: E402


class Pack7CbFakeApp:
    def __init__(self):
        self.scrolled = []

    def ansi_scroll(self, text, delay):
        self.scrolled.append((text, delay))


# Every line in the random one-liner pools; an engine reply must never be one.
ONE_LINER_POOL = {
    "Nice to see everyone here tonight.",
    "Hope your connections are solid!",
    "Good crowd on this channel.",
    "Always good vibes in here.",
    "What is even happening in here?",
    "This channel is pure chaos.",
    "Messages flying faster than 2400 baud.",
    "Someone lost control of their keyboard.",
    "Anyone debugging IRQ conflicts?",
    "Let\u2019s talk BIOS settings.",
    "Who\u2019s tweaking their CONFIG.SYS tonight?",
    "Channel 3: where the tech nerds live.",
    "Eliza really listens, you know.",
    "I told Eliza my troubles last night. Felt better after.",
}


class CbElizaTests(unittest.TestCase):
    def setUp(self):
        self.app = Pack7CbFakeApp()
        compuserve._ELIZA_STATES.clear()

    def test_channel4_registered(self):
        self.assertIn("Eliza", cis_cb.CHANNELS["4"])
        self.assertEqual(get_channel_personality("4"), "eliza")

    def test_engine_reply_reflects_and_not_pool(self):
        reply = eliza_cb_reply(self.app, "70000,0001", "I am worried about my job")
        # Reflection of the user's words, from the engine:
        self.assertIn("your job", reply.lower())
        # Never a random one-liner:
        self.assertNotIn(reply, ONE_LINER_POOL)
        # Posted through the app's ansi_scroll as ELIZA:
        self.assertTrue(self.app.scrolled)
        self.assertTrue(self.app.scrolled[-1][0].startswith("<ELIZA> "))
        self.assertIn(reply, self.app.scrolled[-1][0])

    def test_state_persists_across_turns(self):
        first = eliza_cb_reply(self.app, "70000,0001", "I am worried about my job")
        second = eliza_cb_reply(self.app, "70000,0001", "It keeps me up at night")
        # Engine remembers the earlier topic -> replies differ meaningfully:
        self.assertNotEqual(first, second)
        self.assertIn("job", second.lower())
        self.assertEqual(compuserve._ELIZA_STATES["70000,0001"]["turns"], 2)

    def test_state_keyed_per_user(self):
        eliza_cb_reply(self.app, "70000,0001", "I am worried about my job")
        eliza_cb_reply(self.app, "70001,0002", "Hello there")
        self.assertEqual(set(compuserve._ELIZA_STATES), {"70000,0001", "70001,0002"})
        self.assertEqual(compuserve._ELIZA_STATES["70001,0002"]["turns"], 1)

    def test_quit_yields_goodbye_and_clears_state(self):
        eliza_cb_reply(self.app, "70000,0001", "I am worried about my job")
        reply = eliza_cb_reply(self.app, "70000,0001", "goodbye")
        self.assertIn("goodbye", reply.lower())
        self.assertNotIn("70000,0001", compuserve._ELIZA_STATES)
        # Next visit starts fresh:
        fresh = eliza_cb_reply(self.app, "70000,0001", "hello again")
        self.assertNotIn("job", fresh.lower())

    def test_engine_missing_degrades_gracefully(self):
        # sys.modules entry None makes "import cis_eliza" raise ImportError,
        # simulating a genuinely absent engine (deleting the entry would just
        # re-import the module from disk).
        with mock.patch.dict(sys.modules, {"cis_eliza": None}):
            reply = eliza_cb_reply(self.app, "70000,0001", "hello")
            self.assertIn("away", reply.lower())
            self.assertTrue(self.app.scrolled[-1][0].startswith("<ELIZA> "))

    def test_eliza_ambient_line_is_acknowledgement(self):
        seen = {personality_line("eliza") for _ in range(50)}
        self.assertTrue(seen <= {
            "Eliza really listens, you know.",
            "I told Eliza my troubles last night. Felt better after.",
        })

    def test_channels_1_to_3_unchanged(self):
        self.assertEqual(cis_cb.CHANNELS["1"], "The Lobby - general conversation")
        self.assertEqual(cis_cb.CHANNELS["2"], "The Lounge - friendly social chat")
        self.assertEqual(cis_cb.CHANNELS["3"], "Technical Exchange - computers and communications")
        self.assertEqual(get_channel_personality("1"), "friendly")
        self.assertEqual(get_channel_personality("2"), "chaotic")
        self.assertEqual(get_channel_personality("3"), "technical")

# ---------------------------------------------------------------------------
# Content pack 7: pack7_test_pets
# ---------------------------------------------------------------------------
"""Standalone tests for the Pets & Animals Forum content module (cis_pets)."""



import cis_pets

REQUIRED_KEYS = {"content_id", "section", "date", "author", "subject", "body", "parent"}
VALID_SECTIONS = {"pets_dogs", "pets_cats", "pets_birds", "pets_fish", "pets_small", "pets_vet"}
PACK7_PETS_EXPECTED_SECTIONS = {
    "1": ("pets_dogs", "Dogs"),
    "2": ("pets_cats", "Cats"),
    "3": ("pets_birds", "Birds"),
    "4": ("pets_fish", "Fish & Aquariums"),
    "5": ("pets_small", "Small Pets"),
    "6": ("pets_vet", "Ask the Vet"),
}


class PetsForumTests(unittest.TestCase):
    def test_section_spec_has_six_sections_with_exact_keys(self):
        spec = cis_pets.section_spec()
        self.assertEqual(len(spec), 6)
        self.assertEqual(spec, PACK7_PETS_EXPECTED_SECTIONS)

    def test_seed_posts_count_and_keys(self):
        posts = cis_pets.SEED_POSTS
        self.assertEqual(len(posts), 16)
        for post in posts:
            self.assertEqual(set(post.keys()), REQUIRED_KEYS)

    def test_seed_post_content_ids_unique_and_numbered(self):
        ids = [p["content_id"] for p in cis_pets.SEED_POSTS]
        self.assertEqual(len(set(ids)), 16)
        expected = {"pets-1988-%03d" % n for n in range(1, 17)}
        self.assertEqual(set(ids), expected)

    def test_seed_post_sections_valid(self):
        for post in cis_pets.SEED_POSTS:
            self.assertIn(post["section"], VALID_SECTIONS)

    def test_seed_post_dates_december_1988(self):
        for post in cis_pets.SEED_POSTS:
            self.assertRegex(post["date"], r"^12/\d{2}/88$")

    def test_seed_post_parents_none(self):
        for post in cis_pets.SEED_POSTS:
            self.assertIsNone(post["parent"])

    def test_seed_posts_returns_copies(self):
        posts = cis_pets.seed_posts()
        self.assertEqual(len(posts), 16)
        posts[0]["subject"] = "MUTATED"
        posts[0]["content_id"] = "MUTATED"
        self.assertNotEqual(cis_pets.SEED_POSTS[0]["subject"], "MUTATED")
        self.assertNotEqual(cis_pets.SEED_POSTS[0]["content_id"], "MUTATED")

# ---------------------------------------------------------------------------
# Content pack 7: pack7_test_trains
# ---------------------------------------------------------------------------
"""Standalone tests for content pack 7 worker E: cis_photo + cis_trains.

Run: cd ~/workspace/compuserve-simulator && PYTHONPATH=. python3 /tmp/pack7_test_trains.py -v
"""



import cis_photo
import cis_trains


EXPECTED_KEYS = {"content_id", "section", "date", "author", "subject", "body", "parent"}

PHOTO_SECTIONS = {
    "1": ("photography_general", "General"),
    "2": ("photo_cameras", "Cameras & Lenses"),
    "3": ("photo_darkroom", "Darkroom"),
    "4": ("photo_composition", "Composition & Technique"),
    "5": ("photo_film", "Film & Processing"),
}

TRAINS_SECTIONS = {
    "1": ("trains_layout", "Layout Design"),
    "2": ("trains_dcc", "DCC & Wiring"),
    "3": ("trains_locos", "Locomotives"),
    "4": ("trains_scenery", "Scenery"),
    "5": ("trains_prototype", "Prototype Research"),
    "6": ("trains_trade", "Buy/Sell/Trade"),
}


class TrainsPhotoTests(unittest.TestCase):
    def check_module(self, mod, expected_sections, id_prefix, min_posts, max_posts):
        # section keys exact
        self.assertEqual(mod.section_spec(), expected_sections)
        self.assertEqual(mod.SECTIONS, expected_sections)
        slugs = {slug for slug, _title in expected_sections.values()}

        posts = mod.seed_posts()
        self.assertTrue(min_posts <= len(posts) <= max_posts,
                        f"{mod.FORUM_ID}: {len(posts)} posts out of range")

        seen_ids = set()
        for post in posts:
            # exactly the 7 keys
            self.assertEqual(set(post.keys()), EXPECTED_KEYS, post.get("content_id"))
            # valid section slug
            self.assertIn(post["section"], slugs, post["content_id"])
            # unique content ids with right prefix
            cid = post["content_id"]
            self.assertTrue(cid.startswith(id_prefix), cid)
            self.assertNotIn(cid, seen_ids, f"duplicate {cid}")
            seen_ids.add(cid)
            # December 1988 date, MM/DD/88 shape
            month, day, year = post["date"].split("/")
            self.assertEqual((month, year), ("12", "88"), cid)
            self.assertTrue(1 <= int(day) <= 31, cid)
            # non-empty strings
            for field in ("author", "subject", "body"):
                self.assertTrue(post[field] and isinstance(post[field], str), cid)
            self.assertIsNone(post["parent"], cid)

        # seed_posts() returns copies: mutating must not affect the module
        posts[0]["subject"] = "MUTATED"
        posts[0]["body"] = "MUTATED"
        fresh = mod.seed_posts()
        self.assertNotEqual(fresh[0]["subject"], "MUTATED")
        self.assertNotEqual(fresh[0]["body"], "MUTATED")
        self.assertEqual(mod.SEED_POSTS[0]["subject"], fresh[0]["subject"])

        # repo root rule: no hardcoded absolute paths in module
        self.assertTrue(mod.REPO_ROOT.is_absolute())

    def test_photo_module(self):
        self.assertEqual(cis_photo.FORUM_ID, "photo")
        self.assertEqual(cis_photo.FORUM_TITLE, "Photography Forum")
        # existing section key preserved for wiring compatibility
        self.assertEqual(cis_photo.SECTIONS["1"], ("photography_general", "General"))
        self.check_module(cis_photo, PHOTO_SECTIONS, "photo-1988-", 12, 16)

    def test_trains_module(self):
        self.assertEqual(cis_trains.FORUM_ID, "trains")
        self.assertEqual(cis_trains.FORUM_TITLE, "Model Railroading Forum")
        self.check_module(cis_trains, TRAINS_SECTIONS, "trains-1988-", 16, 16)
        # exactly 16 with sequential ids
        ids = sorted(p["content_id"] for p in cis_trains.seed_posts())
        self.assertEqual(ids, [f"trains-1988-{i:03d}" for i in range(1, 17)])

    def test_photo_ids_sequential(self):
        ids = sorted(p["content_id"] for p in cis_photo.seed_posts())
        self.assertEqual(ids, [f"photo-1988-{i:03d}" for i in range(1, len(ids) + 1)])

# ---------------------------------------------------------------------------
# Content pack 7: pack7_test_hamnet
# ---------------------------------------------------------------------------
"""Standalone tests for the content-pack-7 Broadcast Listening workstream.

Tests the pure broadcast helper, schedule data integrity, and the new
hamnet board menu option -- in cis_hamnet.py only. Run with:

    cd ~/workspace/compuserve-simulator && PYTHONPATH=. python3 /tmp/pack7_test_hamnet.py -v
"""


from datetime import datetime, timezone  # already imported above

import cis_hamnet
from cis_hamnet import (
    BROADCAST_SERVICES,
    broadcasts_on_now,
    render_broadcast_schedule,
    run_hamnet_board,
    section_spec,
    seed_posts,
)

# ITU broadcast bands in use in 1988 (from a contemporary SWL band chart).
BROADCAST_BANDS_KHZ = [
    (2300, 2495), (3200, 3400), (3900, 4000), (4750, 5060),
    (5850, 6200), (7100, 7350), (9400, 9900), (11600, 12050),
    (13570, 13800), (15100, 15800), (17480, 17900), (18900, 19020),
    (21450, 21850), (25600, 26100),
]


def in_broadcast_band(freq_khz):
    return any(lo <= freq_khz <= hi for lo, hi in BROADCAST_BANDS_KHZ)


class HamnetFakeApp:
    """Fake app capturing ansi_scroll output (mirrors ArcadeFakeApp)."""

    def __init__(self):
        self.scrolled = []

    def ansi_scroll(self, text, delay=0.01):
        self.scrolled.append(str(text))
        return True


class HamnetBroadcastTests(unittest.TestCase):
    # -- pure helper: broadcasts_on_now -----------------------------------

    def test_voa_on_in_early_utc_evening(self):
        # VOA English to the Caribbean/Latin America: 00:00-02:00 UTC.
        on = broadcasts_on_now(datetime(1988, 12, 15, 1, 0))
        services = [b["service"] for b in on]
        self.assertIn("Voice of America", services)
        voa = next(b for b in on if b["service"] == "Voice of America")
        self.assertEqual(voa["freqs_khz"], [5995, 6130, 9455, 9775, 11695])

    def test_dead_air_time_returns_empty(self):
        # 04:30 UTC: after the DW 03:00 block, before the 05:00 block.
        self.assertEqual(broadcasts_on_now(datetime(1988, 12, 15, 4, 30)), [])
        # Midday UTC: nothing in the evening-oriented schedule.
        self.assertEqual(broadcasts_on_now(datetime(1988, 12, 15, 12, 0)), [])

    def test_window_edge_boundary(self):
        # BBC evening service is [23:00, 03:30): on just before, off at.
        bbc = lambda dt: [
            b for b in broadcasts_on_now(dt)
            if b["service"] == "BBC World Service"
        ]
        self.assertTrue(bbc(datetime(1988, 12, 15, 23, 0)))
        self.assertTrue(bbc(datetime(1988, 12, 16, 3, 29)))
        self.assertFalse(bbc(datetime(1988, 12, 16, 3, 30)))
        # DW 03:00-03:50 block is still on at 03:30 (independent check).
        dw = [
            b for b in broadcasts_on_now(datetime(1988, 12, 16, 3, 30))
            if b["service"] == "Deutsche Welle"
        ]
        self.assertTrue(dw)

    def test_overnight_wrap(self):
        # 23:00-03:30 window spans midnight; both sides are on air.
        self.assertTrue(
            any(b["service"] == "BBC World Service"
                for b in broadcasts_on_now(datetime(1988, 12, 15, 23, 30)))
        )
        self.assertTrue(
            any(b["service"] == "BBC World Service"
                for b in broadcasts_on_now(datetime(1988, 12, 16, 0, 30)))
        )

    def test_helper_is_pure(self):
        before = [dict(e) for s in BROADCAST_SERVICES for e in s["entries"]]
        on = broadcasts_on_now(datetime(1988, 12, 15, 1, 0))
        self.assertTrue(on)
        for item in on:
            self.assertIn("service", item)
            self.assertIn("freqs_khz", item)
        after = [dict(e) for s in BROADCAST_SERVICES for e in s["entries"]]
        self.assertEqual(before, after)  # no mutation of module data

    def test_timezone_aware_datetime_accepted(self):
        on = broadcasts_on_now(
            datetime(1988, 12, 15, 1, 0, tzinfo=timezone.utc)
        )
        self.assertTrue(any(b["service"] == "BBC World Service" for b in on))

    # -- schedule data integrity -------------------------------------------

    def test_three_services_present(self):
        names = [s["service"] for s in BROADCAST_SERVICES]
        self.assertEqual(
            names, ["BBC World Service", "Voice of America", "Deutsche Welle"]
        )

    def test_frequencies_are_plausible_shortwave_bands(self):
        for service in BROADCAST_SERVICES:
            for entry in service["entries"]:
                self.assertTrue(entry["freqs_khz"], entry["label"])
                for freq in entry["freqs_khz"]:
                    self.assertTrue(
                        in_broadcast_band(freq),
                        f"{freq} kHz not in an ITU broadcast band",
                    )

    def test_entries_carry_verified_or_estimate_marking(self):
        for service in BROADCAST_SERVICES:
            for entry in service["entries"]:
                self.assertIn("verified", entry)
                self.assertIsInstance(entry["verified"], bool)
                self.assertIn("source", entry)
                self.assertTrue(entry["source"].strip())
        rendered = render_broadcast_schedule()
        self.assertIn("(verified)", rendered)
        self.assertIn("(est.)", rendered)

    def test_windows_parse_and_are_sane(self):
        for service in BROADCAST_SERVICES:
            for entry in service["entries"]:
                for key in ("start_utc", "end_utc"):
                    hh, mm = entry[key].split(":")
                    self.assertTrue(0 <= int(hh) < 24, entry[key])
                    self.assertTrue(0 <= int(mm) < 60, entry[key])

    # -- menu wiring --------------------------------------------------------

    def test_section_spec_includes_broadcast_listening(self):
        spec = section_spec()
        self.assertEqual(
            spec["8"], ("hamnet_broadcast", "Broadcast Listening")
        )

    def test_menu_option_4_scrolls_schedule(self):
        app = HamnetFakeApp()
        choices = iter(["4", "Q"])
        real_input = cis_hamnet.input
        cis_hamnet.input = lambda prompt="": next(choices)
        try:
            run_hamnet_board(app)
        finally:
            cis_hamnet.input = real_input
        text = "\n".join(app.scrolled)
        self.assertIn("BBC World Service", text)
        self.assertIn("6175", text)
        self.assertIn("Deutsche Welle", text)
        self.assertIn("VOICE OF AMERICA", text)

    def test_seed_post_announces_broadcast_section(self):
        posts = seed_posts()
        ids = [p["content_id"] for p in posts]
        self.assertEqual(len(ids), len(set(ids)))  # unique ids
        post = next(p for p in posts if p["section"] == "hamnet_broadcast")
        self.assertEqual(post["content_id"], "hamnet-1988-017")
        self.assertEqual(post["date"], "12/17/88")
