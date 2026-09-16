"""Ship the flat application's adjacent resource files in wheels and sdists."""
from pathlib import Path
from setuptools.command.build_py import build_py


ROOT = Path(__file__).resolve().parent


def resources():
    yield from sorted(ROOT.glob('*.json'))
    yield from sorted(path for path in (ROOT / 'web').rglob('*') if path.is_file())


class BuildPy(build_py):
    def run(self):
        super().run()
        for source in resources():
            target = Path(self.build_lib) / source.relative_to(ROOT)
            self.mkpath(str(target.parent))
            self.copy_file(str(source), str(target))

    def get_outputs(self, include_bytecode=1):
        return super().get_outputs(include_bytecode) + [
            str(Path(self.build_lib) / path.relative_to(ROOT)) for path in resources()
        ]
