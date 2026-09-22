#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path, PurePosixPath
from typing import Any

REPOSITORY = "imMamdouhaboammar/get-things-done"
GITHUB_API = "https://api.github.com"
GITHUB_WEB = "https://github.com"
USER_AGENT = "get-things-done-updater/1"
SKILL_NAMES = (
    "get-things-done",
    "building-gtd-domain-packs",
    "gtd-capability-router",
    "gtd-deliberation",
)
STATE_FILE = ".gtd-update-state.json"
MAX_DOWNLOAD_BYTES = 50 * 1024 * 1024
MAX_EXTRACT_BYTES = 100 * 1024 * 1024
MAX_ARCHIVE_FILES = 5000


class UpdateError(RuntimeError):
    pass


@dataclass(frozen=True)
class RemoteSource:
    channel: str
    kind: str
    ref: str
    archive_url: str


def _request(url: str, timeout: float) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        length = response.headers.get("Content-Length")
        if length and int(length) > MAX_DOWNLOAD_BYTES:
            raise UpdateError(f"download is too large: {length} bytes")
        payload = response.read(MAX_DOWNLOAD_BYTES + 1)
    if len(payload) > MAX_DOWNLOAD_BYTES:
        raise UpdateError(f"download exceeded {MAX_DOWNLOAD_BYTES} bytes")
    return payload


def _json_request(url: str, timeout: float) -> dict[str, Any]:
    try:
        payload = _request(url, timeout)
    except urllib.error.HTTPError:
        raise
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UpdateError(f"invalid JSON from {url}: {exc}") from exc
    if not isinstance(data, dict):
        raise UpdateError(f"expected JSON object from {url}")
    return data


