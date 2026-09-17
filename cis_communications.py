"""Local reconstructed communications services; poster menus remain intact."""
import os
from pathlib import Path
from cis_session import read_input as input

LIMIT = 32768


def state(app):
    return app.load_json('dynamic_state.json', default={}).get('communications', {})


def change(app, update):
    def mutate(data):
        update(data.setdefault('communications', {}))
    app.update_json_atomic('dynamic_state.json', {}, mutate)


def member(app):
    if app.current_user_id:
        return app.current_user_id
    app.ansi_scroll('Please sign in to use this service.', 0.01)
    return None


def clean(text, limit=240):
    return ''.join(c for c in text if c.isprintable())[:limit]


def save_listing(app, category, description):
    uid = member(app)
    if not uid:
        return
    record = dict(user_id=uid, handle=clean(app.current_handle or uid, 40),
                  category=clean(category, 60), description=clean(description))
    change(app, lambda data: data.setdefault('directory', {}).__setitem__(uid, record))


def directory(app, choice):
    uid = member(app)
    if not uid:
        return
    if choice == '1':
        app.text_page('poster_subscribers', 'SUBSCRIBER DIRECTORY', [
            'Reconstructed member directory. Only members who add a listing appear.',
            'Your handle, User ID, category and description are visible to other members.',
            'Deleting a listing leaves your account and mail intact.'])
    elif choice == '2':
        query = input('Category or search words (RETURN lists all) ! ').casefold().split()
        rows = state(app).get('directory', {}).values()
        matches = [r for r in rows if all(w in ' '.join(r.values()).casefold() for w in query)]
        app.text_page('poster_subscribers', 'DIRECTORY RESULTS', [
            line for r in sorted(matches, key=lambda r: r['handle'].casefold())
            for line in [f"{r['handle']}  {r['user_id']}  [{r['category']}]", r['description']]]
            or ['No matching member listings.'])
    elif choice == '3':
        old = state(app).get('directory', {}).get(uid, {})
        category = input(f"Category [{old.get('category', 'GENERAL')}] ! ").strip() or old.get('category', 'GENERAL')
        description = input(f"Public description [{old.get('description', '')}] ! ").strip() or old.get('description', '')
        if input('Publish this member listing [Y/N] ! ').upper() == 'Y':
            save_listing(app, category, description)
            app.ansi_scroll('Directory listing saved.', 0.01)
    elif choice == '4' and input('Delete your directory listing [Y/N] ! ').upper() == 'Y':
        change(app, lambda data: data.setdefault('directory', {}).pop(uid, None))
        app.ansi_scroll('Your listing has been removed.', 0.01)


def post(app, category, subject, body):
    uid = member(app)
    if not uid or not subject.strip() or not body.strip() or len(body) > LIMIT:
        return None
    result = []
    def update(data):
        number = data.get('next_bulletin', 1)
        data['next_bulletin'] = number + 1
        data.setdefault('bulletins', []).append(dict(id=number, user_id=uid,
            handle=clean(app.current_handle or uid, 40), category=clean(category, 60),
            subject=clean(subject, 120), body='\n'.join(clean(line, LIMIT) for line in body.splitlines()),
            date=app.SIMULATION_DATE))
        result.append(number)
    change(app, update)
    return result[0]


def delete_post(app, number):
    def update(data):
        data['bulletins'] = [r for r in data.get('bulletins', [])
                             if not (r['id'] == number and r['user_id'] == app.current_user_id)]
    change(app, update)


