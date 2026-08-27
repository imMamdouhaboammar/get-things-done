import importlib.util
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "adapters.py"
spec = importlib.util.spec_from_file_location("gtd_adapter_matrix", MODULE_PATH)
adapters = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(adapters)


def find_skill_file(export: Path, skill: str) -> Path:
    matches = list(export.rglob(f"{skill}/SKILL.md"))
    assert len(matches) == 1, (export, skill, matches)
    return matches[0]


def test_every_nonconditional_skill_export_preserves_canonical_skill_bytes(tmp_path):
    registry = adapters.load_registry()["adapters"]
    canonical = {
        name: (ROOT / "skills" / name / "SKILL.md").read_bytes()
        for name in adapters.SKILL_NAMES
    }
    for item in registry:
        if item["support"] == "conditional" or item["export"] == "homebrew-formula":
            continue
        export = adapters.export_adapter(item["id"], tmp_path / "dist")
        for skill, expected in canonical.items():
            assert find_skill_file(export, skill).read_bytes() == expected, item["id"]


def test_homebrew_export_carries_canonical_skills_as_managed_payload(tmp_path):
    export = adapters.export_adapter("homebrew", tmp_path / "dist")
    for skill in adapters.SKILL_NAMES:
        assert (export / "skills" / skill / "SKILL.md").read_bytes() == (ROOT / "skills" / skill / "SKILL.md").read_bytes()


def test_shell_archive_preserves_installer_executable_bit(tmp_path):
    export = adapters.export_adapter("shell", tmp_path / "dist")
    archive = adapters.package_directory(export)
    with zipfile.ZipFile(archive) as zf:
        info = zf.getinfo("install.sh")
    mode = (info.external_attr >> 16) & 0o777
    assert mode & 0o100
