"""Owned computer setups and bounded, simulated transfer resources."""
import math
from cis_session import read_input as input

# Download capacity is a simplified data budget: one disk per drive or the
# supplied hard disk, not an emulation of each operating system's filesystem.
SPECS = {
    2001: ('DOS', 640, 720, '2 x 360K floppy', 'Monochrome', 80, 0),
    2002: ('DOS', 640, 20480, '20MB hard disk + 360K floppy', 'Monochrome', 80, 0),
    2003: ('DOS', 1024, 40960, '40MB hard disk + 1.2MB floppy', 'EGA color', 80, 0),
    2004: ('MAC', 1024, 800, '800K floppy', 'Built-in monochrome', 80, 0),
    2005: ('MAC', 1024, 20480, '20MB SCSI + 800K floppy', 'Built-in monochrome', 80, 0),
    2006: ('C64', 64, 170, '1541-II floppy', 'TV connection', 40, 0),
    2007: ('AMIGA', 512, 880, '880K floppy', '1084 color', 80, 0),
    2008: ('AMIGA', 1024, 880, '880K floppy', '1084 color', 80, 0),
    2010: ('APPLE2', 128, 280, '2 x 140K floppy', 'Monochrome 80-column', 80, 0),
    2011: ('IIGS', 1280, 800, '800K floppy', 'Apple RGB', 80, 0),
    2012: ('ATARI', 1024, 720, '720K floppy', 'SM124 monochrome', 80, 0),
    2013: ('DOS', 640, 720, '720K floppy', 'Tandy RGB color', 80, 0),
    2014: ('MODEL100', 32, 24, '24K simulated free RAM file budget', 'LCD 40 x 8', 40, 300),
}
EFFECTS = {
    1101: {'modem': 1200}, 1102: {'modem': 2400}, 1103: {'modem': 1200},
    1104: {'modem': 300}, 2114: {'modem': 1200},
    1803: {'disk_kb': 20480}, 2106: {'disk_kb': 20480},
    2107: {'disk_kb': 800}, 2111: {'disk_kb': 170}, 2116: {'disk_kb': 880},
    2115: {'memory_kb': 512}, 2122: {'disk_kb': 800},
    2123: {'disk_kb': 140}, 2125: {'disk_kb': 720},
    2104: {'display': 'EGA color'}, 2105: {'display': 'VGA color'},
    2112: {'display': 'Commodore color'}, 2127: {'display': 'Atari RGB color'},
}
MODEM_CABLE = {'IBM PC/XT': 1201, 'IBM PC AT': 1201, 'MACINTOSH PLUS': 1203,
    'MACINTOSH SE': 1203, 'AMIGA 500': 2118, 'APPLE IIE': 2120,
    'APPLE IIGS': 2121, 'ATARI 1040ST': 2124, 'TANDY 1000 HX': 2126}
UNAVAILABLE = {'RETURN REQUESTED', 'RETURNED', 'SOLD'}


def raw(app):
    return app.load_json('dynamic_state.json', default={})


def member_data(data, uid):
    return data.setdefault('computer_setups', {}).setdefault(uid, {'active': None, 'machines': {}})


def available(asset):
    return asset and asset.get('status') not in UNAVAILABLE


def snapshot(app, data=None):
    data = raw(app) if data is None else data
    member = data.get('computer_setups', {}).get(app.current_user_id, {})
    active = member.get('active')
    inventory = {a['id']: a for a in data.get('owned_equipment', {}).get(app.current_user_id, [])}
    machine = inventory.get(active)
    if not active:
        return None
    if not available(machine) or machine['sku'] not in SPECS:
        return {'error': 'Active computer is unavailable. Choose another with GO SETUP or use OFF.'}
    product = app.cis_store.find_product(machine['sku'])
    platform, memory, disk, drives, display, columns, modem = SPECS[machine['sku']]
    config = member.get('machines', {}).get(active, {})
    attached = [inventory[i] for i in config.get('attached', []) if available(inventory.get(i))]
    for item in attached:
        effect = EFFECTS.get(item['sku'], {})
        memory += effect.get('memory_kb', 0)
        disk += effect.get('disk_kb', 0)
        modem = max(modem, effect.get('modem', 0))
        display = effect.get('display', display)
    files = config.get('files', {})
    return dict(id=active, name=machine['name'], sku=machine['sku'], system=product['system'],
        platform=platform, memory_kb=memory, capacity=disk * 1024,
        used=sum(f['bytes'] for f in files.values()), drives=drives, display=display,
        columns=columns, modem=modem, attached=attached, files=files,
        transfer_seconds=config.get('transfer_seconds', 0))


