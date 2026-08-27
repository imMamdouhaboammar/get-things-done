#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = ("get-things-done", "building-gtd-domain-packs")
SAFE_PATH_FIELDS = ("project_path", "fallback_path", "manifest", "requires")
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
RETIRED_REPO_NAME = "get-things-done-skillpack"
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)


def is_valid_semver(version: Any) -> bool:
    return isinstance(version, str) and bool(SEMVER_PATTERN.match(version))


def load_registry(root: Path = ROOT) -> dict[str, Any]:
    with (root / "adapters" / "registry.json").open(encoding="utf-8") as fh:
        return json.load(fh)


def load_companions(root: Path = ROOT) -> dict[str, Any]:
    with (root / "adapters" / "companions.json").open(encoding="utf-8") as fh:
        return json.load(fh)


def adapters_by_id(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in load_registry(root)["adapters"]}


def companions_by_id(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in load_companions(root)["companions"]}


def interop_matrix(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    matrix: dict[str, dict[str, Any]] = {}
    for item in load_companions(root)["companions"]:
        entry: dict[str, Any] = {
            "label": item["label"],
            "relationship": item["relationship"],
            "gtd_role": item["ownership"]["gtd"],
            "companion_role": item["ownership"]["companion"],
            "inputs": item.get("inputs", []),
            "outputs": item.get("outputs", []),
            "failure_policy": item.get("failure_policy", ""),
            "authority_boundary": item.get("authority_boundary", ""),
        }
        if "transport" in item:
            entry["transport"] = item["transport"]
        matrix[item["id"]] = entry
    return matrix


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _skill_source(root: Path, name: str) -> Path:
    path = root / "skills" / name
    if not (path / "SKILL.md").is_file():
        raise FileNotFoundError(f"missing canonical skill: {path / 'SKILL.md'}")
    return path


def _copy_skills(root: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for name in SKILL_NAMES:
        source = _skill_source(root, name)
        target = destination / name
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)


def validate_registry(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        data = load_registry(root)
    except Exception as exc:
        return [f"registry unreadable: {exc}"]
    if data.get("$schema") != "./registry.schema.json":
        errors.append("registry must reference ./registry.schema.json")
    items = data.get("adapters")
    if not isinstance(items, list) or not items:
        return errors + ["registry adapters must be a non-empty array"]
    ids: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            errors.append("adapter entry must be an object")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ident:
            errors.append("adapter id must be a non-empty string")
            continue
        if ident in ids:
            errors.append(f"duplicate adapter id: {ident}")
        ids.add(ident)
        for key in ("label", "family", "support", "kind", "export"):
            if not isinstance(item.get(key), str) or not item[key]:
                errors.append(f"{ident}: missing {key}")
        capabilities = item.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities or not all(isinstance(value, str) and value for value in capabilities):
            errors.append(f"{ident}: capabilities must be a non-empty string array")
        elif len(capabilities) != len(set(capabilities)):
            errors.append(f"{ident}: duplicate capabilities")
        for key in SAFE_PATH_FIELDS:
            if key in item and not _safe_relative_path(item[key]):
                errors.append(f"{ident}: unsafe {key}: {item[key]}")
        if item.get("support") == "conditional" and not item.get("requires"):
            errors.append(f"{ident}: conditional adapter must declare requires")
    required = {
        "agent-skills", "agent-plugins", "claude-ai", "claude-code", "claude-marketplace",
        "claude-cowork", "chatgpt-web", "chatgpt-work", "chatgpt-plugin", "codex", "cursor",
        "kimi", "grok", "deepseek", "homebrew", "shell", "skills-sh", "skill-kit", "glama"
    }
    missing = sorted(required - ids)
    if missing:
        errors.append("missing required adapters: " + ", ".join(missing))
    if not data.get("portability_contract"):
        errors.append("registry must declare portability_contract")
    return errors


def validate_companions(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        data = load_companions(root)
    except Exception as exc:
        return [f"companions unreadable: {exc}"]
    if data.get("$schema") != "./companions.schema.json":
        errors.append("companions must reference ./companions.schema.json")
    items = data.get("companions")
    if not isinstance(items, list) or not items:
        return errors + ["companions must be a non-empty array"]
    ids: set[str] = set()
    allowed_kinds = {"orchestration", "evaluation", "methodology", "security", "documentation"}
    allowed_relationships = {"complementary", "optional"}
    for item in items:
        if not isinstance(item, dict):
            errors.append("companion entry must be an object")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not ident:
            errors.append("companion id must be a non-empty string")
            continue
        if ident in ids:
            errors.append(f"duplicate companion id: {ident}")
        ids.add(ident)
        if item.get("kind") not in allowed_kinds:
            errors.append(f"{ident}: unsupported companion kind")
        if item.get("relationship") not in allowed_relationships:
            errors.append(f"{ident}: unsupported relationship")
        ownership = item.get("ownership")
        if not isinstance(ownership, dict) or not ownership.get("gtd") or not ownership.get("companion"):
            errors.append(f"{ident}: ownership must declare gtd and companion roles")
        for key in ("integration", "evidence_contract", "failure_policy", "authority_boundary"):
            val = item.get(key)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"{ident}: missing or empty {key}")
        for list_key in ("inputs", "outputs", "guardrails"):
            arr = item.get(list_key)
            if not isinstance(arr, list) or not arr or not all(isinstance(v, str) and v.strip() for v in arr):
                errors.append(f"{ident}: {list_key} must be a non-empty string array")
            elif len(arr) != len(set(arr)):
                errors.append(f"{ident}: duplicate {list_key}")
        for forbidden in ("manifest", "project_path", "export"):
            if forbidden in item:
                errors.append(f"{ident}: companion profiles cannot declare {forbidden}")
    required = {"plugin-autopilot", "plugin-eval", "superpowers", "armorcodex", "context7"}
    missing = sorted(required - ids)
    if missing:
        errors.append("missing required companions: " + ", ".join(missing))
    return errors


def validate_manifests(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    manifests = {
        "plugin.json": root / "plugin.json",
        ".codex-plugin/plugin.json": root / ".codex-plugin" / "plugin.json",
        ".claude-plugin/plugin.json": root / ".claude-plugin" / "plugin.json",
        ".claude-plugin/marketplace.json": root / ".claude-plugin" / "marketplace.json",
        "kimi.plugin.json": root / "kimi.plugin.json",
        "skills.sh.json": root / "skills.sh.json",
    }
    parsed: dict[str, Any] = {}
    for label, path in manifests.items():
        if not path.is_file():
            errors.append(f"missing manifest: {label}")
            continue
        try:
            content = path.read_text(encoding="utf-8")
            if RETIRED_REPO_NAME in content:
                errors.append(f"{label}: references retired repository identity {RETIRED_REPO_NAME}")
            parsed[label] = json.loads(content)
        except Exception as exc:
            errors.append(f"invalid JSON {label}: {exc}")

    # SemVer and version consistency check
    versions: dict[str, str] = {}
    for label in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json", "kimi.plugin.json"):
        data = parsed.get(label)
        if isinstance(data, dict) and "version" in data:
            ver = data["version"]
            if not is_valid_semver(ver):
                errors.append(f"{label}: invalid semver: {ver}")
            else:
                versions[label] = str(ver)
    if versions:
        first_ver = next(iter(versions.values()))
        for label, ver in versions.items():
            if ver != first_ver:
                errors.append(f"{label}: version mismatch ({ver} != {first_ver})")

    ap = parsed.get("plugin.json", {})
    if ap.get("$schema") != "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json":
        errors.append("plugin.json must declare Agent Plugins 1.0.0 schema")
    if ap.get("name") != "get-things-done":
        errors.append("plugin.json name mismatch")
    codex = parsed.get(".codex-plugin/plugin.json", {})
    if codex.get("skills") != "./skills/":
        errors.append("OpenAI plugin must reference ./skills/")
    interface = codex.get("interface") if isinstance(codex.get("interface"), dict) else {}
    for key in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        if not interface.get(key):
            errors.append(f"OpenAI plugin interface missing {key}")
    for key in ("composerIcon", "logo"):
        value = interface.get(key)
        if not isinstance(value, str) or not value.startswith("./"):
            errors.append(f"OpenAI plugin {key} must be a relative ./ path")
        elif not (root / value[2:]).is_file():
            errors.append(f"OpenAI plugin {key} path does not exist: {value}")
    kimi = parsed.get("kimi.plugin.json", {})
    if kimi.get("skills") != "./skills/":
        errors.append("Kimi plugin must reference ./skills/")
    skills_sh = parsed.get("skills.sh.json", {})
    if skills_sh.get("$schema") != "https://skills.sh/schemas/skills.sh.schema.json":
        errors.append("skills.sh.json schema mismatch")
    if not (root / "install.sh").is_file():
        errors.append("missing shell installer: install.sh")
    formula = root / "Formula" / "get-things-done.rb"
    if not formula.is_file():
        errors.append("missing Homebrew formula: Formula/get-things-done.rb")
    else:
        formula_text = formula.read_text(encoding="utf-8")
        if "class GetThingsDone < Formula" not in formula_text:
            errors.append("Homebrew formula class mismatch")
        if RETIRED_REPO_NAME in formula_text:
            errors.append(f"Formula/get-things-done.rb: references retired repository identity {RETIRED_REPO_NAME}")
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors = validate_registry(root) + validate_companions(root) + validate_manifests(root)
    for name in SKILL_NAMES:
        try:
            _skill_source(root, name)
        except FileNotFoundError as exc:
            errors.append(str(exc))
    return errors


def export_adapter(adapter_id: str, out: Path, root: Path = ROOT) -> Path:
    registry = adapters_by_id(root)
    if adapter_id not in registry:
        raise KeyError(f"unknown adapter: {adapter_id}")
    adapter = registry[adapter_id]
    registry_errors = validate_registry(root)
    if registry_errors:
        raise RuntimeError("invalid adapter registry: " + "; ".join(registry_errors))
    if adapter["support"] == "conditional":
        required = root / adapter["requires"]
        if not required.exists():
            raise RuntimeError(f"{adapter_id} requires {adapter['requires']}; refusing to generate fake support")

    target = out / adapter_id
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    export_kind = adapter["export"]

    if export_kind == "skills-layout":
        _copy_skills(root, target / adapter.get("project_path", ".agents/skills"))
    elif export_kind == "agent-plugin":
        shutil.copy2(root / "plugin.json", target / "plugin.json")
        _copy_skills(root, target / "skills")
    elif export_kind == "openai-plugin":
        (target / ".codex-plugin").mkdir()
        shutil.copy2(root / ".codex-plugin" / "plugin.json", target / ".codex-plugin" / "plugin.json")
        _copy_skills(root, target / "skills")
    elif export_kind == "claude-plugin":
        (target / ".claude-plugin").mkdir()
        shutil.copy2(root / ".claude-plugin" / "plugin.json", target / ".claude-plugin" / "plugin.json")
        shutil.copy2(root / ".claude-plugin" / "marketplace.json", target / ".claude-plugin" / "marketplace.json")
        _copy_skills(root, target / "skills")
    elif export_kind == "kimi-plugin":
        shutil.copy2(root / "kimi.plugin.json", target / "kimi.plugin.json")
        _copy_skills(root, target / "skills")
    elif export_kind == "homebrew-formula":
        (target / "Formula").mkdir()
        shutil.copy2(root / "Formula" / "get-things-done.rb", target / "Formula" / "get-things-done.rb")
        _copy_skills(root, target / "skills")
    elif export_kind == "shell-bundle":
        shutil.copy2(root / "install.sh", target / "install.sh")
        _copy_skills(root, target / "skills")
    elif export_kind == "skills-sh":
        shutil.copy2(root / "skills.sh.json", target / "skills.sh.json")
        _copy_skills(root, target / "skills")
    elif export_kind == "skill-kit-bridge":
        _copy_skills(root, target / "skills")
        (target / "README.md").write_text(
            "# Skill Kit bridge\n\nThe canonical GTD skills are already Agent Skills packages. "
            "Use @contentful/skill-kit only when compiling GTD behavior into a typed workflow or reference skill.\n",
            encoding="utf-8",
        )
    elif export_kind == "conditional-mcp":
        shutil.copy2(root / adapter["requires"], target / adapter["requires"])
    else:
        raise RuntimeError(f"unsupported export kind: {export_kind}")

    (target / "adapter.json").write_text(json.dumps(adapter, indent=2) + "\n", encoding="utf-8")
    return target


def package_directory(directory: Path) -> Path:
    zip_path = directory.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(p for p in directory.rglob("*") if p.is_file()):
            relative = path.relative_to(directory).as_posix()
            info = zipfile.ZipInfo(relative, date_time=ZIP_TIMESTAMP)
            info.create_system = 3
            info.compress_type = zipfile.ZIP_DEFLATED
            mode = path.stat().st_mode & 0o777
            info.external_attr = mode << 16
            zf.writestr(info, path.read_bytes())
    return zip_path


def cmd_list(args: argparse.Namespace) -> int:
    items = load_registry(Path(args.root))["adapters"]
    if args.json:
        print(json.dumps(items, indent=2))
        return 0
    for item in items:
        print(f"{item['id']:20} {item['support']:16} {item['label']}")
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    item = adapters_by_id(Path(args.root)).get(args.adapter)
    if not item:
        print(f"unknown adapter: {args.adapter}", file=sys.stderr)
        return 2
    print(json.dumps(item, indent=2))
    return 0


def cmd_companions(args: argparse.Namespace) -> int:
    items = load_companions(Path(args.root))["companions"]
    if args.json:
        print(json.dumps(items, indent=2))
        return 0
    for item in items:
        print(f"{item['id']:20} {item['relationship']:16} {item['label']}")
    return 0


def cmd_interop(args: argparse.Namespace) -> int:
    matrix = interop_matrix(Path(args.root))
    if args.companion:
        item = matrix.get(args.companion)
        if item is None:
            print(f"unknown companion: {args.companion}", file=sys.stderr)
            return 2
        print(json.dumps(item, indent=2))
        return 0
    print(json.dumps(matrix, indent=2))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    errors = validate(Path(args.root))
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    root = Path(args.root)
    print(
        f"PASS: {len(load_registry(root)['adapters'])} adapter contracts and "
        f"{len(load_companions(root)['companions'])} companion profiles valid"
    )
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    try:
        target = export_adapter(args.adapter, Path(args.out), Path(args.root))
    except RuntimeError as exc:
        prefix = "CONDITIONAL" if "refusing to generate fake support" in str(exc) else "ERROR"
        print(f"{prefix}: {exc}", file=sys.stderr)
        return 3 if prefix == "CONDITIONAL" else 2
    except (KeyError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(package_directory(target) if args.package else target)
    return 0


def cmd_export_all(args: argparse.Namespace) -> int:
    root = Path(args.root)
    out = Path(args.out)
    errors = validate_registry(root)
    if errors:
        print("ERROR: invalid adapter registry", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 2
    exported = 0
    packaged = 0
    skipped: list[str] = []
    for item in load_registry(root)["adapters"]:
        try:
            target = export_adapter(item["id"], out, root)
            exported += 1
            if args.package:
                package_directory(target)
                packaged += 1
        except RuntimeError as exc:
            if item.get("support") == "conditional" and "refusing to generate fake support" in str(exc):
                skipped.append(item["id"])
            else:
                raise
    print(f"exported: {exported}")
    if args.package:
        print(f"packaged: {packaged}")
    if skipped:
        print("conditional: " + ", ".join(skipped))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GTD host adapter validator, exporter, and interoperability inspector")
    parser.add_argument("--root", default=str(ROOT))
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("list"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_list)
    p = subs.add_parser("info"); p.add_argument("adapter"); p.set_defaults(func=cmd_info)
    p = subs.add_parser("companions"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_companions)
    p = subs.add_parser("interop"); p.add_argument("companion", nargs="?"); p.set_defaults(func=cmd_interop)
    p = subs.add_parser("validate"); p.set_defaults(func=cmd_validate)
    p = subs.add_parser("export"); p.add_argument("adapter"); p.add_argument("--out", required=True); p.add_argument("--package", action="store_true"); p.set_defaults(func=cmd_export)
    p = subs.add_parser("export-all"); p.add_argument("--out", required=True); p.add_argument("--package", action="store_true"); p.set_defaults(func=cmd_export_all)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
