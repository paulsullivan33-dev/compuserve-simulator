"""Ship the flat application's adjacent resource files in wheels and sdists."""
from pathlib import Path
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist
import importlib.util


ROOT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('release_payload', ROOT / 'release_payload.py')
_policy_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_policy_module)
policy, payload = _policy_module.policy, _policy_module.payload


def resources():
    yield from (ROOT / name for name in policy(ROOT)['files']
                if name.endswith('.json') or name.startswith('web/'))


class BuildPy(build_py):
    def run(self):
        allowed = set(policy(ROOT)['files'])
        for old in Path(self.build_lib).rglob('*.json'):
            if old.relative_to(self.build_lib).as_posix() not in allowed:
                raise RuntimeError(f'Unlisted JSON in build directory; use a clean build directory: {old}')
        super().run()
        for source in resources():
            target = Path(self.build_lib) / source.relative_to(ROOT)
            self.mkpath(str(target.parent))
            target.write_bytes(payload(ROOT, source.relative_to(ROOT)))

    def get_outputs(self, include_bytecode=1):
        return super().get_outputs(include_bytecode) + [
            str(Path(self.build_lib) / path.relative_to(ROOT)) for path in resources()
        ]


class SourceDist(sdist):
    def make_release_tree(self, base_dir, files):
        # Filter stale egg-info manifests and unlisted local JSON files.
        allowed = set(policy(ROOT)['files'])
        files = [name for name in files if not name.endswith('.json') or name in allowed]
        super().make_release_tree(base_dir, files)
        for name in policy(ROOT)['defaults']:
            target = Path(base_dir) / name
            # setuptools may use hard links; unlink before replacing clean state.
            if target.exists():
                target.unlink()
            target.write_bytes(payload(ROOT, name))
