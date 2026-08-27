# v1.3 change notes

This release introduces comprehensive multi-host adapter interoperability, automated package distribution, companion tool contracts, and release hardening across the GTD ecosystem.

Highlights:

- **19 verified host adapter contracts**: Open Agent Skills standard, Agent Plugins 1.0.0, Claude AI, Claude Code, Claude Marketplace, Claude Cowork, ChatGPT Web, ChatGPT Work, ChatGPT Plugins, Codex, Cursor, Kimi Code, Grok Build, DeepSeek DeepCode, Homebrew, Shell installer, Vercel skills.sh, Contentful Skill Kit, and fail-closed Glama MCP boundary.
- **5 companion interoperability contracts**: Explicit non-host companion profiles for Plugin Autopilot (orchestration), Plugin Eval (evaluation), Superpowers (methodology), ArmorCodex (security), and Context7 (documentation retrieval) with strict ownership boundaries and no GTD behavior duplication.
- **Homebrew formula distribution**: First-class HEAD formula (`Formula/get-things-done.rb`) installing the GTD CLI wrapper and canonical skills into Homebrew-managed environments.
- **Hardened multi-host shell installer**: Portable `install.sh` supporting named host targets, custom Agent Skills roots (`--target-path`), all-root installs (`--all`), non-destructive dry runs (`--dry-run`), atomic staging on overwrite (`--force`), and macOS Bash 3.2 compatibility.
- **skills.sh ecosystem distribution**: Discovery metadata (`skills.sh.json`) supporting global and multi-agent install and update flows via the Vercel skills CLI.
- **JSON Schema Draft 2020-12 validation**: Formal schema contracts for `adapters/registry.json` and `adapters/companions.json` with strict enum and property validation.
- **Deterministic packaging and release checksums**: Reproducible ZIP archives with normalized timestamps and POSIX modes, accompanied by streaming SHA-256 checksum generation and verification (`scripts/release_checksums.py`).
- **Unified adapter CLI tooling**: Validates contracts, inspects companion roles, checks runtime dependencies, exports host layouts, and builds distribution packages.

The package version moves to `1.3.0`.
