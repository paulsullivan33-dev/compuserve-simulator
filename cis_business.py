"""Period-style business information and member watch lists."""

from cis_web_files import offer_download

from pathlib import Path

STARTING_CASH = 10000.00

COMPANIES = {
    "IBM": ("International Business Machines", "COMPUTERS", "Armonk, New York", "Mainframes, personal computers, and information systems."),
    "AAPL": ("Apple Computer", "COMPUTERS", "Cupertino, California", "Macintosh personal computers and related software."),
    "DEC": ("Digital Equipment Corporation", "COMPUTERS", "Maynard, Massachusetts", "VAX and PDP minicomputer systems."),
    "T": ("American Telephone & Telegraph", "COMMUNICATIONS", "New York, New York", "Long-distance communications and network services."),
    "MOT": ("Motorola", "ELECTRONICS", "Schaumburg, Illinois", "Semiconductors and communications equipment."),
    "INTC": ("Intel Corporation", "SEMICONDUCTORS", "Santa Clara, California", "Microprocessors and supporting integrated circuits."),
    "MSFT": ("Microsoft Corporation", "SOFTWARE", "Redmond, Washington", "Operating systems, languages, and applications software."),
    "S": ("Sears, Roebuck and Co.", "RETAIL", "Chicago, Illinois", "Retail merchandising and consumer services."),
    "GM": ("General Motors", "AUTOMOTIVE", "Detroit, Michigan", "Passenger cars, trucks, and automotive components."),
    "F": ("Ford Motor Company", "AUTOMOTIVE", "Dearborn, Michigan", "Passenger cars, trucks, and financial services."),
    "BA": ("Boeing Company", "AEROSPACE", "Seattle, Washington", "Commercial jet transports and aerospace systems."),
    "KO": ("Coca-Cola Company", "CONSUMER", "Atlanta, Georgia", "Soft-drink concentrates and branded beverages."),
}

SECTOR_NOTES = {
    "COMPUTERS": "Personal-computer competition remains vigorous while large-system demand is mixed.",
    "COMMUNICATIONS": "Long-distance pricing and digital-network investment remain closely watched.",
    "SEMICONDUCTORS": "Memory pricing is cyclical; newer microprocessors support faster personal systems.",
    "AUTOMOTIVE": "Year-end sales incentives and production schedules dominate the industry outlook.",
}

BUSINESS_WIRE = {
    "COMPUTERS": "PERSONAL COMPUTER SALES STAY FIRM -- Dealers report continued demand for 286 and 386 systems.",
    "SEMICONDUCTORS": "MEMORY-CHIP PRICES DRAW ATTENTION -- Manufacturers monitor component supplies and costs.",
    "COMMUNICATIONS": "LONG-DISTANCE COMPETITION LOWERS SOME RATES -- New off-peak plans reach customers.",
    "RETAIL": "RETAILERS ENTER FINAL HOLIDAY WEEKS -- Merchants extend hours and promotions.",
    "AUTOMOTIVE": "AUTOMAKERS REVIEW U.S. PRODUCTION -- Competition and new investment reshape the market.",
    "AEROSPACE": "AIRLINES REVIEW WINTER CAPACITY -- Transport companies adjust holiday schedules.",
}

def directory(query=""):
    words = query.upper().split()
    return [(symbol, *data) for symbol, data in COMPANIES.items() if all(word in f"{symbol} {' '.join(data)}".upper() for word in words)]

def report(symbol, quotes):
    symbol = symbol.upper()
    company = COMPANIES.get(symbol)
    if not company:
        return ["Company symbol not found in the demonstration directory."]
    name, sector, office, description = company
    quote = quotes.get(symbol)
    lines = [f"{symbol}  {name}", f"INDUSTRY  {sector}", f"OFFICE    {office}", "", description, "", SECTOR_NOTES.get(sector, "Business conditions vary by company and market.")]
    lines.append(f"DELAYED QUOTE  {quote['last']:.2f}  CHANGE {quote['change']:+.2f}" if quote else "DELAYED QUOTE  NOT IN DEMONSTRATION FILE")
    if sector in BUSINESS_WIRE:
        lines.extend(["", "RELATED PERIOD BUSINESS WIRE", BUSINESS_WIRE[sector]])
    lines.extend(["", "Historical-simulation summary; not investment advice."])
    return lines

