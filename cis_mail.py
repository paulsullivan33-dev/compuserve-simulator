"""EasyPlex mail service, isolated from terminal navigation."""
from cis_session import read_input as input

import re
import cis_communications


def load_mail(app):
    messages = app.load_json("easyplex.json", default=[])
    if not isinstance(messages, list):
        raise RuntimeError("easyplex.json must contain a JSON list")
    return messages


def waiting_count(app, user_id):
    return sum(1 for message in load_mail(app) if message.get("to") == user_id and not message.get("read", False))


def service(app, choice):
    actions = {"1": read, "2": compose, "3": folders, "4": settings}
    action = actions.get(choice)
    if action:
        action(app)


def read(app):
    messages = load_mail(app)
    inbox = [message for message in messages if message.get("to") == app.current_user_id]
    message_list(app, inbox, messages, "EASYPLEX WAITING MESSAGES")


def message_list(app, folder, all_messages, title, sent_folder=False):
    while True:
        app.clear()
        app.header_bar("mail")
        app.ansi_scroll(title, 0.01)
        for number, message in enumerate(folder, 1):
            marker = " " if sent_folder or message.get("read") else "*"
            correspondent = message.get("to" if sent_folder else "from", "")
            app.ansi_scroll(f'{number:>2}{marker} {correspondent:>10}  {message.get("subject", "")}', 0.005)
        choice = input("Message number or M ! ").strip().upper()
        if choice == "M":
            return
        if not (choice.isdigit() and 1 <= int(choice) <= len(folder)):
            continue
        message = folder[int(choice) - 1]
        if not sent_folder:
            message["read"] = True
            app.save_json_atomic("easyplex.json", all_messages)
        app.text_page("mail", f'Message {message.get("id", "")}', [
            f'From: {message.get("from", "")}', f'To: {message.get("to", "")}',
            f'Date: {message.get("date", "")}', f'Subject: {message.get("subject", "")}',
            "", message.get("body", ""),
        ], **({'color': message['card_color']} if message.get('card_color') in cis_communications.CARD_COLORS else {}))
        action = input("R Reply, F Forward, V Move, D Delete, or RETURN ! ").strip().upper()
        if action == "R" and not sent_folder:
            compose(app, recipient=message.get("from"), subject_default="RE: " + message.get("subject", ""))
        elif action == "F":
            compose(app, subject_default="FWD: " + message.get("subject", ""), initial_lines=["----- Forwarded message -----"] + message.get("body", "").splitlines())
        elif action == "D":
            all_messages.remove(message)
            folder.remove(message)
            app.save_json_atomic("easyplex.json", all_messages)
            app.ansi_scroll("Message deleted.", 0.01)
        elif action == "V" and not sent_folder:
            available = app.current_profile.get("mail_folders", [])
            destination = input("Move to folder: ").strip().upper()
            if destination in available:
                message["folder"] = destination
                folder.remove(message)
                app.save_json_atomic("easyplex.json", all_messages)
                app.ansi_scroll("Message moved.", 0.01)