def activate(app, asset_id):
    uid = app.current_user_id
    if not uid:
        return 'Sign in first.'
    result = []
    def update(data):
        member = member_data(data, uid)
        if asset_id.upper() == 'OFF':
            member['active'] = None
            result.append('Hardware limits disabled; legacy terminal settings restored.')
            return
        asset = next((a for a in data.get('owned_equipment', {}).get(uid, []) if a['id'] == asset_id.upper()), None)
        if not available(asset) or asset['sku'] not in SPECS:
            result.append('Choose a delivered computer from your own equipment.')
            return
        member['active'] = asset['id']
        member['machines'].setdefault(asset['id'], {'attached': [], 'files': {}})
        result.append(f"Active computer: {asset['name']}.")
    app.update_json_atomic('dynamic_state.json', {}, update)
    apply_settings(app)
    return result[0]


def attach(app, asset_id, detach=False):
    result = []
    def update(data):
        view = snapshot(app, data)
        if not view or view.get('error'):
            result.append('Select an available computer first.')
            return
        member = member_data(data, app.current_user_id)
        config = member['machines'][view['id']]
        attached = config.setdefault('attached', [])
        asset = next((a for a in data.get('owned_equipment', {}).get(app.current_user_id, []) if a['id'] == asset_id.upper()), None)
        if detach:
            if asset_id.upper() in attached:
                removing = next((a for a in view['attached'] if a['id'] == asset_id.upper()), None)
                if removing and removing['sku'] == 1804 and any(a['sku'] == 2105 for a in view['attached']):
                    result.append('Detach the VGA monitor before its adapter.')
                    return
                attached.remove(asset_id.upper())
                revised = snapshot(app, data)
                if revised['used'] > revised['capacity']:
                    attached.append(asset_id.upper())
                    result.append('Remove downloaded files before detaching this storage device.')
                    return
            result.append('Accessory detached.')
            return
        if not available(asset) or asset['sku'] in SPECS:
            result.append('Choose an available owned accessory, not a computer.')
            return
        sku = asset['sku']
        if sku == 1801 and view['memory_kb'] >= 640:
            result.append('This computer already has its full 640K conventional memory.')
            return
        compatible = app.cis_store.COMPATIBILITY.get(view['system'], set())
        if sku not in compatible:
            result.append('This accessory is not compatible with the active computer.')
            return
        if any(asset['id'] in c.get('attached', []) for c in member['machines'].values()):
            result.append('Accessory is already attached. Detach it before moving it.')
            return
        skus = {a['sku'] for a in view['attached']}
        if sku in skus or (sku == 2115 and view['sku'] == 2008):
            result.append('This accessory is already fitted or included in the bundle.')
            return
        if sku == 2105 and 1804 not in skus:
            result.append('Attach VGA adapter 1804 before the VGA monitor.')
            return
        if sku == 2104 and view['sku'] != 2003:
            result.append('This display requires an EGA adapter.')
            return
        if EFFECTS.get(sku, {}).get('modem') and view['modem']:
            result.append('Detach the current modem before fitting another.')
            return
        attached.append(asset['id'])
        result.append(f"Attached {asset['name']}.")
    app.update_json_atomic('dynamic_state.json', {}, update)
    apply_settings(app)
    return result[0]


def apply_settings(app):
    view = snapshot(app)
    if view and not view.get('error'):
        app.SCREEN_WIDTH = view['columns']
        if view['modem']:
            app.connection_baud = view['modem']
    elif not view:
        app.SCREEN_WIDTH = int(app.current_profile.get('columns', 80))
        app.connection_baud = int(app.current_profile.get('baud', 1200))


def platforms(app, file):
    if file.get('platforms'):
        return file['platforms']
    if file['name'].upper().endswith(('.TXT', '.DOC', '.ASC', '.ANS')) or file.get('content_id'):
        return ['ANY']  # Community downloads contain reconstructed text, not executables.
    for section, files in app.library_files.items():
        if any(f.get('number') == file.get('number') for f in files):
            if section.startswith(('ibmhw', 'dos')):
                return ['DOS']
            for prefix, platform in [('appleii', 'APPLE2'), ('commodore', 'C64'), ('atarist', 'ATARI'), ('mac', 'MAC')]:
                if section.startswith(prefix):
                    return [platform]
    return ['UNKNOWN']


