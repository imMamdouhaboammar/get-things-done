#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Validating use-chatgpt Skill Package ==="
echo "Skill directory: $SKILL_DIR"

# 1. Check SKILL.md exists and size
if [ ! -f "$SKILL_DIR/SKILL.md" ]; then
    echo "ERROR: SKILL.md not found!"
    exit 1
fi

LINE_COUNT=$(wc -l < "$SKILL_DIR/SKILL.md")
echo "✓ SKILL.md found ($LINE_COUNT lines, limit 500)"
if [ "$LINE_COUNT" -gt 500 ]; then
    echo "WARNING: SKILL.md exceeds 500 lines ($LINE_COUNT lines)!"
fi

# 2. Check frontmatter
if head -n 1 "$SKILL_DIR/SKILL.md" | grep -q "^---"; then
    echo "✓ YAML frontmatter opening present"
else
    echo "ERROR: SKILL.md missing frontmatter opening!"
    exit 1
fi

# 3. Check references directory
REFS=(
    "operating-contract.md"
    "plugin-role-model.md"
    "execution-surfaces.md"
    "open-pr-bot-gate.md"
    "evidence-trust-ladder.md"
    "capability-graph.md"
    "workflow-state-machine.md"
    "agentic-recipes.md"
    "prompt-contracts.md"
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
AGENTS=("openai.md" "claude.md" "antigravity.md" "cursor.md")
for agent in "${AGENTS[@]}"; do
    if [ -f "$SKILL_DIR/agents/$agent" ]; then
        echo "✓ Agent adapter found: agents/$agent"
    else
        echo "ERROR: Missing agent adapter: agents/$agent"
        exit 1
    fi
done

# 5. Check templates directory
TEMPLATES=("routing-packet.yaml" "evidence-ledger.md" "prompt-contract.yaml" "agentic-mission-skeleton.md")
for tmpl in "${TEMPLATES[@]}"; do
    if [ -f "$SKILL_DIR/templates/$tmpl" ]; then
        echo "✓ Template found: templates/$tmpl"
    else
        echo "ERROR: Missing template: templates/$tmpl"
        exit 1
    fi
done

echo "=== All use-chatgpt Skill Package checks passed successfully! ==="
