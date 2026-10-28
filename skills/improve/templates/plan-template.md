# Plan NNN: <Imperative title — what will be true after this plan>

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md` — unless a reviewer dispatched you and told you they
> maintain the index.
>
> **Drift check (run first)**: `git diff --stat <planned-at SHA>..HEAD -- <in-scope paths>`
> If any in-scope file changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P1 | P2 | P3
- **Effort**: S | M | L
- **Risk**: LOW | MED | HIGH
- **Depends on**: plans/NNN-*.md (or "none")
- **Category**: bug | security | perf | tests | tech-debt | migration | dx | docs | direction
- **Planned at**: commit `<short SHA>`, <YYYY-MM-DD>
- **Issue**: <GitHub issue URL — only when published via `--issues`; omit otherwise>

## Why this matters

2–5 sentences. The problem, its concrete cost, and what improves when this lands.

## Current state

- Relevant files and roles:
  - `path/file.ts` — role
- Code excerpts with `file:line` markers.
- Relevant repo conventions and pointer to exemplar file.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Install | `pnpm install` | exit 0 |
| Typecheck | `pnpm typecheck` | exit 0, no errors |
| Tests | `pnpm test` | all pass |
| Lint | `pnpm lint` | exit 0 |

## Scope

**In scope**:
- `path/file.ts`

**Out of scope**:
- `path/legacy.ts`

## Git workflow

- Branch: `advisor/NNN-<slug>`
- Commit: conventional commits matching repo style
- Do NOT push or open a PR unless instructed

## Steps

### Step 1: <imperative title>

What to do, precisely.

**Verify**: `<command>` → <expected output>

## Test plan

- Tests to write, where, covering which cases.
- Verification command and expected pass output.

## Done criteria

- [ ] `pnpm typecheck` exits 0
- [ ] `pnpm test` exits 0; all tests pass
- [ ] No files outside in-scope list modified
- [ ] `plans/README.md` status row updated

## STOP conditions

- Code at "Current state" does not match live code.
- Verification fails twice after reasonable fix attempt.
- Change requires touching an out-of-scope file.

## Maintenance notes

- Future interactions to consider.
- Review focal points.
