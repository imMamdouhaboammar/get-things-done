import importlib.util
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "adapters.py"
spec = importlib.util.spec_from_file_location("gtd_adapter_packaging", MODULE_PATH)
adapters = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(adapters)


def test_adapter_zip_is_reproducible(tmp_path):
    first_dir = adapters.export_adapter("shell", tmp_path / "first")
    first_zip = adapters.package_directory(first_dir)
    first_bytes = first_zip.read_bytes()

    second_dir = adapters.export_adapter("shell", tmp_path / "second")
    second_zip = adapters.package_directory(second_dir)
    second_bytes = second_zip.read_bytes()

    assert first_bytes == second_bytes


def test_adapter_zip_uses_relative_safe_members(tmp_path):
    directory = adapters.export_adapter("homebrew", tmp_path / "dist")
    archive = adapters.package_directory(directory)
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
    assert names
    assert all(not name.startswith("/") for name in names)
    assert all(".." not in Path(name).parts for name in names)


def test_repackaging_replaces_existing_archive(tmp_path):
    directory = adapters.export_adapter("skills-sh", tmp_path / "dist")
    archive = adapters.package_directory(directory)
    archive.write_bytes(b"stale")
    rebuilt = adapters.package_directory(directory)
    assert rebuilt.read_bytes() != b"stale"


def test_export_replaces_stale_target_directory(tmp_path):
    target = adapters.export_adapter("cursor", tmp_path / "dist")
    stale = target / "stale.txt"
    stale.write_text("stale")
    rebuilt = adapters.export_adapter("cursor", tmp_path / "dist")
    assert rebuilt == target
    assert not stale.exists()