def bulletin(app, category_filter=None):
    if not member(app):
        return
    query = ''
    while True:
        rows = [r for r in state(app).get('bulletins', []) if (not category_filter or r['category'] == category_filter) and query.casefold() in
                (r['category'] + ' ' + r['subject'] + ' ' + r['body']).casefold()]
        app.ansi_scroll((category_filter or 'NATIONAL BULLETIN BOARD') + ' - local simulation', 0.01)
        for r in rows:
            app.ansi_scroll(f"{r['id']:>4} [{r['category']}] {r['subject']} -- {r['handle']}", 0.01)
        if not rows:
            app.ansi_scroll('No matching posts. P creates a post.', 0.01)
        command = input('Number, P post, S search, D delete own post, M ! ').strip().upper()
        if command in ('M', ''):
            return
        if command == 'P':
            category = category_filter or input('Category ! ').strip() or 'GENERAL'
            subject = input('Subject ! ').strip()
            body = app.line_editor()
            if body and subject:
                number = post(app, category, subject, body)
                app.ansi_scroll(f'Posted #{number}.' if number else 'Post exceeds 32K limit.', 0.01)
        elif command == 'S':
            query = input('Search (RETURN clears) ! ').strip()
        elif command == 'D':
            number = input('Your post number ! ').strip()
            if number.isdigit() and input('Delete post [Y/N] ! ').upper() == 'Y':
                delete_post(app, int(number))
        elif command.isdigit():
            row = next((r for r in rows if r['id'] == int(command)), None)
            if row:
                app.text_page('poster_bulletin', row['subject'], [
                    f"{row['handle']} {row['user_id']}  {row['date']}", '', *row['body'].splitlines()])
                if input('R reply by EasyPlex, RETURN ! ').strip().upper() == 'R':
                    app.cis_mail.compose(app, recipient=row['user_id'], subject_default='Re: ' + row['subject'])


def save_file(app, name, body):
    uid = member(app)
    name = clean(name, 40).strip()
    if not uid or not name or len(body) > LIMIT:
        return False
    body = '\n'.join(clean(line, LIMIT) for line in body.splitlines())
    change(app, lambda data: data.setdefault('files', {}).setdefault(uid, {}).__setitem__(name, body))
    return True


def upload_text(app):
    # Remote clients cannot read arbitrary paths on the host.
    remote = any(os.environ.get(k) == '1' for k in ('CIS_WEB_TERMINAL', 'CIS_REMOTE_TERMINAL'))
    if not remote and input('L local UTF-8 file, RETURN paste text ! ').strip().upper() == 'L':
        path = input('Local text file path ! ').strip().strip('"')
        try:
            with Path(path).expanduser().open('rb') as source:
                raw = source.read(LIMIT + 1)
            if len(raw) > LIMIT:
                raise ValueError('Text file exceeds 32K.')
            body = raw.decode('utf-8-sig')
            if '\x00' in body:
                raise ValueError('Please choose a plain text file.')
            return '\n'.join(clean(line, LIMIT) for line in body.splitlines())
        except (OSError, UnicodeError, ValueError) as exc:
            app.ansi_scroll(f'Unable to import text: {exc}', 0.01)
            return None
    app.ansi_scroll('Paste text into the editor; save to finish importing.', 0.01)
    body = app.line_editor()
    if body is not None and len(body) > LIMIT:
        app.ansi_scroll('Text exceeds 32K limit.', 0.01)
        return None
    return body


