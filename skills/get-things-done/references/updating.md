# Self-Update Contract

The GTD Skill can update an installed Agent Skills root through its canonical CLI.

## Primary commands

```bash
python get-things-done/scripts/gtd.py update --check
python get-things-done/scripts/gtd.py update
```

Channels:

- `latest`: prefer the latest GitHub Release; if no release exists, resolve the exact current `main` commit and state that source explicitly
- `stable`: require a published GitHub Release; never silently fall back to `main`
- `main`: track the exact latest commit on `main`

Explicit target:

```bash
python get-things-done/scripts/gtd.py update --target-path ~/.cursor/skills
```

## Update invariants

An update must:

1. resolve the remote source before downloading
2. download only from the canonical GTD GitHub repository
3. stage the complete four-Skill set before mutation
4. reject path traversal, archive symlinks, oversized downloads, and oversized extraction
5. validate required Skill entrypoints
6. verify copied GTD core contracts are synchronized
7. preserve non-colliding custom domain files
8. replace Skill directories transactionally and roll back replacement failures
9. write an update-state manifest containing the source ref and canonical file hashes
10. refuse silent overwrite of canonical files changed after a managed update unless the user explicitly passes `--force`

## Authority boundary

Self-update changes installed executable instructions and is therefore security-sensitive.

Do not:

- accept arbitrary repository or archive URLs
- execute code from the downloaded archive during staging
- disable validation because a newer version exists
- treat a network response alone as successful installation
- mutate a Git checkout or Homebrew-managed package as though it were a normal user Skill root

Repository checkouts should use `git pull --ff-only`.

Homebrew-managed installs should use:

```bash
brew upgrade --fetch-HEAD get-things-done
```

A package-managed CLI may still update a separate user Skill root through `--target-path`.
