# Contributing

Use Python 3.10 or newer. Install development and browser dependencies with:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev,web]"
```

Before building a release, run:

```powershell
.venv\Scripts\python.exe -m unittest -v test_compuserve.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m compileall -q -x "old_versions|build|dist|.venv" .
.venv\Scripts\python.exe smoke_test.py
.venv\Scripts\python.exe -m pip install "setuptools>=75" wheel
.venv\Scripts\python.exe tests/check_installed_package.py
.venv\Scripts\python.exe build_release.py
.venv\Scripts\python.exe -c "import build_release, smoke_test; print(smoke_test.verify_archive(build_release.build_release()))"
```

Tests should isolate persistence with a temporary directory. Do not commit databases,
captures, backups, downloads, uploads, virtual environments, or release archives.

Use UTF-8 explicitly for text files. `.gitattributes` keeps Python, JSON and shell
scripts in LF form and Windows command scripts in CRLF form. Path checks should
use `Path.is_absolute()` rather than assuming a leading slash. Tests comparing
text should normalize line endings without changing the content assertion.

Keep `cis_version.py`, `pyproject.toml`, and the local package version in `uv.lock`
in sync. Verify both the release ZIP and installed wheel before tagging a release.
# Release data privacy

ZIPs, wheels, and source distributions use `release_assets.json` as their asset
list. Add new distributable resources to that list (and JSON resources to
`MANIFEST.in`). Never add member data, databases, exports, or credentials.
The `defaults` section contains clean starter state, including built-in forum
and library content. Builders substitute these defaults for mutable JSON files
without changing the local originals. Unknown JSON files are excluded; stale
unlisted JSON in a wheel build directory causes the build to fail.
Run `python -m unittest discover -s tests -q` and
`python tests/check_installed_package.py` to verify packaging.
