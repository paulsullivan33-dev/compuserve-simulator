"""Comp-U-Store catalog, cart, and fictional order helpers."""

import json
import hashlib
import os
from datetime import timedelta
from pathlib import Path

import cis_dynamic

CATALOG_PATH = Path(__file__).resolve().with_name("store_catalog.json")
CATALOG = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
if len(CATALOG) != 36 or len({item["sku"] for item in CATALOG}) != 36:
    raise RuntimeError("Comp-U-Store catalog must contain 36 unique items.")

COMPATIBILITY = {
    "IBM PC/XT": {1101, 1102, 1103, 1201, 1202, 1204, 1301, 1303, 1304, 1401, 1402, 1403, 1404, 1501, 1502, 1503, 1504, 1505, 1506, 1601, 1602, 1603, 1701, 1702, 1703, 1704, 1801, 1802, 1803, 1804, 1805, 1806},
    "IBM PC AT": {1101, 1102, 1103, 1201, 1202, 1204, 1301, 1302, 1303, 1304, 1401, 1402, 1403, 1404, 1501, 1502, 1503, 1504, 1505, 1506, 1601, 1602, 1603, 1701, 1702, 1703, 1704, 1802, 1803, 1804, 1805, 1806},
    "MACINTOSH PLUS": {1101, 1102, 1104, 1203, 1302, 1304, 1401, 1403, 1404, 1601, 1602, 1604, 1703, 1704},
    "COMMODORE 64": {1101, 1102, 1104, 1202, 1301, 1303, 1304, 1401, 1403, 1404, 1601, 1602, 1703},
    "TRS-80 MODEL I/III": {1101, 1102, 1104, 1202, 1204, 1301, 1303, 1304, 1401, 1403, 1404, 1601, 1602, 1703},
}
REVIEWS = {
    1101: ("ModemMan", "Reliable on noisy evening calls; the front-panel lamps make diagnosis much easier."),
    1102: ("PacketPete", "Fast enough to make a long library transfer practical, provided the serial port is configured properly."),
    1301: ("DiskDoctor", "I still test a new box before trusting it with the only copy of anything important."),
    1503: ("NightOwl", "A capable dialing directory and capture facility for regular information-service callers."),
    1505: ("LadyLogic", "The integrated editor makes small Pascal projects pleasantly quick to revise."),
    1802: ("DataDave", "Useful for programs that support LIM memory, but check the switch settings and available slots first."),
    1804: ("ByteBender", "Sharp text and impressive color; retain compatibility modes for older games."),
    1806: ("ByteBender", "A remarkable improvement in supported games, although software support still varies."),
}

def _daily_number(label, sku=0):
    day = cis_dynamic.simulation_day().isoformat()
    return int.from_bytes(hashlib.sha256(f"{day}:{label}:{sku}".encode()).digest()[:4], "big")

def catalog_issue():
    day = cis_dynamic.simulation_day()
    return f"DECEMBER 1988 CATALOG / ISSUE {day.day:02d}"

def stock_status(sku):
    value = _daily_number("stock", int(sku)) % 20
    if value == 0:
        return "BACK ORDER - ALLOW 3 TO 5 WEEKS"
    if value < 4:
        return "LIMITED QUANTITY"
    return "IN STOCK"

def specials():
    eligible = [item for item in CATALOG if stock_status(item["sku"]).startswith("IN STOCK")]
    ranked = sorted(eligible, key=lambda item: _daily_number("special", item["sku"]))[:4]
    return [{**item, "sale_price": round(item["price"] * (0.85 if index == 0 else 0.9), 2)} for index, item in enumerate(ranked)]

def effective_price(product):
    offer = next((item for item in specials() if item["sku"] == product["sku"]), None)
    return offer["sale_price"] if offer else product["price"]

def compatible_products(system):
    normalized = system.strip().upper()
    key = next((name for name in COMPATIBILITY if name == normalized or normalized in name), None)
    return (key, [item for item in CATALOG if item["sku"] in COMPATIBILITY[key]]) if key else (None, [])

def product_details(product):
    price = effective_price(product)
    lines = [product["name"], product["description"], "", f'CATALOG PRICE ${product["price"]:.2f}']
    if price != product["price"]:
        lines.append(f'DECEMBER SPECIAL ${price:.2f}')
    lines.extend([f'SHIPPING     ${product["shipping"]:.2f}', f'AVAILABILITY {stock_status(product["sku"])}', f'CATEGORY     {product["category"]}'])
    systems = [name for name, skus in COMPATIBILITY.items() if product["sku"] in skus]
    if systems:
        lines.extend(["", "COMPATIBILITY", "  " + ", ".join(systems)])
    if product["sku"] in REVIEWS:
        handle, report = REVIEWS[product["sku"]]
        lines.extend(["", f"OWNER REPORT -- {handle}", f'  "{report}"'])
    if os.environ.get("CIS_STORE_ALERT"):
        lines.extend(["", "CATALOG BULLETIN: " + os.environ["CIS_STORE_ALERT"]])
    lines.extend(["", "Compatibility lists are a catalog guide; verify slots, ports,", "software version, and monitor requirements before ordering."])
    return lines

