# Cursor Agent Adapter for Improve

Profile and runtime rules for Cursor IDE and Cursor Composer agent workflows executing the `improve` senior codebase advisor skill.

---

## 1. Operating Rules

- Run strictly in read-only audit mode when surveying the repository.
- Author implementation plans strictly in `plans/` using markdown templates.
- Enforce self-contained steps with explicit test commands.
- Do not apply in-place refactorings or code edits during advisor sessions.
