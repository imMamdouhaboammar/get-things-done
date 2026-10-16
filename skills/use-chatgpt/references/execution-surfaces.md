# Execution Surface Taxonomy

Before invoking any tool or plugin, classify its execution surface. Never confuse a reviewer with an execution engine or a bot comment with repository-native CI.

---

## 1. The Five Execution Surfaces

```text
1. CHATGPT PLUGIN / SKILL
A capability inside the current ChatGPT, Codex, or agent host.
Examples: @Superpowers, @Context7, @Codex Engineering Guardrails

2. CONNECTED SOURCE
A live account, repository, or database exposed through an authenticated connector.
Examples: @GitHub, @Supabase, @Gmail, @Google Drive

3. GITHUB APP / BOT
An autonomous actor installed on GitHub that comments, reviews, updates checks, or commits to PR branches.
Examples: coderabbitai, Cursor Bugbot, autofix.ci, Qlty, Sourcery

4. REPOSITORY-NATIVE GATE
A check or policy owned and enforced directly by the repository itself.
Examples: GitHub Actions CI workflows, branch protection rules, required reviews, merge queue, CODEOWNERS

5. EXTERNAL AUTHORITY
Current primary documentation, RFCs, or vendor APIs that define contractual behavior.
Examples: OpenAI developer docs, Rust standard library docs, TypeScript specification
```

---

## 2. Invariant Rules Across Surfaces

1. **Reviewers Are Not Sources of Truth**: Never ask `@CodeRabbit` or `@Codex Engineering Guardrails` to act as the primary source of repository state.
2. **Readiness Analyzers Cannot Discover Proof**: Never ask `@PR Readiness Check` to discover repository state it cannot access; supply it with a concrete evidence packet.
3. **Bots Do Not Replace Repository CI**: Never treat a bot approval or review comment as a substitute for passing GitHub Actions workflows.
4. **Bot Comments Are Not Code Proof**: A successful bot run or zero-findings summary does not prove runtime correctness or satisfy unit tests.
5. **Surface Disambiguation**: A plugin name (e.g. `@CodeRabbit`), a GitHub App name (`CodeRabbit`), and a GitHub handle (`@coderabbitai`) are distinct surfaces with different capabilities and permissions.