def watchlist(app, symbol=None, remove=False):
    state = app.cis_dynamic.load_state(app)
    watches = state.setdefault("finance_watchlists", {}).setdefault(app.current_user_id or "GUEST", [])
    if symbol:
        symbol = symbol.upper()
        if symbol not in COMPANIES:
            return "Symbol not found."
        if remove:
            watches[:] = [item for item in watches if item != symbol]
        elif symbol not in watches:
            watches.append(symbol)
        app.cis_dynamic.save_state(app, state)
        return f"{symbol} {'removed from' if remove else 'added to'} watch list."
    return list(watches)

def commission(gross):
    """Fictional period-style brokerage commission."""
    return round(max(15.0, gross * 0.01), 2)

def _portfolio(app, state=None):
    state = app.cis_dynamic.load_state(app) if state is None else state
    return state.setdefault("stock_portfolios", {}).setdefault(app.current_user_id or "GUEST", {
        "cash": STARTING_CASH, "realized": 0.0, "holdings": {}, "transactions": [],
    })

def trade(app, action, symbol, shares, quotes):
    action, symbol = action.upper(), symbol.upper()
    if action not in ("BUY", "SELL") or symbol not in COMPANIES or symbol not in quotes:
        return "Trade not accepted: symbol or action is not available."
    if not isinstance(shares, int) or shares < 1 or shares > 9999:
        return "Trade not accepted: enter 1 to 9999 whole shares."
    price = round(float(quotes[symbol]["last"]), 2)
    gross = round(price * shares, 2)
    fee = commission(gross)
    outcome = {}
    def apply_trade(state):
        portfolio = _portfolio(app, state); holdings = portfolio["holdings"]
        position = holdings.get(symbol, {"shares": 0, "average_cost": 0.0})
        if action == "BUY":
            total = round(gross + fee, 2)
            if total > portfolio["cash"]:
                outcome["error"] = f"Trade not accepted: ${total:.2f} required; ${portfolio['cash']:.2f} available."
                return
            old_basis = position["shares"] * position["average_cost"]
            new_shares = position["shares"] + shares
            holdings[symbol] = {"shares": new_shares, "average_cost": round((old_basis + total) / new_shares, 4)}
            portfolio["cash"] = round(portfolio["cash"] - total, 2); realized = 0.0
        else:
            if shares > position["shares"]:
                outcome["error"] = f"Trade not accepted: only {position['shares']} {symbol} shares held."
                return
            proceeds = round(gross - fee, 2); realized = round(proceeds - position["average_cost"] * shares, 2)
            portfolio["cash"] = round(portfolio["cash"] + proceeds, 2)
            portfolio["realized"] = round(portfolio["realized"] + realized, 2)
            position["shares"] -= shares
            if position["shares"]: holdings[symbol] = position
            else: holdings.pop(symbol, None)
        portfolio["transactions"].append({"date": app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes"), "action": action, "symbol": symbol, "shares": shares, "price": price, "commission": fee, "gross": gross, "realized": realized})
        portfolio["transactions"] = portfolio["transactions"][-200:]
    if hasattr(app, "update_json_atomic"):
        app.update_json_atomic("dynamic_state.json", {}, apply_trade)
    else:
        state = app.cis_dynamic.load_state(app); apply_trade(state); app.cis_dynamic.save_state(app, state)
    if outcome.get("error"):
        return outcome["error"]
    app.cis_dynamic.record_activity(app, app.current_user_id, "FINANCE", f"Fictional {action} {shares} {symbol} at ${price:.2f}.")
    return f"{action} RECORDED: {shares} {symbol} @ ${price:.2f}; COMMISSION ${fee:.2f}."


def place_limit(app, action, symbol, shares, limit_price):
    action, symbol = action.upper(), symbol.upper()
    if action not in ("BUY", "SELL") or symbol not in COMPANIES or shares < 1 or limit_price <= 0:
        return "Limit order not accepted."
    state = app.cis_dynamic.load_state(app); orders = state.setdefault("limit_orders", {}).setdefault(app.current_user_id or "GUEST", [])
    number = max((item.get("id", 0) for item in orders), default=0) + 1
    orders.append({"id": number, "action": action, "symbol": symbol, "shares": shares, "limit": round(limit_price, 2), "status": "OPEN", "date": app.cis_dynamic.simulation_datetime().isoformat(timespec="minutes")})
    app.cis_dynamic.save_state(app, state)
    return f"LIMIT ORDER #{number} OPEN: {action} {shares} {symbol} AT ${limit_price:.2f}."


def process_limits(app, quotes):
    state = app.cis_dynamic.load_state(app); orders = state.setdefault("limit_orders", {}).setdefault(app.current_user_id or "GUEST", [])
    filled = []
    for order in orders:
        quote = quotes.get(order["symbol"]); price = quote and quote["last"]
        eligible = price is not None and ((order["action"] == "BUY" and price <= order["limit"]) or (order["action"] == "SELL" and price >= order["limit"]))
        if order["status"] == "OPEN" and eligible:
            result = trade(app, order["action"], order["symbol"], order["shares"], quotes)
            if "RECORDED" in result:
                order["status"] = "FILLED"; order["fill_price"] = price; filled.append(order)
    latest = app.cis_dynamic.load_state(app)
    latest.setdefault("limit_orders", {})[app.current_user_id or "GUEST"] = orders
    app.cis_dynamic.save_state(app, latest)
    for order in filled:
        app.cis_dynamic.schedule_event(app, "mail", {"to": app.current_user_id, "from": "MICROQUOTE", "subject": f'LIMIT ORDER #{order["id"]} FILLED', "body": f'{order["action"]} {order["shares"]} {order["symbol"]} filled at fictional price ${order["fill_price"]:.2f}.'})
    return filled


def limit_lines(app):
    orders = app.cis_dynamic.load_state(app).get("limit_orders", {}).get(app.current_user_id or "GUEST", [])
    return [f'#{item["id"]} {item["action"]:<4} {item["shares"]:>4} {item["symbol"]:<5} LIMIT ${item["limit"]:.2f} [{item["status"]}]' for item in orders] or ["No limit orders."]


def market_arc_lines(app):
    day = app.cis_dynamic.simulation_day().day
    stages = [(17, "SEMICONDUCTOR SHORTAGE RUMOR REACHES BUSINESS WIRE"), (18, "ANALYSTS DISAGREE ON MEMORY SUPPLY"), (19, "LIMIT-ORDER VOLUME INCREASES"), (20, "INVESTMENT CLUB HOLDS EVENING CONFERENCE"), (21, "MANUFACTURER CLARIFIES AUTHORIZED SUPPLY"), (22, "SEMICONDUCTOR QUOTATIONS PARTIALLY REVERSE"), (23, "FORECAST SCORECARD AND CLUB RESULTS POSTED")]
    forecasts = ["Robert/Research: semiconductor strength may fade after clarification.", "MarketMaven: computer demand should support selected manufacturers."]
    return ["SEVEN-DAY MARKET WATCH", *[f'DEC {date:02d} [{"POSTED" if day >= date else "PENDING"}] {title}' for date, title in stages], "", "ANALYST FORECASTS", *forecasts, "", "CHIP-88 decisions may alter the interpretation of shortage reports."]


def member_quotes(app, base_quotes):
    """Return normal delayed quotes with a small, fictional CHIP-88 sentiment effect."""
    quotes = app.cis_dynamic.market_quotes(base_quotes)
    state = app.cis_dynamic.load_state(app)
    decision = state.get("story_cases", {}).get(app.current_user_id or "GUEST", {}).get("decision")
    effect = {"REPORT": -0.35, "PUBLISH": 0.80, "HOLD": 0.20}.get(decision, 0.0)
    if effect and app.cis_dynamic.simulation_day().day <= 23:
        for symbol, weight in (("INTC", 1.0), ("MOT", 0.45)):
            if symbol in quotes:
                quotes[symbol] = dict(quotes[symbol])
                quotes[symbol]["last"] = round(quotes[symbol]["last"] + effect * weight, 2)
                quotes[symbol]["change"] = round(quotes[symbol]["change"] + effect * weight, 2)
    return quotes


def submit_forecast(app, symbol, direction):
    symbol, direction = symbol.upper(), direction.upper()
    if symbol not in ("INTC", "MOT") or direction not in ("UP", "DOWN"):
        return "Forecast not accepted. Enter INTC or MOT and UP or DOWN."
    state = app.cis_dynamic.load_state(app); user = app.current_user_id or "GUEST"
    forecasts = state.setdefault("investment_club", {})
    if user in forecasts:
        return "Your Investment Club forecast is already on file."
    forecasts[user] = {"symbol": symbol, "direction": direction, "filed": app.cis_dynamic.simulation_day().isoformat(), "score": None}
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.record_activity(app, app.current_user_id, "FINANCE", f"Investment Club forecast: {symbol} {direction}.")
    return f"FORECAST FILED: {symbol} {direction}. Results post December 23."


def settle_forecast(app):
    state = app.cis_dynamic.load_state(app); user = app.current_user_id or "GUEST"
    entry = state.get("investment_club", {}).get(user)
    if not entry or entry.get("score") is not None or app.cis_dynamic.simulation_day().day < 23:
        return False
    # The closing fictional tape resolves INTC down and MOT up after the clarification.
    result = {"INTC": "DOWN", "MOT": "UP"}[entry["symbol"]]
    entry["result"] = result; entry["score"] = 100 if entry["direction"] == result else 25
    app.cis_dynamic.save_state(app, state)
    app.cis_dynamic.schedule_event(app, "mail", {"to": user, "from": "CIS INVESTMENT CLUB", "subject": "MARKET FORECAST SCORECARD", "body": f'{entry["symbol"]} closed {result}; your {entry["direction"]} forecast earned {entry["score"]} points.'})
    return True


def investment_club_lines(app, quotes):
    settle_forecast(app)
    entry = app.cis_dynamic.load_state(app).get("investment_club", {}).get(app.current_user_id or "GUEST")
    lines = [*market_arc_lines(app), "", "MEMBER FORECAST DESK"]
    if not entry:
        lines.extend(["No forecast filed.", "File one forecast: INTC or MOT, then UP or DOWN."])
    else:
        lines.append(f'{entry["symbol"]} {entry["direction"]}  FILED {entry["filed"]}')
        if entry.get("score") is None:
            lines.append("RESULT PENDING UNTIL DECEMBER 23")
        else:
            lines.extend([f'ACTUAL {entry["result"]}', f'SCORE  {entry["score"]} POINTS', f'CLUB RANK  {"LEADING TABLE" if entry["score"] == 100 else "PARTICIPANT"}'])
    lines.extend(["", *challenge_lines(app, quotes)])
    return lines


def apply_corporate_actions(app):
    state = app.cis_dynamic.load_state(app); user = app.current_user_id or "GUEST"; portfolio = _portfolio(app, state)
    applied = state.setdefault("corporate_actions", {}).setdefault(user, [])
    notices = []
    day = app.cis_dynamic.simulation_day().day
    if day >= 21 and "INTC-DIV-88" not in applied:
        shares = portfolio["holdings"].get("INTC", {}).get("shares", 0); amount = round(shares * .12, 2)
        portfolio["cash"] = round(portfolio["cash"] + amount, 2); applied.append("INTC-DIV-88")
        if shares: notices.append(("INTC DIVIDEND CREDIT", f"{shares} shares credited ${amount:.2f}."))
    if day >= 23 and "AAPL-SPLIT-88" not in applied:
        position = portfolio["holdings"].get("AAPL"); applied.append("AAPL-SPLIT-88")
        if position:
            position["shares"] *= 2; position["average_cost"] = round(position["average_cost"] / 2, 4)
            notices.append(("AAPL TWO-FOR-ONE SPLIT", f'Position adjusted to {position["shares"]} shares.'))
    app.cis_dynamic.save_state(app, state)
    for subject, body in notices:
        app.cis_dynamic.schedule_event(app, "mail", {"to": user, "from": "MICROQUOTE", "subject": subject, "body": body + " Fictional simulation entry only."})
    return notices

def portfolio_lines(app, quotes):
    portfolio = _portfolio(app)
    lines = ["FICTIONAL MARKET SIMULATION -- NO REAL SECURITIES", "", "SYMBOL SHARES AVG COST   LAST    VALUE       GAIN/LOSS"]
    market_value = unrealized = 0.0
    for symbol, position in sorted(portfolio["holdings"].items()):
        quote = quotes.get(symbol)
        if not quote:
            lines.append(f"{symbol:<6} {position['shares']:>6} QUOTE UNAVAILABLE")
            continue
        value = round(position["shares"] * quote["last"], 2)
        gain = round(value - position["shares"] * position["average_cost"], 2)
        market_value += value
        unrealized += gain
        lines.append(f"{symbol:<6} {position['shares']:>6} {position['average_cost']:>8.2f} {quote['last']:>7.2f} {value:>10.2f} {gain:>+11.2f}")
    if not portfolio["holdings"]:
        lines.append("No positions held.")
    total = round(portfolio["cash"] + market_value, 2)
    lines.extend(["", f"CASH                 ${portfolio['cash']:>10.2f}", f"MARKET VALUE         ${market_value:>10.2f}", f"TOTAL ACCOUNT VALUE  ${total:>10.2f}", f"UNREALIZED P/L       ${unrealized:>+10.2f}", f"REALIZED P/L         ${portfolio['realized']:>+10.2f}", f"TOTAL RETURN         ${total - STARTING_CASH:>+10.2f}"])
    return lines

def ledger_lines(app):
    transactions = _portfolio(app)["transactions"]
    return [f'{item["date"]} {item["action"]:<4} {item["shares"]:>4} {item["symbol"]:<5} @ ${item["price"]:.2f}  COMM ${item["commission"]:.2f}' + (f'  REALIZED {item["realized"]:+.2f}' if item["action"] == "SELL" else "") for item in transactions[-25:]] or ["No simulated trades recorded."]

def economic_indicators():
    return [
        "U.S. ECONOMIC INDICATORS -- DECEMBER 1988 SIMULATION", "",
        "PRIME RATE                 10.50%", "FEDERAL FUNDS              8.75%",
        "3-MONTH TREASURY BILL      8.20%", "10-YEAR TREASURY NOTE      9.10%",
        "30-YEAR TREASURY BOND      9.18%", "CONSUMER PRICE TREND       +4.4% Y/Y",
        "UNEMPLOYMENT RATE          5.3%", "INDUSTRIAL PRODUCTION      FIRM",
        "", "Illustrative historical-simulation figures; not current data or advice.",
    ]

def export_packet(app, quotes):
    destination = app.BASE_DIR / "downloads" / f"FINANCE_{(app.current_user_id or 'GUEST').replace(',', '_')}.TXT"
    destination.parent.mkdir(exist_ok=True)
    watches = watchlist(app)
    lines = ["COMPUSERVE BUSINESS & FINANCIAL RESEARCH PACKET", "DECEMBER 1988 HISTORICAL SIMULATION", "", *portfolio_lines(app, quotes), "", "WATCH LIST"]
    lines.extend(f"{symbol}  {COMPANIES[symbol][0]}  " + (f"{quotes[symbol]['last']:.2f} {quotes[symbol]['change']:+.2f}" if symbol in quotes else "QUOTE UNAVAILABLE") for symbol in watches)
    lines.extend(["", *economic_indicators(), "", "All transactions, prices, and balances are fictional."])
    destination.write_text("\n".join(lines) + "\n", encoding="ascii", errors="replace")
    app.cis_dynamic.record_activity(app, app.current_user_id, "FINANCE", f"Prepared research packet {destination.name}.")
    offer_download(destination)
    return destination

def challenge_lines(app, quotes):
    portfolio = _portfolio(app)
    state = app.cis_dynamic.load_state(app)
    challenge = state.setdefault("market_challenges", {}).setdefault(app.current_user_id or "GUEST", {"name": "PRESERVE CAPITAL", "started": app.cis_dynamic.simulation_day().isoformat(), "target": STARTING_CASH})
    values = portfolio_lines(app, quotes)
    total_line = next(line for line in values if line.startswith("TOTAL ACCOUNT VALUE"))
    total = float(total_line.split("$")[-1])
    return ["DECEMBER MARKET CHALLENGE", f'OBJECTIVE  {challenge["name"]}', f'STARTED    {challenge["started"]}', f"TARGET     ${challenge['target']:.2f}", f"CURRENT    ${total:.2f}", f"STATUS     {'ABOVE TARGET' if total >= challenge['target'] else 'BELOW TARGET'}", "", "Optional fictional exercise; no prize, money, or securities are involved."]

