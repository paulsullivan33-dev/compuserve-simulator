"""Cross-service discovery and period-style search."""

import cis_reference
import cis_store
import cis_business
import cis_travel
import cis_timeline
import cis_features
import cis_magazine


def whats_new(app):
    state = app.cis_dynamic.load_state(app)
    messages = app.load_json("easyplex.json", default=[])
    unread = sum(m.get("to") == app.current_user_id and not m.get("read") for m in messages)
    last_read = app.current_profile.get("forum_last_read", {})
    new_posts = sum(m.get("id", 0) > last_read.get(section, 0) for section, group in app.forum_threads.items() for m in group)
    recent_files = sorted((f for group in app.library_files.values() for f in group if f.get("status", "approved") == "approved"), key=lambda f: f.get("number", 0), reverse=True)[:3]
    pending = sum(not event.get("processed") for event in state["events"])
    topic, conference_status = app.cis_dynamic.conference_schedule("ibmhw")
    lines = [f"EASYPLEX WAITING       {unread}", f"NEW FORUM MESSAGES     {new_posts}", f"SCHEDULED EVENTS       {pending}", f"TONIGHT: {topic}", f"          {conference_status}", "", "RECENT LIBRARY FILES"]
    lines.extend(f'{f["number"]:>4} {f["name"]:<12} {f["description"]}' for f in recent_files)
    lines.extend(["", "Use FIND words to search forums, libraries, classifieds, and references."])
    return lines


def activity_items(app):
    """Return selectable, currently relevant activity for the signed-in member."""
    items = []
    issues = cis_magazine.available(app.cis_dynamic.simulation_day())
    if issues:
        issue = issues[0]
        unread = len(issue['articles']) - cis_magazine.read_count(app, issue)
        token = f"magazine:{issue['id']}"
        if unread and token not in app.current_profile.get('activity_seen', []):
            items.append({'kind': 'MAGAZINE', 'token': token,
                          'summary': f"ONLINE WEEKLY - {issue['title']} ({unread} unread)", 'record': issue})
    seen_activity = set(app.current_profile.get("activity_seen", []))
    read_features = set(app.current_profile.get("features_read", []))
    for feature in cis_features.FEATURES:
        token = f'feature:{feature["id"]}'
        if feature["id"] not in read_features and token not in seen_activity:
            items.append({"kind": "FEATURE", "token": token, "summary": f'NEW FEATURE - {feature["title"]}', "record": feature})
    for draft in app.cis_drafts.list_drafts(app):
        token = f'draft:{draft.get("service")}:{draft.get("updated_at")}'
        if token not in seen_activity:
            items.append({"kind": "DRAFT", "token": token, "summary": app.cis_drafts.draft_summary(draft), "record": draft})
    for record in cis_timeline.records_for_date(app.cis_dynamic.simulation_day()):
        token = f'timeline:{record["id"]}'
        if token not in seen_activity:
            items.append({"kind": "HISTORY", "token": token, "summary": f'{record["category"]} - {record["title"]}', "record": record})
    for announcement in app.cis_announcements.active(app, app.current_user_id or "GUEST", include_read=False):
        items.append({"kind": "NOTICE", "token": f'announcement:{announcement["id"]}', "summary": f'{announcement.get("priority", "NORMAL")} - {announcement.get("title")}', "record": announcement})
    messages = app.load_json("easyplex.json", default=[])
    for message in messages:
        if message.get("to") == app.current_user_id and not message.get("read"):
            items.append({
                "kind": "MAIL", "token": f'mail:{message.get("id")}',
                "summary": f'{message.get("from", "UNKNOWN")}: {message.get("subject", "(no subject)")}',
                "message_id": message.get("id"),
            })

    last_read = app.current_profile.get("forum_last_read", {})
    watched = set(app.current_profile.get("watched_threads", []))
    for section, messages_in_section in app.forum_threads.items():
        for message in messages_in_section:
            if message.get("id", 0) <= last_read.get(section, 0):
                continue
            root_id = app.cis_forums.thread_root_id(messages_in_section, message.get("id"))
            marker = "WATCHED" if root_id in watched else section.upper()
            items.append({
                "kind": "FORUM", "token": f'forum:{section}:{message.get("id")}',
                "summary": f'{marker} #{message.get("id")} {message.get("subject", "")}',
                "section": section, "message_id": message.get("id"),
            })

    seen = set(app.current_profile.get("activity_seen", []))
    for order in app.load_json("orders.json", default=[]):
        if order.get("user_id") != app.current_user_id:
            continue
        token = f'order:{order.get("number")}:{order.get("status", "RECEIVED")}'
        if token not in seen:
            items.append({"kind": "ORDER", "token": token, "summary": f'{order.get("number")} {order.get("name")} [{order.get("status", "RECEIVED")}]', "record": order})

    state = app.cis_dynamic.load_state(app)
    for reservation in state.get("reservations", []):
        if reservation.get("user_id") != app.current_user_id:
            continue
        token = f'reservation:{reservation.get("confirmation")}:{reservation.get("status")}'
        if token not in seen:
            items.append({"kind": "TRAVEL", "token": token, "summary": f'{reservation.get("confirmation")} {reservation.get("origin")}-{reservation.get("destination")} [{reservation.get("status")}]', "record": reservation})
    for event in state.get("events", []):
        payload = event.get("payload", {})
        owner = payload.get("to") or payload.get("user_id")
        token = f'event:{event.get("id")}'
        if not event.get("processed") and owner == app.current_user_id and token not in seen:
            items.append({"kind": "EVENT", "token": token, "summary": f'{event.get("type", "event").replace("_", " ").upper()} due {event.get("due_at", "")}', "record": event})
    return items