def resolve_remote(channel: str, timeout: float = 15.0) -> RemoteSource:
    if channel not in {"latest", "stable", "main"}:
        raise UpdateError(f"unsupported channel: {channel}")

    if channel in {"latest", "stable"}:
        try:
            release = _json_request(f"{GITHUB_API}/repos/{REPOSITORY}/releases/latest", timeout)
            tag = release.get("tag_name")
            if not isinstance(tag, str) or not tag.strip():
                raise UpdateError("latest release does not contain a tag_name")
            encoded = urllib.parse.quote(tag, safe="")
            return RemoteSource(
                channel=channel,
                kind="release",
                ref=tag,
                archive_url=f"{GITHUB_WEB}/{REPOSITORY}/archive/refs/tags/{encoded}.zip",
            )
        except urllib.error.HTTPError as exc:
            if exc.code != 404 or channel == "stable":
                raise UpdateError(f"cannot resolve latest release: HTTP {exc.code}") from exc

    try:
        branch = _json_request(f"{GITHUB_API}/repos/{REPOSITORY}/branches/main", timeout)
    except urllib.error.HTTPError as exc:
        raise UpdateError(f"cannot resolve main branch: HTTP {exc.code}") from exc
    commit = branch.get("commit")
    sha = commit.get("sha") if isinstance(commit, dict) else None
    if not isinstance(sha, str) or len(sha) < 7:
        raise UpdateError("main branch response does not contain a commit SHA")
    return RemoteSource(
        channel=channel,
        kind="main",
        ref=sha,
        archive_url=f"{GITHUB_WEB}/{REPOSITORY}/archive/{sha}.zip",
    )


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_manifest(skills_root: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for skill_name in SKILL_NAMES:
        skill = skills_root / skill_name
        if not skill.is_dir():
            continue
        for path in sorted(skill.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or path.name == ".DS_Store":
                continue
            rel = path.relative_to(skills_root).as_posix()
            manifest[rel] = _file_hash(path)
    return manifest


def _read_state(skills_root: Path) -> dict[str, Any] | None:
    path = skills_root / STATE_FILE
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _write_state(skills_root: Path, source: RemoteSource, manifest: dict[str, str]) -> None:
    payload = {
        "schema_version": 1,
        "repository": REPOSITORY,
        "source": asdict(source),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "canonical_manifest": manifest,
    }
    path = skills_root / STATE_FILE
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, path)


def local_modifications(skills_root: Path, state: dict[str, Any] | None) -> list[str]:
    if not state:
        return []
    expected = state.get("canonical_manifest")
    if not isinstance(expected, dict):
        return []
    changed: list[str] = []
    for rel, expected_hash in expected.items():
        if not isinstance(rel, str) or not isinstance(expected_hash, str):
            continue
        path = skills_root / rel
        if not path.is_file() or _file_hash(path) != expected_hash:
            changed.append(rel)
    return changed


def _safe_skill_member(name: str) -> tuple[str, PurePosixPath] | None:
    pure = PurePosixPath(name)
    if pure.is_absolute() or ".." in pure.parts or len(pure.parts) < 3:
        return None
    # GitHub archive layout: <repo-ref>/skills/<skill>/...
    try:
        skills_index = pure.parts.index("skills")
    except ValueError:
        return None
    remaining = pure.parts[skills_index + 1 :]
    if len(remaining) < 2 or remaining[0] not in SKILL_NAMES:
        return None
    rel = PurePosixPath(*remaining)
    return remaining[0], rel


def extract_skill_archive(archive: bytes, staged_skills_root: Path) -> None:
    try:
        zf = zipfile.ZipFile(BytesIO(archive))
    except zipfile.BadZipFile as exc:
        raise UpdateError("downloaded archive is not a valid ZIP") from exc

    infos = zf.infolist()
    if len(infos) > MAX_ARCHIVE_FILES:
        raise UpdateError(f"archive contains too many files: {len(infos)}")
    expanded = sum(info.file_size for info in infos)
    if expanded > MAX_EXTRACT_BYTES:
        raise UpdateError(f"archive expands beyond {MAX_EXTRACT_BYTES} bytes")

    extracted = 0
    for info in infos:
        parsed = _safe_skill_member(info.filename)
        if parsed is None or info.is_dir():
            continue
        unix_mode = (info.external_attr >> 16) & 0o170000
        if unix_mode == 0o120000:
            raise UpdateError(f"archive contains a symlink: {info.filename}")
        _, rel = parsed
        target = staged_skills_root / Path(*rel.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(info, "r") as source, target.open("wb") as dest:
            shutil.copyfileobj(source, dest)
        extracted += 1

    if not extracted:
        raise UpdateError("archive did not contain GTD skills")


def validate_staged_skills(skills_root: Path) -> None:
    missing = [name for name in SKILL_NAMES if not (skills_root / name / "SKILL.md").is_file()]
    if missing:
        raise UpdateError(f"archive is missing required skills: {', '.join(missing)}")

    canonical = skills_root / "get-things-done/references/core-contract.md"
    builder = skills_root / "building-gtd-domain-packs/references/core-contract.md"
    router = skills_root / "gtd-capability-router/references/core-contract.md"
    if not canonical.is_file() or not builder.is_file() or not router.is_file():
        raise UpdateError("core contract copies are incomplete")
    canonical_text = canonical.read_text(encoding="utf-8")
    if builder.read_text(encoding="utf-8") != canonical_text:
        raise UpdateError("domain-pack builder core contract is not synchronized")
    if router.read_text(encoding="utf-8") != canonical_text:
        raise UpdateError("capability-router core contract is not synchronized")


def preserve_custom_domains(current_skills_root: Path, staged_skills_root: Path) -> list[str]:
    current = current_skills_root / "get-things-done/domains"
    staged = staged_skills_root / "get-things-done/domains"
    if not current.is_dir() or not staged.is_dir():
        return []
    preserved: list[str] = []
    for path in current.glob("*.md"):
        dest = staged / path.name
        if dest.exists():
            continue
        shutil.copy2(path, dest)
        preserved.append(path.name)
    return sorted(preserved)


def _transactional_replace(staged_skills_root: Path, target_skills_root: Path) -> None:
    target_skills_root.mkdir(parents=True, exist_ok=True)
    backup_parent = Path(tempfile.mkdtemp(prefix=".gtd-backup-", dir=str(target_skills_root.parent)))
    backups: dict[str, Path] = {}
    installed: list[str] = []
    try:
        for name in SKILL_NAMES:
            source = staged_skills_root / name
            target = target_skills_root / name
            backup = backup_parent / name
            if target.exists():
                os.replace(target, backup)
                backups[name] = backup
            os.replace(source, target)
            installed.append(name)
    except Exception:
        for name in reversed(installed):
            target = target_skills_root / name
            if target.exists():
                shutil.rmtree(target, ignore_errors=True)
        for name, backup in backups.items():
            target = target_skills_root / name
            if backup.exists():
                os.replace(backup, target)
        raise
    finally:
        shutil.rmtree(backup_parent, ignore_errors=True)


def update_from_archive(
    archive: bytes,
    target_skills_root: Path,
    source: RemoteSource,
    *,
    force: bool = False,
) -> dict[str, Any]:
    target_skills_root = target_skills_root.expanduser().resolve()
    target_skills_root.parent.mkdir(parents=True, exist_ok=True)
    state = _read_state(target_skills_root)
    modified = local_modifications(target_skills_root, state)
    if modified and not force:
        sample = ", ".join(modified[:5])
        more = "" if len(modified) <= 5 else f" (+{len(modified) - 5} more)"
        raise UpdateError(
            "local canonical files changed since the previous update: "
            f"{sample}{more}. Re-run with --force to replace them."
        )

    temp_root = Path(tempfile.mkdtemp(prefix=".gtd-update-", dir=str(target_skills_root.parent)))
    staged = temp_root / "skills"
    staged.mkdir(parents=True)
    try:
        extract_skill_archive(archive, staged)
        validate_staged_skills(staged)
        manifest = _canonical_manifest(staged)
        preserved = preserve_custom_domains(target_skills_root, staged)
        _transactional_replace(staged, target_skills_root)
        validate_staged_skills(target_skills_root)
        _write_state(target_skills_root, source, manifest)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    return {
        "source": asdict(source),
        "target": str(target_skills_root),
        "preserved_custom_domains": preserved,
        "canonical_files": len(manifest),
    }


def resolve_target_skills_root(pack_root: Path, target_path: str | None = None) -> Path:
    if target_path:
        return Path(target_path).expanduser().resolve()

    root = pack_root.expanduser().resolve()
    if (root / "SKILL.md").is_file() and root.name == "get-things-done":
        return root.parent
    if (root / "skills").is_dir():
        return root / "skills"
    raise UpdateError("cannot infer the installed skills root; pass --target-path")


def _looks_like_homebrew(pack_root: Path) -> bool:
    parts = {part.lower() for part in pack_root.resolve().parts}
    return "cellar" in parts and "get-things-done" in parts


def run_update(
    *,
    pack_root: Path,
    channel: str = "latest",
    target_path: str | None = None,
    check: bool = False,
    force: bool = False,
    timeout: float = 15.0,
) -> int:
    root = pack_root.expanduser().resolve()
    if target_path is None and (root / ".git").exists():
        print("REFUSED: repository checkout detected.")
        print("Use git pull --ff-only for the repository, or pass --target-path for an installed Agent Skills root.")
        return 2
    if target_path is None and _looks_like_homebrew(root):
        print("REFUSED: Homebrew-managed installation detected.")
        print("Use: brew upgrade --fetch-HEAD get-things-done")
        print("Or pass --target-path to update a user Agent Skills root.")
        return 2

    try:
        skills_root = resolve_target_skills_root(root, target_path)
        source = resolve_remote(channel, timeout=timeout)
    except (UpdateError, urllib.error.URLError, OSError) as exc:
        print(f"UPDATE ERROR: {exc}")
        return 1

    state = _read_state(skills_root)
    current_ref = None
    if state and isinstance(state.get("source"), dict):
        current_ref = state["source"].get("ref")

    if current_ref == source.ref:
        print(f"UP TO DATE: {source.kind} {source.ref}")
        print(f"target: {skills_root}")
        return 0

    if check:
        print(f"UPDATE AVAILABLE: {source.kind} {source.ref}")
        print(f"installed: {current_ref or 'unknown/untracked'}")
        print(f"target: {skills_root}")
        return 0

    try:
        archive = _request(source.archive_url, timeout)
        result = update_from_archive(archive, skills_root, source, force=force)
    except (UpdateError, urllib.error.URLError, OSError, zipfile.BadZipFile) as exc:
        print(f"UPDATE ERROR: {exc}")
        return 1

    print(f"UPDATED: {source.kind} {source.ref}")
    print(f"target: {result['target']}")
    print(f"canonical files: {result['canonical_files']}")
    if result["preserved_custom_domains"]:
        print("preserved custom domains: " + ", ".join(result["preserved_custom_domains"]))
    doctor = skills_root / "get-things-done" / "scripts" / "gtd.py"
    print(f"Run: python {doctor} doctor")
    return 0
