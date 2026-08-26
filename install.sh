#!/usr/bin/env bash
set -euo pipefail
MODE="agents"
FORCE="false"
for arg in "$@"; do
  case "$arg" in
    --agents) MODE="agents" ;;
    --claude) MODE="claude" ;;
    --both) MODE="both" ;;
    --force) FORCE="true" ;;
    -h|--help) echo "Usage: ./install.sh [--agents|--claude|--both] [--force]"; exit 0 ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
install_to() {
  local base="$1"
  mkdir -p "$base"
  for skill in get-things-done building-gtd-domain-packs; do
    local dest="$base/$skill"
    if [[ -e "$dest" && "$FORCE" != "true" ]]; then
      echo "Refusing to overwrite $dest. Use --force" >&2
      exit 2
    fi
    rm -rf "$dest"
    cp -R "$ROOT/skills/$skill" "$dest"
    echo "Installed $skill -> $dest"
  done
}
case "$MODE" in
  agents) install_to "$HOME/.agents/skills" ;;
  claude) install_to "$HOME/.claude/skills" ;;
  both) install_to "$HOME/.agents/skills"; install_to "$HOME/.claude/skills" ;;
esac
