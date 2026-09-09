"""Persistent EasyPlex and Forum composition drafts."""

from datetime import datetime, timezone


def _user(app):
    return app.current_user_id or "GUEST"


def get_draft(app, service):
    state = app.cis_dynamic.load_state(app)
    return state.get("drafts", {}).get(_user(app), {}).get(service)


def list_drafts(app):
    drafts = app.cis_dynamic.load_state(app).get("drafts", {}).get(_user(app), {})
    return sorted((dict(draft) for draft in drafts.values()), key=lambda item: item.get("updated_at", ""), reverse=True)


def save_draft(app, service, **fields):
    draft = {"service": service, "updated_at": datetime.now(timezone.utc).isoformat(timespec="microseconds"), **fields}

    def save(state):
        state.setdefault("drafts", {}).setdefault(_user(app), {})[service] = draft

    app.update_json_atomic("dynamic_state.json", {}, save)
    return draft


def delete_draft(app, service):
    def remove(state):
        user_drafts = state.setdefault("drafts", {}).setdefault(_user(app), {})
        user_drafts.pop(service, None)

    app.update_json_atomic("dynamic_state.json", {}, remove)


def draft_summary(draft):
    if not draft:
        return "No saved draft."
    destination = draft.get("recipient") or draft.get("section") or "UNKNOWN"
    return f'{draft.get("service", "DRAFT").upper()} to {destination}: {draft.get("subject") or "(no subject)"}'
