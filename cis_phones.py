"""Offline, pre-login CompuServe access-number directory.

Historical rows: CompuServe Information Service Access Numbers, March 1,
1983, page 1 (300 baud CNS lines). Preserve the printed period area codes.
https://www.pagetable.com/docs/cbm1600modem/compuserve2.pdf
Fictional rows fill geographic gaps; they are not claims of historical service.
"""

import re
import unicodedata


SOURCE_URL = "https://www.pagetable.com/docs/cbm1600modem/compuserve2.pdf"
PAGE_SIZE = 6

# City | state/province | country | documented number(s)
_HISTORICAL = """
Birmingham|AL|USA|205-879-2280
Huntsville|AL|USA|205-536-4405
Little Rock|AR|USA|501-666-8464
Phoenix|AZ|USA|602-994-8495
Tucson|AZ|USA|602-748-2004
Vancouver|BC|Canada|604-687-6043
Anaheim|CA|USA|714-991-8060
Fresno|CA|USA|209-252-1892
Irvine|CA|USA|714-851-9612
Long Beach|CA|USA|213-591-8392
Los Angeles|CA|USA|213-739-8906
Mountain View|CA|USA|415-961-7242
Newport Beach|CA|USA|714-851-9612
Palo Alto|CA|USA|415-591-5591
Pleasanton|CA|USA|415-846-0828
Riverside|CA|USA|714-359-7801
Sacramento|CA|USA|916-483-3235
San Bernardino|CA|USA|714-884-3263
San Diego|CA|USA|619-283-6021
San Francisco|CA|USA|415-956-4191
San Jose|CA|USA|408-249-5361
San Mateo|CA|USA|415-591-5591
Thousand Oaks|CA|USA|805-497-3177
Colorado Springs|CO|USA|303-593-9200
Denver|CO|USA|303-629-5563
Grand Junction|CO|USA|303-241-1885
Bridgeport|CT|USA|203-366-5555
Hartford|CT|USA|203-236-2581
Stamford|CT|USA|203-358-0015
Waterbury|CT|USA|203-573-0771
Washington|DC|USA|202-452-8930,202-822-8985
Wilmington|DE|USA|302-652-8732
Fort Lauderdale|FL|USA|305-772-3240
Jacksonville|FL|USA|904-246-9961
Miami|FL|USA|305-667-3564
Orlando|FL|USA|305-273-8780
Tallahassee|FL|USA|904-222-4144
Tampa|FL|USA|813-876-1060
Atlanta|GA|USA|404-237-3003,404-237-8113
Augusta|GA|USA|404-733-0346
Des Moines|IA|USA|515-270-1581
Boise|ID|USA|208-384-5660,208-336-2052
Chicago|IL|USA|312-443-1250
Springfield|IL|USA|217-522-5101
Fort Wayne|IN|USA|219-447-0536
Indianapolis|IN|USA|317-638-2517
Wichita|KS|USA|316-689-8765
Lexington|KY|USA|606-255-8821
Louisville|KY|USA|502-581-9526
Baton Rouge|LA|USA|504-273-0184
New Orleans|LA|USA|504-948-9542
Shreveport|LA|USA|318-424-4460
Boston|MA|USA|617-267-2569
Springfield|MA|USA|413-734-7362
Worcester|MA|USA|617-793-9839
Baltimore|MD|USA|301-254-7113
Ann Arbor|MI|USA|313-761-1202
Detroit|MI|USA|313-964-4745
Kalamazoo|MI|USA|616-344-2298
Lansing|MI|USA|517-321-2388
Minneapolis|MN|USA|612-375-9163
Kansas City|MO|USA|816-474-3770
St. Louis|MO|USA|314-432-7585
Jackson|MS|USA|601-982-0463
Charlotte|NC|USA|704-333-6654
Greensboro|NC|USA|919-373-1635
Raleigh|NC|USA|919-872-8130
Omaha|NE|USA|402-895-7131
Merrimack|NH|USA|603-880-1450
Newark|NJ|USA|201-624-4885
Paterson|NJ|USA|201-684-3434
Albuquerque|NM|USA|505-345-4551
Las Vegas|NV|USA|702-877-1334
Reno|NV|USA|702-323-2072
Buffalo|NY|USA|716-837-9650
New York|NY|USA|212-758-4114
Rochester|NY|USA|716-458-3460
White Plains|NY|USA|914-428-9270
Akron|OH|USA|216-867-1237
Canton|OH|USA|216-455-2516
Cincinnati|OH|USA|513-579-0908,513-721-2691
Cleveland|OH|USA|216-566-0657
Columbus|OH|USA|614-457-2105
Dayton|OH|USA|513-461-1064
Toledo|OH|USA|419-255-8116
Oklahoma City|OK|USA|405-946-4799
Tulsa|OK|USA|918-743-5808
Toronto|ON|Canada|416-365-9621
Portland|OR|USA|503-232-1072
Allentown|PA|USA|215-776-6960
Harrisburg|PA|USA|717-657-9633
Philadelphia|PA|USA|215-563-0814
Pittsburgh|PA|USA|412-391-8818
Providence|RI|USA|401-781-8500
Charleston|SC|USA|803-762-1740
Columbia|SC|USA|803-798-7903
Rapid City|SD|USA|605-341-4580
Memphis|TN|USA|901-452-8530
Nashville|TN|USA|615-366-1947
Austin|TX|USA|512-444-7234
Dallas|TX|USA|214-761-9040,214-761-0599
El Paso|TX|USA|915-565-4661
Fort Worth|TX|USA|817-870-2461
Houston|TX|USA|713-225-2550
Lubbock|TX|USA|806-744-5091
San Antonio|TX|USA|512-435-3883
Salt Lake City|UT|USA|801-521-2890
Norfolk|VA|USA|804-461-6128
Richmond|VA|USA|804-358-8274
Seattle|WA|USA|206-634-1713
Spokane|WA|USA|509-326-0515
Milwaukee|WI|USA|414-475-6681,414-475-6935
Charleston|WV|USA|304-768-9700
Huntington|WV|USA|304-736-2331
Parkersburg|WV|USA|304-422-4005
Wheeling|WV|USA|304-232-3589
"""

