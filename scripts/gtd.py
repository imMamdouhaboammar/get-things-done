#!/usr/bin/env python3
"""Full-pack convenience wrapper for the canonical Get Things Done CLI."""
from __future__ import annotations

import os
import runpy
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
CANONICAL = PACK_ROOT / "skills" / "get-things-done" / "scripts" / "gtd.py"


def main() -> int:
    os.environ.setdefault("GTD_PACK_ROOT", str(PACK_ROOT))
    namespace = runpy.run_path(str(CANONICAL), run_name="gtd_canonical")
    canonical_main = namespace.get("main")
    if not callable(canonical_main):
        raise RuntimeError(f"canonical GTD CLI has no main(): {CANONICAL}")
    return int(canonical_main())


if __name__ == "__main__":
    raise SystemExit(main())
