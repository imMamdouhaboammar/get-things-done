# Example: Security-Sensitive Change & Audit

A walkthrough of handling a security-sensitive change using policy registration and specialized security reviews.

---

## 1. Scenario
User requests exposing an internal metrics endpoint to a public webhook.

---

## 2. Policy & Trust Boundary Analysis

1. **Policy Gate via `@ArmorCodex`**:
   - Boundary changed: Private endpoint $\rightarrow$ Public Internet.
   - Requirement: Enforce HMAC SHA-256 signature verification and IP rate limiting.
2. **Implementation via `Codex Engineering Guardrails code-work`**:
   - Add constant-time signature comparison (`subtle::ConstantTimeEq`).
   - Add token expiration check (replay attack prevention).
3. **Executable Proof (Level B)**:
   - Test valid HMAC signature $\rightarrow$ HTTP 200.
   - Test invalid signature $\rightarrow$ HTTP 401.
   - Test replayed timestamp older than 300s $\rightarrow$ HTTP 403.
4. **Independent Security Review (Level C)**:
   - `@Codex Security` inspects timing-attack resistance and secret storage.
   - Result: PASS with zero high or medium findings.
5. **Ledger Record**:
   - `Final Verdict: COMPLETE`
