#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

VERSION_JSON_PATHS = (
    "package.json",
    "plugin.json",
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    "kimi.plugin.json",
)
SHA_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class ProvenanceError(ValueError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pyproject_version(root: Path) -> str:
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']\s*$', text, re.MULTILINE)
    if match is None:
        raise ProvenanceError("pyproject.toml has no project version")
    return match.group(1)


def manifest_versions(root: Path) -> dict[str, str]:
    versions: dict[str, str] = {"pyproject.toml": pyproject_version(root)}
    for relative in VERSION_JSON_PATHS:
        path = root / relative
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ProvenanceError(f"cannot read version manifest {relative}: {exc}") from exc
        version = data.get("version")
        if not isinstance(version, str) or not version:
            raise ProvenanceError(f"{relative} has no non-empty version")
        versions[relative] = version
    return versions


def validate_release_identity(root: Path, ref: str) -> tuple[str, dict[str, str]]:
    versions = manifest_versions(root)
    unique = set(versions.values())
    if len(unique) != 1:
        detail = ", ".join(f"{path}={version}" for path, version in sorted(versions.items()))
        raise ProvenanceError(f"release version mismatch: {detail}")
    version = next(iter(unique))

    prefix = "refs/tags/"
    if ref.startswith(prefix):
        tag = ref[len(prefix):]
        expected = f"v{version}"
        if tag != expected:
            raise ProvenanceError(f"release tag {tag!r} does not match project version {expected!r}")
    return version, versions


def artifact_records(dist: Path, output: Path) -> list[dict[str, Any]]:
    candidates = {
        path.resolve()
        for path in dist.rglob("*.zip")
        if path.is_file()
    }
    candidates.update(
        path.resolve()
        for path in dist.rglob("SHA256SUMS")
        if path.is_file()
    )
    candidates.discard(output.resolve())
    if not candidates:
        raise ProvenanceError(f"no release artifacts found under {dist}")

    records: list[dict[str, Any]] = []
    for path in sorted(candidates, key=lambda item: item.relative_to(dist.resolve()).as_posix()):
        records.append(
            {
                "path": path.relative_to(dist.resolve()).as_posix(),
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    return records


def build_provenance(root: Path, dist: Path, source_sha: str, ref: str, output: Path) -> dict[str, Any]:
    source_sha = source_sha.lower()
    if SHA_PATTERN.fullmatch(source_sha) is None:
        raise ProvenanceError("source SHA must be a full 40-character lowercase-or-uppercase hexadecimal commit SHA")
    version, versions = validate_release_identity(root, ref)
    return {
        "schema_version": 1,
        "project": "get-things-done",
        "version": version,
        "source": {"sha": source_sha, "ref": ref},
        "version_manifests": dict(sorted(versions.items())),
        "artifacts": artifact_records(dist, output),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write deterministic GTD release provenance")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        payload = build_provenance(
            args.root.resolve(),
            args.dist.resolve(),
            args.source_sha,
            args.ref,
            args.out.resolve(),
        )
    except (OSError, ProvenanceError) as exc:
        print(f"PROVENANCE ERROR: {exc}")
        return 2

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
