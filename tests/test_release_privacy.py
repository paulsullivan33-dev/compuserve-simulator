import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import build_release
from release_payload import payload


class ReleasePrivacyTests(unittest.TestCase):
    def test_build_rejects_missing_runtime_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'release_assets.json').write_text(
                json.dumps({'files': [], 'defaults': {}}), encoding='utf-8')
            (root / 'cis_future.py').write_text('', encoding='utf-8')
            with patch.object(build_release, 'BASE_DIR', root), \
                 patch.object(build_release, 'DIST_DIR', root / 'dist'):
                with self.assertRaisesRegex(ValueError, 'cis_future.py'):
                    build_release.build_release()

    def test_zip_uses_clean_state_and_ignores_unlisted_private_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rules = {'files': ['profiles.json', 'forums.json'],
                     'defaults': {'profiles.json': {}, 'forums.json': {'seed': []}}}
            (root / 'release_assets.json').write_text(json.dumps(rules))
            for name in ('profiles.json', 'forums.json', 'dynamic_state.json', 'private.json'):
                (root / name).write_text('{"private": "SECRET-MARKER"}')
            with patch.object(build_release, 'BASE_DIR', root), patch.object(build_release, 'DIST_DIR', root / 'dist'):
                archive = build_release.build_release()
            with zipfile.ZipFile(archive) as release:
                self.assertEqual(set(release.namelist()), {'profiles.json', 'forums.json', 'RELEASE_MANIFEST.json'})
                for name, clean in rules['defaults'].items():
                    self.assertEqual(json.loads(release.read(name)), clean)
                self.assertFalse(any(b'SECRET-MARKER' in release.read(n) for n in release.namelist()))
            self.assertIn('SECRET-MARKER', (root / 'profiles.json').read_text())
            with self.assertRaises(ValueError):
                payload(root, 'private.json')