def transfer_plan(app, file, size, protocol='B', data=None):
    view = snapshot(app, data)
    if not view:
        return dict(seconds=math.ceil(size * 10 / max(300, app.connection_baud)), baud=app.connection_baud)
    if view.get('error'):
        return view
    if not view['modem']:
        return {'error': 'Attach an owned modem in GO SETUP before downloading.'}
    skus = {a['sku'] for a in view['attached']}
    if skus.intersection({1101, 1102, 1104}):
        cable = MODEM_CABLE.get(view['system'])
        if cable and cable not in skus:
            return {'error': f'Attach modem cable/interface SKU {cable} in GO SETUP.'}
    supported = platforms(app, file)
    if 'ANY' not in supported and view['platform'] not in supported and not (view['platform'] == 'IIGS' and 'APPLE2' in supported):
        return {'error': f"Software platform {', '.join(supported)} does not match {view['platform']}. Text files work across systems."}
    if file.get('min_memory_kb', 0) > view['memory_kb']:
        return {'error': 'Not enough memory for this software.'}
    old_size = view['files'].get(file['name'], {}).get('bytes', 0)
    if view['used'] - old_size + size > view['capacity']:
        return {'error': 'Disk full. Use GO SETUP to remove a downloaded file or attach storage.'}
    baud = min(view['modem'], max(300, app.connection_baud))
    seconds = math.ceil(size * 10 / (baud * (0.85 if protocol == 'B' else 0.7)))
    return dict(seconds=seconds, baud=baud, machine=view['id'], bytes=size)


def record_download(app, file, size, protocol, writer=None):
    result = []
    def update(data):
        plan = transfer_plan(app, file, size, protocol, data)
        if not plan.get('error') and writer:
            writer()
        if not plan.get('error') and plan.get('machine'):
            config = member_data(data, app.current_user_id)['machines'][plan['machine']]
            config.setdefault('files', {})[file['name']] = {'bytes': size, 'platforms': platforms(app, file)}
            config['transfer_seconds'] = config.get('transfer_seconds', 0) + plan['seconds']
        result.append(plan)
    app.update_json_atomic('dynamic_state.json', {}, update)
    return result[0]


def remove_file(app, name):
    def update(data):
        member = member_data(data, app.current_user_id)
        if member.get('active'):
            member['machines'][member['active']].setdefault('files', {}).pop(name, None)
    app.update_json_atomic('dynamic_state.json', {}, update)


def lines(app):
    view = snapshot(app)
    if not view:
        return ['No active computer. Select a delivered computer below.', 'Legacy downloads remain unrestricted until you select a computer.']
    if view.get('error'):
        return [view['error']]
    return [f"ACTIVE {view['id']} {view['name']}",
        f"{view['memory_kb']}K RAM | {view['display']} | {view['columns']} columns",
        f"Drives: {view['drives']} (attached storage adds to budget)",
        f"Modem: {view['modem']} baud" if view['modem'] else 'Modem: none fitted',
        f"Download storage: {view['used']} / {view['capacity']} bytes",
        f"Simulated transfer time: {view['transfer_seconds']} seconds",
        *[f"  {a['id']} {a['name']}" for a in view['attached']],
        *[f"FILE {name} ({entry['bytes']} bytes)" for name, entry in view['files'].items()]]


def service(app):
    if not app.current_user_id:
        return
    while True:
        app.ansi_scroll('MY COMPUTER SETUP - reconstructed hardware simulation', 0.01)
        for line in lines(app):
            app.ansi_scroll(line, 0.005)
        for asset in raw(app).get('owned_equipment', {}).get(app.current_user_id, []):
            app.ansi_scroll(f"{asset['id']} {asset['name']} [{asset['status']}]", 0.005)
        command = input('USE id, ATTACH id, DETACH id, DELETE filename, OFF, M ! ').strip()
        verb, _, argument = command.partition(' ')
        verb = verb.upper()
        if verb in ('M', ''):
            return
        if verb in ('USE', 'OFF'):
            result = activate(app, argument if verb == 'USE' else 'OFF')
        elif verb in ('ATTACH', 'DETACH'):
            result = attach(app, argument, detach=verb == 'DETACH')
        elif verb == 'DELETE':
            remove_file(app, argument)
            result = 'Removed from the simulated disk; exported host copies are retained.'
        else:
            result = 'Unknown setup command.'
        app.ansi_scroll(result, 0.01)
