# Claude Code Agent Adapter

Profile and runtime rules for the Claude Code CLI and Anthropic agent environments.

---

## 1. Tool Call Mapping
- Translate `@GitHub` operations to `gh` CLI commands executed via Bash tool.
- Translate `@Remote Desktop Commander` operations to native local terminal/file editing tools.
- Translate `@Context7` queries to web search or local documentation lookups.

---

## 2. Process & Execution
- In Claude Code, run tests and builds using local bash execution (`cargo test`, `bun test`).
- Enforce the evidence ledger directly in PR descriptions or conversation artifacts.
- Use `chatgpt-skill` binary directly from the CLI to automate routing, state transitions, and bot gating.
