#!/usr/bin/env python3
"""Build self-contained, store-ready ZIP archives for each skill in the catalog."""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"


ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


def package_skill(skill_dir: Path, output_zip: Path) -> list[str]:
    """Package a skill directory into a self-contained, deterministic zip archive."""
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    if output_zip.exists():
        output_zip.unlink()
    packaged_files: list[str] = []
    
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(p for p in skill_dir.rglob("*") if p.is_file()):
            if file_path.name.startswith(".DS_Store") or "__pycache__" in file_path.parts:
                continue
            rel_path = file_path.relative_to(skill_dir).as_posix()
            info = zipfile.ZipInfo(rel_path, date_time=ZIP_TIMESTAMP)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = file_path.stat().st_mode & 0o777
            info.external_attr = mode << 16
            zf.writestr(info, file_path.read_bytes())
            packaged_files.append(rel_path)
                
    return packaged_files


def package_all(root: Path, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, Path] = {}
    skills_root = root / "skills"
    
    for skill_name in ["get-things-done", "building-gtd-domain-packs"]:
        s_dir = skills_root / skill_name
        if not s_dir.is_dir():
            continue
        zip_dest = out_dir / f"{skill_name}.zip"
        files = package_skill(s_dir, zip_dest)
        results[skill_name] = zip_dest
        print(f"📦 Built {zip_dest.name} ({len(files)} files, {zip_dest.stat().st_size:,} bytes)")
        
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Package skills into distribution ZIPs")
    parser.add_argument("--root", default=str(ROOT), help="Project root directory")
    parser.add_argument("--out", default=str(ROOT / "dist"), help="Output directory for zip files")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out).resolve()
    
    results = package_all(root, out_dir)
    print(f"✅ Successfully packaged {len(results)} standalone skill bundles into {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