# Supplemental cities use stable fictional 555-01xx numbers.
_SUPPLEMENTAL = """
Anchorage|AK|USA|907
Fairbanks|AK|USA|907
Montgomery|AL|USA|205
Mobile|AL|USA|205
Mesa|AZ|USA|602
Scottsdale|AZ|USA|602
Chandler|AZ|USA|602
Glendale|AZ|USA|602
Oakland|CA|USA|415
Bakersfield|CA|USA|805
Stockton|CA|USA|209
Chula Vista|CA|USA|619
Fremont|CA|USA|415
Santa Ana|CA|USA|714
Modesto|CA|USA|209
Oxnard|CA|USA|805
Aurora|CO|USA|303
New Haven|CT|USA|203
St. Petersburg|FL|USA|813
Hialeah|FL|USA|305
Savannah|GA|USA|912
Honolulu|HI|USA|808
Cedar Rapids|IA|USA|319
Peoria|IL|USA|309
Rockford|IL|USA|815
Overland Park|KS|USA|913
Portland|ME|USA|207
Grand Rapids|MI|USA|616
St. Paul|MN|USA|612
Springfield|MO|USA|417
Billings|MT|USA|406
Missoula|MT|USA|406
Durham|NC|USA|919
Winston-Salem|NC|USA|919
Fayetteville|NC|USA|919
Fargo|ND|USA|701
Bismarck|ND|USA|701
Lincoln|NE|USA|402
Manchester|NH|USA|603
Jersey City|NJ|USA|201
Henderson|NV|USA|702
Syracuse|NY|USA|315
Albany|NY|USA|518
Eugene|OR|USA|503
Salem|OR|USA|503
Sioux Falls|SD|USA|605
Knoxville|TN|USA|615
Chattanooga|TN|USA|615
Arlington|TX|USA|817
Corpus Christi|TX|USA|512
Plano|TX|USA|214
Laredo|TX|USA|512
Amarillo|TX|USA|806
Irving|TX|USA|214
Garland|TX|USA|214
Virginia Beach|VA|USA|804
Chesapeake|VA|USA|804
Arlington|VA|USA|703
Burlington|VT|USA|802
Tacoma|WA|USA|206
Madison|WI|USA|608
Green Bay|WI|USA|414
Cheyenne|WY|USA|307
San Juan|PR|USA|809
Calgary|AB|Canada|403
Edmonton|AB|Canada|403
Victoria|BC|Canada|604
Winnipeg|MB|Canada|204
Moncton|NB|Canada|506
Saint John|NB|Canada|506
St. John's|NL|Canada|709
Halifax|NS|Canada|902
Ottawa|ON|Canada|613
Hamilton|ON|Canada|416
London|ON|Canada|519
Kitchener|ON|Canada|519
Windsor|ON|Canada|519
Mississauga|ON|Canada|416
Charlottetown|PE|Canada|902
Montreal|QC|Canada|514
Quebec City|QC|Canada|418
Regina|SK|Canada|306
Saskatoon|SK|Canada|306
"""

