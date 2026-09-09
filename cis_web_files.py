"""Queue immutable copies of explicitly requested files for a web session."""

import json
import os
from pathlib import Path
import shutil
import uuid


def offer_download(path):
    """No-op in the console; publish a snapshot to the web launcher's private queue."""
    export_dir = os.environ.get('CIS_WEB_EXPORT_DIR')
    if os.environ.get('CIS_WEB_TERMINAL') != '1' or not export_dir:
        return False
    source = Path(path)
    directory = Path(export_dir)
    token = uuid.uuid4().hex
    snapshot = directory / (token + '.bin')
    manifest = directory / (token + '.json')
    temporary = directory / (token + '.tmp')
    try:
        shutil.copyfile(source, snapshot)
        temporary.write_text(json.dumps({'name': source.name}), encoding='utf-8')
        temporary.replace(manifest)
    except OSError:
        snapshot.unlink(missing_ok=True)
        temporary.unlink(missing_ok=True)
        print('Browser download could not be prepared. The server copy is still available.')
        return False
    return True
