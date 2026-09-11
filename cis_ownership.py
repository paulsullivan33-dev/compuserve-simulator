"""Persistent ownership and after-sale support for fictional catalog products."""
from cis_session import read_input as input


def receive_order(app, order):
    """Convert a delivered order into member-owned equipment exactly once."""
    state = app.cis_dynamic.load_state(app)
    inventories = state.setdefault("owned_equipment", {})
    inventory = inventories.setdefault(order.get("user_id") or "GUEST", [])
    existing = {(item.get("order"), item.get("sku"), item.get("unit")) for item in inventory}
    added = []
    for line in order.get("items", []):
        for unit in range(1, int(line.get("quantity", 1)) + 1):
            key = (order.get("number"), line.get("sku"), unit)
            if key in existing:
                continue
            asset = {
                "id": f'EQ-{len(inventory) + 1:04d}', "order": order.get("number"),
                "sku": line.get("sku"), "name": line.get("name", "Catalog item"),
                "unit": unit, "status": "DELIVERED - NOT INSTALLED",
                "received": app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes"),
                "system": None, "support_case": None, "review": None,
            }
            inventory.append(asset); added.append(asset)
    app.cis_dynamic.save_state(app, state)
    if added:
        app.cis_dynamic.record_activity(app, order.get("user_id"), "EQUIPMENT", f'{len(added)} item(s) from {order.get("number")} added to owned equipment.')
    return added


def equipment(app):
    return app.cis_dynamic.load_state(app).get("owned_equipment", {}).get(app.current_user_id or "GUEST", [])


def inventory_lines(app):
    items = equipment(app)
    lines = ["MY COMP-U-STORE EQUIPMENT", ""]
    for item in items:
        lines.append(f'{item["id"]}  {item["sku"]}  {item["name"][:38]:<38} [{item["status"]}]')
        detail = f'  ORDER {item["order"]}' + (f'  SYSTEM {item["system"]}' if item.get("system") else "")
        if item.get("support_case"):
            detail += f'  CASE {item["support_case"]}'
        lines.append(detail)
    return lines if items else [*lines, "No delivered catalog equipment."]


def _asset(app, asset_id, state=None):
    state = state or app.cis_dynamic.load_state(app)
    return next((item for item in state.get("owned_equipment", {}).get(app.current_user_id or "GUEST", []) if item.get("id") == asset_id.upper()), None)


def install(app, asset_id, system):
    state = app.cis_dynamic.load_state(app); asset = _asset(app, asset_id, state)
    if not asset:
        return "Equipment item not found."
    normalized, compatible = app.cis_store.compatible_products(system)
    if not normalized:
        return "System not in compatibility index."
    asset["system"] = normalized
    if asset["sku"] in {product["sku"] for product in compatible}:
        asset["status"] = "INSTALLED"
        result = f'{asset["name"]} installed for {normalized}.'
    else:
        asset["status"] = "COMPATIBILITY HELP NEEDED"
        result = f'{asset["name"]} is not listed for {normalized}; open a WARRANTY case for assistance.'
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.record_activity(app, app.current_user_id, "EQUIPMENT", result)
    return result


def warranty(app, asset_id, description):
    state = app.cis_dynamic.load_state(app); asset = _asset(app, asset_id, state)
    if not asset or not description.strip():
        return "Equipment item and problem description are required."
    cases = state.setdefault("equipment_cases", [])
    number = max((case.get("number", 7000) for case in cases), default=7000) + 1
    asset["support_case"] = f"W{number}"
    asset["status"] = "WARRANTY REVIEW"
    cases.append({"number": number, "asset": asset["id"], "user_id": app.current_user_id, "status": "OPEN", "description": description[:500]})
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.schedule_event(app, "mail", {"to": app.current_user_id, "from": "Helen/Orders", "subject": f'WARRANTY CASE W{number}', "body": f'We received your report for {asset["name"]}: {description[:500]}\n\nA vendor response and return guidance will follow.'})
    app.cis_dynamic.remember_member_for_user(app, app.current_user_id, "Helen/Orders", "warranty support", description)
    section = app.forum_threads.setdefault("ibmhw_tech", [])
    ids = [message.get("id", 0) for messages in app.forum_threads.values() for message in messages]
    section.append({"id": max(ids, default=1000) + 1, "date": app.cis_dynamic.simulation_day().strftime("%m/%d/%y"), "author": "VendorLiaison", "author_user_id": "SIMULATED", "subject": f'GENERAL INSTALLATION NOTES FOR SKU {asset["sku"]}', "body": "Verify power is off, record switch and jumper settings, and preserve original packaging before requesting exchange service."})
    app.save_json_atomic("forums.json", app.forum_threads)
    return f"Warranty case W{number} opened; EasyPlex and Forum guidance will follow."


def return_item(app, asset_id):
    state = app.cis_dynamic.load_state(app); asset = _asset(app, asset_id, state)
    if not asset:
        return "Equipment item not found."
    if asset.get("status") in ("RETURN REQUESTED", "RETURNED"):
        return "A return is already recorded for this item."
    asset["status"] = "RETURN REQUESTED"
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.schedule_event(app, "mail", {"to": app.current_user_id, "from": "COMP-U-STORE RETURNS", "subject": f'RETURN AUTHORIZATION {asset["id"]}', "body": f'Retain all accessories and packaging for {asset["name"]}. This fictional authorization does not move real goods or funds.'})
    return "Return authorization requested; instructions will arrive by EasyPlex."


def review(app, asset_id, text):
    state = app.cis_dynamic.load_state(app); asset = _asset(app, asset_id, state)
    if not asset or not text.strip():
        return "Equipment item and review text are required."
    asset["review"] = text.strip()[:500]
    state.setdefault("owner_reviews", []).append({"sku": asset["sku"], "user_id": app.current_user_id, "asset": asset["id"], "text": asset["review"], "date": app.cis_dynamic.simulation_day().isoformat()})
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.record_activity(app, app.current_user_id, "EQUIPMENT", f'Posted owner report for {asset["name"]}.')
    return "Owner report recorded."


def sell(app, asset_id, price):
    state = app.cis_dynamic.load_state(app); asset = _asset(app, asset_id, state)
    if not asset:
        return "Equipment item not found."
    try:
        amount = float(price)
    except ValueError:
        return "Enter a numeric asking price."
    result = app.cis_dynamic.post_classified(app, f'FOR SALE: {asset["name"]} ({asset["id"]}), ${amount:.2f}. USER {app.current_user_id}', "COMPUTERS")
    state = app.cis_dynamic.load_state(app)
    asset = _asset(app, asset_id, state)
    asset["status"] = f"LISTED AS CLASSIFIED #{result}"
    app.cis_dynamic.save_state(app, state)
    return f"Equipment listed as classified #{result}."


def service(app):
    app.text_page("shopping", "OWNED EQUIPMENT AND SUPPORT", inventory_lines(app))
    asset_id = input("Equipment ID, or RETURN ! ").strip().upper()
    if not asset_id:
        return
    action = input("INSTALL, WARRANTY, RETURN, REVIEW, or SELL ! ").strip().upper()
    if action == "INSTALL":
        result = install(app, asset_id, input("Computer system: ").strip())
    elif action == "WARRANTY":
        result = warranty(app, asset_id, input("Describe the problem: ").strip())
    elif action == "RETURN":
        result = return_item(app, asset_id)
    elif action == "REVIEW":
        result = review(app, asset_id, input("Owner report: ").strip())
    elif action == "SELL":
        result = sell(app, asset_id, input("Asking price: ").strip())
    else:
        result = "Unknown equipment action."
    app.ansi_scroll(result, 0.01)