def mark_activity_seen(app, item):
    if item["kind"] == "NOTICE":
        app.cis_announcements.mark_read(app, item["record"]["id"], app.current_user_id or "GUEST")
    elif item["kind"] == "MAIL":
        messages = app.load_json("easyplex.json", default=[])
        message = next((entry for entry in messages if entry.get("id") == item.get("message_id") and entry.get("to") == app.current_user_id), None)
        if message:
            message["read"] = True
            app.save_json_atomic("easyplex.json", messages)
    elif item["kind"] == "FORUM":
        reads = app.current_profile.setdefault("forum_last_read", {})
        reads[item["section"]] = max(reads.get(item["section"], 0), item.get("message_id", 0))
        app.save_profiles()
    else:
        seen = app.current_profile.setdefault("activity_seen", [])
        if item["token"] not in seen:
            seen.append(item["token"])
            del seen[:-100]
            app.save_profiles()


def mark_all_activity_seen(app, items=None):
    for item in items if items is not None else activity_items(app):
        mark_activity_seen(app, item)


def open_activity(app, item):
    mark_activity_seen(app, item)
    if item['kind'] == 'MAGAZINE':
        cis_magazine.service(app, item['record']['id'])
        return True
    if item["kind"] == "DRAFT":
        app.resume_draft_record(item["record"])
        return True
    if item["kind"] == "HISTORY":
        app.timeline_record_page(item["record"])
        return True
    if item["kind"] == "FEATURE":
        app.feature_service(item["record"]["id"])
        return True
    if item["kind"] == "NOTICE":
        record = item["record"]
        app.text_page("main", record.get("title", "SYSTEM ANNOUNCEMENT"), app.cis_announcements.article_lines(record))
        return True
    if item["kind"] == "MAIL":
        messages = app.load_json("easyplex.json", default=[])
        message = next((entry for entry in messages if entry.get("id") == item.get("message_id")), None)
        if message:
            app.text_page("mail", f'Message {message.get("id", "")}', [f'From: {message.get("from", "")}', f'To: {message.get("to", "")}', f'Date: {message.get("date", "")}', f'Subject: {message.get("subject", "")}', "", message.get("body", "")])
            return True
    elif item["kind"] == "FORUM":
        return open_result(app, f'FORUM {item["section"]} #{item["message_id"]} {item["summary"]}')
    elif item["kind"] == "ORDER":
        order = item["record"]
        app.text_page("shopping", f'ORDER {order.get("number")}', [f'Item: {order.get("name")}', f'Date: {order.get("date", "")}', f'Status: {order.get("status", "RECEIVED")}', "", "All orders and charges are fictional."])
        return True
    elif item["kind"] == "TRAVEL":
        reservation = item["record"]
        app.text_page("travel", f'RESERVATION {reservation.get("confirmation")}', [f'{reservation.get("origin")} to {reservation.get("destination")}', f'Status: {reservation.get("status")}', reservation.get("flight", ""), "", "All schedules and reservations are fictional."])
        return True
    elif item["kind"] == "EVENT":
        event = item["record"]
        app.text_page("support", "SCHEDULED EVENT", [f'Type: {event.get("type")}', f'Due: {event.get("due_at")}', f'Details: {event.get("payload", {})}'])
        return True
    return False


