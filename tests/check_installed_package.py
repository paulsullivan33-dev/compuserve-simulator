"""Build and install a wheel, then run it outside the source checkout.

Run with python tests/check_installed_package.py. Requires pip and the build
dependencies from pyproject.toml; no network or runtime dependencies are needed.
"""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile
import json
import tarfile


ROOT = Path(__file__).resolve().parents[1]


def run():
    env = {**os.environ, 'PIP_DISABLE_PIP_VERSION_CHECK': '1', 'PIP_NO_INDEX': '1',
           'PIP_NO_CACHE_DIR': '1'}
    env.pop('PYTHONPATH', None)
    with tempfile.TemporaryDirectory() as temporary:
        work = Path(temporary)
        wheels = work / 'wheels'
        installed = work / 'installed'
        sources = work / 'sources'
        sources.mkdir()
        subprocess.run([sys.executable, '-c',
                        'import setuptools.build_meta, sys; setuptools.build_meta.build_sdist(sys.argv[1])',
                        str(sources)], cwd=ROOT, env=env, check=True)
        source = next(sources.glob('*.tar.gz'))
        rules = json.loads((ROOT / 'release_assets.json').read_text(encoding='utf-8'))
        with tarfile.open(source) as archive:
            for member in archive.getmembers():
                name = '/'.join(member.name.split('/')[1:])
                if name.endswith('.json'):
                    assert name in rules['files'], name
                if name in rules['defaults']:
                    assert json.load(archive.extractfile(member)) == rules['defaults'][name], name
        subprocess.run([sys.executable, '-m', 'pip', 'wheel', '--no-build-isolation',
                        '--no-deps', '--wheel-dir', str(wheels), str(source)],
                       cwd=work, env=env, check=True)
        wheel = next(wheels.glob('*.whl'))
        with zipfile.ZipFile(wheel) as archive:
            names = set(archive.namelist())
            required = {path.name for path in ROOT.glob('cis_*.py')}
            assert all(not name.endswith('.json') or name in rules['files'] for name in names)
            required.update(name for name in rules['files'] if name.endswith('.json'))
            for name, clean in rules['defaults'].items():
                assert json.loads(archive.read(name)) == clean, name
            required.update({'compuserve.py', 'web_app.py', 'telnet_app.py',
                             'event_worker.py', 'web/index.html'})
            missing = required - names
            if missing:
                raise RuntimeError(f'Wheel is missing: {sorted(missing)}')
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--no-deps',
                        '--target', str(installed), str(wheel)], cwd=work, env=env, check=True)
        # -I excludes PYTHONPATH, user site packages, and the checkout. All app
        # imports must come from the actual pip installation above.
        probe = '''
import importlib, importlib.metadata, pathlib, sys, tempfile
from datetime import date
sys.path.insert(0, sys.argv[1])
installed = pathlib.Path(sys.argv[1]).resolve()
import compuserve, cis_discovery, cis_timecapsule, cis_yearend
assert pathlib.Path(compuserve.__file__).resolve().parent == installed
for path in installed.glob('cis_*.py'):
    importlib.import_module(path.stem)
assert len(cis_timecapsule.PACKS) == 14
assert len(cis_discovery.start_suggestions(date(1981, 4, 12))) == 3
assert cis_yearend.yearend_menu_lines(date(1981, 4, 12)) == []
assert compuserve.resolve_go_destination('ARCADE', 'main') == 'arcade'
assert (installed / 'web' / 'index.html').is_file()
dist = importlib.metadata.distribution('classic-compuserve')
entry = next(e for e in dist.entry_points if e.name == 'classic-compuserve')
assert entry.load() is compuserve.main
assert dist.version == compuserve.VERSION
with tempfile.TemporaryDirectory() as state:
    compuserve.BASE_DIR = pathlib.Path(state)
    compuserve.initialize_database()
    assert compuserve.BASE_DIR.joinpath('compuserve.db').is_file()
print('Installed wheel: all runtime modules, 14 content packs, navigation, assets, entry point, and database initialization passed.')
'''
        subprocess.run([sys.executable, '-I', '-c', probe, str(installed)],
                       cwd=work, env=env, check=True)


if __name__ == '__main__':
    run()