ALIASES = {"nyc": "new york", "new york city": "new york", "la": "los angeles",
           "sf": "san francisco", "dc": "washington dc", "washington d c": "washington dc"}


def normalize(value):
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    value = re.sub(r"[^a-z0-9\s]", "", value)
    value = re.sub(r"\bsaint\b", "st", value)
    value = re.sub(r"\bft\b", "fort", value)
    return " ".join(value.split())


def _build_directory():
    rows = []
    for line in _HISTORICAL.strip().splitlines():
        city, region, country, numbers = line.split("|")
        rows.append(dict(city=city, region=region, country=country,
                         numbers=numbers.split(","), historical=True))
    existing = {(row["city"], row["region"], row["country"]) for row in rows}
    for index, line in enumerate(_SUPPLEMENTAL.strip().splitlines()):
        city, region, country, area = line.split("|")
        if (city, region, country) not in existing:
            rows.append(dict(city=city, region=region, country=country,
                             numbers=[f"{area}-555-{100 + index:04d}"], historical=False))
    return tuple(sorted(rows, key=lambda row: (row["city"], row["region"], row["country"])))


DIRECTORY = _build_directory()


def search(query):
    """Match all words across city, region and country; blank does not list all."""
    query = normalize(query)
    query = ALIASES.get(query, query)
    if not query:
        return []
    tokens = query.split()
    regions = {row['region'].lower() for row in DIRECTORY}
    region = tokens.pop() if len(tokens) > 1 and tokens[-1] in regions else None
    return [row for row in DIRECTORY if (region is None or row['region'].lower() == region) and all(
        token in normalize(f"{row['city']} {row['region']} {row['country']}") for token in tokens
    )]


def run(emit, read=None, return_to="Host Name"):
    """Browse without an account; return to the caller's hostname prompt."""
    if read is None:
        read = input
    emit("CompuServe - PHONES")
    emit("Local Access Number Directory")
    emit("Major U.S. cities and Canadian centers.")
    emit("Historical: CNS, 300 baud, 03/01/1983.")
    emit("Fictional: supplemental simulator entries.")
    emit("Archive/simulation only; not current dial-in service.")
    while True:
        emit("City or city, state/province; ALL lists cities.")
        emit(f"SOURCES shows references. M returns to {return_to}.")
        query = read("City ! ").strip()
        if not query or query.upper() in {"M", "Q", "CIS"}:
            return
        if query.upper() == "SOURCES":
            emit("CompuServe Information Service Access Numbers")
            emit("March 1, 1983, page 1; original CNS 300-baud list.")
            emit(SOURCE_URL)
            emit("Period area codes retained. Fictional rows fill gaps.")
            continue
        matches = list(DIRECTORY) if query.upper() == "ALL" else search(query)
        if not matches:
            emit("No cities found. Try part of a city name or ALL.")
            continue
        emit(f"{len(matches)} cities found.")
        for offset in range(0, len(matches), PAGE_SIZE):
            for row in matches[offset:offset + PAGE_SIZE]:
                emit(f"{row['city']}, {row['region']} - {row['country']}")
                label = "HISTORICAL" if row["historical"] else "FICTIONAL"
                for number in row["numbers"]:
                    emit(f"  {number} [{label}]")
            if offset + PAGE_SIZE < len(matches):
                while True:
                    choice = read("Enter: more, S: search, M: host ! ").strip().upper()
                    if choice in {"M", "Q", "CIS"}:
                        return
                    if choice in {"", "S"}:
                        break
                    emit("Press Enter, S, or M.")
                if choice == "S":
                    break