def search(app, query):
    query = query.strip().lower()
    if not query:
        return ["Enter FIND followed by one or more words."]
    results = []
    for section, messages in app.forum_threads.items():
        for message in messages:
            haystack = " ".join(str(message.get(k, "")) for k in ("author", "subject", "body")).lower()
            if query in haystack:
                results.append(f'FORUM {section} #{message.get("id")} {message.get("subject", "")[:45]}')
    for section, files in app.library_files.items():
        for file in files:
            if query in f'{file.get("name", "")} {file.get("description", "")}'.lower():
                results.append(f'LIB {section} #{file.get("number")} {file.get("name")} - {file.get("description", "")[:40]}')
    state = app.cis_dynamic.load_state(app)
    for item in state.get("classifieds", []):
        if item.get("status") == "ACTIVE" and query in item.get("text", "").lower():
            results.append("CLASSIFIED " + item["text"][:65])
    for entry in app.service_data.get("reference", []):
        if query in f'{entry.get("term", "")} {entry.get("text", "")}'.lower():
            results.append(f'REFERENCE {entry.get("term")}: {entry.get("text", "")[:50]}')
    for database in cis_reference.DATABASES:
        for record in cis_reference.search(database, query):
            results.append(f'REFERENCE {record[0]} {record[1]}')
    for product in cis_store.search(query):
        results.append(f'STORE #{product["sku"]} {product["name"]} ${product["price"]:.2f}')
    for company in cis_business.directory(query):
        results.append(f'COMPANY {company[0]} {company[1]} - {company[2]}')
    for code, city in cis_travel.AIRPORTS.items():
        if query in f"{code} {city}".lower():
            results.append(f"AIRPORT {code} {city}")
    for city, hotels in cis_travel.HOTELS.items():
        for name, rate, _ in hotels:
            if query in f"{city} {name}".lower():
                results.append(f"HOTEL {city} {name} FROM ${rate}")
    for record in cis_timeline.search(query):
        results.append(f'TIMELINE {record["id"]} {record["date"]} {record["title"]}')
    for feature in cis_features.FEATURES:
        text = " ".join([feature["title"], feature["deck"], *[chapter["title"] + " " + chapter["text"] for chapter in feature["chapters"]]])
        if query in text.lower():
            results.append(f'FEATURE {feature["id"]} {feature["title"]}')
    for issue, article in cis_magazine.search(query, app.cis_dynamic.simulation_day()):
        results.append(f"MAGAZINE {issue['id']} {article['id']} {article['title']}")
    return results[:50] or ["No matching service records found."]


def open_result(app, result):
    if result.startswith('MAGAZINE '):
        parts = result.split()
        if len(parts) >= 3:
            issue = cis_magazine.find_issue(parts[1], app.cis_dynamic.simulation_day())
            if issue and any(article['id'] == parts[2] for article in issue['articles']):
                cis_magazine.service(app, issue['id'], parts[2])
                return True
        return False
    if result.startswith("FORUM ") and " #" in result:
        message_id = result.split(" #", 1)[1].split()[0]
        for section, messages in app.forum_threads.items():
            message = next((m for m in messages if str(m.get("id")) == message_id), None)
            if message:
                app.text_page("forums", f'Message #{message_id}', [f'From: {message.get("author", "")}', f'Subject: {message.get("subject", "")}', "", message.get("body", "")])
                return True
    if result.startswith("LIB ") and " #" in result:
        number = result.split(" #", 1)[1].split()[0]
        for files in app.library_files.values():
            file = next((f for f in files if str(f.get("number")) == number), None)
            if file:
                app.library_transfer(file)
                return True
    if result.startswith("REFERENCE "):
        record_id = result.split()[1]
        for database, definition in cis_reference.DATABASES.items():
            record = next((item for item in definition["records"] if item[0] == record_id), None)
            if record:
                app.text_page("reference", record[1], cis_reference.article_lines(record, database))
                return True
    if result.startswith("STORE #"):
        sku = result.split("#", 1)[1].split()[0]
        product = cis_store.find_product(sku)
        if product:
            app.text_page("shopping", f'CATALOG ITEM {product["sku"]}', cis_store.product_details(product))
            return True
    if result.startswith("COMPANY "):
        symbol = result.split()[1]
        app.text_page("finance", "STANDARD & POOR'S COMPANY REPORT", cis_business.report(symbol, app.cis_dynamic.market_quotes(app.service_data.get("quotes", {}))))
        return True
    if result.startswith(("AIRPORT ", "HOTEL ")):
        app.text_page("travel", "TRAVEL DIRECTORY RESULT", [result, "Schedules, rates, and availability are fictional simulation data."])
        return True
    if result.startswith("TIMELINE "):
        record = cis_timeline.find(result.split()[1])
        if record:
            app.timeline_record_page(record)
            return True
    app.text_page("command", "SEARCH RESULT", [result])
    return True
