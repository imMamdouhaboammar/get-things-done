# Fable Architecture: Ultra-Connected Use-ChatGPT Integration

## 1. Architectural Inception & 3-Vector Evaluation

In accordance with `/fable-architecture` governance, the integration of `use-chatgpt` into the Get Things Done (GTD) ecosystem was evaluated across three discrete vectors prior to implementation:

| Evaluation Vector | Score (0-10) | Observable Rationale |
|---|---|---|
| **Scale & Load** | **7.5** | High-throughput sub-millisecond intent routing across large multi-specialist capability graphs; continuous streaming parsing of multi-author PR review threads. |
| **Domain Decoupling** | **8.5** | Complete orthogonal separation between **GTD Work Modeling / Execution Brief Lifecycle** (Python) and **High-Performance Intent Classification / Bot Fencing / macOS Native Subsystem** (Rust). |
| **Resource Intensity** | **7.0** | Workload heterogeneity: Heavy CPU-bound compiled regex DAG evaluation, binary checksumming, and native OS interop in Rust vs. I/O-bound human-agent brief editing and multi-adapter registry synthesis in Python. |
| **Composite Score** | **7.78** | $(0.35 \times 7.5) + (0.40 \times 8.5) + (0.25 \times 7.0) = 7.775 \ge 6.0$ |

### Architectural Verdict
- **Verdict**: `microservices` (Decoupled Polyglot Modules)
- **Monolith Scaffolding**: `allowMonolith: false` (Hard lockout enforced)
- **Manifest**: Serialized in `microservices_manifest.toon`

---

## 2. Situation Classification & Stack Assignment

| Service Name | Situation Category | Technology Stack | Core Competency | Primary Responsibilities |
|---|---|---|---|---|
| `gtd-orchestrator` | **Category D / B** | Python 3.10+ (GTD CLI) | Workstream Lifecycle & Contract Orchestrator | Execution Brief schemas, Definition of Ready/Done, Knowledge Ledger, domain pack inheritance. |
| `use-chatgpt-engine` | **Category C** | Pure Rust 1.80+ (`chatgpt-skill`) | High-Performance Computational Kernel | Intent routing precedence DAG, Bot Gate Fencer (`BOT != NOISE, BOT != TRUTH`), Evidence Trust Ladder, macOS CLI integration. |

---

## 3. Communication Standards & Dual-Transport Contract

```
       +-------------------------------------------------------+
       |   North-South Ingress (User / AI Agent / Skills CLI)  |
       |      Agent Skills Markdown + Execution Brief JSON     |
       +-------------------------------------------------------+
                                   |
                                   v
       +-------------------------------------------------------+
       |       gtd-orchestrator (Python Category B/D)          |
       |     skills/get-things-done/scripts/gtd.py             |
       +-------------------------------------------------------+
                                   |
        East-West Typed IPC Bridge | (proto/gtd_chatgpt_bridge.proto)
        Structured Subprocess JSON | Stdio IPC with exit code semantics
                                   v
       +-------------------------------------------------------+
       |      use-chatgpt-engine (Pure Rust Category C)        |
       |        crates/use-chatgpt-engine/src/main.rs          |
       +-------------------------------------------------------+
           |                 |                     |
           v                 v                     v
   [Router Precedence]  [Bot Gate Fencer]   [macOS System CLI]
   (Classifier & DAG)   (Noise vs Blocker)  (pbcopy, osascript)
```

### North-South Contract
- Human and AI agents interact via standard CLI commands (`gtd doctor`, `gtd new-brief`, `gtd chatgpt-route`, `gtd bot-gate`, `gtd evidence-ladder`) and standardized Agent Skills metadata (`SKILL.md`).

### East-West Contract
- Defined via `proto/gtd_chatgpt_bridge.proto`.
- Executed via `skills/get-things-done/scripts/chatgpt_bridge.py`.
- Subprocess transport guarantees zero runtime Python C-extensions, fully isolated memory boundaries, and fail-safe graceful degradation.

---

## 4. Ultra-Connected Features

### 1. Intent Routing & Brief Hydration (`gtd chatgpt-route`)
```bash
python scripts/gtd.py chatgpt-route "refactor auth token verification" --into-brief brief.json
```
- Runs the Rust DAG classifier.
- Automatically maps specialists to `workstreams`.
- Seeds `verification.success_criteria` and `verification.evidence` with Evidence Trust Ladder levels.
- Records routing telemetry under `domain_data.chatgpt_routing`.

### 2. Open-PR Bot Gate Fencing (`gtd bot-gate`)
```bash
python scripts/gtd.py bot-gate --into-brief brief.json
```
- Enforces the invariant: **BOT != NOISE, BOT != TRUTH**.
- Flags actionable comments against the current git HEAD as blocking items in `brief.blockers`.
- Downgrades comments on older commits to non-blocking facts in `knowledge.facts` (`STALE_AFTER_NEW_HEAD`).
- Flags automated formatting patches as resolved facts (`ALREADY_FIXED`).

### 3. Evidence Trust Ladder (`gtd evidence-ladder`)
```bash
python scripts/gtd.py evidence-ladder brief.json --into-brief
```
- Grades verification items into 5 strict tiers:
  - **Level A**: Deterministic Machine Proof (automated tests, compiler output, checksums)
  - **Level B**: Integration / Runtime Proof (live endpoint, e2e browser test)
  - **Level C**: Observed Runtime / CLI Output (terminal logs, command traces)
  - **Level D**: Static Inspection (code review, schema inspection)
  - **Level E**: Unverified Assertion ("looks good", "should work")
- Definition of Done requires at least Level C, with Level A/B preferred for production promotion.

### 4. macOS Subsystem Bridge (`gtd macos`)
```bash
python scripts/gtd.py macos --copy "Brief content"
python scripts/gtd.py macos --paste
python scripts/gtd.py macos --notify "Task completed" --title "GTD"
```
- Direct native macOS integration for clipboard and Notification Center alerts.
