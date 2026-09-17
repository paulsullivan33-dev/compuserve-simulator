"""Photo-backed navigation with explicitly identified reconstructed directories."""

from cis_session import read_input as input
import cis_communications

# Direct service handlers in select(), apart from declarative screen targets.
IMPLEMENTED_CHOICES = {
    'poster_communicate': {'7', '8', '9'}, 'poster_mail': {'2', '3', '4', '5', '6'},
    'poster_subscribers': {'1', '2', '3', '4'}, 'poster_computers': {'7'},
    'poster_cb': {'1', '6'}, 'poster_mall': {'1', '5', '6'},
    'poster_cus': {'2', '4'}, 'poster_order': {'1', '3'}, 'poster_ebb': {'4'},
    'poster_hotel': {'1'}, 'poster_topics': {'1', '2', '3'},
    'poster_help': {'3', '5', '7', '8'}, 'poster_air': {'1'},
    'poster_travel': {'4'}, 'poster_travel_news': {'5', '7'},
    'poster_news': {'9'}, 'poster_money': {'1', '2', '4', '8', '9'},
    'poster_business': {'8'}, 'poster_games': {'1', '2', '7', '8'}, 'poster_tour': {'1'},
}
PHOTO_REQUESTS = [
    'Column 3: full CUPCAKE panel below Feedback, Access and Hallmark Color Mail.',
    'Column 5: panels below TRA-5, starting with Car Information.',
    'Column 2: complete INDEX topic prompt, alphabetical list, and explanation.',
    'Quick words: Heath, HP Series 100, IBM Users Network, and Orch-90 (IMG_3287 glare).',
    'Quick words: LDOS/TRSDOS, Living Videotext, and MicroPro (IMG_3288 glare).',
    'Remaining quick-reference columns: overlapping close-ups with headings.',
    'Shopping: merchant directory, product index and screens inside MALL/SOFTEX, if shown.',
    'All twelve top categories are readable; no retakes needed.',
    'Capture one or two whole panels, including page codes, with indirect light and no flash.',
]


def photo_requests(app):
    app.text_page('poster_topics', 'PHOTOS THAT WOULD HELP', PHOTO_REQUESTS)


def selection_status(app, key, choice):
    screen = app.screens[key]
    if choice in IMPLEMENTED_CHOICES.get(key, set()) or choice in screen.get('related_targets', {}):
        return 'working / reconstructed'
    if choice in screen.get('targets', {}):
        target = screen['targets'][choice]
        if app.screens.get(target, {}).get('poster'):
            return 'working / poster menu'
        return 'working / reconstructed'
    return 'unimplemented'


def coverage_records(app):
    result = []
    for key, screen in app.screens.items():
        if not screen.get('poster'):
            continue
        for choice, label in screen.get('options', {}).items():
            status = selection_status(app, key, choice)
            result.append(dict(label=f'{app.destination_label(key)} / {choice} {label}',
                word=screen.get('page', ''), destination=key, status=status,
                source=screen.get('source', 'poster'),
                note=(f'Parent menu is transcribed. A full photo of the {label} destination would help, if shown elsewhere.'
                      if status == 'unimplemented' else 'Opens the parent menu; choose ' + choice + '.')))
    return result


def install(app):
    for record in app.poster_words:
        app.go_map['GO ' + record['word']] = 'quick:' + record['word']
    app.go_map.update({'GO QUICK': 'quick', 'GO PHONES': 'phones'})
    app.go_map['GO PER'] = 'personal_files'
    app.go_map['GO SETUP'] = 'computer_setup'
    # Convenience words for reconstructed services; no claim these are poster aliases.
    app.go_map.update({'GO ACCESS': 'public_files', 'GO SOCIETY': 'cb_society',
                       'GO CARDS': 'color_cards', 'GO COVERAGE': 'coverage', 'GO PHOTOS': 'photo_requests'})


def open_word(app, word, stack):
    record = next((r for r in app.poster_words if r['word'] == word), None)
    if record is None:
        return False
    lines = ['Listed on the original poster as GO ' + word + '.']
    if record.get('target'):
        lines += ['', 'Opening a related existing simulation:',
                  app.destination_label(record['target']),
                  'Its contents are reconstructed, not a transcription of this service.']
    else:
        lines += ['', 'This historical service has not yet been recreated.']
    app.text_page('poster_topics', record['label'], lines)
    if record.get('target'):
        app.open_go_destination(record['target'], stack)
    return True


