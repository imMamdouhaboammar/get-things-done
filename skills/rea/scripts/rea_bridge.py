#!/usr/bin/env python3
"""REA Bridge & Verification Utility for GTD Workflows.

Validates reverse engineering evidence ledgers, checks tool availability,
and converts binary analysis findings into GTD Execution Briefs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

SHA256_HEX_PATTERN = re.compile(r"^[a-fA-F0-9]{64}$")
VIRTUAL_ADDR_PATTERN = re.compile(r"^0x[0-9a-fA-F]+$")


def check_runtime_tools() -> dict[str, bool]:
    """Inspect availability of REA engines and external decompilers."""
    tools = {
        "bun": bool(shutil.which("bun")),
        "rea": bool(shutil.which("rea")),
        "jadx": bool(shutil.which("jadx")),
        "hopper": bool(shutil.which("hopper")),
        "ghidra": bool(shutil.which("ghidra")),
        "otool": bool(shutil.which("otool")),
        "objdump": bool(shutil.which("objdump")),
    }
    return tools


def validate_evidence_ledger(payload: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate that an evidence ledger complies with the REA evidence contract."""
    errors: list[str] = []
    
    if "target" not in payload:
        errors.append("Missing required field: 'target'")
    if "digest" not in payload:
        errors.append("Missing required field: 'digest'")
    else:
        digest_val = payload["digest"]
        if digest_val.startswith("sha256:"):
            digest_val = digest_val.split(":", 1)[1]
        if not SHA256_HEX_PATTERN.match(digest_val):
            errors.append(f"Invalid SHA-256 digest format: {payload['digest']}")

    locations = payload.get("locations", [])
    if not isinstance(locations, list) or len(locations) == 0:
        errors.append("Evidence must provide at least one verified location in 'locations'")
        
    symbols = payload.get("symbols", [])
    if not isinstance(symbols, list):
        errors.append("'symbols' must be a list of identifiers")

    return len(errors) == 0, errors


def compute_file_sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="REA Bridge & Verification Utility")
    subparsers = parser.add_subparsers(dest="command")

    # doctor
    subparsers.add_parser("doctor", help="Check installed reverse-engineering tools and engines")

    # hash
    hash_parser = subparsers.add_parser("hash", help="Compute SHA-256 evidence digest for an artifact")
    hash_parser.add_argument("path", type=str, help="Path to artifact")

    # validate-evidence
    val_parser = subparsers.add_parser("validate-evidence", help="Validate a JSON evidence ledger")
    val_parser.add_argument("file", type=str, help="Path to evidence JSON file")

    args = parser.parse_args()

    if args.command == "doctor":
        tools = check_runtime_tools()
        print("REA Tool & Engine Status:")
        for name, available in sorted(tools.items()):
            icon = "✅" if available else "⚪"
            status = "available" if available else "not found (fallback will be used)"
            print(f"  {icon} {name:<10}: {status}")
        return 0

    elif args.command == "hash":
        target = Path(args.path)
        if not target.is_file():
            print(f"Error: file not found: {target}", file=sys.stderr)
            return 1
        digest = compute_file_sha256(target)
        print(f"sha256:{digest}")
        return 0

    elif args.command == "validate-evidence":
        path = Path(args.file)
        if not path.is_file():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 1
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Error reading JSON: {e}", file=sys.stderr)
            return 1

        valid, errors = validate_evidence_ledger(data)
        if valid:
            print("VALID: Evidence ledger complies with REA contract")
            return 0
        else:
            print("INVALID: Evidence ledger fails contract checks:")
            for err in errors:
                print(f"  - {err}")
            return 1

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
