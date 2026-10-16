# Copy-Ready Autonomous Mission Prompt Skeleton

MISSION
[Observable finished state]

TARGET
[Repository / PR / Issue / Environment]

SOURCE OF TRUTH
[Current connected source: @GitHub / local repo]

OPERATING CONTRACT
- Inspect before mutation
- Preserve unrelated work
- One write owner per mutable surface
- Current state beats memory
- Evidence before claims
- Mutation invalidates stale verification
- For any open PR, inspect existing GitHub App / bot comments, review threads, and check summaries before deciding or triggering new review

SCOPE
IN:
- [Item 1]
- [Item 2]

OUT:
- [Item 1]
- [Item 2]

PERMISSIONS
ALLOWED:
- [Reads / local edits / local test runs]

CONFIRMATION-REQUIRED:
- [Landing / force-push / database drop]

ROLES
Source: [Tool / plugin]
Planner: [Tool / plugin]
Executor: [Tool / plugin]
Specialist: [Tool / plugin]
Verifier: [Tool / test command]
Reviewer: [Tool / plugin]
Readiness: [Tool / plugin]
Landing: [Tool / plugin]
Handoff: [Tool / plugin]

STATE MACHINE
RESTORE
-> INVESTIGATE
-> CONTRACT
-> EXECUTE
-> VERIFY
-> REVIEW
-> REPAIR
-> REVERIFY
-> READY
-> LAND
-> VERIFY LANDED STATE
-> DOCUMENT

EVIDENCE GATES
- Unit test pass: [Command]
- Typecheck clean: [Command]
- Review sign-off: [Reviewer]

STOP CONDITIONS
- COMPLETE
- BLOCKED
- AUTHORITY REQUIRED
- UNSAFE / AMBIGUOUS

FINAL RECEIPT
- Source state
- Changes
- Verification
- Reviews
- Current SHA / artifact
- Limitations
- Next action
