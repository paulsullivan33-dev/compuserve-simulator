"""Original weekly magazine, released according to the simulation calendar."""
from cis_session import read_input as input

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


# ---------------------------------------------------------------------------
# Content pack 4 (Worker D): three new recurring departments in every issue.
# The JSON catalog above is loaded verbatim and must stay untouched: issue
# dates and the original article IDs (suffixes 1-10) are load-bearing for
# reading history. The new departments below are merged into ISSUES at import
# time, so the unchanged service code (menus, search, export, history) picks
# them up. New article IDs use the -11/-12/-13 block per issue; the merge
# refuses to run if any ID collides with an existing one.
# ---------------------------------------------------------------------------

NEW_DEPARTMENT_ARTICLES = {
    'OW881201': [
        {
            'id': 'OW881201-11',
            'department': 'News Briefs',
            'title': 'Notes from the first week of December',
            'author': 'NewsNina',
            'paragraphs': [
                "Short items for the start of the month, collected from club newsletters, service bulletins, and reader tips. If you have a brief worth printing, address it to the editors and mark it NEWS BRIEF.",
                "The downtown computer club holds its December meeting on the second Thursday of the month, and the swap table returns by popular request. Members may bring up to five items, each tagged with a price and a working description. The club asks that nobody bring a monitor without first checking with the program chair, because last spring three of them arrived and none of them left. A short talk on cleaning floppy drive heads precedes the trading.",
                "Registration reminders are due for the shareware you actually use. The authors of the most-downloaded terminal programs and file utilities this autumn report that fewer than one caller in fifty ever sends the requested fee. December is a reasonable month to settle those small debts, and most authors still answer their own mail. Keep the registration letter short, include the version number you run, and say which machine it runs on.",
                "Prices on Hayes-compatible 2400-baud modems continue their slow slide. Two mail-order houses now list name-brand 2400-baud units below the price that 1200-baud units carried two Christmases ago. Club buyers report good results from the discount units as long as the box promises Hayes command-set compatibility and includes a real manual. A modem without a manual is a puzzle, not a bargain.",
                "A new paperback reference on DOS batch files reached the bookstores this week, and the early chapters are the useful ones. It covers the difference between AUTOEXEC.BAT conveniences and CONFIG.SYS necessities without assuming you memorized the manual. The chapter on menus built from batch files is worth the price for households where more than one person uses the same machine.",
                "The telephone company reminds callers that winter storms do not improve long-distance lines. If your evening session crackles after a cold snap, try the same board an hour later before blaming your modem. Sysops report that most December line complaints trace to weather, not hardware. Off-peak hours also bring quieter lines along with lower bills.",
                "Finally, a note from our own desk. The mailbag for the first issue overflowed the box, which tells us the readership writes as eagerly as it reads. Keep the letters coming, but put your return address on the letter itself, not just the envelope. Envelopes and letters part company in our office with depressing regularity."
            ],
            'related': [
                "GO FORUMS - find a community"
            ]
        },
        {
            'id': 'OW881201-12',
            'department': 'SysOp Q&A',
            'title': 'The sysop answers: memory, modems, and manners',
            'author': 'SysopSam',
            'paragraphs': [
                "Questions for the sysop arrive by electronic mail all month. Send yours to the editors marked SYSOP QA, and include your machine, your DOS version, and the exact wording of any error message. Here are four from the November mail.",
                "Q: My machine has two megabytes of memory, but programs keep telling me there is not enough. How can both things be true? -- R.T., Fort Worth. A: Because DOS programs ask for conventional memory, the first 640K, and almost nothing else counts toward that request. Your extra memory sits above that line as extended or expanded memory, useful to some programs and invisible to most. The fix is to make the first 640K as empty as possible: move device drivers and memory-resident utilities out of CONFIG.SYS and AUTOEXEC.BAT unless you truly use them every session. One reader recovered ninety thousand bytes by removing a print spooler he had loaded two years earlier and never invoked.",
                "Q: A salesman tells me I need expanded memory, and my brother-in-law says extended. Who is right? -- M.L., Cleveland. A: It depends entirely on your software, not on the salesman or the relative. Spreadsheet and database programs of this era generally want expanded memory following the LIM specification, while DOS itself and a few utilities use extended memory. Check the manual of the one program that matters most to you, buy what it names, and ignore advice that starts with what you ought to want someday.",
                "Q: What are the rules for uploading files to a board? I have a useful utility I did not write. -- D.K., Portland. A: Describe the file honestly, keep the author's documentation with it, and never rename it to hide its origin. Test that it actually runs before you upload it, and say which machine and DOS version you tested on. If the author asks for a registration fee, say so in the description. A board's library is only as trustworthy as its least careful uploader, and sysops remember who wasted everyone's download time.",
                "Q: Call waiting keeps breaking my downloads. Is there a civilized fix? -- S.P., Chicago. A: Dial *70 before the board's number to disable call waiting for that call, where your phone company supports it. Schedule long downloads for late evening, when both the lines and your household are quieter. And if someone must reach you, agree on a signal: three rings, hang up, and you call back between transfers. Technology has not yet solved the shared telephone line, but courtesy covers most of it."
            ],
            'related': [
                "GO FORUMS - find a community"
            ]
        },
        {
            'id': 'OW881201-13',
            'department': 'Letters to the Editor',
            'title': 'Our readers write: the winter desk',
            'author': 'The Editors',
            'paragraphs': [
                "Letters to the editor arrive daily, and we print as many as fit. Keep them under two hundred words, sign them the way you want them printed, and tell us your city. Opinions are the writers' own.",
                "Dear Editors: Your DOS memory article sent me into CONFIG.SYS with a red pen, and I am writing to report the casualties. Out went a mouse driver for a mouse I sold in 1986, a RAM disk I used exactly once, and a calendar program that popped up whenever it felt like it. Ninety-two thousand bytes came home. My spreadsheet has not said the dreaded words since. The lesson cost me an evening and saved me a memory board. -- Harold B., Dayton.",
                "Dear Editors: I finally replaced my 300-baud modem, and I feel I should apologize to everyone who waited while my screen painted one character at a time. At 2400 baud the words arrive in sentences, and a file that once took a lunch hour now takes a coffee break. To anyone still at 300: the upgrade is the single best money you will spend on this hobby. Tell your family it is for efficiency. It is, partly. -- Marcy T., Tulsa.",
                "Dear Editors: Not everyone here owns a PC, and I appreciated seeing the Commodore workshop in the first issue. My 64 does the club newsletter mailing list, tracks my overtime hours, and runs the games my kids actually ask for. The new machines are lovely, but mine is paid for, understood, and fast enough for the jobs I give it. Room at the table for the eight-bit crowd, please. -- Doug W., Sacramento.",
                "Dear Editors: Winter brings static to my radio and my telephone line alike, and I have learned to schedule important downloads for the small hours when the air is calm. My logbook now notes the weather beside each session, a habit borrowed from my shortwave days. Fellow sufferers: the noise passes, the files wait, and patience is the cheapest upgrade ever sold. -- Walt K., Duluth.",
                "Dear Editors: The first issue reached me through a friend who printed it at work, and I have now subscribed from my own terminal. The tone is right: practical, patient, and free of the sneer that creeps into so many computer publications. Keep the small examples coming. A three-line program I understand beats a thirty-line program I merely admire. -- Priya S., Minneapolis.",
                "Write to us about the job your computer actually does this winter. The best letters teach something, even if it is only that the rest of us are not alone in our particular confusion."
            ]
        }
    ],
    'OW881208': [
        {
            'id': 'OW881208-11',
            'department': 'News Briefs',
            'title': 'Notes from the second week of December',
            'author': 'NewsNina',
            'paragraphs': [
                "Short items for gift-buying season, when every computerist is someone's difficult relative to shop for. Send seasonal briefs to the editors marked NEWS BRIEF.",
                "Computer shops in three cities report extended December hours and a run on practical accessories. Surge protectors, printer ribbons, diskette storage boxes, and modem cables are outselling the glamorous peripherals by a wide margin. One retailer told us the perfect gift is the boring one: the thing the recipient needs, would never buy for themselves, and will use weekly. Ribbons and cables qualify.",
                "Shareware registrations make excellent gifts for the computerist who has everything. Several authors now offer gift registrations: you pay the fee, the author mails a printed manual or the latest version to your friend, and everyone avoids duplicate boxes. Include a card explaining what the program does, because a registration code in an envelope looks suspiciously like a mistake.",
                "The December club meeting in Riverside adds a gift exchange with strict rules learned from painful experience. Gifts must cost under fifteen dollars, must be computer-related, and must be new or demonstrably working. Last year's exchange produced a serial cable of unknown pinout and a box of single-sided diskettes, both of which found grateful homes. Wrapped manuals are discouraged but not forbidden.",
                "A reminder for the season: back up before the holidays. Guests, children, and well-meaning relatives will use your machine while you are carving something, and the combination of curiosity and a full hard disk has ended more than one December badly. Two diskettes, labeled and dated, take twenty minutes. Rebuilding a year's correspondence takes considerably longer.",
                "Bookstores report strong sales for the new illustrated guide to desktop publishing, bought mostly as gifts for the family member who does the church bulletin. The first three chapters assume no prior knowledge, which is exactly right for the intended recipient. Pair it with a box of blank diskettes and you have a complete present under twenty-five dollars.",
                "One shop reports a run on gift certificates, sold mostly to spouses who have learned not to guess at model numbers. The certificates come with a printed list of suggested beginner titles, which the staff updates monthly. It is the rare present that cannot be wrong: if the recipient knows exactly what they want, the certificate obliges, and if they do not, the list guides them.",
                "Finally, the service announces special holiday calling hours on Christmas Eve and New Year's Eve, with extra lines open for seasonal greetings in the CB simulator. The sysops volunteer their own evenings for it. If you drop by to say hello, keep the greeting short; the queue behind you is full of people doing the same kind thing."
            ],
            'related': [
                "GO FORUMS - find a community"
            ]
        },
        {
            'id': 'OW881208-12',
            'department': 'SysOp Q&A',
            'title': 'The sysop answers: gifts for the computerist',
            'author': 'SysopSam',
            'paragraphs': [
                "December mail brings gift questions by the dozen. Send yours to the editors marked SYSOP QA. Here are five that cover most of the season's dilemmas.",
                "Q: My brother just bought his first computer. What do I get him that he will actually use? -- J.H., Denver. A: Buy knowledge, not hardware. A well-reviewed beginner's book for his exact machine, a box of quality diskettes, and a printed list of two or three local user groups will serve him better than any accessory you choose blind. Beginners drown in options; they thrive on one trusted guide and permission to ask foolish questions.",
                "Q: Is a surge protector a real gift or an insult? -- K.R., Atlanta. A: It is a real gift, and a thoughtful one. One summer thunderstorm can erase a machine that cost two thousand dollars, and the protector costs less than a dinner out. Wrap it with a card that says you are protecting the novel, the spreadsheet, or the mailing list by name. Specificity turns a gray box into affection.",
                "Q: Can I give software? I worry about already owning it or hating it. -- T.N., Seattle. A: Give a registration for shareware the recipient already uses and loves. It cannot duplicate, it supports the author, and it converts a free ride into a clear conscience. Alternatively, give a bookstore gift certificate with a note suggesting two titles. Certificates feel impersonal only when the giver clearly grabbed the first thing in sight; a short list of suggestions fixes that.",
                "Q: My teenager wants a modem. Am I buying trouble? -- P.W., Dallas. A: You are buying a education, with some supervision required. Set the ground rules first: no long-distance calls without asking, homework before logon, and you get to see the phone bill. Then buy the 2400-baud unit, because a slow modem on a teenager's patience is its own kind of trouble. Many sysops started exactly this way, at exactly this age.",
                "Q: How do I avoid buying the wrong cable, card, or cartridge? -- L.M., Boston. A: Ask for the exact model number of the machine and the device it must connect to, and take that note to the shop. Better yet, bring the recipient shopping and call it a outing rather than a failure of surprise. Computerists would rather pick their own interface than unwrap yours twice: once with delight and once with the receipt."
            ]
        },
        {
            'id': 'OW881208-13',
            'department': 'Letters to the Editor',
            'title': 'Our readers write: the gift list',
            'author': 'The Editors',
            'paragraphs': [
                "December letters turn to the subject of giving. Keep them under two hundred words, sign them as you wish to appear, and include your city.",
                "Dear Editors: The best computer gift I ever received was a diskette storage box, given by my wife in 1985. It cost eleven dollars. Before it, my disks lived in a shoebox sorted by optimism; after it, I could find anything in thirty seconds. Three years later it is still the most-used object on my desk. Practical beats impressive every time. -- Alan G., Phoenix.",
                "Dear Editors: A warning from experience. Last Christmas my father gave me a beautiful printer cable with the wrong connector on one end. He had asked a salesman, who had guessed. The cable sat in a drawer until June, when the club swap table finally matched it to a grateful owner. Ask for model numbers, people. Love is not pin-compatible. -- Susan D., Nashville.",
                "Dear Editors: I give my computer time, not computer things. Every December I spend one Saturday at a neighbor's house setting up whatever they bought in November: formatting disks, installing the word processor, writing down the three commands they will actually need. It costs me nothing but an afternoon, and it is the only gift I give that gets used daily. Consider it. -- Ray C., St. Louis.",
                "Dear Editors: My wish list has exactly one item this year: a second floppy drive. Not a hard disk, not a new machine, just the end of disk-swapping during backups. I have told everyone, written it down, and taped the note to the refrigerator. If desire were currency, I would own the factory. We will see what Santa's budget allows. -- Beth K., Milwaukee.",
                "Dear Editors: To the reader who suggested gift registrations for shareware: I did it, and the author wrote back to my brother personally. He now thinks I am far more thoughtful than I am. Take the credit; the authors deserve the money. -- Tom W., Indianapolis.",
                "Dear Editors: My children pooled their allowance and bought me a modem cable, because mine had developed an intermittent fault I complained about for months. It cost them eight dollars and most of their savings. I have received more expensive gifts and none more thoughtful. Listen to what the computerists in your life complain about; they are writing your shopping list aloud. -- Henry M., Des Moines.",
                "Tell us what is on your list, what you are giving, and what the best computer gift you ever received turned out to be. January's letters will need the cheering."
            ]
        }
    ],
    'OW881215': [
        {
            'id': 'OW881215-11',
            'department': 'News Briefs',
            'title': 'Notes from mid-December',
            'author': 'NewsNina',
            'paragraphs': [
                "Short items for the middle of the month, with a tilt toward the device that connects us all. Send briefs to the editors marked NEWS BRIEF.",
                "The 2400-baud modem is now the default recommendation at four of the five shops we surveyed. The holdouts still stock 1200-baud units for tight budgets, but even they admit the price gap has narrowed to the cost of a pizza. If you bought 1200 this year, nobody will mock you; if you are buying now, buy 2400 and skip the intermediate regret.",
                "Error-correcting protocols move from luxury to expectation. Modems advertising MNP error correction now appear in the mid-price range, and boards that support it report noticeably cleaner transfers during winter line noise. It does not make a bad line good, but it makes a mediocre line tolerable, which in December is nearly the same thing.",
                "The telephone company notes that touch-tone dialing now reaches most exchanges in its territory, which simplifies modem setup for new callers. If your line still pulses, check the modem manual for the dial modifier before assuming the board is at fault. More than one returned modem was perfectly innocent.",
                "Holiday calling schedules are posted in the CB simulator and the main conference rooms. Christmas week brings extended evening hours and a volunteer staff of sysops who would rather be online with you than watching television. New callers are explicitly welcome; the regulars have been instructed to be on their best behavior, and most of them will manage it.",
                "Two new terminal programs appeared in the file library this month, both emphasizing easy setup for first-time callers. The reviewers praise the one with the plain-English manual and damn the one with the clever one. In communications software, clarity is a feature and cuteness is a bug.",
                "Board sysops remind callers that December message traffic doubles, and with it the chance that your reply scrolls away before its recipient logs on. Mark time-sensitive messages clearly in the subject line, and consider electronic mail for anything truly urgent. The public conferences are for conversation; private mail is for the message that cannot wait.",
                "A final note for travelers: if you carry your modem to relatives for the holidays, pack the manual, the cable, and the phone cord in the same bag, and label the bag. Every December a modem arrives somewhere without its cord, and every January someone mails a cord to someone who needed it last week."
            ]
        },
        {
            'id': 'OW881215-12',
            'department': 'SysOp Q&A',
            'title': 'The sysop answers: the modem on your desk',
            'author': 'SysopSam',
            'paragraphs': [
                "This month's mail is all modems, which suits the season: more people call in December than any other month. Send questions to the editors marked SYSOP QA.",
                "Q: Is upgrading from 1200 to 2400 baud really worth it, or is it just numbers? -- E.F., Richmond. A: It is worth it, and the numbers understate the case. At 2400 baud, message reading feels instant instead of merely fast, and a file that took twenty minutes now takes ten. The real gain is psychological: at higher speeds you explore more, because every menu costs less of your evening. Buy the 2400-baud unit from a maker whose name you recognize, and keep the 1200 as a spare or pass it to a beginner.",
                "Q: My modem connects, then drops the call every few minutes. The board's sysop says his end is fine. -- G.H., Des Moines. A: Suspect the line before the hardware. Unplug every other device on the line, including the answering machine, and try again. Listen for static, clicks, or the faint ghost of another conversation. If the drops happen at the same minute past the hour, suspect call waiting or a scheduled device. If they happen only in wet weather, report the line to the phone company and mention data use; the magic phrase is usually enough.",
                "Q: What is an init string, and do I need to understand mine? -- I.J., San Jose. A: An init string is the row of commands your terminal program sends the modem before dialing, setting speed, speaker volume, and answer behavior. You do not need to memorize it, but you should know where it lives in your software's setup and keep a copy on paper. When a new program misbehaves, the init string is the first suspect and the easiest fix. The manual's factory-reset command is worth knowing by heart.",
                "Q: The board offers XMODEM, YMODEM, and ZMODEM. Which do I choose? -- K.L., Pittsburgh. A: Choose ZMODEM if both ends support it; it resumes interrupted transfers and generally gets out of your way. YMODEM batch is fine for sending several files at once. XMODEM is the old reliable that everything speaks, and the one to fall back on when the fancy protocols argue. The differences matter less than matching what the board offers: ask the sysop rather than guessing.",
                "Q: Half duplex, full duplex -- my screen shows double characters. What did I do? -- M.N., Buffalo. A: You told your software to echo characters that the distant computer is already echoing, so each keystroke appears twice. Switch your terminal program to full duplex, or the board to half, until each character appears exactly once. It is the most common first-night problem in online computing, and the fix takes ten seconds once you know where the setting hides."
            ],
            'related': [
                "GO FORUMS - find a community"
            ]
        },
        {
            'id': 'OW881215-13',
            'department': 'Letters to the Editor',
            'title': 'Our readers write: voices on the line',
            'author': 'The Editors',
            'paragraphs': [
                "December's letters hum with carrier tones. Keep them under two hundred words and include your city.",
                "Dear Editors: I remember my first modem the way some men remember their first car. It was 300 baud, it cost more than the computer, and it connected me to a bulletin board eleven miles away where a stranger helped me fix a printer driver at midnight. That stranger is now my brother-in-law. I tell this story whenever someone calls the hobby antisocial. -- Frank D., Akron.",
                "Dear Editors: A cautionary tale for new callers. My first month online, I called a board two area codes away every evening for a week before noticing the phone bill implications. The bill arrived like a second rent. Now I keep a kitchen timer by the computer and a list of local numbers by the phone. The hobby is affordable; carelessness is not. -- Linda P., El Paso.",
                "Dear Editors: Rural lines deserve a mention. My connection crackles whenever the wind blows, and I have learned more about error-correcting protocols than any city caller ever will. But the board is my user group, my library, and some evenings my only conversation. Distance is relative; eleven miles or eleven hundred, the modem erases both. -- Carl H., rural Vermont.",
                "Dear Editors: To the sysop who stayed up past 2 a.m. helping me configure my terminal program: you know who you are, and so does everyone on your board. Volunteers like you are the reason the rest of us keep calling. This letter is inadequate thanks, but it is a start. -- Anonymous, by request.",
                "Dear Editors: My children think the modem's dialing sounds are the computer singing. They gather around to listen to the handshake, and they cheer when it connects. They are not entirely wrong. There is music in a successful call, if you have ever waited through an unsuccessful one. -- Grace W., Tucson.",
                "Dear Editors: My modem taught me typing. At 300 baud every mistake arrived slowly enough to regret, so I learned to compose before connecting and to proofread offline. My correspondence improved, my phone bills shrank, and my friends stopped receiving messages that read like telegrams from a sinking ship. Limitations, properly respected, are teachers. -- Ruth E., Bangor.",
                "Next month we turn to the boards themselves. Tell us about yours: the first board you called, the one you call still, and the sysop who made the difference."
            ]
        }
    ],
    'OW881222': [
        {
            'id': 'OW881222-11',
            'department': 'News Briefs',
            'title': 'Notes from the week before Christmas',
            'author': 'NewsNina',
            'paragraphs': [
                "Short items for the last full week before the holiday, when the boards glow late and the sysops earn their legends. Send briefs marked NEWS BRIEF.",
                "Bulletin boards across the country post holiday hours this week, and most of them are longer, not shorter. Volunteer sysops trade Christmas Eve shifts so the boards stay up for travelers, night owls, and everyone avoiding their relatives' television. If your favorite board is dark on the 25th, remember the sysop has a family too, and thank them in January.",
                "The holiday message traffic is already setting records. One regional network reports twice the usual echomail volume, most of it seasonal greetings hopping from board to board across three time zones. Netiquette reminder: greetings are welcome, chain greetings are not, and nobody needs the same animated greeting forwarded eleven times.",
                "Door games enter their traditional winter peak, when cold evenings and school vacations fill every available node. Sysops ask players to respect posted time limits, especially on single-line boards where a forty-minute game is forty minutes of busy signal for everyone else. Play, enjoy, log off, and let the next caller have their turn.",
                "The Riverside club's board adds a second line for the holidays, paid for by passing the hat at the December meeting. The hat came back heavier than expected, which says something pleasant about that membership. A second line halves the busy signals and doubles the arguments about who gets to be first.",
                "Year-end download quotas reset on most boards January first, so December is the month to fetch the files you have been postponing. Check the new-files listings rather than re-downloading the classics; the sysops curate those lists by hand, and the good stuff hides in the middle. Leave a thank-you message. It costs nothing and it keeps the uploaders uploading.",
                "The club's annual awards night named its sysop of the year, and the winner was not the biggest board but the most patient one. The citation praised three years of midnight troubleshooting and a message base kept friendly by example. Hardware gets the advertisements, but patience gets the plaque. Congratulations to all the nominees, named and unnamed.",
                "Our own holiday note: the magazine's editors will be mostly offline Christmas Eve and Christmas Day, reading paper books like our ancestors. The January issue is already in preparation. If the holiday gives you a story, a question, or a particularly good letter, write it down while it is fresh. We will be here when you get back."
            ]
        },
        {
            'id': 'OW881222-12',
            'department': 'SysOp Q&A',
            'title': 'The sysop answers: boards, doors, and message bases',
            'author': 'SysopSam',
            'paragraphs': [
                "With the holidays filling the boards, this month's questions turn to the care and feeding of bulletin boards themselves. Send questions marked SYSOP QA.",
                "Q: I want to start my own BBS. Is one phone line really enough? -- O.P., Fresno. A: One line is how nearly every board starts, and it is enough to learn whether you enjoy being a sysop. Run the board on your existing line for three months before spending money on a second. You will discover your real calling patterns, your patience for busy signals, and whether 3 a.m. maintenance appeals to you. Most boards that fail do so from sysop exhaustion, not from too few lines.",
                "Q: What are the unwritten rules of message bases? I do not want to embarrass myself. -- Q.R., Madison. A: Read for a week before posting, and you will absorb most of them. Quote only the part you are answering, not the entire message. Stay on the conference topic; the sysop did not create twelve conferences so everyone could chat in all of them. Never post a private argument in public, and never assume a joke reads as a joke at 2400 baud. When in doubt, wait a day.",
                "Q: Door games on my favorite board have a thirty-minute limit, and I keep getting cut off mid-game. Is the sysop being unreasonable? -- S.T., Knoxville. A: The sysop is being fair to everyone else. On a single-line board, your game occupies the entire board: no messages, no downloads, no new callers. Thirty minutes is generous. Save often, learn the game's own save commands, and consider it part of the challenge. The limit is not about you; it is about the eleven people getting busy signals.",
                "Q: My board uses download ratios, and I never have anything to upload. How do I earn credits honestly? -- U.V., Albany. A: Upload descriptions, not just files: a well-described public-domain utility earns its keep. Write a review of a file you downloaded, answer a newcomer's question in the messages, or report a broken download so the sysop can fix it. Most sysops quietly credit contributors who improve the board, and the honest paths are the ones that keep boards alive.",
                "Q: How should callers handle a troublesome user without starting a war? -- W.X., Baton Rouge. A: Do not engage on the board. Send a private note to the sysop describing exactly what happened, with dates if you have them, and let the sysop handle it. Public confrontations reward the troublemaker with exactly the attention they wanted. Good sysops act on solid reports; good callers make solid reports and then go back to enjoying the board."
            ],
            'related': [
                "GO FORUMS - find a community"
            ]
        },
        {
            'id': 'OW881222-13',
            'department': 'Letters to the Editor',
            'title': 'Our readers write: the board at the end of the line',
            'author': 'The Editors',
            'paragraphs': [
                "Holiday letters turn to the bulletin boards that anchor so many evenings. Two hundred words, your city, and your handle if you like.",
                "Dear Editors: My board is eleven miles away and might as well be next door. The sysop knows my machine, my interests, and the fact that I call after the news. When my hard disk died in October, three callers I had never met in person talked me through the recovery over three evenings. Try getting that from a manual. -- NightOwl, Harrisburg.",
                "Dear Editors: A word for the much-maligned door game. My father, who calls computers a waste of electricity, got hooked on a door trivia game during a visit and now calls the board himself twice a week. He still will not touch the word processor, but he knows forty state capitals. Progress arrives by strange doors. -- Jenny F., Spokane.",
                "Dear Editors: I sysop a small board, and I want to answer the letter about volunteers from last month. We do it because the 2 a.m. thank-you messages outnumber the complaints, because somebody has to keep the lights on, and because we remember being the confused newcomer. The pay is terrible and the hours are worse and I would not trade it. Mostly. Ask me again after a crash. -- Sysop of The Night Desk, Boise.",
                "Dear Editors: The first file I ever uploaded was a phone-cost calculator I wrote for myself, all forty lines of it. Someone downloaded it within the hour and left a message saying it saved them real money. I have written better programs since, but none that felt better. Upload something, newcomers. The water is fine. -- BASICBob's neighbor, Gary, Columbus.",
                "Dear Editors: To everyone I have argued with in message bases this year: merry Christmas. To everyone who proved me wrong in message bases this year: thank you, and merry Christmas. The boards are at their best when disagreement stays friendly, and most of you manage it. See you in the new year. -- Contrarian, Philadelphia.",
                "Dear Editors: I lurk. I have called the same board for two years and posted exactly eleven messages. But I read every day, I download the new files, and the board is the best part of my evening. To the sysops who wonder whether the quiet callers are out there: we are. We are grateful. We are just shy. -- Lurker, Cincinnati.",
                "January's letters will look back at the whole year. Send us your 1988: the purchase, the lesson, the surprise, and the resolution."
            ]
        }
    ],
    'OW881229': [
        {
            'id': 'OW881229-11',
            'department': 'News Briefs',
            'title': 'Notes from the last week of the year',
            'author': 'NewsNina',
            'paragraphs': [
                "Short items for the year's final week: a little looking back, a little battening down. Send briefs marked NEWS BRIEF.",
                "The year's end is the year's backup. Before the calendar turns, copy the files you cannot reconstruct: correspondence, financial records, the mailing list, and whatever you have been meaning to organize since spring. Label the diskettes with the date, store one set away from the computer, and test that the copies actually restore. A backup you have never tested is a hope, not a backup.",
                "Virus caution closes out the year as it dominated the autumn. The disk-exchange column's advice stands: know the source of every disk you boot, keep write-protect tabs on masters, and treat alarmist rumors with calm verification rather than panic. The community handled this year's scares well, mostly by refusing to forward what it had not confirmed.",
                "The hardware year in review fits in one paragraph. The 386 moved from exotic to merely expensive, VGA settled in as the display to want, hard disks kept getting bigger while getting cheaper, and 2400 baud became the speed everyone recommends. Nothing this year obsolete the careful buyer of last year, which is the best kind of progress: faster without punishing the prudent.",
                "Club elections happen in January, and most clubs are quietly desperate for volunteers. The jobs nobody wants -- newsletter editor, librarian, meeting-room booker -- are the jobs that keep the club alive. If you attended all year and never volunteered, consider this your personal invitation. The current officers are tired, and they are too polite to say so directly.",
                "The January meeting calendar is already filling. Topics announced so far include taxes and the home computer, a hands-on night with modems for beginners, and the traditional show-us-your-setup evening where members demonstrate the desks the magazine keeps writing about. Bring your questions from this year's issues; several speakers read them.",
                "File libraries report their annual statistics, and the most-downloaded categories are familiar: terminal programs, utilities, and games, in that order. The most-uploaded category is messages of thanks, which appear in no statistics but keep every sysop going. Upload something in January. The counters reset, and so does your reputation.",
                "Our thanks to close the year. Twelve months ago this magazine was an idea; tonight it is five issues, fifty articles, and a mailbag that never empties. The correspondents are fictional, but the readership is gloriously real. Keep writing, keep calling, and keep the coffee away from the diskette box. See you in 1989."
            ]
        },
        {
            'id': 'OW881229-12',
            'department': 'SysOp Q&A',
            'title': 'The sysop answers: closing the year carefully',
            'author': 'SysopSam',
            'paragraphs': [
                "The year's last questions are about endings and beginnings: backups, archives, and resolutions. Send questions marked SYSOP QA.",
                "Q: What does a proper year-end backup actually look like? I keep meaning to do it right. -- Y.Z., Tampa. A: It looks like an evening, not a minute. Start with a full backup of everything you cannot replace, then verify it by restoring one or two files to a scratch diskette. Store one copy somewhere other than the computer room: a drawer at work, a relative's house, anywhere a burst pipe cannot reach both copies. Write the date on every diskette in permanent marker. Then, and only then, consider the job done. The readers who lost files this year almost all had backups; they just had them next to the machine that failed.",
                "Q: My hard disk is full of files from 1986 that I am afraid to delete. What is the archival answer? -- A.B., San Antonio. A: Archive, do not agonize. Copy the doubtful files to labeled diskettes, verify the copies, note what is on them in a simple text file, and then delete them from the hard disk. You will almost never need them again, and on the rare day you do, the diskettes are on the shelf. A hard disk is a workspace, not a museum. Museums have labels and visiting hours.",
                "Q: How do I review a year's worth of subscriptions, services, and shareware fees without it taking a weekend? -- C.D., Charlotte. A: Pull twelve months of canceled checks or statements and highlight every computer-related charge. For each one, ask whether you used it in December. Anything unused since summer gets canceled in January; anything used weekly gets renewed without guilt. The middle category -- used twice, might need someday -- is where the money hides. Be ruthless with the middle category. Your 1989 budget will thank you.",
                "Q: What is one good computing resolution for 1989? I make them every year and keep none. -- E.F., Detroit. A: Make it small and specific: learn one program deeply instead of five shallowly, finish the backup routine you keep postponing, or write one useful batch file a month. Vague resolutions fail because they cannot be finished; specific ones succeed because they can. And tell someone your resolution. A resolution announced to the club meeting has a way of getting kept.",
                "Q: Should I clean up my hard disk or just buy a bigger one? -- G.H., Kansas City. A: Clean first, then decide. Run through the disk directory by directory, archiving what is old and deleting what is duplicated. Most readers find a third of their disk is files they forgot existed. If it is still full after an honest cleaning, then buy the bigger disk with a clear conscience -- and resolve to clean it annually, before it fills again."
            ],
            'related': [
                "GO FORUMS - find a community"
            ]
        },
        {
            'id': 'OW881229-13',
            'department': 'Letters to the Editor',
            'title': 'Our readers write: the year in the rear-view mirror',
            'author': 'The Editors',
            'paragraphs': [
                "The year's last letters look back at 1988 and forward to 1989. Two hundred words, your city, and your honest assessment.",
                "Dear Editors: Best purchase of 1988, no contest: the hard disk. I resisted for two years, calling it a luxury, and then spent a Saturday watching twenty diskettes become one directory. My computing changed more that afternoon than in any upgrade before or since. To everyone still swapping floppies: start saving. You are living in the past, and the past is slow. -- Victor H., Phoenix.",
                "Dear Editors: My year's biggest lesson cost me nothing but pride. I spent March arguing in a message base that my setup needed no backup routine, and spent April rebuilding three months of a mailing list from printed copies. The regulars were kind about it, which somehow made it worse. I now back up monthly, verify quarterly, and keep my opinions about backups to myself. -- Chastened, Omaha.",
                "Dear Editors: The surprise of my year was the people. I bought the modem for files and stayed for the conversations: the sysop who debugged my config at midnight, the stranger who mailed me a manual for the cost of postage, the club members who applauded my first uploaded program. The machine on my desk is a fine tool. The community at the end of the phone line is the real purchase. -- Diane R., Portland.",
                "Dear Editors: For 1989 I resolve to finish things. My disk holds eleven half-written programs, four half-read manuals, and one newsletter that was due in June. This year I start smaller and end more often. If any reader wants an accountability partner, I am in the messages most evenings, username Finisher. Somebody hold me to it. -- Procrastinator, no fixed city.",
                "Dear Editors: A prediction for 1989, offered humbly. The machines will get faster, the disks will get bigger, and the arguments about which is best will continue unchanged. But the real story will be the networks: more boards, more callers, more strangers helping strangers at midnight. The technology is the excuse. The community is the point. See you all online. -- Optimist, Austin.",
                "Dear Editors: My resolution for 1988 was to learn one new program properly, and I chose the spreadsheet. Twelve months later I can build a budget, track a mailing list, and explain absolute versus relative references without notes. One program, deeply learned, beat five programs skimmed. For 1989: the database. Small promises, kept. -- Methodical, San Diego.",
                "That closes our first year of letters. Thank you for writing, for arguing kindly, and for teaching the editors as much as the readers. The mailbag reopens January second. Happy new year."
            ]
        }
    ]
}


def _merge_new_departments():
    """Append content-pack-4 articles; originals are never modified."""
    seen = {article['id'] for issue in ISSUES for article in issue['articles']}
    for issue in ISSUES:
        for article in NEW_DEPARTMENT_ARTICLES.get(issue['id'], ()):
            if article['id'] in seen:
                raise ValueError('Duplicate magazine article id: ' + article['id'])
            seen.add(article['id'])
            issue['articles'].append(article)


_merge_new_departments()