def personal_files(app, use_for_mail=False):
    uid = member(app)
    if not uid:
        return
    while True:
        files = state(app).get('files', {}).get(uid, {})
        names = sorted(files)
        app.ansi_scroll('PERSONAL TEXT FILE AREA - private to your User ID', 0.01)
        for number, name in enumerate(names, 1):
            app.ansi_scroll(f'{number:>3} {name} ({len(files[name])} characters)', 0.01)
        command = input('Number, N new, U upload, D delete, M ! ').strip().upper()
        if command in ('M', ''):
            return
        if command in ('N', 'U'):
            name = clean(input('File name ! '), 40).strip()
            body = upload_text(app) if command == 'U' else app.line_editor()
            if body is not None and name:
                if name in files and input('Replace existing file [Y/N] ! ').upper() != 'Y':
                    continue
                app.ansi_scroll('File saved.' if save_file(app, name, body) else 'Unable to save (32K limit).', 0.01)
        elif command == 'D':
            number = input('File number ! ').strip()
            if number.isdigit() and 1 <= int(number) <= len(names) and input('Delete file [Y/N] ! ').upper() == 'Y':
                name = names[int(number) - 1]
                change(app, lambda data: data.setdefault('files', {}).setdefault(uid, {}).pop(name, None))
        elif command.isdigit() and 1 <= int(command) <= len(names):
            name = names[int(command) - 1]
            if use_for_mail:
                app.cis_mail.compose(app, initial_lines=files[name].splitlines())
                return
            app.text_page('poster_mail', name, files[name].splitlines())
            action = input('E edit, C compose mail using file, RETURN ! ').strip().upper()
            if action == 'E':
                body = app.line_editor(initial_lines=files[name].splitlines())
                if body is not None:
                    app.ansi_scroll('File saved.' if save_file(app, name, body) else 'Unable to save (32K limit).', 0.01)
            elif action == 'C':
                app.cis_mail.compose(app, initial_lines=files[name].splitlines())


def mail_upload(app):
    if member(app):
        body = upload_text(app)
        if body:
            app.cis_mail.compose(app, initial_lines=body.splitlines())


def publish_file(app, name, description):
    uid = member(app)
    files = state(app).get('files', {}).get(uid, {})
    if not uid or name not in files or not description.strip():
        return None
    body = files[name]
    result = []
    def update(data):
        number = data.get('next_public_file', 1)
        data['next_public_file'] = number + 1
        # Published text is a snapshot; later private edits do not change it.
        data.setdefault('public_files', []).append(dict(public_id=number, number=number,
            name=f'ACCESS{number}.TXT', original_name=name, description=clean(description),
            user_id=uid, author=clean(app.current_handle or uid, 40), text_content=body,
            bytes=len(body.encode('utf-8')), platforms=['ANY'], date=app.SIMULATION_DATE, downloads=0))
        result.append(number)
    change(app, update)
    return result[0]


def remove_public_file(app, number):
    change(app, lambda data: data.__setitem__('public_files', [r for r in data.get('public_files', [])
        if not (r['public_id'] == number and r['user_id'] == app.current_user_id)]))


def public_files(app):
    if not member(app):
        return
    query = ''
    while True:
        rows = [r for r in state(app).get('public_files', []) if query.casefold() in
                (r['original_name'] + ' ' + r['description']).casefold()]
        app.ansi_scroll('ACCESS PUBLIC FILE AREA - reconstructed text sharing', 0.01)
        for row in rows:
            app.ansi_scroll(f"{row['public_id']} {row['original_name']} -- {row['description']} ({row['downloads']} downloads)", 0.005)
        command = input('Number download, P publish PER file, S search, D delete own, M ! ').strip().upper()
        if command in ('M', ''):
            return
        if command == 'P':
            files = state(app).get('files', {}).get(app.current_user_id, {})
            for name in files:
                app.ansi_scroll(name, 0.005)
            name = input('Exact private file name ! ').strip()
            description = input('Public description ! ').strip()
            if input('Share a copy with all members [Y/N] ! ').strip().upper() == 'Y':
                number = publish_file(app, name, description)
                app.ansi_scroll(f'Published #{number}.' if number else 'File not found or description missing.', 0.01)
        elif command == 'S':
            query = input('Search words ! ').strip()
        elif command == 'D':
            number = input('Public file number ! ').strip()
            if number.isdigit() and input('Remove your public copy [Y/N] ! ').strip().upper() == 'Y':
                remove_public_file(app, int(number))
        elif command.isdigit():
            record = next((r for r in rows if r['public_id'] == int(command)), None)
            if record:
                app.library_transfer(record)


