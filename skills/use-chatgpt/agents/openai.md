# OpenAI ChatGPT & Codex Agent Adapter

Profile and runtime rules for ChatGPT Plus/Team/Enterprise and OpenAI Codex environments.

---

## 1. Plugin Invocation & Discovery
- In ChatGPT/Codex, capabilities are invoked via exact `@Plugin Name` syntax.
- If a plugin is installed but its tool call is not surfaced in the current context:
  - Classify as `INSTALLED_BUT_NOT_CALLABLE_HERE`.
  - Continue using the available callable toolset.
  - Never fabricate or simulate the missing plugin's outputs.

---

## 2. Long-Running Local Jobs
- For tests, builds, or evaluations taking > 60 seconds, use `@Codex Process Jobs`.
- Do not use `@Codex Process Jobs` for long-running servers or background interactive coding.
- Do not busy-poll in the same turn.

---

## 3. Landing Policy
- Shepherding Pull Requests to completion is owned by `@PR Completion`.
- Exact-head SHA confirmation is mandatory before landing.
