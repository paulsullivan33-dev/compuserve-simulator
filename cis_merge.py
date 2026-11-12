"""Three-way merge for shared JSON documents.

Each simulator session is its own process holding long-lived copies of shared
documents (profiles, forums, library files). Writing a whole stale copy back
would erase every change other sessions made since it was loaded. Instead, a
save merges this session's edits (``mine`` relative to the ``base`` it loaded)
into the latest stored version (``theirs``):

* dicts merge key by key, recursively, so two sessions editing different
  fields of one profile both keep their change;
* lists whose items are all dicts with unique ``id`` values merge item by item,
  keeping the stored order and appending this session's new items;
* other lists merge as additions and removals, so appends from both sides
  survive;
* anything else that this session changed takes this session's value.
"""
import json
from collections import Counter

MISSING = object()


def snapshot(data):
    """Return a detached, JSON-normalized copy (tuples become lists, etc.)."""
    return json.loads(json.dumps(data, ensure_ascii=False))


def _key(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _identifiable(*lists):
    for items in lists:
        if not all(isinstance(item, dict) and "id" in item for item in items):
            return False
        ids = [_key(item["id"]) for item in items]
        if len(ids) != len(set(ids)):
            return False
    return True


def _next_id(items):
    numbers = [item["id"] for item in items if isinstance(item.get("id"), int) and not isinstance(item.get("id"), bool)]
    return max(numbers, default=0) + 1


def _merge_by_id(base, mine, theirs):
    base_map = {_key(item["id"]): item for item in base}
    mine_map = {_key(item["id"]): item for item in mine}
    theirs_map = {_key(item["id"]): item for item in theirs}
    result = []
    for item in theirs:
        key = _key(item["id"])
        if key in base_map and key not in mine_map:
            if base_map[key] == item:
                continue  # this session deleted it and nobody else changed it
            result.append(item)
        elif key in base_map:
            result.append(merge(base_map[key], mine_map[key], item))
        else:
            result.append(item)
    for item in mine:
        key = _key(item["id"])
        if key in base_map:
            continue  # merged above, or deleted by another session
        if key not in theirs_map:
            result.append(item)
        elif theirs_map[key] != item:
            # Another session stored a different item under the same new id.
            if isinstance(item["id"], int) and not isinstance(item["id"], bool):
                result.append(dict(item, id=_next_id(result)))
            else:
                result[result.index(theirs_map[key])] = item
    return result


def _merge_multiset(base, mine, theirs):
    base_count = Counter(_key(item) for item in base)
    mine_count = Counter(_key(item) for item in mine)
    removed = base_count - mine_count
    added = mine_count - base_count
    result = []
    for item in theirs:
        key = _key(item)
        if removed[key]:
            removed[key] -= 1
            continue
        result.append(item)
    for item in mine:
        key = _key(item)
        if added[key]:
            added[key] -= 1
            result.append(item)
    return result


def merge(base, mine, theirs):
    """Merge ``mine`` (edited from ``base``) into ``theirs`` (latest stored)."""
    if theirs is MISSING:
        return mine
    if mine == base:
        return theirs
    if theirs == base or mine == theirs:
        return mine
    if isinstance(mine, dict) and isinstance(theirs, dict) and isinstance(base, (dict, type(MISSING))):
        base = base if isinstance(base, dict) else {}
        result = dict(theirs)
        for key in set(base) | set(mine):
            mine_value = mine.get(key, MISSING)
            base_value = base.get(key, MISSING)
            if mine_value == base_value:
                continue
            if mine_value is MISSING:
                result.pop(key, None)
                continue
            result[key] = merge(base_value, mine_value, theirs.get(key, MISSING))
        return result
    if isinstance(mine, list) and isinstance(theirs, list) and isinstance(base, (list, type(MISSING))):
        base = base if isinstance(base, list) else []
        if _identifiable(base, mine, theirs):
            return _merge_by_id(base, mine, theirs)
        return _merge_multiset(base, mine, theirs)
    return mine


def refresh_in_place(target, source):
    """Make ``target`` equal ``source`` while keeping container identities.

    Other code holds references into these documents (the signed-on member's
    profile, a forum section's message list), so nested dicts and lists are
    updated in place rather than replaced. Returns the object to store.
    """
    if isinstance(target, dict) and isinstance(source, dict):
        for key in [key for key in target if key not in source]:
            del target[key]
        for key, value in source.items():
            target[key] = refresh_in_place(target[key], value) if key in target else value
        return target
    if isinstance(target, list) and isinstance(source, list):
        if _identifiable(target, source):
            existing = {_key(item["id"]): item for item in target}
            target[:] = [
                refresh_in_place(existing[_key(item["id"])], item) if _key(item["id"]) in existing else item
                for item in source
            ]
        else:
            target[:] = source
        return target
    return source