def records(app, group=None):
    """Index only documented words and destinations this build actually knows."""
    result = []
    for record in app.poster_words:
        if group and record['group'] != group:
            continue
        result.append(dict(record, destination='quick:' + record['word'],
                           status='working / reconstructed' if record.get('target') else 'unimplemented'))
    if group:
        related = {
            'hardware': [('IBM PC Hardware Forum', 'ibmhw'), ('Macintosh Developers Forum', 'macdev')],
            'software': [('DOS Software Forum', 'dos')],
            'publications': [('Online Weekly Magazine', 'magazine')],
        }
        for label, target in related.get(group, []):
            result.append(dict(label=label, word='', destination=target, status='simulation addition'))
    else:
        known = {record['word'] for record in app.poster_words}
        for command, target in app.go_map.items():
            word = command[3:]
            if word in known or target.startswith('quick:'):
                continue
            result.append(dict(label=app.destination_label(target), word=word,
                               destination=target, status='working / poster menu' if app.screens.get(target, {}).get('poster') else 'working / reconstructed'))
    return sorted(result, key=lambda record: (record['label'].casefold(), record['word']))


def directory(app, stack, group=None, search_first=False, coverage=False):
    """Paginated, searchable catalogue. Navigation stays on the caller's stack."""
    catalog = coverage_records(app) if coverage else records(app, group)
    status_filter = ''
    query = input('Enter topic ! ').strip() if search_first else ''
    page = 0
    size = 6 if app.SCREEN_WIDTH == 40 else 10
    while True:
        terms = query.casefold().split()
        matches = [r for r in catalog if (not status_filter or status_filter in r['status']) and all(
            term in (r['label'] + ' ' + r['word']).casefold() for term in terms)]
        pages = max(1, (len(matches) + size - 1) // size)
        page = min(page, pages - 1)
        visible = matches[page * size:(page + 1) * size]
        app.clear()
        app.header_bar('poster_topics')
        app.ansi_scroll('IMPLEMENTATION COVERAGE' if coverage else ('QUICK REFERENCE WORDS' if not group else group.upper() + ' DIRECTORY'), 0.01)
        app.ansi_scroll('Reconstructed directory from readable poster entries and simulation services.', 0.01)
        app.ansi_scroll(f'Page {page + 1}/{pages}  {len(matches)} topics' + (f'  Search: {query}' if query else ''), 0.01)
        for number, record in enumerate(visible, 1):
            app.ansi_scroll(f'{number:>2}  {record["label"]}', 0.01)
            quick = 'GO ' + record['word'] + '  ' if record['word'] else ''
            app.ansi_scroll(f'    {quick}[{record["status"]}]', 0.01)
        if not visible:
            app.ansi_scroll('No matching topics.', 0.01)
        app.ansi_scroll('W working, R reconstructed, U unimplemented, PHOTOS, COVERAGE', 0.005)
        command = input('Number, F/B, S words, ALL, W/R/U, PHOTOS, COVERAGE, M ! ').strip()
        upper = command.upper()
        if upper in ('M', '0', ''):
            return
        if upper == 'F':
            page = min(page + 1, pages - 1)
        elif upper == 'B':
            page = max(0, page - 1)
        elif upper == 'ALL':
            query, page = '', 0
            status_filter = ''
        elif upper in ('W', 'R', 'U'):
            status_filter = {'W': 'working', 'R': 'reconstructed', 'U': 'unimplemented'}[upper]
            page = 0
        elif upper == 'PHOTOS':
            photo_requests(app)
        elif upper == 'COVERAGE':
            coverage = True
            catalog = coverage_records(app)
            query, status_filter, page = '', '', 0
        elif upper == 'S' or upper.startswith('S '):
            query, page = (command[2:].strip() if len(command) > 1 else input('Enter topic ! ').strip()), 0
        elif command.isdigit() and 1 <= int(command) <= len(visible):
            destination = visible[int(command) - 1]['destination']
            # Avoid recursively opening this directory from its own listing.
            if destination in ('quick', 'coverage'):
                query, page = '', 0
                coverage = destination == 'coverage'
                catalog = coverage_records(app) if coverage else records(app, group)
                continue
            if visible[int(command) - 1].get('note'):
                app.text_page('poster_topics', 'COVERAGE NOTE', [visible[int(command) - 1]['status'], visible[int(command) - 1]['note']])
            before = list(stack)
            app.open_go_destination(destination, stack)
            if stack != before:
                return
        else:
            app.ansi_scroll('Huh', 0.01)


def select(app, current, choice, stack):
    """Dispatch photo menu choices without changing legacy service numbering."""
    if current == 'poster_communicate' and choice in ('7', '8', '9'):
        {'7': cis_communications.society, '8': cis_communications.public_files,
         '9': cis_communications.cards}[choice](app)
        return
    if current == 'poster_cb' and choice == '6':
        cis_communications.society(app)
        return
    if current == 'poster_feedback' and not choice:
        app.ansi_scroll('Historical welcome text reproduced above. This simulation saves feedback locally; the stated credits and representative replies are not implemented.', 0.01)
        app.customer_support('4')
        return
    if current == 'poster_bulletin' and not choice:
        cis_communications.bulletin(app)
        return
    if current == 'poster_subscribers':
        cis_communications.directory(app, choice)
        return
    if current == 'poster_computers' and choice == '7':
        cis_communications.personal_files(app)
        return
    if current == 'poster_mail' and choice == '3':
        cis_communications.mail_upload(app)
        return
    if current == 'poster_mail' and choice == '4':
        cis_communications.personal_files(app, use_for_mail=True)
        return
    if current == 'poster_mail' and choice == '5':
        app.cis_mail.address_book(app)
        return
    if current == 'poster_cb' and choice == '1':
        app.cb_help()
        return
    shopping_action = {
        ('poster_mall', '1'): '4', ('poster_mall', '6'): '1',
        ('poster_cus', '4'): '1', ('poster_order', '1'): '4',
        ('poster_ebb', '4'): '2',
    }.get((current, choice))
    if shopping_action:
        app.ansi_scroll('Opening the existing reconstructed shopping service. Original merchant catalogs, instructions, and advertisements are not reproduced.', 0.01)
        app.shopping_service(shopping_action)
        return
    if (current, choice) in (('poster_cus', '2'), ('poster_mall', '5')):
        query = input('Search simulated products (RETURN lists all) ! ').strip()
        products = app.cis_store.search(query)
        app.text_page(current, 'SIMULATED PRODUCT INDEX - BROWSING ONLY', [
            'Reconstructed catalog; original merchant products are not transcribed.',
            *[f"{p['sku']}  {p['name']} - ${p['price']:.2f}" for p in products],
            *([] if products else ['No matching products.']),
        ])
        return
    if current == 'poster_order' and choice == '3':
        orders = [order for order in app.load_json('orders.json', default=[])
                  if app.current_user_id and order.get('user_id') == app.current_user_id]
        app.text_page(current, 'SIMULATED ORDER STATUS', [
            'Orders recorded by this simulation only.',
            *[f"{o.get('order_id', o.get('number', ''))}  {o.get('status', 'RECEIVED')}  {o.get('name', '')}" for o in orders],
            *([] if orders else ['No orders recorded for this member.']),
        ])
        return
    related = app.screens[current].get('related_targets', {}).get(choice)
    if related:
        app.text_page(current, app.screens[current]['options'][choice], [
            'Opening a related reconstructed simulation:', app.destination_label(related),
            'The original historical forum content is not reproduced.',
        ])
        app.open_go_destination(related, stack)
        return
    if current == 'poster_aae' and not choice:
        app.ansi_scroll('The preceding welcome text describes the historical encyclopedia. This simulation contains a small reconstructed sample.', 0.01)
        app.reference_service('1')
        return
    if current == 'poster_hotel' and choice == '1':
        app.ansi_scroll('Opening the reconstructed hotel directory; original ABC guide content is not reproduced.', 0.01)
        app.travel_service('2')
        return
    if current == 'poster_topics':
        if choice in ('1', '2'):
            directory(app, stack, search_first=choice == '1')
        else:
            app.text_page(current, 'EXPLANATION OF INDEX', [
                'Reconstructed help for this simulation.',
                'Search by service name or GO word, or list all indexed destinations.',
                'F and B turn pages. S words searches. ALL clears the search.',
                'Enter a displayed number to open a destination. M returns.',
                'Not recreated means the poster names a service with no implementation.',
                'Related simulation means existing content covers part of that topic.',
                'The original complete topic index is not yet transcribed.',
                'On the poster, E denotes an Executive Option offering.',
            ])
        return
    if current == 'poster_help' and choice == '5':
        app.cis_phones.run(app.ansi_scroll, read=input, return_to="the previous menu")
        return
    action = {
        ('poster_mail', '2'): (app.mail_service, '2'),
        ('poster_mail', '6'): (app.mail_service, '4'),
        ('poster_air', '1'): (app.travel_service, '1'),
        ('poster_travel', '4'): (app.travel_service, '6'),
        ('poster_travel_news', '5'): (app.travel_service, '4'),
        ('poster_travel_news', '7'): (app.customer_support, '4'),
        ('poster_news', '9'): (app.news_section, 'Business'),
        ('poster_money', '1'): (app.finance_service, '2'),
        ('poster_money', '2'): (app.finance_service, '3'),
        ('poster_money', '4'): (app.finance_service, '6'),
        ('poster_money', '8'): (app.finance_service, '1'),
        ('poster_money', '9'): (app.news_section, 'Business'),
        ('poster_business', '8'): (app.finance_service, '2'),
        ('poster_games', '1'): (app.games_service, '4'),
        ('poster_games', '2'): (app.games_service, '1'),
        ('poster_games', '7'): (app.games_service, '3'),
        ('poster_games', '8'): (app.games_service, '2'),
        ('poster_help', '3'): (app.customer_support, '1'),
        ('poster_help', '7'): (app.customer_support, '5'),
        ('poster_help', '8'): (app.customer_support, '2'),
        ('poster_tour', '1'): (app.customer_support, '10'),
    }.get((current, choice))
    target = app.screens[current].get('targets', {}).get(choice)
    if action:
        action[0](action[1])
    elif target:
        app.open_go_destination(target, stack)
    else:
        app.text_page(current, app.screens[current]['options'][choice], [
            'This service appears on the original CompuServe poster.',
            'It has not yet been recreated in this simulation.',
        ])
