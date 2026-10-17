# Example: Native Binary Inspection & Evidence Ledger

This example demonstrates how `/rea` performs summary-first inspection of a compiled native Mach-O executable, gathers verified assembly locations, and prepares GTD-compliant completion evidence.

## 1. Scenario

* **Request**: "Inspect the license validation routine in the native agent binary, confirm whether it uses hardware UUID, and cite exact offsets."
* **Artifact**: `bin/agent-daemon` (Mach-O 64-bit arm64)

## 2. Command Pipeline

```bash
# 1. Inspect binary layout (offline, safe, no engine needed)
rea inspect-binary-layout bin/agent-daemon --json

# 2. Search candidate procedures
rea search bin/agent-daemon --query "checkHardwareLicense" --json

# 3. Analyze target function & xrefs
rea function bin/agent-daemon --target "checkHardwareLicense" --json
```

## 3. Verified Evidence Table

| Property | Value |
|---|---|
| Artifact SHA-256 | `a1b2c3d4e5f6...` |
| Text Section Range | `0x100000000 - 0x100084000` |
| Method Virtual Address | `0x100021b80` |
| Instruction Count | 42 instructions |
| Observed System Calls | `sysctlbyname("kern.uuid", ...)` |
| Unknowns | External remote activation server certificate pins |

## 4. GTD Integration Outcome

The verified evidence is mapped into the GTD Execution Brief:
* `knowledge.facts`: "Binary checks hardware UUID via `sysctlbyname(kern.uuid)` at `0x100021b80`."
* `knowledge.unknowns`: "Remote activation server TLS certificate pin rotation schedule."
* `verification.evidence`: "Level A machine inspection log and disassembly trace from REA."
