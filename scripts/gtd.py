#!/usr/bin/env python3
"""Full-pack convenience wrapper for the canonical Get Things Done CLI."""
from __future__ import annotations

import os
import runpy
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
CANONICAL = PACK_ROOT / "skills" / "get-things-done" / "scripts" / "gtd.py"
os.environ.setdefault("GTD_PACK_ROOT", str(PACK_ROOT))
runpy.run_path(str(CANONICAL), run_name="__main__")
