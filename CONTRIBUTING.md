# Contributing

Use Python 3.10 or newer. Install development and browser dependencies with:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev,web]"
```

Before building a release, run:

```powershell
.venv\Scripts\python.exe -m unittest -v test_compuserve.py
.venv\Scripts\python.exe -m compileall -q -x "old_versions" .
.venv\Scripts\python.exe smoke_test.py
.venv\Scripts\python.exe build_release.py
```

Tests should isolate persistence with a temporary directory. Do not commit databases,
captures, backups, downloads, uploads, virtual environments, or release archives.
