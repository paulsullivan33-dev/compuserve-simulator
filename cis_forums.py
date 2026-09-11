"""Forum message persistence and authorization rules."""
from cis_session import read_input as input


def post(app, section_key, subject, body, parent_id=None):
    ids = [m.get("id", 0) for messages in app.forum_threads.values() for m in messages]
    message_id = max(ids, default=1000) + 1
    app.forum_threads.setdefault(section_key, []).append({
        "id": message_id, "date": app.SIMULATION_DATE, "parent_id": parent_id,
        "author": app.current_handle or app.current_user_id,
        "author_user_id": app.current_user_id, "subject": subject[:120], "body": body[:5000],
    })
    app.save_json_atomic("forums.json", app.forum_threads)
    app.cis_dynamic.record_activity(app, app.current_user_id, "FORUM", f'Posted message #{message_id}: {subject}.', {"section": section_key, "message_id": message_id})
    suggestions = app.cis_reference.suggest_records(f"{subject} {body}", 2)
    if suggestions:
        app.ansi_scroll("Reference Data Bases: " + "; ".join(f"{record[0]} {record[1]}" for _, record in suggestions), 0.005)
    if parent_id is None:
        correspondent = app.cis_dynamic.begin_forum_case(app, section_key, message_id, subject, body)
        if correspondent:
            app.ansi_scroll(f"Your message has been entered. {correspondent} usually reads this section.", 0.01)
    if parent_id is not None:
        root_id = thread_root_id(app.forum_threads[section_key], parent_id)
        for user_id, profile in app.profiles.items():
            if root_id in profile.get("watched_threads", []) and user_id != app.current_user_id:
                app.cis_dynamic.schedule_event(app, "mail", {"to": user_id, "from": "FORUMS", "subject": f"REPLY TO THREAD #{root_id}", "body": f"A new reply, message #{message_id}, has been posted in {section_key}. Use FIND {subject} to locate it."})
    app.ansi_scroll("Message posted.", 0.01)


def thread_root_id(messages, message_id):
    by_id = {message.get("id"): message for message in messages}
    current = by_id.get(message_id)
    seen = set()
    while current and current.get("parent_id") is not None and current.get("id") not in seen:
        seen.add(current.get("id"))
        current = by_id.get(current.get("parent_id"), current)
    return current.get("id") if current else message_id


def message_actions(app, section_key, message):
    action = input("R Reply, W Watch, D Delete, or RETURN ! ").strip().upper()
    if action == "R":
        if message.get("author_user_id") == "SIMULATED":
            app.cis_dynamic.remember_member(app, message.get("author", "MEMBER"), "forum reply", message.get("subject", ""))
        subject = message.get("subject", "")
        reply_subject = subject if subject.upper().startswith("RE:") else "RE: " + subject
        initial = [f'In reply to message #{message["id"]}:']
        app.cis_drafts.save_draft(app, "forum", section=section_key, subject=reply_subject, parent_id=message["id"], lines=initial)
        body = app.line_editor(initial_lines=initial, on_change=lambda lines: app.cis_drafts.save_draft(app, "forum", section=section_key, subject=reply_subject, parent_id=message["id"], lines=lines))
        if body:
            post(app, section_key, reply_subject, body, parent_id=message["id"])
            app.cis_drafts.delete_draft(app, "forum")
    elif action == "W":
        watched = app.current_profile.setdefault("watched_threads", [])
        root_id = thread_root_id(app.forum_threads[section_key], message["id"])
        if root_id not in watched:
            watched.append(root_id)
            app.save_profiles()
        app.ansi_scroll("Thread watch is active.", 0.01)
    elif action == "D":
        legacy_owner = message.get("author") == (app.current_handle or app.current_user_id)
        owner = message.get("author_user_id") == app.current_user_id or legacy_owner
        if not (owner or app.current_profile.get("is_sysop")):
            app.ansi_scroll("Only the author or SysOp may delete this message.", 0.01)
            return
        app.forum_threads[section_key].remove(message)
        app.save_json_atomic("forums.json", app.forum_threads)
        app.ansi_scroll("Message deleted.", 0.01)


def set_watch(app, message_id, enabled=True):
    watched = app.current_profile.setdefault("watched_threads", [])
    if enabled and message_id not in watched:
        watched.append(message_id)
    elif not enabled and message_id in watched:
        watched.remove(message_id)
    app.save_profiles()
    return "Thread watch is active." if enabled else "Thread watch removed."


def thread_lines(messages, root_id):
    by_parent = {}
    by_id = {message.get("id"): message for message in messages}
    for message in messages:
        by_parent.setdefault(message.get("parent_id"), []).append(message)
    root = by_id.get(root_id)
    if not root:
        return ["Thread not found."]
    while root.get("parent_id") in by_id:
        root = by_id[root["parent_id"]]
    lines = []
    def visit(message, depth):
        branch = "  " * depth + ("+- " if depth else "")
        lines.append(f'{branch}#{message.get("id")} {message.get("author", "")} - {message.get("subject", "")}')
        for child in sorted(by_parent.get(message.get("id"), []), key=lambda item: item.get("id", 0)):
            visit(child, depth + 1)
    visit(root, 0)
    return lines
