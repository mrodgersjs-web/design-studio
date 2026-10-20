# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

Fix (2026-10-19, this commit): `pyproject.toml`'s `[tool.setuptools.packages.find]` now
searches `where = ["src", "."]`. Before this commit `tokens_toolkit` (which lives under
`src/`) was not installed by `pip install -e .`, so the README quickstart command
`tokens-toolkit validate tokens/base.json` failed with `ModuleNotFoundError` and
`import tokens_toolkit` failed in a fresh venv. After this commit both work:
`import tokens_toolkit` prints version 0.1.0 and `tokens-toolkit validate tokens/base.json`
returns `"ok": true`.


Polish wave (2026-10-19, this commit): `.github/CODEOWNERS` (`* @mrodgersjs-web`) and
`.github/copilot-instructions.md` were added, the README CI badge moved to the shields
`github/actions/workflow/status` form (the old badge.svg line was removed),
`timeout-minutes: 15` was added to every job in `.github/workflows/ci.yml` and
`rig-lattice.yml`, and `tests/test_repo_hygiene.py` was added. That test asserts from
the files on disk that `.github/CODEOWNERS` contains `* @mrodgersjs-web`, that
`.github/copilot-instructions.md` exists within 8000 bytes and names a test command,
that the README carries a `github/actions/workflow/status` badge, the
`rodgersintelligence.com` footer, a test command word and clone examples targeting
`mrodgersjs-web/design-studio`, and that every workflow job has `timeout-minutes` and
no `continue-on-error`.


## [1.2.0] - 2026-10-19

### Added
- `tokens_toolkit` package: rule-based JSON parser (`parser.py`), pure-Python
  WCAG 2.1 contrast checker (`contrast.py`), exporters for CSS / JSON /
  Tailwind / Markdown (`exporter.py`), checklist parser and renderer
  (`checklists.py`), and a CLI entry point with five subcommands
  (`validate`, `export`, `contrast`, `checklist`, `tokens`).
- 69 pytest tests across `tests/test_parser.py`, `tests/test_contrast.py`,
  `tests/test_exporter.py`, `tests/test_checklists.py`,
  `tests/test_cli.py`, and `tests/conftest.py`.
- `src/tokens_toolkit/py.typed` (PEP 561 marker).
- `tokens/base.json` enriched with 25 tokens across color, font, size,
  and space groups, including a `clamp()` token pair.
- `checklists/ui-review.md` structured as YAML frontmatter + a tabular
  Markdown body.
- `[project.optional-dependencies].dev`: pytest, pytest-cov, ruff.
- `[project.scripts]`: `tokens-toolkit` alongside the existing
  `rigds-mcp` entry.
- `[project.urls]`: Homepage, Repository, Issues, Changelog.
- `[tool.coverage.run]` / `[tool.coverage.report]`: branch coverage on
  the `tokens_toolkit` source.
- `[tool.ruff]`: line 120, extend-exclude for legacy `mcp/` and
  `rigds_mcp/` directories and `assets/` / `examples/`.
- `[tool.pytest.ini_options]`: `addopts = ["--strict-markers", "-ra"]`.
- `.github/workflows/ci.yml`: lint + pytest on Python 3.10-3.13 plus
  the smoke.

### Changed
- Bumped `rigds-mcp` from 1.1.0 to 1.2.0; consolidated the project
  description to mention both packages.
- `scripts/smoke.sh` now installs the package, lints, runs pytest with
  coverage, and exercises `tokens-toolkit validate` against
  `tokens/base.json`.

## [1.1.0] - 2026-10-10

- Initial public release with the `rigds-mcp` MCP server.
