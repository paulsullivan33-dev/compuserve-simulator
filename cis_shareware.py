"""Seven-day forum and Data Library shareware release arc."""
from cis_session import read_input as input


ARC_ID = "TERMLINK-88"
MILESTONES = (
    (10, "ANNOUNCE", "TERMLINK TERMINAL UTILITY ANNOUNCED", "ByteBender announces TERMLINK, a capture and dialing utility for IBM-compatible systems."),
    (11, "RELEASE10", "TERMLINK 1.0 NOW IN LIBRARY 1", "Version 1.0 is approved as TERM10.TXT with installation and transfer notes."),
    (12, "REPORTS", "TERMLINK 1.0 SERIAL-PORT REPORTS", "Members report a possible COM2/IRQ3 conflict when another adapter shares the interrupt."),
    (13, "DIAGNOSTICS", "AUTHOR REQUESTS MODE AND IRQ DETAILS", "ByteBender asks testers to report DOS version, serial port, IRQ, and modem initialization string."),
    (14, "PATCH", "TERMLINK 1.1 PATCH SUBMITTED", "A candidate patch adds explicit COM-port selection and clearer conflict warnings."),
    (15, "APPROVED", "TERMLINK 1.1 APPROVED", "SysOp review approves TERM11.TXT and withdraws version 1.0 from new transfers."),
    (16, "THANKS", "TERMLINK TESTERS THANKED", "The author thanks members whose reports reproduced and corrected the conflict."),
)


def _arc(state):
    return state.setdefault("shareware_arcs", {}).setdefault(ARC_ID, {"published": [], "watchers": [], "participants": {}, "reputation_awarded": []})


def _add_file(app, name, number, version, status, description):
    files = app.library_files.setdefault("ibmhw_lib1", [])
    existing = next((item for item in files if item.get("shareware_arc") == ARC_ID and item.get("version") == version), None)
    if existing:
        existing["status"] = status
        return existing
    item = {"number": number, "name": name, "bytes": 4096, "date": app.cis_dynamic.simulation_day().strftime("%m/%d/%y"), "downloads": 0, "description": description, "status": status, "version": version, "shareware_arc": ARC_ID}
    files.append(item)
    return item


def _forum_post(app, milestone, subject, body):
    section = app.forum_threads.setdefault("ibmhw_tech", [])
    if any(message.get("shareware_milestone") == milestone for message in section):
        return
    ids = [message.get("id", 0) for messages in app.forum_threads.values() for message in messages]
    section.append({"id": max(ids, default=1000) + 1, "date": app.cis_dynamic.simulation_day().strftime("%m/%d/%y"), "author": "ByteBender", "author_user_id": "SIMULATED", "subject": subject, "body": body, "shareware_arc": ARC_ID, "shareware_milestone": milestone})


def ensure_arc(app):
    """Publish every due milestone once as the simulated date advances."""
    day = app.cis_dynamic.simulation_day().day
    state = app.cis_dynamic.load_state(app); arc = _arc(state)
    due = [(number, key, subject, body) for number, key, subject, body in MILESTONES if number <= day and key not in arc["published"]]
    if not due:
        return []
    notices = []
    for _, key, subject, body in due:
        _forum_post(app, key, subject, body)
        if key == "RELEASE10":
            _add_file(app, "TERM10.TXT", 1880, "1.0", "approved", "TERMLINK 1.0 terminal utility release notes and usage guide")
        elif key == "PATCH":
            _add_file(app, "TERM11.TXT", 1881, "1.1", "pending", "TERMLINK 1.1 candidate patch and tester notes")
        elif key == "APPROVED":
            old = _add_file(app, "TERM10.TXT", 1880, "1.0", "withdrawn", "TERMLINK 1.0 withdrawn after serial-port reports")
            old["replacement"] = 1881
            _add_file(app, "TERM11.TXT", 1881, "1.1", "approved", "TERMLINK 1.1 corrected release with explicit COM-port selection")
        arc["published"].append(key); notices.append(subject)
    app.save_json_atomic("forums.json", app.forum_threads)
    app.save_json_atomic("library_files.json", app.library_files)
    app.cis_dynamic.save_state(app, state)
    for user_id in arc["watchers"]:
        for subject in notices:
            app.cis_dynamic.schedule_event(app, "mail", {"to": user_id, "from": "IBMHW LIBRARY", "subject": subject, "body": f"The {ARC_ID} watched release has changed. Enter GO SHAREWARE for the project record and current files."})
    if "THANKS" in arc["published"]:
        state = app.cis_dynamic.load_state(app)
        arc = _arc(state)
        awarded = []
        for user_id, report in arc["participants"].items():
            if user_id in arc["reputation_awarded"]:
                continue
            report["reputation"] = report.get("reputation", 0) + 10
            arc["reputation_awarded"].append(user_id)
            awarded.append(user_id)
        app.cis_dynamic.save_state(app, state)
        for user_id in awarded:
            app.cis_dynamic.schedule_event(app, "mail", {"to": user_id, "from": "ByteBender", "subject": "THANKS FOR TESTING TERMLINK 1.1", "body": "Your configuration report helped the Forum reproduce the serial-port conflict. Ten contributor reputation points were recorded."})
    return notices


