> **Sample output.** A real plan produced by `/improve` against
> [shadcn/ui](https://github.com/shadcn-ui/ui) at commit `1994caba0`
> (2026-06-10), kept here as an example of the format. The codebase has
> moved on — don't execute this; run `/improve` on your own repo instead.

# Plan 001: Extract shared shadow-config resolution used by search and view

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat 1994caba0..HEAD -- packages/shadcn/src/commands/search.ts packages/shadcn/src/commands/view.ts packages/shadcn/src/registry/config.ts`
> If any of these changed since this plan was written, compare the
> "Current state" excerpts against the live code before proceeding; on a
> mismatch, treat it as a STOP condition.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: MED
- **Depends on**: none
- **Category**: tech-debt
- **Planned at**: commit `1994caba0`, 2026-06-10

## Why this matters

`search.ts` and `view.ts` each hand-roll the same "shadow config" fallback —
build a default config, overlay a partial `components.json` if present, then
try the full `getConfig()` and fall back on failure. The duplication is
acknowledged in-code (`search.ts:31`: "TODO: We're duplicating logic for
shadowConfig here. Revisit and properly abstract this."), and the two copies
have **already drifted**: search seeds its defaults with
`createConfig({style: "new-york", resolvedPaths: {cwd}})` while view starts
from bare `configWithDefaults({})`. Any future change to partial-config
handling (new defaults, validation rules) must currently be made twice and
can silently diverge.

## Current state

- `packages/shadcn/src/commands/search.ts` — search/list command; shadow-config block at ~91–115:

```ts
// search.ts ~91 (after `await loadEnvFiles(options.cwd)`)
// Start with a shadow config to support partial components.json.
// Use createConfig to get proper default paths
const defaultConfig = createConfig({
  style: "new-york",
  resolvedPaths: {
    cwd: options.cwd,
  },
})
let shadowConfig = configWithDefaults(defaultConfig)

// Check if there's a components.json file (partial or complete).
const componentsJsonPath = path.resolve(options.cwd, "components.json")
const hasComponentsJson = fsExtra.existsSync(componentsJsonPath)
if (hasComponentsJson) {
  const existingConfig = await fsExtra.readJson(componentsJsonPath)
  const partialConfig = rawConfigSchema.partial().parse(existingConfig)
  shadowConfig = configWithDefaults({
    ...defaultConfig,
    ...partialConfig,
  })
}

// Try to get the full config, but fall back to shadow config if it fails.
let config = shadowConfig
try {
  const fullConfig = await getConfig(options.cwd)
  if (fullConfig) {
    config = configWithDefaults(fullConfig)
  }
} catch {
  // Use shadow config if getConfig fails (partial components.json).
}
```

- `packages/shadcn/src/commands/view.ts` — view command; same pattern at ~36–55, but seeded from `configWithDefaults({})` (no style/cwd seed — this is the drift).
- `packages/shadcn/src/registry/config.ts:20` — `configWithDefaults(config?: DeepPartial<Config>)`, the natural home for the shared helper. Has colocated tests in `packages/shadcn/src/registry/config.test.ts` — use those as the test pattern.
- Conventions: TypeScript ESM, `@/src/...` import aliases, zod schemas from `@/src/schema`, colocated `*.test.ts` vitest files. Match `registry/config.ts` style.

## Commands you will need

| Purpose   | Command                          | Expected on success |
|-----------|----------------------------------|---------------------|
| Install   | `pnpm install`                   | exit 0              |
| Tests     | `pnpm shadcn:test`               | all pass            |
| Lint+types| `pnpm check`                     | exit 0              |

Run from the repo root.

## Scope

**In scope** (the only files you should modify):
- `packages/shadcn/src/registry/config.ts` (add the shared helper)
- `packages/shadcn/src/registry/config.test.ts` (tests for it)
- `packages/shadcn/src/commands/search.ts` (use it)
- `packages/shadcn/src/commands/view.ts` (use it)

**Out of scope** (do NOT touch, even though they look related):
- `packages/shadcn/src/commands/init.ts` — builds config via prompts, not the shadow pattern; no duplication there.
- `packages/shadcn/src/utils/get-config.ts` — `getConfig`/`createConfig` stay as-is; the helper composes them.
- Any behavior change to how a *complete* `components.json` is resolved — both commands must behave identically to today when a full config exists.

## Git workflow

- Branch: `advisor/001-extract-shadow-config-resolution`
- Commit per step; messages follow the repo's conventional style (e.g. `refactor(cli): extract shadow-config resolution` — see `git log` for examples like `feat(cli): improve search command`).
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Add `resolveShadowConfig` to `registry/config.ts`

Add an exported async function:

```ts
export async function resolveShadowConfig(
  cwd: string,
  seed?: DeepPartial<Config>
): Promise<Config>
```

Behavior (extracted from search.ts above): build `configWithDefaults(createConfig({...seed, resolvedPaths: {cwd}}))`; if `components.json` exists at `cwd`, partial-parse it with `rawConfigSchema.partial()` and overlay; then try `getConfig(cwd)` and, when it returns a config, use `configWithDefaults(fullConfig)`; on throw, keep the shadow config. The `seed` parameter preserves search's `{style: "new-york"}` seeding.

Add tests in `config.test.ts` (model after the existing tests there): no components.json → defaults; partial components.json → overlay; full components.json → getConfig path; malformed full config → falls back to shadow.

**Verify**: `pnpm shadcn:test` → all pass, including the 4 new tests.

### Step 2: Switch `search.ts` to the helper

Replace the block at ~91–115 with a call to `resolveShadowConfig(options.cwd, { style: "new-york" })`. Remove now-unused imports (`createConfig`, `rawConfigSchema`, `fsExtra`/`path` if no longer used elsewhere in the file).

**Verify**: `pnpm shadcn:test` → pass; `pnpm check` → exit 0.

### Step 3: Switch `view.ts` to the helper

Replace the block at ~36–55 with `resolveShadowConfig(options.cwd)` (no seed — preserves its current bare-defaults behavior). Clean up unused imports.

**Verify**: `pnpm shadcn:test` → pass; `pnpm check` → exit 0; `grep -rn "shadow config" packages/shadcn/src/commands/` → no matches.

## Test plan

- 4 new unit tests on `resolveShadowConfig` (Step 1), in `registry/config.test.ts`, modeled on the existing tests in that file.
- Existing command tests must stay green: `pnpm shadcn:test`.
- This plan adds no integration tests; the two commands' behavior is unchanged by construction (same logic, one home).

## Done criteria

- [ ] `pnpm shadcn:test` exits 0; 4 new tests for `resolveShadowConfig` exist and pass
- [ ] `pnpm check` exits 0
- [ ] `grep -rn "TODO: We're duplicating logic for shadowConfig" packages/shadcn/src/` returns no matches (comment removed with the duplication)
- [ ] Both `search.ts` and `view.ts` call `resolveShadowConfig`; neither contains an inline shadow-config block
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `plans/README.md` status row updated

## STOP conditions

Stop and report back (do not improvise) if:

- The code at the locations above doesn't match the excerpts (drift since `1994caba0`).
- The seeding difference between search (`style: "new-york"`, cwd resolved paths) and view (bare defaults) turns out to be load-bearing in a way the `seed` parameter can't express — i.e. tests fail unless the helper grows command-specific branches.
- Removing the block from either command requires touching files outside the in-scope list.

## Maintenance notes

- Future commands needing partial-config support should call `resolveShadowConfig`, not copy the pattern — reviewers should reject new inline shadow-config blocks.
- If `init.ts` ever gains partial-config resumption, it should also use this helper; that's deferred (out of scope here) because init's prompt-driven flow has different semantics.
- Reviewer focus: confirm view's behavior is byte-identical for the no-seed path — the drift between the two copies was likely unintentional, but if view *depended* on bare defaults, the no-seed call preserves that.