def compose(app, recipient=None, subject_default="", initial_lines=None, resume_saved=False):
    messages = load_mail(app)
    draft = app.cis_drafts.get_draft(app, "mail")
    if resume_saved and draft:
        recipient = draft.get("recipient")
        subject_default = draft.get("subject", "")
        initial_lines = draft.get("lines", [])
    elif draft and recipient is None and not subject_default and initial_lines is None:
        app.ansi_scroll("SAVED DRAFT: " + app.cis_drafts.draft_summary(draft), 0.01)
        action = input("R Resume, D Delete, N New, or M ! ").strip().upper()
        if action == "M":
            return
        if action == "D":
            app.cis_drafts.delete_draft(app, "mail")
            app.ansi_scroll("EasyPlex draft deleted.", 0.01)
            return
        if action == "R":
            recipient = draft.get("recipient")
            subject_default = draft.get("subject", "")
            initial_lines = draft.get("lines", [])
    recipient = recipient or input("To (or DIR): ").strip()
    if recipient.upper() == "DIR":
        app.text_page("mail", "COMPUSERVE USER DIRECTORY", [
            f"{user_id}  {listing['handle']}  [{listing['category']}]"
            for user_id, listing in sorted(cis_communications.state(app).get('directory', {}).items())
        ] or ['No public listings. Members can opt in from Communications choice 5.'])
        recipient = input("To: ").strip()
    contacts = app.current_profile.get("address_book", {})
    if recipient.upper() in contacts:
        recipient = contacts[recipient.upper()]
    if not re.fullmatch(r"\d{5},\d{4}", recipient):
        app.ansi_scroll("Invalid User ID. Message cancelled.", 0.01)
        return
    known_recipient = recipient in app.profiles
    if not known_recipient and input("User ID is not in directory. Send anyway [Y/N]? ").strip().upper() != "Y":
        return
    subject = input(f"Subject [{subject_default}]: ").strip()[:120] or subject_default[:120]
    if not subject:
        app.ansi_scroll("Message cancelled.", 0.01)
        return
    app.cis_drafts.save_draft(app, "mail", recipient=recipient, subject=subject, lines=list(initial_lines or []))
    body = app.line_editor(initial_lines=initial_lines, on_change=lambda lines: app.cis_drafts.save_draft(app, "mail", recipient=recipient, subject=subject, lines=lines))
    if not subject or body is None:
        app.ansi_scroll("Message cancelled.", 0.01)
        return
    next_id = max((message.get("id", 0) for message in messages), default=0) + 1
    messages.append({"id": next_id, "from": app.current_user_id, "to": recipient, "date": app.SIMULATION_DATE, "subject": subject, "body": body, "read": False})
    if not known_recipient:
        messages.append({"id": next_id + 1, "from": "POSTMASTER", "to": app.current_user_id, "date": app.SIMULATION_DATE, "subject": "DELIVERY FAILURE: " + subject, "body": f"User ID {recipient} is not listed. Your message could not be delivered.", "read": False})
    app.save_json_atomic("easyplex.json", messages)
    app.cis_drafts.delete_draft(app, "mail")
    app.ansi_scroll("Message accepted by EasyPlex.", 0.01)


def folders(app):
    messages = load_mail(app)
    inbox = [m for m in messages if m.get("to") == app.current_user_id and m.get("folder", "INBOX") == "INBOX"]
    sent = [m for m in messages if m.get("from") == app.current_user_id]
    app.clear()
    app.header_bar("mail")
    for line in [f"INBOX    {len(inbox):>4}", f"WAITING  {sum(not m.get('read') for m in inbox):>4}", f"SENT     {len(sent):>4}", "Messages are addressed by numeric CompuServe User ID."]:
        app.ansi_scroll(line, 0.01)
    custom = app.current_profile.get("mail_folders", [])
    for number, name in enumerate(custom, 1):
        app.ansi_scroll(f"{number}  {name}", 0.01)
    choice = input("I INBOX, S SENT, C Create folder, A Address book, number, or M ! ").strip().upper()
    if choice == "I":
        message_list(app, inbox, messages, "EASYPLEX INBOX")
    elif choice == "S":
        message_list(app, sent, messages, "EASYPLEX SENT MESSAGES", sent_folder=True)
    elif choice == "C":
        name = input("Folder name: ").strip().upper()[:20]
        if name and name not in custom and name not in ("INBOX", "SENT"):
            custom.append(name)
            app.current_profile["mail_folders"] = custom
            app.save_profiles()
    elif choice == "A":
        address_book(app)
    elif choice.isdigit() and 1 <= int(choice) <= len(custom):
        name = custom[int(choice) - 1]
        contents = [m for m in messages if m.get("to") == app.current_user_id and m.get("folder") == name]
        message_list(app, contents, messages, f"EASYPLEX FOLDER: {name}")


def address_book(app):
    contacts = app.current_profile.setdefault("address_book", {})
    app.text_page("mail", "EASYPLEX ADDRESS BOOK", [f"{name:<16} {user_id}" for name, user_id in sorted(contacts.items())] or ["No contacts stored."])
    action = input("A Add contact, D Delete contact, or RETURN ! ").strip().upper()
    if action == "A":
        name = input("Short name: ").strip().upper()[:16]
        user_id = input("User ID: ").strip()
        if name and re.fullmatch(r"\d{5},\d{4}", user_id):
            contacts[name] = user_id
            app.save_profiles()
    elif action == "D":
        name = input("Short name to delete: ").strip().upper()
        if contacts.pop(name, None) is not None:
            app.save_profiles()


def settings(app):
    current = app.current_profile.get("mail_notice", True)
    app.ansi_scroll(f'Waiting-message notice is {"ON" if current else "OFF"}.', 0.01)
    if input("Enter Y to change it, or RETURN ! ").strip().upper() == "Y":
        app.current_profile["mail_notice"] = not current
        app.save_profiles()
