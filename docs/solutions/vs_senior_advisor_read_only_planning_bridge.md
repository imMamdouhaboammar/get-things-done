# Verification Specification: Senior Advisor Read-Only Planning Bridge

## Problem Statement
AI agents frequently fail when asked to audit codebases by immediately writing speculative, untested edits across arbitrary files, mutating the user's working tree, reproducing API tokens, and leaving broken states.

## Solution Specification
The `improve` skill establishes a strict barrier:
1. **Senior Advisor vs. Mechanical Executor**:
   - High-ceiling discernment is preserved by banning direct source modification.
   - The primary deliverable is a self-contained, machine-checkable plan in `plans/NNN-<slug>.md`.
2. **GTD Execution Brief Synthesis**:
   - Plans map 1:1 to GTD Execution Briefs (v1.0 & v2.0):
     - Scope in/out $\rightarrow$ brief `scope.in` and `scope.out`
     - Plan steps $\rightarrow$ brief `workstreams`
     - Plan done criteria $\rightarrow$ brief `verification.criteria` and `verification.evidence`
     - Stop conditions $\rightarrow$ brief `risks` and `blockers`
3. **Evidence Verification Gate**:
   - Done criteria must be verified using Level A (compiler/typecheck/test pass) or Level B (integration) evidence.
   - Plans failing the self-containment check, containing session-relative references ("as discussed above"), or reproducing secrets are rejected at the bridge gate.
