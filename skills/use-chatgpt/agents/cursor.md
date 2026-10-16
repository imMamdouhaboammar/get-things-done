# Cursor IDE Agent Adapter

Profile and runtime rules for Cursor IDE and Composer workflows.

---

## 1. Bot Triggers
- Trigger Cursor Bugbot on PRs via:
  - `cursor review`
  - `bugbot run`
  - `cursor review verbose=true`
- Treat Bugbot findings as review evidence (Level C), not proof.

---

## 2. Workspace Symbol Navigation
- Use Cursor `@Codebase` and `@Folder` references for Stage 1 (Restore) and Stage 2 (Investigate).
- Run `chatgpt-skill` CLI in terminal to automate routing decisions and verification checks.
