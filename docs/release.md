# Release and recovery

GTD treats installation and release delivery as recoverable operations.

## Shell installer transaction

Each target Skill root is one install transaction.

Before replacement, the installer:

1. validates that all four canonical Skills exist
2. refuses existing destinations unless `--force` is explicit
3. stages and validates the complete replacement set

For a forced replacement, existing GTD Skill directories are moved to a temporary backup under the target root before any staged Skill becomes authoritative.

If replacement fails after mutation starts, the installer:

- removes newly installed GTD Skill directories from that transaction
- restores the previous directories from the backup
- removes staging and backup directories
- exits non-zero

On success, the backup is deleted.

The transaction boundary is one target root. With `--all` or multiple target paths, a root that completed successfully is not rolled back merely because a later independent root fails.

## Release qualification

A release job must pass the same source and distribution contracts used in CI before publication:

```bash
python -m pip install -e ".[dev]"
gtd --help
python scripts/catalog_stylist.py --validate
python scripts/adapters.py validate
python -m ruff check scripts tests skills/get-things-done/scripts
pytest -q
```

It then builds deterministic Skill archives and adapter archives, writes SHA-256 manifests, verifies them, and creates a provenance record before the GitHub Release action runs.

## Provenance

`dist/PROVENANCE.json` records:

- project version
- exact source commit SHA
- Git ref
- all version-bearing manifest versions
- every release ZIP path, byte size, and SHA-256
- checksum manifests and their SHA-256

The record intentionally has no wall-clock timestamp. For identical source identity and identical artifacts, the provenance payload is deterministic.

For a tag release, the tag must equal `v<project-version>`. A version mismatch in any tracked manifest or the tag fails the release before publication.

## Package reproducibility

Canonical Skill ZIPs and adapter ZIPs use fixed ZIP timestamps, stable file ordering, and preserved file mode bits. The repository has deterministic archive regression tests.

Reproducibility means the packaging implementation is deterministic for the same input tree. It does not claim two different source commits or environments are interchangeable.

## Consumer verification

For a downloaded release:

1. verify the relevant archive against `SHA256SUMS`
2. inspect `PROVENANCE.json`
3. confirm `source.sha` and `version` match the release you intended to consume

The provenance artifact links a release bundle to its exact source identity; it is not a cryptographic signature.

## Recovery and rollback

Do not silently mutate a published release artifact.

If a published release is defective:

1. stop recommending that version
2. document the defect on the release
3. publish a corrective version from a reviewed source commit
4. keep prior immutable artifacts and checksums available when safe to do so

For local recovery:

- shell install: reinstall a known-good checkout or release with `--force`; failed force replacement restores the immediately previous target-root installation automatically
- managed self-update: use the updater's recorded state and transactional rollback behavior
- Git checkout: checkout or revert to the known-good commit
- Homebrew HEAD: install the desired known-good revision/formula state
- skills.sh or another package manager: use that manager's version/update authority

A rollback is successful only after `gtd doctor` or the equivalent host verification passes against the restored version.

## Workflow dispatch

Manual `workflow_dispatch` runs are qualification runs unless the ref is a tag. The GitHub Release publication step is tag-gated.
