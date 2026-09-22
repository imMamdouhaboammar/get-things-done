#!/usr/bin/env bash
set -euo pipefail

FORCE="false"
DRY_RUN="false"
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
  --target <name>       agents|codex|claude|cursor|kimi|grok|deepseek|antigravity|gemini-cli
  --target-path <dir>   Install to an explicit Agent Skills-compatible root
  --all                 Install to all distinct supported user skill roots
  --list-targets        Print named shell targets without installing
  --dry-run             Print intended writes without changing files
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
agents       ~/.agents/skills
codex        ~/.agents/skills
claude       ~/.claude/skills
cursor       ~/.cursor/skills
kimi         ${KIMI_CODE_HOME:-~/.kimi-code}/skills
grok         ~/.grok/skills
deepseek     ~/.agents/skills
antigravity  ~/.gemini/config/skills
gemini-cli   ~/.gemini/config/skills
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
    --all) TARGETS+=("agents" "claude" "cursor" "kimi" "grok" "deepseek" "antigravity"); shift ;;
    --list-targets) list_targets; exit 0 ;;
    --dry-run) DRY_RUN="true"; shift ;;
    --force) FORCE="true"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ ${#TARGETS[@]} -gt 0 || ${#TARGET_PATHS[@]} -gt 0 ]] || TARGETS=("agents")
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SEEN_PATHS=()
SKILLS=(get-things-done building-gtd-domain-packs gtd-capability-router gtd-deliberation)

has_seen() {
  local target="$1"
  [[ ${#SEEN_PATHS[@]} -gt 0 ]] || return 1
  for seen in "${SEEN_PATHS[@]}"; do
    if [[ "$seen" == "$target" ]]; then
      return 0
    fi
  done
  return 1
}

rollback_install() {
  local base="$1"
  local stage_root="$2"
  local backup_root="$3"
  local installed_list="$4"
  local skill

  for skill in $installed_list; do
    rm -rf "$base/$skill"
  done

  for skill in "${SKILLS[@]}"; do
    if [[ -e "$backup_root/$skill" ]]; then
      rm -rf "$base/$skill"
      mv "$backup_root/$skill" "$base/$skill" || {
        echo "ROLLBACK ERROR: could not restore $base/$skill" >&2
      }
    fi
  done

  rm -rf "$stage_root" "$backup_root"
}

install_to() {
  local base="$1"
  [[ -n "$base" ]] || { echo "Install root cannot be empty" >&2; exit 2; }
  if has_seen "$base"; then
    return 0
  fi
  SEEN_PATHS+=("$base")

  local skill
  for skill in "${SKILLS[@]}"; do
    local source="$ROOT/skills/$skill"
    local dest="$base/$skill"
    [[ -f "$source/SKILL.md" ]] || { echo "Missing canonical skill: $source/SKILL.md" >&2; return 2; }
    if [[ "$DRY_RUN" != "true" && -e "$dest" && "$FORCE" != "true" ]]; then
      echo "Refusing to overwrite $dest. Use --force" >&2
      return 2
    fi
  done

  if [[ "$DRY_RUN" == "true" ]]; then
    for skill in "${SKILLS[@]}"; do
      echo "Would install $skill -> $base/$skill"
    done
    return 0
  fi

  mkdir -p "$base"
  local stage_root="$base/.gtd-install-stage.$$"
  local backup_root="$base/.gtd-install-backup.$$"
  rm -rf "$stage_root" "$backup_root"
  mkdir -p "$stage_root" "$backup_root"

  for skill in "${SKILLS[@]}"; do
    local source="$ROOT/skills/$skill"
    if ! cp -R "$source" "$stage_root/$skill"; then
      rollback_install "$base" "$stage_root" "$backup_root" ""
      echo "Failed to stage $skill" >&2
      return 1
    fi
    if [[ ! -f "$stage_root/$skill/SKILL.md" ]]; then
      rollback_install "$base" "$stage_root" "$backup_root" ""
      echo "Failed to validate staged skill: $skill" >&2
      return 1
    fi
  done

  if [[ "$FORCE" == "true" ]]; then
    for skill in "${SKILLS[@]}"; do
      if [[ -e "$base/$skill" ]]; then
        if ! mv "$base/$skill" "$backup_root/$skill"; then
          rollback_install "$base" "$stage_root" "$backup_root" ""
          echo "Failed to back up existing skill: $skill" >&2
          return 1
        fi
      fi
    done
  fi

  local installed_list=""
  for skill in "${SKILLS[@]}"; do
    if ! mv "$stage_root/$skill" "$base/$skill"; then
      rollback_install "$base" "$stage_root" "$backup_root" "$installed_list"
      echo "Install failed while replacing $skill; previous installation restored" >&2
      return 1
    fi
    installed_list="$installed_list $skill"
    echo "Installed $skill -> $base/$skill"

    if [[ "${GTD_TEST_FAIL_AFTER_SKILL:-}" == "$skill" ]]; then
      rollback_install "$base" "$stage_root" "$backup_root" "$installed_list"
      echo "Install failed after $skill; previous installation restored" >&2
      return 1
    fi
  done

  rm -rf "$stage_root" "$backup_root"
}

if [[ ${#TARGETS[@]} -gt 0 ]]; then
  for target in "${TARGETS[@]}"; do
    case "$target" in
      agents|codex|deepseek) install_to "$HOME/.agents/skills" ;;
      claude) install_to "$HOME/.claude/skills" ;;
      cursor) install_to "$HOME/.cursor/skills" ;;
      kimi) install_to "${KIMI_CODE_HOME:-$HOME/.kimi-code}/skills" ;;
      grok) install_to "$HOME/.grok/skills" ;;
      antigravity|gemini-cli) install_to "$HOME/.gemini/config/skills" ;;
      *) echo "Unknown target: $target" >&2; exit 2 ;;
    esac
  done
fi

if [[ ${#TARGET_PATHS[@]} -gt 0 ]]; then
  for target_path in "${TARGET_PATHS[@]}"; do
    install_to "$target_path"
  done
fi
