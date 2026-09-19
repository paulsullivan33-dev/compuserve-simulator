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

# Branch workflow

- Do all work on a feature branch (`feature/<short-name>`); keep history
  strictly linear — no merge commits on feature branches.
- The maintainer pulls the branch, tests it on the dev server, merges to
  `main`, and pushes.
- Pushing to GitHub goes through the API helper (`gh.py push`), which
  **cannot push merge commits**: it replays commits via the git-database API
  using `git diff-tree -r`, which outputs nothing for merge commits, silently
  dropping merge resolutions and potentially reverting files to the wrong
  side. Always squash a merge into a single linear commit before pushing —
  never push a merge commit with `gh.py`.

# Running the simulator and tests (Linux)

```bash
cd <repo>
~/.local/bin/uv run --python 3.11 compuserve.py   # terminal simulator
PY=$(~/.local/bin/uv python find 3.11)
$PY -m unittest test_compuserve                   # full suite
$PY smoke_test.py
```

# Content packs

`cis_communities.install()` (via `install_content_pack`) installs each content
pack **once**, keyed by the pack `id` in `computer_communities.json`. When
appending new seed posts/files to that JSON in a later pack, **bump the pack
id** (e.g. v1 -> v2); otherwise existing member databases skip the merge and
the new forums appear empty. The merge itself is idempotent (it skips known
`content_id`s), so bumping is safe.

# Simulator conventions

- Interactive game/menu output must go through `app.ansi_scroll(text, 0.01)`,
  never bare `print()` — bare prints bypass baud-rate delay, fast mode, flow
  control, capture, and page pauses.
- The 16-line page pause resets its line count at each user input prompt, so
  "More!" only triggers when a single output block exceeds 16 lines.
- The simulated "Present Day" is the December 1988 cycle, not the real date;
  shared daily forum arcs stay December 1988-flavored in every era by design.
- The poster photo-menus own `GO NEWS` / `GO FORUMS` / `GO GAMES` /
  `GO TRAVEL` / `GO SHOPPING` / `GO MONEY`; the legacy service screens remain
  reachable via `GO NEWSSIM` / `GO FORUMSSIM` and similar aliases.

# Documentation

- `USER_GUIDE.md` is a slim index; per-service-area pages live under `docs/`.
  Put new user-facing docs in the matching `docs/` page, not in the index.
- `CHANGELOG.md` gets an entry for every user-visible change.

# Releases and tracking

- Tag releases on GitHub (`v1.17.0` style) at the commit that was `main` when
  the version was cut. Consider a version bump in `CHANGELOG.md`,
  `pyproject.toml`, `cis_version.py`, and `uv.lock` (kept in sync) when a
  batch of work lands.
- GitHub Issues are the work tracker; file new work there instead of leaving
  it in chat history.
