# Self-updating GTD Skills

The canonical GTD CLI can refresh an installed Agent Skills root from GitHub.

## Commands

Check without changing files:

```bash
python ~/.agents/skills/get-things-done/scripts/gtd.py update --check
```

Update to the newest available source:

```bash
python ~/.agents/skills/get-things-done/scripts/gtd.py update
```

The default channel is `latest`:

1. use the latest GitHub Release when one exists
2. otherwise use the exact current commit on `main`
3. print which source was selected

Require a published release:

```bash
python ~/.agents/skills/get-things-done/scripts/gtd.py update --channel stable
```

Track the newest `main` commit explicitly:

```bash
python ~/.agents/skills/get-things-done/scripts/gtd.py update --channel main
```

Update another Agent Skills root:

```bash
python ~/.agents/skills/get-things-done/scripts/gtd.py update \
  --target-path ~/.cursor/skills
```

## Safety behavior

The updater:

- downloads only from the canonical GitHub repository
- resolves an exact tag or commit before installation
- stages the complete four-Skill set before replacing anything
- validates that required Skills exist
- verifies GTD, Domain Pack Builder, and Capability Router carry the same core contract
- rejects archive path traversal, symlinks, oversized downloads, and oversized extraction
- replaces the four Skills transactionally and rolls back if replacement fails
- preserves custom domain files that do not collide with an upstream domain
- records canonical file hashes in `.gtd-update-state.json`
- refuses to overwrite canonical files modified after the previous managed update unless `--force` is supplied

## Repository and package-manager installs

A Git checkout is source code, not a managed Skill install. The updater refuses to rewrite it automatically. Use:

```bash
git pull --ff-only
```

For Homebrew-managed GTD, use:

```bash
brew upgrade --fetch-HEAD get-things-done
```

You can still update a separate user Skill root from either environment with `--target-path`.

## First managed update

An installation made before updater state existed has no canonical hash baseline. The first successful managed update establishes that baseline. Custom domain files are still preserved.