def society(app):
    uid = member(app)
    if not uid:
        return
    while True:
        members = state(app).get('society', {})
        app.ansi_scroll('CB SOCIETY - reconstructed member club', 0.01)
        app.ansi_scroll('Original Cupcake column is not reproduced. Club Notes is new simulation content.', 0.005)
        command = input('1 Club Notes, 2 members, 3 discussions, J join, L leave, M ! ').strip().upper()
        if command in ('M', ''):
            return
        if command == '1':
            app.text_page('poster_cb', 'CLUB NOTES - SIMULATION EDITION', [
                'Welcome to the December computer-and-modem get-together.',
                'Introduce your handle and favorite computer on the club discussion board.',
                'Keep messages friendly, give newcomers time to type, and ask before private chats.',
                'Share your terminal tips through the Access public file area.',
                'Use GO CB for the existing simulated CB channels.'])
        elif command == '2':
            app.text_page('poster_cb', 'CB SOCIETY MEMBERS', [f'{key} {value}' for key, value in sorted(members.items())] or ['No members yet. J joins.'])
        elif command == 'J':
            change(app, lambda data: data.setdefault('society', {}).__setitem__(uid, clean(app.current_handle or uid, 40)))
            app.ansi_scroll('You joined the CB Society.', 0.01)
        elif command == 'L':
            change(app, lambda data: data.setdefault('society', {}).pop(uid, None))
            app.ansi_scroll('Membership removed. Your previous posts remain on the board.', 0.01)
        elif command == '3':
            if uid in members:
                bulletin(app, category_filter='CB SOCIETY')
            else:
                app.ansi_scroll('Join the club with J to enter its discussion board.', 0.01)


CARD_DESIGNS = {
    '1': ('Birthday', 'MAGENTA', ['  *  .  *  .  *', '   HAPPY BIRTHDAY', '     | | | |', '    [=======]', '    [_______]']),
    '2': ('Thank you', 'CYAN', ['  +----------------+', '  |   THANK YOU!   |', '  +----------------+']),
    '3': ('Season greetings', 'GREEN', ['        *', '       /\\', '      /o \\', '     /_o__\\', '        ||', '  SEASON\'S GREETINGS']),
}
CARD_COLORS = {'MAGENTA': '\x1b[35m', 'CYAN': '\x1b[36m', 'GREEN': '\x1b[32m'}


def card_body(design, message, sender):
    title, color, art = CARD_DESIGNS[design]
    return '\n'.join([*art, '', clean(message, 500), '', 'From: ' + clean(sender, 40)])


def send_card(app, recipient, design, message):
    if not app.current_user_id or recipient not in app.profiles or design not in CARD_DESIGNS:
        return None
    result = []
    def update(messages):
        number = max((m.get('id', 0) for m in messages), default=0) + 1
        messages.append(dict(id=number, to=recipient, **{'from': app.current_user_id},
            date=app.SIMULATION_DATE, subject='GREETING: ' + CARD_DESIGNS[design][0],
            body=card_body(design, message, app.current_handle or app.current_user_id), read=False,
            card_color=CARD_DESIGNS[design][1]))
        result.append(number)
    app.update_json_atomic('easyplex.json', [], update)
    return result[0]


def cards(app):
    if not member(app):
        return
    app.ansi_scroll('COLOR MAIL - original simulated cards, not historical Hallmark designs', 0.01)
    for key, (title, color, art) in CARD_DESIGNS.items():
        app.ansi_scroll(f'{key} {title} ({color.lower()})', 0.005)
    design = input('Design number, M ! ').strip()
    if design not in CARD_DESIGNS:
        return
    recipient = input('Recipient User ID ! ').strip()
    if recipient not in app.profiles:
        app.ansi_scroll('No such member. Card not sent.', 0.01)
        return
    message = input('Greeting text ! ').strip()
    app.text_page('poster_mail', 'CARD PREVIEW', card_body(design, message, app.current_handle or app.current_user_id).splitlines(), color=CARD_DESIGNS[design][1])
    if input('Send simulated card via EasyPlex [Y/N] ! ').strip().upper() == 'Y':
        number = send_card(app, recipient, design, message)
        app.ansi_scroll(f'Card #{number} delivered to EasyPlex.', 0.01)
