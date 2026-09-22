import importlib.util
import io
import stat
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UPDATER_PATH = ROOT / "skills/get-things-done/scripts/updater.py"

spec = importlib.util.spec_from_file_location("gtd_updater_security", UPDATER_PATH)
updater = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = updater
assert spec.loader is not None
spec.loader.exec_module(updater)


def test_remote_source_is_fixed_to_canonical_repository(monkeypatch):
    calls = []

    def fake_json(url, timeout):
        calls.append(url)
        if url.endswith("/releases/latest"):
            return {"tag_name": "v9.9.9"}
        raise AssertionError(url)

    monkeypatch.setattr(updater, "_json_request", fake_json)
    source = updater.resolve_remote("stable")

    assert calls == [
        "https://api.github.com/repos/imMamdouhaboammar/get-things-done/releases/latest"
    ]
    assert source.archive_url.startswith(
        "https://github.com/imMamdouhaboammar/get-things-done/"
    )


def test_archive_symlink_is_rejected(tmp_path):
    buf = io.BytesIO()
    info = zipfile.ZipInfo("repo/skills/get-things-done/SKILL.md")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16

    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(info, "../../outside")

    with pytest.raises(updater.UpdateError, match="symlink"):
        updater.extract_skill_archive(buf.getvalue(), tmp_path)


def test_archive_path_traversal_cannot_escape_stage(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("repo/skills/get-things-done/../../../outside.txt", "bad")
        zf.writestr("repo/skills/get-things-done/SKILL.md", "safe")

    updater.extract_skill_archive(buf.getvalue(), tmp_path)

    assert (tmp_path / "get-things-done/SKILL.md").is_file()
    assert not (tmp_path.parent / "outside.txt").exists()


def test_homebrew_managed_install_refuses_direct_mutation(tmp_path, capsys):
    root = tmp_path / "Cellar" / "get-things-done" / "HEAD-test" / "libexec"
    root.mkdir(parents=True)

    rc = updater.run_update(pack_root=root)

    assert rc == 2
    out = capsys.readouterr().out
    assert "Homebrew-managed installation detected" in out
    assert "brew upgrade --fetch-HEAD get-things-done" in out
