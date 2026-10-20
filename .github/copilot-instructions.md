# design-studio

Reads, validates and exports design tokens, checks WCAG contrast, and renders
UI review checklists. The `tokens-toolkit` CLI (from `rigds_mcp`) is a pure
Python, fully typed design-token model that is committed alongside the tokens
it consumes: parse `tokens/*.json`, validate them, grade colour contrast, and
export to the formats downstream tools read.

## Layout

- `src/` - the token model, parser, contrast checker and exporters
  (`tokens-toolkit` CLI entry point).
- `tokens/` - the committed token files the tools consume. `checklists/` -
  UI review checklists. `tests/` - pytest suite with `tests/fixtures/`.
- `examples/` - runnable examples. `docs/` - design notes. `mcp/`, `skills/` -
  MCP server and skill surfaces. `scripts/` - helper scripts.

## Setup and test (exact commands)

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
python3 -m pytest -q tests/test_parser.py tests/test_contrast.py tests/test_exporter.py
```

Smoke check on real tokens: `tokens-toolkit validate tokens/base.json`.

## Lint

```bash
python -m ruff check .
```

Must be clean before a PR, together with `pytest -q`.

## Conventions

- Conventional commit subjects (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).
- Every change ships a test that can fail; token parsing and contrast maths
  must assert real expected values, not just "did not throw".
- No secrets, tokens or credentials in tracked files. No machine-specific
  paths (`/Users/...`, `~/Developer/...`) in tracked files.
- Numbers in docs and README must come from a command you ran; quote the
  command, not a remembered figure. If a number changes, re-run the command.
