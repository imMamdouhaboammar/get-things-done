# Example: PR Repair with Open-PR Bot Gate

A walkthrough of repairing an open Pull Request with bot review comments using `chatgpt-skill`.

---

## 1. Inspecting & Classifying Bot Comments

```bash
chatgpt-skill bot-gate inspect --pr 87
```

Output:
```text
Inspecting PR #87 (Head SHA: 7b89f2a)...
Found 3 bot comments:

1. [coderabbitai] (SHA: 7b89f2a)
   "Potential resource leak in file handle `fd` when error returned early."
   -> Disposition: CURRENT_ACTIONABLE
   -> Verification: Line 44 in src/storage.rs returns Err without dropping fd.

2. [sourcery-ai] (SHA: 3a10c4d)
   "Use list comprehension instead of manual append loop."
   -> Disposition: STALE_AFTER_NEW_HEAD
   -> Verification: Method was refactored in commit 7b89f2a; comment applies to old SHA.

3. [autofix.ci] (SHA: 7b89f2a)
   "Format fix applied: rustfmt."
   -> Disposition: ALREADY_FIXED
   -> Verification: Format commit already merged into branch.
```

---

## 2. Actioning the Actionable Finding

1. Edit `src/storage.rs` using RAII or explicit drop on early return.
2. Run targeted test: `cargo test test_storage_cleanup`.
3. Commit and push: `git commit -am "fix(storage): close file descriptor on error" && git push`.
4. Refresh head SHA (new SHA: `9e14f8b`).
5. Respond to CodeRabbit thread:
   ```text
   @coderabbitai resolve
   Addressed in 9e14f8b by wrapping handle in RAII guard. Verified with test_storage_cleanup.
   ```
6. Verify all CI checks are green on head SHA `9e14f8b`.
