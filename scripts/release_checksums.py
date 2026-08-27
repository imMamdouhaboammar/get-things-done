#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(directory: Path, output: Path) -> int:
    archives = sorted(path for path in directory.glob("*.zip") if path.is_file())
    if not archives:
        print(f"no .zip artifacts found in {directory}", file=sys.stderr)
        return 2
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(f"{checksum(path)}  {path.name}\n" for path in archives),
        encoding="utf-8",
    )
    print(output)
    return 0


def verify_manifest(directory: Path, manifest_path: Path) -> int:
    if not manifest_path.is_file():
        print(f"manifest file not found: {manifest_path}", file=sys.stderr)
        return 1
    lines = [line.strip() for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        print(f"manifest file is empty: {manifest_path}", file=sys.stderr)
        return 1
    verified_count = 0
    for line in lines:
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            print(f"invalid manifest line: {line}", file=sys.stderr)
            return 1
        expected_hash, name = parts[0], parts[1].strip()
        target = directory / name
        if not target.is_file():
            print(f"missing archive file: {target} (FAILED)", file=sys.stderr)
            return 1
        actual_hash = checksum(target)
        if actual_hash != expected_hash:
            print(f"checksum mismatch for {name}: expected {expected_hash}, got {actual_hash} (FAILED)", file=sys.stderr)
            return 1
        verified_count += 1
    print(f"OK: {verified_count} archives verified against {manifest_path.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write and verify deterministic SHA256 checksums for GTD release ZIP artifacts")
    parser.add_argument("directory", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--out", type=Path, help="Path to write the SHA256SUMS manifest file")
    group.add_argument("--verify", type=Path, help="Path to existing SHA256SUMS manifest to verify")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.verify:
        return verify_manifest(args.directory, args.verify)
    return write_manifest(args.directory, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
