---
name: rea
description: >
  Use when users ask to /rea; reverse engineer native binaries, Electron/JavaScript apps,
  Android packages, .NET assemblies, firmware, network captures, and crashes using the REA
  framework with verifiable evidence; understand how this feature works in the binary, show
  evidence, and reconstruct it; or analyze an Electron ASAR or JavaScript bundle. Do NOT
  use for review this git pull request diff for code quality; run playwright browser smoke
  tests on my web app.
metadata:
  version: "1.0.0"
  author: "Antigravity & REA"
---


# REA: Reverse Engineer Anything

Reverse engineer compiled native binaries, Electron/JavaScript applications, Android packages, .NET assemblies, firmware, network captures, and crashes with verifiable evidence ledgers.

---

## 1. Quick Start by Target Type

Before invoking tools, identify the target type and follow its dedicated pathway:

### A. Electron & JavaScript Applications (ASAR / `.js` bundles)
* **Engine Required**: None (pure AST & static analysis).
* **MCP Tool**: `analyze_javascript_application` with `{ "target": "/path/to/app.asar" }`.
* **Deep Tracing**: `trace_application_feature` or `trace_javascript_semantics`.
* **CLI Fallback**:
  ```bash
  rea analyze-javascript-application /path/to/app.asar --json
  ```

### B. Native Binaries (Mach-O, ELF, Windows PE)
* **Session Binding**: Active target requires binding first.
* **MCP Sequence**:
  1. `open_binary` with `{ "binary_path": "/path/to/executable" }`.
  2. `binary_overview` or `search_procedures` / `search_strings` to locate candidate seeds.
  3. `analyze_function` with `{ "procedure_name": "targetSymbol" }` or `{ "address": "0x1000..." }`.
  4. `xrefs` to inspect inbound call sites and reference flows.
* **CLI Fallback**:
  ```bash
  rea open-binary /path/to/executable
  rea function /path/to/executable --target "targetSymbol" --json
  ```

### C. Android APKs
* **Engine Required**: JADX / Java runtime.
* **MCP Sequence**:
  1. `inspect_android_package` with `{ "apk_path": "/path/to/app.apk" }`.
  2. `search_android_classes` &rarr; `inspect_android_class` &rarr; `inspect_android_method`.
* **CLI Fallback**:
  ```bash
  rea inspect-android-package /path/to/app.apk --json
  ```

### D. Web Network & API Captures
* **Formats**: `.har` archives, mitmproxy flows.
* **MCP Tool**: `inspect_web_network_capture` with `{ "capture_path": "/path/to/traffic.har" }`.

---

## 2. Invariants & Rules

1. **Evidence-First Invariant**:
   - Never speculate or hallucinate functionality. Every claim must cite concrete REA Evidence (artifact SHA-256 digest, virtual address offset, or demangled symbol).
2. **Summary-First Pattern**:
   - Start broad with overview tools (`binary_overview`, `inspect_artifact`, `search_procedures`). Never dump unconstrained raw byte ranges or hundreds of disassembly lines into context.
3. **Graceful Engine Fallback**:
   - If a deep disassembler (Hopper / Ghidra / IDA) is not installed on the system, do not crash or stall. Fall back to static offline layout tools (`inspect_binary_layout`, `inspect_macho`, `inspect_plist`) or JavaScript AST tools.
4. **Bun-Native Execution**:
   - When executing CLI commands or scripts, always use the global `rea` binary or `bunx rea-agents`. Never invoke npm or Yarn.

---

## 3. Evidence Ledger & Feature Reconstruction

When asked to "reconstruct" or "build a version of" a feature found in a target app:

1. **Extract Core Logic**:
   - Locate the decompiled pseudocode or JS AST representation.
2. **Translate to Clean-Room Code**:
   - Convert compiler artifacts, mangled registers, and unrolled loops into clean, modern TypeScript or Rust.
3. **Attach Attribution & Evidence Ledger**:
   - Include a top-of-file header linking the implementation back to verified binary evidence:
   ```typescript
   /**
    * Feature Reconstruction: [Feature Name]
    * Reverse-Engineered from: [Target Binary / App Name]
    * Evidence Digest: sha256:1a82f...
    * Binary Location: 0x100004f20 (Method: SecurityManager.verifyToken)
    */
   ```
4. **Document Unknowns**:
   - Explicitly list external API dependencies or opaque cryptographic secrets that require runtime environment keys.

---

## 4. Reference Documentation & Examples

- [`references/target-routing.md`](references/target-routing.md) &mdash; Complete tool mapping for all 138 REA capabilities.
- [`references/cli-recipes.md`](references/cli-recipes.md) &mdash; Shell recipes for CLI reverse engineering.
- [`references/evidence-contract.md`](references/evidence-contract.md) &mdash; The JSON Evidence schema and reconstruction rules.
- [`references/host-notes.md`](references/host-notes.md) &mdash; Multi-host compatibility instructions.
- [`examples/electron-feature-reconstruction.md`](examples/electron-feature-reconstruction.md) &mdash; Walkthrough of ASAR deconstruction and clean-room implementation.
- [`examples/native-binary-evidence.md`](examples/native-binary-evidence.md) &mdash; Native Mach-O function tracing and evidence ledgers.

---

## 5. Integration with GTD Execution Briefs

REA outputs translate cleanly into GTD Execution Briefs:

* **Facts (`knowledge.facts`)**: Validated binary architecture, entrypoint addresses, observed system calls, and cryptographic digests.
* **Unknowns (`knowledge.unknowns`)**: Server-side APIs, encrypted payload formats, or runtime keys not present in the static artifact.
* **Deliverables (`deliverables`)**: Clean-room reconstructions, TypeScript/Rust replacements, and de-obfuscated algorithm implementations.
* **Verification Evidence (`verification.evidence`)**: Disassembly address citations, AST node traces, and Level A deterministic test suites certifying reconstruction accuracy.

