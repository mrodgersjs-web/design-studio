#!/bin/bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
NAME="rig-design-studio-satori-apple"
for dest in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.hermes/skills"; do
  mkdir -p "$dest"
  ln -sfn "$SRC" "$dest/$NAME"
  printf 'linked %s/%s -> %s\n' "$dest" "$NAME" "$SRC"
done
