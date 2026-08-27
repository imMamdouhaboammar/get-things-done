#!/usr/bin/env bash
set -euo pipefail

FORCE="false"
TARGETS=()
TARGET_PATHS=()

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Legacy options:
  --agents              Install to ~/.agents/skills
  --claude              Install to ~/.claude/skills
  --both                Install to both universal and Claude locations

Multi-host options:
  --target <name>       agents|codex|claude|cursor|kimi|grok|deepseek
  --target-path <dir>   Install to an explicit Agent Skills-compatible root
  --all                 Install to all distinct supported user skill roots
  --list-targets        Print named shell targets without installing
  --force               Replace existing GTD skill directories
  -h, --help            Show this help

Examples:
  ./install.sh --target codex
  ./install.sh --target claude --target cursor
  ./install.sh --target-path "$HOME/.my-agent/skills"
  ./install.sh --all --force
EOF
}

list_targets() {
  cat <<'EOF'
agents     ~/.agents/skills
codex      ~/.agents/skills
claude     ~/.claude/skills
cursor     ~/.cursor/skills
kimi       ${KIMI_CODE_HOME:-~/.kimi-code}/skills
grok       ~/.grok/skills
deepseek   ~/.agents/skills
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
    --target-path)
      [[ $# -ge 2 ]] || { echo "--target-path requires a value" >&2; exit 2; }
      [[ -n "$2" ]] || { echo "--target-path cannot be empty" >&2; exit 2; }
      TARGET_PATHS+=("$2"); shift 2 ;;
    --all) TARGETS+=("agents" "claude" "cursor" "kimi" "grok" "deepseek"); shift ;;
    --list-targets) list_targets; exit 0 ;;
    --force) FORCE="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ ${#TARGETS[@]} -gt 0 || ${#TARGET_PATHS[@]} -gt 0 ]] || TARGETS=("agents")
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

declare -A SEEN=()

install_to() {
  local base="$1"
  [[ -n "$base" ]] || { echo "Install root cannot be empty" >&2; exit 2; }
  [[ -z "${SEEN[$base]:-}" ]] || return 0
  SEEN[$base]=1
  mkdir -p "$base"
  for skill in get-things-done building-gtd-domain-packs; do
    local source="$ROOT/skills/$skill"
    local dest="$base/$skill"
    [[ -f "$source/SKILL.md" ]] || { echo "Missing canonical skill: $source/SKILL.md" >&2; exit 2; }
    if [[ -e "$dest" && "$FORCE" != "true" ]]; then
      echo "Refusing to overwrite $dest. Use --force" >&2
      exit 2
    fi
    rm -rf "$dest"
    cp -R "$source" "$dest"
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

for target_path in "${TARGET_PATHS[@]}"; do
  install_to "$target_path"
done