def categories():
    return sorted({item["category"] for item in CATALOG})

def find_product(sku):
    return next((item for item in CATALOG if str(item["sku"]) == str(sku)), None)

def search(query="", category=None):
    words = query.lower().split()
    return [item for item in CATALOG if (not category or item["category"] == category.upper()) and all(word in f'{item["name"]} {item["description"]} {item["category"]}'.lower() for word in words)]

def _cart(app, state=None):
    state = app.cis_dynamic.load_state(app) if state is None else state
    return state.setdefault("store_carts", {}).setdefault(app.current_user_id or "GUEST", [])

def add_to_cart(app, sku, quantity=1):
    product = find_product(sku)
    if not product or quantity < 1 or quantity > 9:
        return "Item or quantity not valid."
    def update(state):
        cart = _cart(app, state); line = next((item for item in cart if item["sku"] == product["sku"]), None)
        if line: line["quantity"] = min(9, line["quantity"] + quantity)
        else: cart.append({"sku": product["sku"], "quantity": quantity})
    if hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = app.cis_dynamic.load_state(app); update(state); app.cis_dynamic.save_state(app, state)
    return f'{product["name"]} added to order.'

def remove_from_cart(app, sku):
    removed = {"value": False}
    def update(state):
        cart = _cart(app, state); before = len(cart)
        cart[:] = [line for line in cart if str(line["sku"]) != str(sku)]; removed["value"] = len(cart) < before
    if hasattr(app, "update_json_atomic"): app.update_json_atomic("dynamic_state.json", {}, update)
    else:
        state = app.cis_dynamic.load_state(app); update(state); app.cis_dynamic.save_state(app, state)
    return "Item removed." if removed["value"] else "Item was not in the order."

def cart_summary(app):
    cart = _cart(app)
    lines, subtotal, shipping = [], 0.0, 0.0
    for line in cart:
        product = find_product(line["sku"])
        if not product:
            continue
        unit_price = effective_price(product)
        extended = unit_price * line["quantity"]
        subtotal += extended
        shipping += product["shipping"] + max(0, line["quantity"] - 1) * product["shipping"] * 0.35
        lines.append(f'{product["sku"]} {line["quantity"]} @ ${unit_price:.2f}  {product["name"]}  ${extended:.2f}')
    return lines, round(subtotal, 2), round(shipping, 2)

def checkout(app):
    lines, subtotal, shipping = cart_summary(app)
    if not lines:
        return None
    state = app.cis_dynamic.load_state(app)
    cart = list(_cart(app, state))
    orders = app.load_json("orders.json", default=[])
    order_id = max((int(order.get("order_id", 1000)) for order in orders), default=1000) + 1
    event_key = f"STORE-{app.current_user_id}-{order_id}"
    items = [{**line, "name": find_product(line["sku"])["name"], "unit_price": effective_price(find_product(line["sku"])), "availability": stock_status(line["sku"])} for line in cart]
    backordered = any(item["availability"].startswith("BACK ORDER") for item in items)
    order = {"order_id": order_id, "number": f"CIS-{order_id}", "name": f"{len(items)} CATALOG ITEM(S)", "items": items, "subtotal": subtotal, "shipping": shipping, "price": round(subtotal + shipping, 2), "user_id": app.current_user_id, "date": app.SIMULATION_DATE, "status": "RECEIVED", "event_key": event_key, "catalog_issue": catalog_issue()}
    orders.append(order)
    app.save_json_atomic("orders.json", orders)
    state["store_carts"][app.current_user_id or "GUEST"] = []
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.schedule_event(app, "order_status", {"event_key": event_key, "status": "BACK ORDER" if backordered else "PROCESSING", "to": app.current_user_id, "number": order["number"]}, app.cis_dynamic.simulation_datetime() + timedelta(days=1))
    app.cis_dynamic.schedule_event(app, "order_status", {"event_key": event_key, "status": "SHIPPED", "to": app.current_user_id, "number": order["number"]}, app.cis_dynamic.simulation_datetime() + timedelta(days=7 if backordered else 3))
    app.cis_dynamic.schedule_event(app, "order_status", {"event_key": event_key, "status": "DELIVERED", "to": app.current_user_id, "number": order["number"]}, app.cis_dynamic.simulation_datetime() + timedelta(days=10 if backordered else 5))
    app.cis_dynamic.schedule_event(app, "mail", {"to": app.current_user_id, "from": "COMP-U-STORE", "subject": f'ORDER {order["number"]} RECEIVED', "body": f'Your fictional catalog order totals ${order["price"]:.2f}, including ${shipping:.2f} shipping. Status changes will appear under GO PROFILE.'})
    app.cis_dynamic.record_activity(app, app.current_user_id, "STORE", f'Placed fictional order {order["number"]} for ${order["price"]:.2f}.')
    return order
