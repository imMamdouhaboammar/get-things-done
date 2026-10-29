#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Validating improve Skill Package ==="
echo "Skill directory: $SKILL_DIR"

# 1. Check SKILL.md exists
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "ERROR: SKILL.md not found!"
    exit 1
fi

LINE_COUNT=$(wc -l < "$SKILL_DIR/SKILL.md")
echo "✓ SKILL.md found ($LINE_COUNT lines)"

# 2. Check frontmatter
if head -n 1 "$SKILL_DIR/SKILL.md" | grep -q "^---"; then
    echo "✓ YAML frontmatter opening present"
else
    echo "ERROR: SKILL.md missing frontmatter opening!"
    exit 1
fi

# 3. Check references directory
REFS=(
    "audit-playbook.md"
    "closing-the-loop.md"
    "plan-template.md"
    "core-contract.md"
    "gtd-plan-bridge.md"
)

for ref in "${REFS[@]}"; do
    if [ -f "$SKILL_DIR/references/$ref" ]; then
        echo "✓ Reference found: references/$ref"
    else
        echo "ERROR: Missing reference: references/$ref"
        exit 1
    fi
done

# 4. Check agents directory
AGENTS=(
    "openai.yaml"
    "antigravity.md"
    "claude.md"
    "cursor.md"
    "openai.md"
)

for ag in "${AGENTS[@]}"; do
    if [ -f "$SKILL_DIR/agents/$ag" ]; then
        echo "✓ Agent adapter found: agents/$ag"
    else
        echo "ERROR: Missing agent adapter: agents/$ag"
        exit 1
    fi
done

# 5. Check assets
if [ -f "$SKILL_DIR/assets/small-logo.svg" ] && [ -f "$SKILL_DIR/assets/large-logo.svg" ]; then
    echo "✓ Brand logos found (small and large SVG)"
else
    echo "ERROR: Missing brand logo SVGs in assets/"
    exit 1
fi

# 6. Check templates and evals
if [ -f "$SKILL_DIR/templates/plan-template.md" ] && [ -f "$SKILL_DIR/evals/eval-suite.yaml" ]; then
    echo "✓ Templates and Eval suite found"
else
    echo "ERROR: Missing templates or evals"
    exit 1
fi

echo "=== PASS: All improve Skill package assertions verified ==="
