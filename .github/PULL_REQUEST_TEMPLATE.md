## What changed

<!-- One or two paragraphs describing the change. -->
<!-- List the user-visible behaviour change in one sentence first. -->

## How I verified

<!-- Paste the exact commands and their output. -->

- [ ] `python -m ruff check .` exits 0
- [ ] `python -m pytest -q --cov=tokens_toolkit` reports coverage and exits 0
- [ ] `bash scripts/smoke.sh` ends with `design-studio smoke PASS`
- [ ] If tokens/base.json changed: `python -m tokens_toolkit.cli validate tokens/base.json` returns ok:true

## Boundary impact

<!-- Public boundary check per docs/public-boundary.md. -->

- [ ] No PII, secrets, customer data, or internal paths added
- [ ] No banned words (unlock, empower, synergy, leverage, disrupt, hustle,
  utilize, iterate, optimize) in the diff
- [ ] No machine paths like `/Users/...` or `~/Developer/...` left in tracked files
