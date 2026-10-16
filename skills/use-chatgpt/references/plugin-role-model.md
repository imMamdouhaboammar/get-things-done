# Plugin Role Model

Use plugins and tools by explicit role, not by popularity. A plugin must have a distinct job inside the workflow.

---

## 1. Role Taxonomy

### 1.1 Source of Truth / Connected State
Use when the answer depends on live external state.
- `@GitHub`: Remote repository state, branches, files, PRs, issues, CI evidence, review threads.
- `@Remote Desktop Commander`: Authorized local machine, local repository, filesystem, terminal, runtime execution.
- `@Supabase`: Live Supabase projects, schema, SQL, RLS, functions, logs, advisors.
- `@Vercel`: Live projects, deployments, build/runtime state.
- `@Gmail` / `@Hostinger Mail`: Mailbox messages, threads, drafts, email actions.
- `@Google Drive` / `@Notion` / `@GitBook`: Source documents, workspace pages, knowledge bases, published docs.
- `@Hugging Face`: Models, datasets, Spaces, metadata.

*Rule: When live connected state exists, inspect it before reasoning from memory or stale context.*

---

### 1.2 Current Documentation / External Research
Use research plugins to remove uncertainty, not as decorative filler.
- `@Context7`: Current framework/library documentation and version-specific implementation contracts.
- `@Parallel Search`: Broad current web research and multi-source discovery.
- `@Tavily AI`: Targeted web search, deep extraction, crawling, and source retrieval.
- `@Deep Research`: Multi-source synthesis where conflicting evidence matters.

---

### 1.3 Planning / Orchestration / Long-Running State
Planning plugins do not replace execution evidence.
- `@Superpowers`: Engineering process discipline: planning, systematic debugging, TDD, worktrees, verification-before-completion.
- `@get-fable`: Repository lifecycle routing across discovery, research, planning, TDD, execution, verification, review, recovery, and handoff.
- `@Adaptive Codex Orchestrator`: Use only when parallel subtasks have disjoint ownership.
- `@AI Task Brief Builder`: Analyzes supplied materials into evidence-backed goals, scope, tests, and risks (does not crawl repos or run tests).
- `@taskplane`: Governed product/design/build/engineering workflow with formal stage gates.
- `@Create State`: Persists durable project decisions and cross-session continuation state.
- `@Codex Process Jobs`: Runs ordinary finite local workloads (tests, builds, benchmarks) that exceed ~60 seconds.

---

### 1.4 Engineering Execution
Only one plugin or CLI owns a write surface at a time.
- `@Remote Desktop Commander` / Local CLI: Primary executor for local code, shell, tests, builds, and runtime checks.
- `@GitHub`: Remote repository writes, branches, PR/issue creation, comments.
- `@Supabase`: Database migrations, SQL execution, RLS policies, Edge functions.
- `@Vercel`: Production/preview deployment triggers and environment configuration.
- `@Build Web Apps`: Frontend implementation and application scaffolding.
- `@FastAPI Cloud` / `@3Min API`: Rapid API backend creation and deployment.
- `@Temporal`: Durable workflow execution, distributed state, retries, and saga patterns.
- `@Remotion` / `@Canva` / `@Mermaid Chart`: Programmatic video, visual design, and diagram generation.

---

### 1.5 Code Review / Quality / Readiness
A reviewer can identify risk but cannot manufacture verification proof.
- `@CodeRabbit`: Independent code review after a meaningful diff exists (local CLI or GitHub PR integration).
- `@Codex Engineering Guardrails`:
  - `code-work`: Scope-bounded implementation with test-backed slices.
  - `code-verification`: Independent read-only review, diagnosis, testing, and evidence-based verdicts.
- `@Fallow Code Analysis`: Graph-grounded static analysis for blast radius, changed-code risk, duplication, complexity, and boundaries.
- `@SonarQube`: Static quality, security, coverage, duplication, and quality gates.
- `@PR Readiness Check`: Analyzes concrete PR materials supplied to it (does not inspect live repos or run tests).
- `@PR Completion`: Shepherds a real PR through commits, push, CI, review threads, conflicts, and landing.

---

### 1.6 Security
Inspect changed trust boundaries, not generic noise.
- `@Codex Security`: Security-focused code and architecture review.
- `@ArmorCodex`: Agent/tool policy, credential boundaries, and security control audit.
- `@SonarQube`: Static vulnerability and taint analysis findings.

---

### 1.7 Runtime QA / UX Verification
Runtime QA verifies user-visible behavior. It does not replace unit/integration tests.
- `@Testifly`: Browser/E2E website testing and runtime validation.
- `@Impeccable`: UI quality, interaction states, responsive layouts, accessibility, hierarchy, visual polish.
- `@Agent Ready`: Agent readability, crawlability, `llms.txt`, and machine-consumption quality.
- `@Test Android Apps`: Android emulator QA, UI inspection, logs, and screenshots.

---

### 1.8 Marketing / Content / Creative
- `@Marketing Council`: Strategic marketing reasoning and challenge.
- `@Marketing Swarm`: Multi-angle parallel marketing analysis.
- `@Slop Curator`: Removes generic AI phrasing, fluff, repetition, and artificial formatting.
- `@AI Humanizer`: Naturalizes copy while preserving core meaning.
- `@Designly` / `@Presentations` / `@Canva`: Visual concepts, pitch decks, and presentations.

---

### 1.9 Plugin / Skill Engineering
- `@OpenAI Developers`: Current OpenAI developer workflows (Agents SDK, ChatGPT Apps SDK).
- `@Plugin Autopilot`: Workflow discovery, Skill compilation, packaging, and directory metadata.
- `@Plugin Eval`: Skill/plugin evaluation and gap analysis.
- `@Universal Plugin Installer`: Adapts and reviews local candidate skill folders.
- `@Skill Submission Pack Writer`: Generates evidence-bound submission packs for Skills-only plugins.
- `@Matt Skills Curated` / `@Skillquiver`: Engineering discipline, prompt contracts, and specialist skills.

---

### 1.10 Conditional Specialists
Do NOT auto-route these purely from their name unless explicitly requested or verified callable:
`@AgentProof`, `@CompText Guard`, `@Develoop`, `@gstack Workflows`, `@Keystone`, `@OGENIC GOD TOOLKIT`, `@pipeboard`, `@PrePilot Lite`, `@prepilot Working`, `@pstack`, `@Riqor`, `@Shiro`, `@Template Creator`, `@ZzzOps`.
