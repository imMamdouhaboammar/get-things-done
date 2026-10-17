# REA: Reverse Engineer Anything

The `rea` skill provides verifiable reverse engineering and clean-room reconstruction capabilities across native binaries, Electron ASAR and JavaScript bundles, Android APKs, .NET assemblies, firmware images, and network traffic captures.

---

## 1. Role within Get Things Done

In GTD workflows, understanding an existing compiled or obfuscated system is often required before planning or implementing a change. `rea` ensures this investigation is grounded in **verifiable physical evidence** rather than speculative hallucination:

| GTD Component | REA Contribution |
|---|---|
| **Facts (`knowledge.facts`)** | Target artifact SHA-256 digests, section addresses, symbol demangled signatures, and system call boundaries. |
| **Unknowns (`knowledge.unknowns`)** | Remote API dependencies, cryptographic secret keys, and runtime-dependent behaviors not present in static code. |
| **Deliverables (`deliverables`)** | Clean-room TypeScript, Rust, or Go implementations reconstructed from decompiled or AST evidence. |
| **Verification (`verification.evidence`)** | Exact byte offsets, virtual address citations, and Level A deterministic test proofs. |

---

## 2. Supported Target Pathways

| Target | Entrypoint Tool | Decompilation Engine | Fallback Mode |
|---|---|---|---|
| **Electron & JavaScript** | `analyze_javascript_application` | None (pure AST & static analysis) | `rea analyze-javascript-application <path> --json` |
| **Native (Mach-O, ELF, PE)** | `open_binary` | Hopper, Ghidra, or IDA | `rea inspect-binary-layout <path>` (layout & headers) |
| **Android APK** | `inspect_android_package` | JADX / Java runtime | `rea inspect-android-package <path>` |
| **Managed .NET** | `inspect_managed_artifact` | Metadata reader | `rea inspect-managed-artifact <dll>` |
| **Firmware Images** | `inspect_firmware_regions` | Binwalk / Unblob | `rea inspect-firmware-regions <bin>` |
| **Web & Network Captures** | `inspect_web_network_capture` | HAR parser | `rea inspect-web-network-capture <har>` |

---

## 3. Evidence-First Invariant

Every claim generated under `rea` must cite an **Evidence Ledger**:

```json
{
  "target": "release-darwin-x64/app.asar",
  "digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "locations": [
    "lib/auth/token-refresh.js:L42-L88"
  ],
  "symbols": [
    "verifyAndRefreshToken",
    "calculateBackoffDelay"
  ],
  "limitations": "Static AST analysis; server private key omitted from bundle as expected.",
  "unknowns": [
    "Remote token revocation endpoint rate-limit policy"
  ]
}
```

---

## 4. CLI Recipes

```bash
# Check tool status
python skills/rea/scripts/rea_bridge.py doctor

# Validate an evidence ledger JSON file
python skills/rea/scripts/rea_bridge.py validate-evidence path/to/evidence.json

# Compute artifact SHA-256 digest
python skills/rea/scripts/rea_bridge.py hash path/to/binary
```

---

## 5. Verification & Quality Gates

The REA skill package is validated via `tests/test_rea_skill.py`, `tests/test_skill_frontmatter.py`, and `tests/test_catalog_assets.py`. Run tests via:

```bash
pytest tests/test_rea_skill.py
```
