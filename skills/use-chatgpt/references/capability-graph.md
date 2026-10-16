# Capability Graph & Routing Matrix

The canonical capability graph maps installed plugins, skills, and tools to distinct lifecycle stages, ensuring clear boundaries and zero duplicate ownership.

---

## 1. Primary Owner & Overlap Rule

```text
ONE PRIMARY OWNER
+ ZERO OR MORE SPECIALIST INPUTS
+ ONE INDEPENDENT VERIFICATION PATH
+ ONE LANDING OWNER
```

### 1.1 Orchestrator Selection
- `@get-fable`: When lifecycle state and evidence precedence determine the next engineering phase.
- `@Riqor`: When coordinating a broad senior agency-style specialist roster.
- `@ZzzOps`: When work already lives as durable ZzzOps goals.
- `@taskplane`: When the project requires formal stage-gated requirements, design, build, and engineering sign-offs.
- `@gstack Workflows`: When a single modular workflow (ship, review, retro, qa) directly matches the job.
- `@Superpowers`: Process discipline (TDD, systematic debugging, worktrees) inside the selected mission.

*Rule: Never appoint multiple orchestrators as co-directors. Pick one primary lifecycle owner.*

---

## 2. Canonical Routing Table

| Capability | Primary Job | Enter When | Write Authority | Typical Continuation | Do Not Substitute For |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `@GitHub` | Source of truth & remote mutations | Issues, PRs, CI, branches, repo files in scope | Yes (scoped to action) | local execution / review | Local runtime behavior |
| `@Codex Engineering Guardrails` | Bounded code-work or read-only verification | Scope discipline or independent audit needed | `code-work` (yes); `code-verification` (no) | CodeRabbit / tests | Product requirements discovery |
| `@Codex Process Jobs` | Finite local process runner | Local jobs (tests, builds, benchmarks) exceeding ~60s | Process effects only | verify / repair | Persistent servers or coding agent |
| `@Fallow Code Analysis` | Graph static analysis | TS/JS changed-code blast radius, complexity, boundaries | Read-only | targeted repair | Runtime correctness proof |
| `@CodeRabbit` | Independent AI review | Meaningful diff exists | Reviewer surface | triage / reverify | Unit tests or CI |
| `@PR Readiness Check` | Readiness judgment on supplied packet | Evidence packet already compiled | Read-only | PR Completion | Live repository inspection |
| `@PR Completion` | PR lifecycle & landing | PR exists and landing ownership is in scope | Yes (commits/push/merge) | merge / closed | Broad pre-authorization of unknown heads |
| `@Codex Security` | Security review | Auth, secrets, trust boundaries, public APIs changed | Read-only | security tests | General code review |
| `@Context7` | Current library docs | Version-sensitive external contracts in question | Read-only | implementation | Web search or code truth |
| `@Impeccable` | Frontend UX & UI polish | UI interaction, responsive states, accessibility | Bounded UI files | runtime QA | Backend engineering |
| `@Testifly` | Browser E2E testing | Real browser rendering and E2E validation | Read-only | bug repair | Unit/integration tests |

---

## 3. Capability Availability States

Every capability is assigned one of six states:

```text
CALLABLE
Current tool or Skill contract is visible and callable in the current host session.

CONNECTED
An authenticated connector is active for the current account/workspace.

INSTALLED_BUT_NOT_CALLABLE_HERE
Plugin is installed in the ChatGPT/Codex environment, but not exposed in the current session.

KNOWN_NAME_UNRESOLVED
Name referenced by prompt, but no canonical contract is currently resolved.

UNAVAILABLE
The integration explicitly reports that it cannot execute.

BLOCKED
Capability exists but is constrained by rate limits, billing, or lack of permissions.
```

### Block Reasons:
- `review_rate_limited`
- `billing_blocked`
- `auth_missing`
- `device_offline`
- `permission_denied`

---

## 4. Unresolved Names Policy

The following names have been historically referenced in prompts but lack exact canonical plugin contracts:
- `Codex Dev Workflows`
- `Code`
- `Codex Coordinator`
- `Codex Advisor`

**Policy**:
1. Do not delete them from user prompts if meaningful to user intent.
2. Search installed catalogs to see if they resolve to an active tool.
3. If unresolvable, classify as `KNOWN_NAME_UNRESOLVED` and proceed with verified callable tools. Never invent fabricated tools or outputs for them.
