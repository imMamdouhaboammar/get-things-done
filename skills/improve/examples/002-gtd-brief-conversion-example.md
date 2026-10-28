# Example 002: Improve Plan to GTD Execution Brief Conversion

This example demonstrates how a self-contained implementation plan authored by `improve` translates directly into a GTD Execution Brief v2.0 with full verification evidence and workstreams.

## Source Improve Plan: `plans/001-extract-shadow-config.md`

```markdown
# Plan 001: Extract shadow config resolution from build pipeline

## Status
- Priority: P1
- Effort: S
- Risk: LOW
- Category: tech-debt
- Planned at: commit `533f441`, 2026-10-28

## Why this matters
The shadow config resolution logic is currently duplicated across the build runner and CLI adapter. Consolidating into a single resolver eliminates config drift between environments.

## Current state
- `src/config/shadow.ts` — contains duplicate resolution logic (lines 40-75).

## Commands you will need
| Purpose | Command | Expected on success |
|---|---|---|
| Tests | `bun test` | all pass |
| Typecheck | `bun run typecheck` | exit 0 |

## Scope
**In scope**: `src/config/shadow.ts`, `src/config/resolver.ts`
**Out of scope**: `src/legacy/config.ts`

## Steps
### Step 1: Create canonical resolver
Extract resolution into `src/config/resolver.ts`.
Verify: `bun test test/config_test.ts` -> all pass

## Done criteria
- [ ] `bun run typecheck` exits 0
- [ ] `bun test` exits 0; all pass
- [ ] No files outside in-scope modified
```

---

## Resulting GTD Execution Brief v2.0 (`brief.json`)

```json
{
  "version": "2.0",
  "title": "Extract shadow config resolution from build pipeline",
  "domain": "software",
  "intent": {
    "problem": "The shadow config resolution logic is currently duplicated across the build runner and CLI adapter.",
    "desired_outcome": "Consolidating into a single resolver eliminates config drift between environments.",
    "actor": "executor-agent"
  },
  "status": "ready",
  "scope": {
    "in": ["src/config/shadow.ts", "src/config/resolver.ts"],
    "out": ["src/legacy/config.ts"],
    "constraints": ["Follow repo Result error handling pattern", "Zero mutating commands outside worktree"]
  },
  "knowledge": {
    "facts": [
      "src/config/shadow.ts contains duplicate resolution logic (lines 40-75)",
      "Planned at commit 533f441"
    ],
    "assumptions": [],
    "unknowns": []
  },
  "decisions": [
    {
      "decision": "Extract resolution into src/config/resolver.ts",
      "rationale": "Single source of truth for build runner and CLI",
      "reversible": true
    }
  ],
  "open_decisions": [],
  "workstreams": [
    {
      "name": "Step 1: Create canonical resolver",
      "outcome": "Resolution logic extracted into src/config/resolver.ts",
      "dependencies": []
    }
  ],
  "deliverables": [
    "src/config/resolver.ts",
    "Passing test suite"
  ],
  "risks": [
    "LOW: Minor risk of breaking legacy consumer if interface signature changes"
  ],
  "verification": {
    "success_criteria": [
      "bun run typecheck exits 0",
      "bun test exits 0; all pass",
      "No files outside in-scope modified"
    ],
    "evidence": [
      "Level A: bun run typecheck exit 0",
      "Level A: bun test exit 0"
    ]
  },
  "next_action": "Execute Step 1: Create canonical resolver",
  "blockers": []
}
```