def lines(app):
    state = app.cis_dynamic.load_state(app); arc = _arc(state); user = app.current_user_id or "GUEST"
    published = set(arc["published"])
    output = ["TERMLINK-88 SHAREWARE PROJECT", "SEVEN-DAY IBM HARDWARE FORUM AND DATA LIBRARY ARC", ""]
    for day, key, subject, _ in MILESTONES:
        output.append(f'DEC {day:02d}  [{"POSTED" if key in published else "PENDING"}] {subject}')
    output.extend(["", f'WATCH {"ACTIVE" if user in arc["watchers"] else "OFF"}'])
    report = arc["participants"].get(user)
    output.append(f'CONTRIBUTOR {report.get("status", "NO REPORT")}  REPUTATION {report.get("reputation", 0)}' if report else "CONTRIBUTOR NO REPORT  REPUTATION 0")
    output.append("FILES")
    for item in app.library_files.get("ibmhw_lib1", []):
        if item.get("shareware_arc") == ARC_ID:
            output.append(f'  #{item["number"]} {item["name"]} VERSION {item["version"]} [{item["status"].upper()}]')
    return output


def watch(app):
    state = app.cis_dynamic.load_state(app); arc = _arc(state); user = app.current_user_id or "GUEST"
    if user in arc["watchers"]:
        arc["watchers"].remove(user); result = "Shareware project watch removed."
    else:
        arc["watchers"].append(user); result = "Shareware project watch active; updates will arrive by EasyPlex."
    app.cis_dynamic.save_state(app, state)
    return result


def report(app, details):
    if not details.strip():
        return "Configuration details are required."
    state = app.cis_dynamic.load_state(app); arc = _arc(state); user = app.current_user_id or "GUEST"
    arc["participants"][user] = {"status": "REPORT FILED", "details": details[:500], "reputation": arc["participants"].get(user, {}).get("reputation", 0)}
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.remember_member_for_user(app, user, "ByteBender", "TERMLINK testing", details)
    app.cis_dynamic.record_activity(app, user, "SHAREWARE", "Filed a TERMLINK configuration report.")
    return "Tester report filed with ByteBender and the IBM Hardware Forum project."


def service(app):
    ensure_arc(app)
    app.text_page("ibmhw", "TERMLINK SHAREWARE PROJECT", lines(app))
    action = input("W watch, R report configuration, D download current release, or RETURN ! ").strip().upper()
    if action == "W":
        app.ansi_scroll(watch(app), 0.01)
    elif action == "R":
        app.ansi_scroll(report(app, input("DOS, port, IRQ, modem and symptoms: ").strip()), 0.01)
    elif action == "D":
        candidates = [item for item in app.library_files.get("ibmhw_lib1", []) if item.get("shareware_arc") == ARC_ID and item.get("status") == "approved"]
        if candidates:
            newest = sorted(candidates, key=lambda item: item.get("version", ""))[-1]
            destination = app.cis_library.materialize_download(app, newest, "B")
            app.ansi_scroll(f"Transfer complete: {destination.name}", 0.01)
        else:
            app.ansi_scroll("No approved TERMLINK release is available yet.", 0.01)
