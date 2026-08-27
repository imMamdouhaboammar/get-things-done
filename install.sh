#!/usr/bin/env bash
set -euo pipefail

FORCE="false"
TARGETS=()

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Legacy options:
  --agents              Install to ~/.agents/skills
  --claude              Install to ~/.claude/skills
  --both                Install to both universal and Claude locations

Multi-host options:
  --target <name>       agents|codex|claude|cursor|kimi|grok|deepseek
  --all                 Install to all distinct supported user skill roots
  --force               Replace existing GTD skill directories
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agents) TARGETS+=("agents"); shift ;;
    --claude) TARGETS+=("claude"); shift ;;
    --both) TARGETS+=("agents" "claude"); shift ;;
    --target)
      [[ $# -ge 2 ]] || { echo "--target requires a value" >&2; exit 2; }
      TARGETS+=("$2"); shift 2 ;;
    --all) TARGETS+=("agents" "claude" "cursor" "kimi" "grok" "deepseek"); shift ;;
    --force) FORCE="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ ${#TARGETS[@]} -gt 0 ]] || TARGETS=("agents")
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

declare -A SEEN=()

install_to() {
  local base="$1"
  [[ -z "${SEEN[$base]:-}" ]] || return 0
  SEEN[$base]=1
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

for target in "${TARGETS[@]}"; do
  case "$target" in
    agents|codex|deepseek) install_to "$HOME/.agents/skills" ;;
    claude) install_to "$HOME/.claude/skills" ;;
    cursor) install_to "$HOME/.cursor/skills" ;;
    kimi) install_to "${KIMI_CODE_HOME:-$HOME/.kimi-code}/skills" ;;
    grok) install_to "$HOME/.grok/skills" ;;
    *) echo "Unknown target: $target" >&2; exit 2 ;;
  esac
done
