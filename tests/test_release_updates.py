"""Regression coverage for time-capsule boundaries and service discovery."""
from datetime import date
import unittest
from unittest.mock import patch

import compuserve as app
import cis_discovery
import cis_yearend
from cis_archive import archive_service, in_archive
from cis_session import GoNavigation, SessionState, active_session


class PublicationTests(unittest.TestCase):
    def test_1981_has_no_yearend_stories(self):
        self.assertEqual(cis_yearend.yearend_menu_lines(date(1981, 4, 12)), [])

    def test_election_publication_boundary(self):
        self.assertEqual(cis_yearend.election_lines(date(1988, 11, 8)), [])
        self.assertTrue(cis_yearend.election_lines(date(1988, 11, 9)))

    def test_roundup_publication_boundary(self):
        self.assertEqual(cis_yearend.bestof_lines(date(1988, 12, 30)), [])
        self.assertTrue(cis_yearend.bestof_lines(date(1988, 12, 31)))

    def test_empty_menu_explains_date_without_prompting(self):
        with patch.object(app, 'text_page') as page:
            cis_yearend.yearend_menu(app, date(1981, 4, 12))
        self.assertIn('No year-end stories', page.call_args.args[2][0])

    def test_briefing_does_not_reuse_future_anniversary(self):
        with active_session(SessionState(simulation_date=date(1981, 12, 7))), \
                patch.object(app.cis_discovery, 'activity_items', return_value=[]), \
                patch.object(app.cis_timeline, 'RECORDS', [
                    {'id': 'FUTURE', 'date': '1988-12-07', 'title': 'Future earthquake'}]):
            self.assertNotIn('Future earthquake', '\n'.join(app.today_in_1988_lines(False)))

    def test_archive_scope_clears_after_go_jump(self):
        @archive_service
        def leave():
            self.assertTrue(cis_discovery.archive_notice('news'))
            raise GoNavigation('GO CB')
        with self.assertRaises(GoNavigation):
            leave()
        self.assertFalse(in_archive.get())
        self.assertFalse(cis_discovery.archive_notice('news'))

    def test_archive_label_on_nested_news_page(self):
        output = []
        with patch.object(app, 'ansi_scroll', side_effect=lambda line, *args: output.append(line)), \
                patch.object(app, 'clear'), patch.object(app, 'input', side_effect=['1', '', 'M']):
            app.sports_menu()
        self.assertGreaterEqual(output.count('DECEMBER 1988 ARCHIVE'), 3)


class DiscoveryTests(unittest.TestCase):
    def test_three_resolvable_choices_across_eras(self):
        for day in (date(1979, 1, 1), date(1981, 4, 12), date(1988, 12, 1),
                    date(1988, 12, 25), date(1988, 12, 31), date(1998, 12, 31)):
            with self.subTest(day=day):
                choices = cis_discovery.start_suggestions(day)
                self.assertEqual(len(choices), 3)
                self.assertEqual(len({item[1] for item in choices}), 3)
                for _, command, _ in choices:
                    self.assertTrue(app.resolve_go_destination(command[3:], 'main'))

    def test_featured_and_seasonal_recommendations(self):
        self.assertEqual(cis_discovery.start_suggestions(date(1981, 4, 12))[0][1], 'GO NEWS')
        self.assertEqual(cis_discovery.start_suggestions(date(1988, 12, 20))[1][1], 'GO CHRISTMAS')
        self.assertEqual(cis_discovery.start_suggestions(date(1988, 12, 31))[1][1], 'GO YEARINREVIEW')

    def test_start_choice_uses_navigation_jump(self):
        with active_session(SessionState(simulation_date=date(1981, 4, 12))), \
                patch.object(app, 'ansi_scroll'), patch.object(app, 'clear'), \
                patch.object(app, 'input', side_effect=['bad', '1']):
            with self.assertRaises(GoNavigation) as caught:
                app.start_here()
        self.assertEqual(caught.exception.command, 'GO NEWS')

    def test_direct_shortcuts_open_services(self):
        handlers = {'SPORTS': 'sports_menu', 'BOOKS': 'books_menu',
                    'ENTERTAINMENT': 'entertainment_menu', 'WEATHERWIRE': 'weather_menu',
                    'YEARINREVIEW': 'yearend_menu', 'GIFTGUIDE': 'giftguide_menu',
                    'CHRISTMAS': 'christmas_menu', 'START': 'start_here'}
        for command, handler in handlers.items():
            with self.subTest(command=command), patch.object(app, handler) as service:
                self.assertTrue(app.open_go_destination(app.resolve_go_destination(command, 'main'), ['main']))
                service.assert_called_once_with()
        for command, handler, choice in [('CROSSWORD', 'games_service', '8'),
                                          ('TRADINGPOST', 'shopping_service', '6')]:
            with patch.object(app, handler) as service:
                app.open_go_destination(app.resolve_go_destination(command, 'main'), ['main'])
                service.assert_called_once_with(choice)
        with patch.object(app.cis_arcade, 'play') as play:
            app.open_go_destination(app.resolve_go_destination('ARCADE', 'main'), ['main'])
            play.assert_called_once_with(app)


if __name__ == '__main__':
    unittest.main()
