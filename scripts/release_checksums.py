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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Write deterministic SHA256 checksums for GTD release ZIP artifacts")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return write_manifest(args.directory, args.out)


if __name__ == "__main__":
    raise SystemExit(main())
