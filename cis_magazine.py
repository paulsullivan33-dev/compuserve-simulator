"""Original weekly magazine, released according to the simulation calendar."""

from datetime import date
import json
from pathlib import Path

from cis_terminal import wrap_terminal_text
from cis_web_files import offer_download


CATALOG = json.loads(Path(__file__).with_name('magazine_issues.json').read_text(encoding='utf-8'))
ISSUES = CATALOG['issues']


def available(day):
    return sorted((issue for issue in ISSUES if date.fromisoformat(issue['date']) <= day),
                  key=lambda issue: issue['date'], reverse=True)


def find_issue(identifier, day):
    return next((issue for issue in available(day) if issue['id'] == identifier.upper()), None)


def search(query, day):
    words = query.casefold().split()
    if not words:
        return []
    return [(issue, article) for issue in available(day) for article in issue['articles'] if all(
        word in ' '.join([article['title'], article['department'], article['author'], *article['paragraphs']]).casefold()
        for word in words)]


def read_count(app, issue):
    seen = set(app.current_profile.get('magazine_read', []))
    return sum(article['id'] in seen for article in issue['articles'])


def mark_read(app, issue, article):
    seen = app.current_profile.setdefault('magazine_read', [])
    last = app.current_profile.setdefault('magazine_last', {})
    changed = last.get(issue['id']) != article['id'] or article['id'] not in seen
    last[issue['id']] = article['id']
    if article['id'] not in seen:
        seen.append(article['id'])
    if changed:
        app.save_profiles()


def article_lines(issue, article):
    lines = [f"{CATALOG['title']} / {issue['id']} / {issue['date']}",
             article['department'].upper(), article['title'], f"By {article['author']}", '']
    for paragraph in article['paragraphs']:
        lines.extend([paragraph, ''])
    if article.get('related'):
        lines.extend(['ELSEWHERE ON THE SERVICE', *article['related'], ''])
    return lines


def export_issue(app, issue):
    if find_issue(issue['id'], app.cis_dynamic.simulation_day()) is None:
        raise ValueError('This issue has not been published yet.')
    lines = [CATALOG['title'].upper(), f"{issue['id']} - {issue['date']}", issue['title'],
             CATALOG['notice'], '', 'CONTENTS']
    lines.extend(f"{index}. {article['department']} - {article['title']}" for index, article in enumerate(issue['articles'], 1))
    for article in issue['articles']:
        lines.extend(['', '=' * 72, '', *article_lines(issue, article)])
    rendered = [line for text in lines for line in wrap_terminal_text(text, 72)]
    destination = app.BASE_DIR / 'downloads' / f"{issue['id']}.TXT"
    destination.parent.mkdir(exist_ok=True)
    destination.write_bytes(('\r\n'.join(rendered) + '\r\n').encode('ascii'))
    offer_download(destination)
    return destination


def _download(app, issue):
    path = export_issue(app, issue)
    app.ansi_scroll(f'Full issue saved: {path.name}', 0.01)


def read_article(app, issue, index):
    while True:
        app.clear()
        app.header_bar('magazine')
        article = issue['articles'][index]
        app.ansi_scroll(f"ARTICLE {index + 1} OF {len(issue['articles'])}", 0.01)
        for line in article_lines(issue, article):
            app.ansi_scroll(line, 0.005)
        mark_read(app, issue, article)
        while True:
            command = input('N next, P previous, D download issue, M contents ! ').strip().upper()
            if command in ('', 'M'):
                return
            if command in ('D', 'DOWNLOAD'):
                _download(app, issue)
                continue
            if command == 'N' and index + 1 < len(issue['articles']):
                index += 1
                break
            if command == 'P' and index > 0:
                index -= 1
                break
            app.ansi_scroll('No next article.' if command == 'N' else 'No previous article.' if command == 'P' else 'Enter N, P, D, or M.', 0.01)


def issue_menu(app, issue, article_id=None):
    if article_id:
        index = next((i for i, article in enumerate(issue['articles']) if article['id'] == article_id), None)
        if index is not None:
            read_article(app, issue, index)
    while True:
        app.clear()
        app.header_bar('magazine')
        app.ansi_scroll(f"{issue['id']} / {issue['date']} / {issue['title']}", 0.01)
        app.ansi_scroll(CATALOG['notice'], 0.005)
        seen = set(app.current_profile.get('magazine_read', []))
        for index, article in enumerate(issue['articles'], 1):
            status = 'READ' if article['id'] in seen else 'NEW'
            app.ansi_scroll(f"{index} [{status}] {article['department']}: {article['title']}", 0.005)
        command = input('Article number, R resume, D download issue, M issues ! ').strip().upper()
        if command in ('', 'M'):
            return
        if command in ('D', 'DOWNLOAD'):
            _download(app, issue)
        elif command == 'R':
            last = app.current_profile.get('magazine_last', {}).get(issue['id'])
            index = next((i for i, article in enumerate(issue['articles']) if article['id'] == last), 0)
            read_article(app, issue, index)
        elif command.isdigit() and 1 <= int(command) <= len(issue['articles']):
            read_article(app, issue, int(command) - 1)
        else:
            app.ansi_scroll('Choose an article number, R, D, or M.', 0.01)


def service(app, issue_id=None, article_id=None):
    if issue_id:
        issue = find_issue(issue_id, app.cis_dynamic.simulation_day())
        if issue:
            issue_menu(app, issue, article_id)
        return
    while True:
        issues = available(app.cis_dynamic.simulation_day())
        app.clear()
        app.header_bar('magazine')
        app.ansi_scroll(CATALOG['title'].upper(), 0.01)
        app.ansi_scroll('Weekly issues and back issues / December 1988', 0.005)
        app.ansi_scroll(CATALOG['notice'], 0.005)
        for index, issue in enumerate(issues, 1):
            count = read_count(app, issue)
            app.ansi_scroll(f"{index} {issue['id']} {issue['date']} [{count}/{len(issue['articles'])} read]", 0.005)
            app.ansi_scroll('  ' + issue['title'], 0.005)
        if not issues:
            app.ansi_scroll('The first issue is scheduled for December 1, 1988.', 0.01)
        command = input('Issue number/ID, L latest, S words, M return ! ').strip()
        upper = command.upper()
        if upper in ('', 'M'):
            return
        if upper.startswith('S '):
            matches = search(command[2:], app.cis_dynamic.simulation_day())
            for index, (issue, article) in enumerate(matches, 1):
                app.ansi_scroll(f"{index} {issue['id']} - {article['title']}", 0.005)
            if not matches:
                app.ansi_scroll('No articles found in published issues.', 0.01)
                continue
            choice = input('Result number, or RETURN ! ').strip()
            if choice.isdigit() and 1 <= int(choice) <= len(matches):
                issue, article = matches[int(choice) - 1]
                issue_menu(app, issue, article['id'])
            continue
        issue = issues[0] if upper == 'L' and issues else issues[int(command) - 1] if command.isdigit() and 1 <= int(command) <= len(issues) else find_issue(upper, app.cis_dynamic.simulation_day())
        if issue:
            issue_menu(app, issue)
        else:
            app.ansi_scroll('Issue unavailable. Choose a listed number or ID.', 0.01)
