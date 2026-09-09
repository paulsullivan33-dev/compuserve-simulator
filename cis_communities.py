"""Original computer-community content for the December 1988 simulation."""

import copy
import json
from pathlib import Path

from cis_storage import install_content_pack


PACK = json.loads(Path(__file__).with_name('computer_communities.json').read_text(encoding='utf-8'))
FORUMS = PACK['forums']
FILES = {item['content_id']: item for item in PACK['files']}
LIBRARIES = {forum_id: forum['library'] for forum_id, forum in FORUMS.items()}


def merge_forums(data):
    next_id = max((m.get('id', 0) for messages in data.values() for m in messages), default=1000) + 1
    known = {m.get('content_id'): m['id'] for messages in data.values() for m in messages if m.get('content_id')}
    for source in PACK['messages']:
        key = source['content_id']
        if key in known:
            continue
        message = copy.deepcopy(source)
        section = message.pop('section')
        parent = message.pop('parent', None)
        message.update(id=next_id, parent_id=known[parent] if parent else None, author_user_id='SIMULATED')
        data.setdefault(section, []).append(message)
        known[key] = next_id
        next_id += 1
    return data


def merge_files(data):
    next_number = max((f.get('number', 0) for files in data.values() for f in files), default=400) + 1
    known = {f.get('content_id') for files in data.values() for f in files}
    for source in PACK['files']:
        if source['content_id'] in known:
            continue
        record = {key: copy.deepcopy(value) for key, value in source.items() if key not in ('content', 'library')}
        record.update(number=next_number, bytes=len(source['content'].encode('ascii')), downloads=0, status='approved')
        data.setdefault(source['library'], []).append(record)
        next_number += 1
    return data


def install(base_dir):
    return install_content_pack(base_dir, PACK['id'], {
        'forums.json': merge_forums, 'library_files.json': merge_files,
    })


def download_content(record):
    source = FILES.get(record.get('content_id'))
    return source['content'] if source else None


def detail_lines(record):
    lines = [record['description'], '', 'Version: ' + record.get('version', 'Unspecified'),
             'System: ' + record.get('system', 'See file documentation'),
             record.get('instructions', ''), '', 'RELEASE HISTORY']
    lines.extend(record.get('history', ['No release history supplied.']))
    lines.extend(['', 'MEMBER REVIEWS (SIMULATED)'])
    lines.extend(f"{review['author']}: {review['text']}" for review in record.get('reviews', []))
    return lines
