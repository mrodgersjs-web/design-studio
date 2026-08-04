#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test -f README.md
test -f docs/public-boundary.md
test -d assets
echo "design-studio smoke PASS"
