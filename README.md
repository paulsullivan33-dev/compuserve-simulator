# Classic CompuServe Simulation

An independent historical simulation of the text-mode CompuServe Information
Service circa 1988. See [USER_GUIDE.md](USER_GUIDE.md) for the player guide and
[ARCHITECTURE.md](ARCHITECTURE.md) for implementation notes.

Version **1.17.0** includes fourteen historical time-capsule destinations,
21 forums, six arcade games, and expanded period news and magazines.
After signing in, enter `GO START` for three suggestions tailored to your date.
Fixed period collections carry a **DECEMBER 1988 ARCHIVE** label; featured-date
headlines and explicitly live services are separate. See [CHANGELOG.md](CHANGELOG.md).

## Run locally

Python 3.10 or newer is required.

```powershell
py -3 compuserve.py
```

For the optional browser terminal:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[web]"
.venv\Scripts\python.exe web_app.py
```

## Development

```powershell
.venv\Scripts\python.exe -m pip install -e ".[dev,web]"
.venv\Scripts\python.exe -m unittest -v test_compuserve.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe smoke_test.py
.venv\Scripts\python.exe -m pip install "setuptools>=75" wheel
.venv\Scripts\python.exe tests/check_installed_package.py
.venv\Scripts\python.exe build_release.py
```

The installed-package check builds a wheel and installs it in a temporary directory,
then imports every runtime module and checks content, navigation, assets, and the
console entry point outside the checkout. GitHub Actions runs Windows and Linux
checks on Python 3.10 and 3.13.

Python wheels include the seed JSON and browser assets. Use a user-owned virtual
environment: the current storage model keeps runtime state beside the application.
For managed Linux installations and upgrades, use the release ZIP and installer below.

Runtime databases, backups, captures, uploads, downloads, virtual environments,
and release archives are intentionally excluded from source control and releases.

## Linux upgrades

Extract a new release outside the live installation and run:

```bash
./install-linux.sh --install-dir ~/compuserve --upgrade --systemd-user
```

Add `--telnet` if used, or `--non-interactive` for unattended operation. The updater
verifies the release manifest, stages and smoke-tests the application, backs up the
database, preserves runtime directories, restarts selected systemd units, and restores
the prior application files if installation or a service health check fails.

This project is not affiliated with or endorsed by CompuServe, AOL, or their
successors. Transactions and charges in the simulation are fictional.
