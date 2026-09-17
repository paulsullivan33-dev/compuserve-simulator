"""Explicit distributable assets and clean starter state, independent of Git."""
import json
from pathlib import Path


def policy(root):
    return json.loads((Path(root) / 'release_assets.json').read_text(encoding='utf-8'))


def payload(root, relative):
    name = Path(relative).as_posix()
    rules = policy(root)
    if name not in rules['files']:
        raise ValueError(f'Not a release asset: {name}')
    if name in rules['defaults']:
        return (json.dumps(rules['defaults'][name], indent=2) + '\n').encode('utf-8')
    source = Path(root) / relative
    if source.is_symlink() or not source.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError(f'Release asset escapes source tree: {name}')
    return source.read_bytes()
