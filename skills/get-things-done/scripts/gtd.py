#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import runpy
import sys
import zipfile
from decimal import Decimal
from pathlib import Path
from typing import Any

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

try:
    from chatgpt_bridge import ChatgptBridge
except ImportError:
    try:
        from .chatgpt_bridge import ChatgptBridge
    except Exception:
        ChatgptBridge = None

try:
    from improve_bridge import ImproveBridge
except ImportError:
    try:
        from .improve_bridge import ImproveBridge
    except Exception:
        ImproveBridge = None

STATUSES = {
    "captured",
    "clarifying",
    "researching",
    "modeling",
    "ready",
    "executing",
    "verifying",
    "done",
    "blocked",
}
REQUIRED_TOP = [
    "version",
    "title",
    "domain",
    "intent",
    "status",
    "scope",
    "knowledge",
    "decisions",
    "workstreams",
    "deliverables",
    "verification",
    "next_action",
]
NESTED_REQUIRED = {
    "intent": ["problem", "desired_outcome", "actor"],
    "scope": ["in", "out", "constraints"],
    "knowledge": ["facts", "assumptions", "unknowns"],
    "verification": ["success_criteria", "evidence"],
}
EXPORT_SUFFIXES = {
    "md": ".md",
    "json": ".json",
    "toon": ".toon",
    "mermaid": ".mmd",
    "graph-json": ".graph.json",
}


def pack_root(explicit: str | None = None) -> Path:
    if explicit:
        return Path(explicit).expanduser().resolve()
    inherited = os.environ.get("GTD_PACK_ROOT")
    if inherited:
        return Path(inherited).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def skill_dir(root: Path) -> Path:
    """Resolve the get-things-done skill in a full pack or standalone install."""
    if (root / "SKILL.md").exists() and (root / "domains").is_dir():
        return root
    return root / "skills" / "get-things-done"


def domains_dir(root: Path) -> Path:
    return skill_dir(root) / "domains"


def references_dir(root: Path) -> Path:
    return skill_dir(root) / "references"


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _runtime_script(root: Path, filename: str) -> dict[str, Any]:
    path = skill_dir(root) / "scripts" / filename
    if not path.is_file():
        raise FileNotFoundError(path)
    return runpy.run_path(str(path), run_name=f"gtd_runtime_{path.stem}")


def _schema_errors(payload: Any, root: Path) -> list[str]:
    if not isinstance(payload, dict):
        return ["$: brief must be a JSON object"]

    version = payload.get("version")
    if version is None:
        return ["$.version: required property is missing"]
    if version not in {"1.0", "2.0"}:
        return [f"$.version: unsupported brief version {version!r}"]

    schema_name = "execution-brief.schema.json" if version == "1.0" else "execution-brief-v2.schema.json"
    schema = read_json(references_dir(root) / schema_name)
    validator_ns = _runtime_script(root, "schema_validation.py")
    validate_instance = validator_ns.get("validate_instance")
    if not callable(validate_instance):
        raise RuntimeError("schema validator has no validate_instance()")
    errors = list(validate_instance(payload, schema))

    if version == "2.0" and not errors:
        v2_ns = _runtime_script(root, "brief_v2.py")
        semantic = v2_ns.get("semantic_validation_errors_v2")
        if not callable(semantic):
            raise RuntimeError("brief_v2 runtime has no semantic_validation_errors_v2()")
        errors.extend(semantic(payload))
    return errors


def validate_brief(payload: Any, root: Path | None = None) -> list[str]:
    return _schema_errors(payload, root or pack_root())



def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def readiness_gaps(payload: dict[str, Any]) -> list[str]:
    """Return deterministic structural gaps for the core Definition of Ready."""
    gaps: list[str] = []
    intent = payload.get("intent") if isinstance(payload.get("intent"), dict) else {}
    scope = payload.get("scope") if isinstance(payload.get("scope"), dict) else {}
    verification = payload.get("verification") if isinstance(payload.get("verification"), dict) else {}

    if not _nonempty_text(intent.get("desired_outcome")):
        gaps.append("desired outcome is empty")
    if not scope.get("in"):
        gaps.append("in-scope work is empty")
    if payload.get("open_decisions"):
        gaps.append("blocking decisions remain open")
    if payload.get("blockers"):
        gaps.append("blockers remain")
    if not verification.get("success_criteria"):
        gaps.append("success criteria are empty")
    if not _nonempty_text(payload.get("next_action")):
        gaps.append("next executable action is missing")
    return gaps


def done_gaps(payload: dict[str, Any]) -> list[str]:
    """Return deterministic structural gaps for the legacy v1 Definition of Done."""
    gaps: list[str] = []
    verification = payload.get("verification") if isinstance(payload.get("verification"), dict) else {}

    if not payload.get("deliverables"):
        gaps.append("deliverables are empty")
    if not verification.get("success_criteria"):
        gaps.append("success criteria are empty")
    if not verification.get("evidence"):
        gaps.append("verification evidence is empty")
    else:
        gaps.append(
            "v1 verification evidence is unlinked and cannot prove verified Done; migrate to v2 for criterion-linked evidence"
        )
    if payload.get("open_decisions"):
        gaps.append("blocking decisions remain open")
    if payload.get("blockers"):
        gaps.append("blockers remain")
    return gaps


def assess_brief(payload: dict[str, Any]) -> dict[str, Any]:
    ready_gaps = readiness_gaps(payload)
    completion_gaps = done_gaps(payload)
    return {
        "version": "1.0",
        "ready": not ready_gaps,
        "done": not completion_gaps,
        "ready_gaps": ready_gaps,
        "done_gaps": completion_gaps,
    }


def cmd_doctor(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    skill = skill_dir(root)
    required = [
        skill / "SKILL.md",
        skill / "references/core-contract.md",
        skill / "references/domain-pack-spec.md",
        skill / "references/execution-brief.schema.json",
        skill / "references/execution-brief-v2.schema.json",
        skill / "scripts/schema_validation.py",
        skill / "scripts/brief_v2.py",
        skill / "templates/execution-brief.md",
        skill / "scripts/updater.py",
        skill / "references/updating.md",
    ]
    builder = root / "skills/building-gtd-domain-packs/SKILL.md"
    router = root / "skills/gtd-capability-router/SKILL.md"
    deliberation = root / "skills/gtd-deliberation/SKILL.md"
    if (root / "skills").is_dir():
        required.extend([builder, router, deliberation])
    missing = [str(p.relative_to(root)) for p in required if not p.exists()]
    try:
        schema_v1 = read_json(references_dir(root) / "execution-brief.schema.json")
        schema_v2 = read_json(references_dir(root) / "execution-brief-v2.schema.json")
        schema_ok = (
            schema_v1.get("title") == "Execution Brief v1"
            and schema_v2.get("title") == "Execution Brief v2"
        )
    except (json.JSONDecodeError, OSError, KeyError):
        schema_ok = False
    names = sorted(p.stem for p in domains_dir(root).glob("*.md")) if domains_dir(root).exists() else []
    adapter_ok = True
    if (root / "adapters" / "registry.json").is_file():
        try:
            reg_data = read_json(root / "adapters" / "registry.json")
            comps_data = read_json(root / "adapters" / "companions.json")
            adapter_ok = bool(reg_data.get("adapters")) and bool(comps_data.get("companions"))
        except (json.JSONDecodeError, OSError, KeyError):
            adapter_ok = False
    if missing or not schema_ok or not names or not adapter_ok:
        print("FAIL")
        if missing:
            print("missing:", ", ".join(missing))
        if not schema_ok:
            print("schema: invalid")
        if not names:
            print("domains: none")
        if not adapter_ok:
            print("adapters: invalid")
        return 1
    adapter_msg = ", adapter registry verified" if (root / "adapters" / "registry.json").is_file() else ""
    print(f"PASS: core files valid, schema readable, {len(names)} domain packs found{adapter_msg}")
    return 0


def cmd_list_domains(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    for path in sorted(domains_dir(root).glob("*.md")):
        print(path.stem)
    return 0


def valid_slug(value: str) -> str:
    slug = value.strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("slug must contain lowercase letters, numbers, and hyphens only")
    return slug


def domain_template(slug: str, name: str) -> str:
    lines = [
        "---",
        f"domain: {slug}",
        "version: 1",
        "extends: gtd-core-v1",
        "---",
        "",
        f"# GTD Domain Pack: {name}",
        "",
        "## Selection signals",
        "",
        "Describe tasks and intent patterns that indicate this field, plus at least one non-selection signal",
        "",
        "## Domain vocabulary",
        "",
        "List concepts that must remain distinct because confusing them changes the work",
        "",
        "## Diagnostic questions",
        "",
        "List only questions whose answers can materially change scope, decisions, execution, risk, or verification",
        "",
        "## Extra brief fields",
        "",
        "List optional keys stored under `domain_data`",
        "",
        "## Readiness additions",
        "",
        "List observable extra checks before execution",
        "",
        "## Workstream patterns",
        "",
        "List 2 to 4 reusable decompositions with outcomes and dependency edges",
        "",
        "## Review additions",
        "",
        "List field-specific checks that catch plausible near-misses",
        "",
        "## Completion checks",
        "",
        "List observable evidence required for completion",
        "",
        "## Common traps",
        "",
        "List productive-looking failure patterns",
        "",
    ]
    return "\n".join(lines)


def cmd_new_domain(args: argparse.Namespace) -> int:
    try:
        slug = valid_slug(args.slug)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    name = args.name or slug.replace("-", " ").title()
    out = Path(args.output).expanduser().resolve() if args.output else domains_dir(pack_root(args.root)) / f"{slug}.md"
    if out.exists() and not args.force:
        print(f"ERROR: exists: {out}", file=sys.stderr)
        return 2
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(domain_template(slug, name), encoding="utf-8")
    print(out)
    return 0


def blank_brief(title: str, domain: str | None) -> dict[str, Any]:
    return {
        "version": "1.0",
        "title": title,
        "domain": domain,
        "intent": {"problem": "", "desired_outcome": "", "actor": None},
        "status": "captured",
        "scope": {"in": [], "out": [], "constraints": []},
        "knowledge": {"facts": [], "assumptions": [], "unknowns": []},
        "decisions": [],
        "open_decisions": [],
        "workstreams": [],
        "deliverables": [],
        "risks": [],
        "domain_data": {},
        "verification": {"success_criteria": [], "evidence": []},
        "next_action": None,
        "blockers": [],
    }


def cmd_new_brief(args: argparse.Namespace) -> int:
    out = Path(args.out).expanduser().resolve()
    if out.exists() and not args.force:
        print(f"ERROR: exists: {out}", file=sys.stderr)
        return 2
    if getattr(args, "version", "1.0") == "2.0":
        namespace = _runtime_script(pack_root(args.root), "brief_v2.py")
        constructor = namespace.get("blank_brief_v2")
        if not callable(constructor):
            print("ERROR: brief_v2 runtime has no blank_brief_v2()", file=sys.stderr)
            return 1
        payload = constructor(args.title, args.domain)
    else:
        payload = blank_brief(args.title, args.domain)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


def _read_payload_for_cli(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = read_json(path)
    except (json.JSONDecodeError, OSError, UnicodeError) as exc:
        return None, f"cannot read JSON: {exc}"
    if not isinstance(payload, dict):
        return None, "brief must be a JSON object"
    return payload, None


def _domain_error(payload: dict[str, Any], root: Path) -> str | None:
    domain = payload.get("domain")
    if isinstance(domain, str):
        domain_path = domains_dir(root) / f"{domain}.md"
        if not domain_path.exists():
            return f"domain pack not found: {domain}"
    return None


def cmd_validate_brief(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    payload, read_error = _read_payload_for_cli(path)
    if read_error:
        print(f"INVALID: {read_error}")
        return 1
    assert payload is not None
    root = pack_root(args.root)
    errors = validate_brief(payload, root)
    domain_error = _domain_error(payload, root)
    if domain_error:
        errors.append(domain_error)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALID v{payload['version']}")
    return 0


def cmd_assess_brief(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    payload, read_error = _read_payload_for_cli(path)
    if read_error:
        print(f"INVALID: {read_error}")
        return 1
    assert payload is not None
    root = pack_root(args.root)
    errors = validate_brief(payload, root)
    domain_error = _domain_error(payload, root)
    if domain_error:
        errors.append(domain_error)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    if payload["version"] == "2.0":
        namespace = _runtime_script(root, "brief_v2.py")
        assessor = namespace.get("assess_brief_v2")
        if not callable(assessor):
            print("ERROR: brief_v2 runtime has no assess_brief_v2()", file=sys.stderr)
            return 1
        assessment = assessor(payload)
    else:
        assessment = assess_brief(payload)

    requirement_met = (
        args.require == "valid"
        or (args.require == "ready" and bool(assessment["ready"]))
        or (args.require == "done" and bool(assessment["done"]))
    )
    assessment["requirement"] = args.require
    assessment["requirement_met"] = requirement_met

    if args.json:
        print(json.dumps(assessment, indent=2))
    else:
        print(f"VERSION: {assessment['version']}")
        print(f"READY: {'YES' if assessment['ready'] else 'NO'}")
        for gap in assessment["ready_gaps"]:
            print(f"- ready gap: {gap}")
        print(f"DONE: {'YES' if assessment['done'] else 'NO'}")
        for gap in assessment["done_gaps"]:
            print(f"- done gap: {gap}")
        print(f"REQUIREMENT {args.require.upper()}: {'MET' if requirement_met else 'NOT MET'}")
    return 0 if requirement_met else 2


def cmd_migrate_brief(args: argparse.Namespace) -> int:
    source = Path(args.path).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    if out.exists() and not args.force:
        print(f"ERROR: exists: {out}", file=sys.stderr)
        return 2
    payload, read_error = _read_payload_for_cli(source)
    if read_error:
        print(f"INVALID: {read_error}")
        return 1
    assert payload is not None
    root = pack_root(args.root)
    if payload.get("version") != "1.0":
        print("INVALID: migration requires an Execution Brief with version 1.0")
        return 1
    errors = validate_brief(payload, root)
    if errors:
        print("INVALID SOURCE")
        for error in errors:
            print(f"- {error}")
        return 1

    namespace = _runtime_script(root, "brief_v2.py")
    migrate = namespace.get("migrate_v1_to_v2")
    if not callable(migrate):
        print("ERROR: brief_v2 runtime has no migrate_v1_to_v2()", file=sys.stderr)
        return 1
    migrated = migrate(payload)
    migrated_errors = validate_brief(migrated, root)
    if migrated_errors:
        print("INVALID MIGRATION OUTPUT", file=sys.stderr)
        for error in migrated_errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(migrated, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0



def render_brief(payload: dict[str, Any]) -> str:
    def bullets(items: list[Any]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- None recorded"

    intent, scope = payload["intent"], payload["scope"]
    knowledge, verification = payload["knowledge"], payload["verification"]
    decisions = payload.get("decisions", [])
    workstreams = payload.get("workstreams", [])
    decision_rows = (
        "\n".join(
            f"| {d.get('decision', '')} | {d.get('rationale', '')} | {d.get('reversible', '')} |" for d in decisions
        )
        or "| None | | |"
    )
    work_rows = (
        "\n".join(
            f"| {w.get('name', '')} | {w.get('outcome', '')} | {', '.join(w.get('dependencies', []))} |"
            for w in workstreams
        )
        or "| None | | |"
    )
    parts = [
        f"# Execution Brief: {payload['title']}",
        "",
        "## Outcome",
        f"- Problem: {intent.get('problem', '')}",
        f"- Desired outcome: {intent.get('desired_outcome', '')}",
        f"- Actor: {intent.get('actor')}",
        f"- Status: {payload.get('status')}",
        f"- Domain: {payload.get('domain')}",
        "",
        "## Scope",
        "### In",
        bullets(scope.get("in", [])),
        "",
        "### Out",
        bullets(scope.get("out", [])),
        "",
        "### Constraints",
        bullets(scope.get("constraints", [])),
        "",
        "## Knowledge Ledger",
        "### Facts",
        bullets(knowledge.get("facts", [])),
        "",
        "### Assumptions",
        bullets(knowledge.get("assumptions", [])),
        "",
        "### Unknowns",
        bullets(knowledge.get("unknowns", [])),
        "",
        "## Decisions",
        "| Decision | Rationale | Reversible |",
        "|---|---|---|",
        decision_rows,
        "",
        "## Open Decisions",
        bullets(payload.get("open_decisions", [])),
        "",
        "## Workstreams",
        "| Workstream | Outcome | Dependencies |",
        "|---|---|---|",
        work_rows,
        "",
        "## Deliverables",
        bullets(payload.get("deliverables", [])),
        "",
        "## Risks",
        bullets(payload.get("risks", [])),
        "",
        "## Verification",
        "### Success criteria",
        bullets(verification.get("success_criteria", [])),
        "",
        "### Evidence",
        bullets(verification.get("evidence", [])),
        "",
        "## Blockers",
        bullets(payload.get("blockers", [])),
        "",
        "## Next executable action",
        f"- {payload.get('next_action') or 'Not set'}",
        "",
    ]
    return "\n".join(parts)


def _toon_is_primitive(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _toon_quote(value: str) -> str:
    escaped: list[str] = []
    for char in value:
        codepoint = ord(char)
        if char == "\\":
            escaped.append("\\\\")
        elif char == '"':
            escaped.append('\\"')
        elif char == "\n":
            escaped.append("\\n")
        elif char == "\r":
            escaped.append("\\r")
        elif char == "\t":
            escaped.append("\\t")
        elif codepoint < 0x20:
            escaped.append(f"\\u{codepoint:04x}")
        else:
            escaped.append(char)
    return f'"{"".join(escaped)}"'


def _toon_key(value: str) -> str:
    return value if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", value) else _toon_quote(value)


def _toon_string(value: str, delimiter: str = ",") -> str:
    numeric_like = re.fullmatch(r"[+-]?[0-9]+(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?", value, re.IGNORECASE)
    must_quote = (
        not value
        or value[:1] in {"-", "#"}
        or value in {"true", "false", "null"}
        or value[:1] in {" ", "\t"}
        or value[-1:] in {" ", "\t"}
        or numeric_like is not None
        or delimiter in value
        or any(char in value for char in ':"\\[]{}')
        or any(ord(char) < 0x20 for char in value)
    )
    return _toon_quote(value) if must_quote else value


def _toon_number(value: int | float) -> str:
    if isinstance(value, int):
        return str(value)
    if not math.isfinite(value):
        return "null"
    if value == 0:
        return "0"
    magnitude = abs(value)
    if 1e-6 <= magnitude < 1e21:
        text = format(Decimal(repr(value)), "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text
    text = repr(value).lower()
    if "e" not in text:
        return text
    mantissa, exponent = text.split("e", 1)
    normalized_exponent = int(exponent)
    sign = "+" if normalized_exponent >= 0 else "-"
    return f"{mantissa}e{sign}{abs(normalized_exponent)}"


def _toon_primitive(value: Any, delimiter: str = ",") -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return _toon_number(value)
    if isinstance(value, str):
        return _toon_string(value, delimiter)
    raise TypeError(f"TOON supports JSON values only, got {type(value).__name__}")


def _toon_uniform_fields(objects: list[dict[str, Any]]) -> list[tuple[str, Any]] | None:
    if not objects or any(not item for item in objects):
        return None
    keys = list(objects[0])
    expected = set(keys)
    if any(set(item) != expected for item in objects[1:]):
        return None

    fields: list[tuple[str, Any]] = []
    for key in keys:
        values = [item[key] for item in objects]
        if all(_toon_is_primitive(value) for value in values):
            fields.append((key, None))
            continue
        if all(isinstance(value, dict) and value for value in values):
            nested = _toon_uniform_fields(values)
            if nested is not None:
                fields.append((key, nested))
                continue
        return None
    return fields


def _toon_field_list(fields: list[tuple[str, Any]]) -> str:
    encoded: list[str] = []
    for key, nested in fields:
        item = _toon_key(key)
        if nested is not None:
            item += "{" + _toon_field_list(nested) + "}"
        encoded.append(item)
    return ",".join(encoded)


def _toon_row_values(payload: dict[str, Any], fields: list[tuple[str, Any]]) -> list[Any]:
    values: list[Any] = []
    for key, nested in fields:
        if nested is None:
            values.append(payload[key])
        else:
            values.extend(_toon_row_values(payload[key], nested))
    return values


def _toon_keyed_fields(payload: dict[str, Any]) -> list[tuple[str, Any]] | None:
    if len(payload) < 2 or not all(isinstance(value, dict) for value in payload.values()):
        return None
    return _toon_uniform_fields(list(payload.values()))


def _toon_emit_keyed_table(
    key: str | None,
    payload: dict[str, Any],
    fields: list[tuple[str, Any]],
    depth: int,
    lines: list[str],
) -> None:
    prefix = _toon_key(key) if key is not None else ""
    lines.append(f"{'  ' * depth}{prefix}[{len(payload)}:]{{{_toon_field_list(fields)}}}:")
    for entry_key, entry in payload.items():
        values = ",".join(_toon_primitive(value) for value in _toon_row_values(entry, fields))
        lines.append(f"{'  ' * (depth + 1)}{_toon_key(entry_key)}: {values}")


def _toon_emit_array(key: str | None, values: list[Any], depth: int, lines: list[str]) -> None:
    prefix = _toon_key(key) if key is not None else ""
    indentation = "  " * depth
    if not values:
        lines.append(f"{indentation}{prefix}: []" if key is not None else "[]")
        return
    if all(_toon_is_primitive(value) for value in values):
        encoded = ",".join(_toon_primitive(value) for value in values)
        lines.append(f"{indentation}{prefix}[{len(values)}]: {encoded}")
        return
    if all(isinstance(value, dict) for value in values):
        fields = _toon_uniform_fields(values)
        if fields is not None:
            lines.append(f"{indentation}{prefix}[{len(values)}]{{{_toon_field_list(fields)}}}:")
            for value in values:
                row = ",".join(_toon_primitive(cell) for cell in _toon_row_values(value, fields))
                lines.append(f"{'  ' * (depth + 1)}{row}")
            return
    lines.append(f"{indentation}{prefix}[{len(values)}]:")
    for value in values:
        _toon_emit_list_item(value, depth + 1, lines)


def _toon_emit_field(key: str, value: Any, depth: int, lines: list[str]) -> None:
    indentation = "  " * depth
    encoded_key = _toon_key(key)
    if _toon_is_primitive(value):
        lines.append(f"{indentation}{encoded_key}: {_toon_primitive(value)}")
    elif isinstance(value, list):
        _toon_emit_array(key, value, depth, lines)
    elif isinstance(value, dict):
        fields = _toon_keyed_fields(value)
        if fields is not None:
            _toon_emit_keyed_table(key, value, fields, depth, lines)
            return
        lines.append(f"{indentation}{encoded_key}:")
        for child_key, child_value in value.items():
            _toon_emit_field(child_key, child_value, depth + 1, lines)
    else:
        raise TypeError(f"TOON supports JSON values only, got {type(value).__name__}")


def _toon_emit_list_item(value: Any, depth: int, lines: list[str]) -> None:
    indentation = "  " * depth
    if _toon_is_primitive(value):
        lines.append(f"{indentation}- {_toon_primitive(value)}")
        return
    if isinstance(value, list):
        if value and all(_toon_is_primitive(item) for item in value):
            encoded = ",".join(_toon_primitive(item) for item in value)
            lines.append(f"{indentation}- [{len(value)}]: {encoded}")
        else:
            lines.append(f"{indentation}- [{len(value)}]:")
            for item in value:
                _toon_emit_list_item(item, depth + 1, lines)
        return
    if isinstance(value, dict):
        if not value:
            lines.append(f"{indentation}-")
            return
        items = list(value.items())
        first_lines: list[str] = []
        _toon_emit_field(items[0][0], items[0][1], depth + 1, first_lines)
        field_indentation = "  " * (depth + 1)
        lines.append(f"{indentation}- {first_lines[0][len(field_indentation) :]}")
        lines.extend(first_lines[1:])
        for key, item in items[1:]:
            _toon_emit_field(key, item, depth + 1, lines)
        return
    raise TypeError(f"TOON supports JSON values only, got {type(value).__name__}")


def render_toon(payload: Any) -> str:
    """Encode a JSON-shaped value using TOON Specification 4.1 defaults."""
    lines: list[str] = []
    if _toon_is_primitive(payload):
        lines.append(_toon_primitive(payload))
    elif isinstance(payload, list):
        _toon_emit_array(None, payload, 0, lines)
    elif isinstance(payload, dict):
        fields = _toon_keyed_fields(payload)
        if fields is not None:
            _toon_emit_keyed_table(None, payload, fields, 0, lines)
        else:
            for key, value in payload.items():
                _toon_emit_field(key, value, 0, lines)
    else:
        raise TypeError(f"TOON supports JSON values only, got {type(payload).__name__}")
    return "\n".join(lines)


def brief_graph(payload: dict[str, Any]) -> dict[str, Any]:
    """Project an Execution Brief into a deterministic directed relational graph."""
    nodes: list[dict[str, Any]] = [
        {
            "id": "brief",
            "type": "brief",
            "label": payload["title"],
            "status": payload.get("status"),
            "domain": payload.get("domain"),
        }
    ]
    edges: list[dict[str, str]] = []
    workstreams = [item for item in payload.get("workstreams", []) if isinstance(item, dict)]
    workstream_ids: dict[str, str] = {}

    for index, workstream in enumerate(workstreams):
        node_id = f"workstream:{index}"
        label = str(workstream.get("name", f"Workstream {index + 1}"))
        workstream_ids.setdefault(label.strip().casefold(), node_id)
        nodes.append(
            {
                "id": node_id,
                "type": "workstream",
                "label": label,
                "outcome": workstream.get("outcome", ""),
            }
        )
        edges.append({"source": "brief", "target": node_id, "relation": "contains"})

    external_dependencies: dict[str, str] = {}
    for index, workstream in enumerate(workstreams):
        source = f"workstream:{index}"
        for dependency in workstream.get("dependencies", []):
            label = str(dependency)
            target = workstream_ids.get(label.strip().casefold())
            if target is None:
                normalized = label.strip().casefold()
                target = external_dependencies.get(normalized)
                if target is None:
                    target = f"dependency:{len(external_dependencies)}"
                    external_dependencies[normalized] = target
                    nodes.append({"id": target, "type": "external_dependency", "label": label})
            edges.append({"source": source, "target": target, "relation": "depends_on"})

    collections = [
        ("deliverables", "deliverable", "produces"),
        ("success_criteria", "success_criterion", "verified_by"),
        ("blockers", "blocker", "blocked_by"),
    ]
    verification = payload.get("verification", {})
    for field, node_type, relation in collections:
        values = verification.get(field, []) if field == "success_criteria" else payload.get(field, [])
        for index, value in enumerate(values):
            node_id = f"{node_type}:{index}"
            nodes.append({"id": node_id, "type": node_type, "label": str(value)})
            edges.append({"source": "brief", "target": node_id, "relation": relation})

    if payload.get("next_action"):
        nodes.append({"id": "next_action", "type": "next_action", "label": str(payload["next_action"])})
        edges.append({"source": "brief", "target": "next_action", "relation": "starts_with"})

    return {"graph_version": "1.0", "directed": True, "nodes": nodes, "edges": edges}


def render_mermaid(graph: dict[str, Any]) -> str:
    node_names = {node["id"]: f"n{index}" for index, node in enumerate(graph["nodes"])}
    lines = ["flowchart LR"]
    for node in graph["nodes"]:
        label = html.escape(str(node["label"]), quote=True).replace("\r\n", "<br/>")
        label = label.replace("\r", "<br/>").replace("\n", "<br/>")
        lines.append(f'  {node_names[node["id"]]}["{label}"]')
    for edge in graph["edges"]:
        source = node_names[edge["source"]]
        target = node_names[edge["target"]]
        lines.append(f"  {source} -->|{edge['relation']}| {target}")
    return "\n".join(lines) + "\n"


def render_export(payload: dict[str, Any], export_format: str) -> str:
    if export_format == "md":
        return render_brief(payload)
    if export_format == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if export_format == "toon":
        return render_toon(payload)
    graph = brief_graph(payload)
    if export_format == "mermaid":
        return render_mermaid(graph)
    if export_format == "graph-json":
        return json.dumps(graph, ensure_ascii=False, indent=2) + "\n"
    raise ValueError(f"unsupported brief export format: {export_format}")


def cmd_export_brief(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    try:
        payload = read_json(path)
    except (json.JSONDecodeError, OSError, UnicodeError) as exc:
        print(f"INVALID: cannot read JSON: {exc}", file=sys.stderr)
        return 1
    errors = validate_brief(payload)
    if errors:
        print("INVALID", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if payload.get("version") == "2.0":
        print(
            "ERROR: export-brief currently supports v1 only; use render-brief for v2 or migrate/export downstream explicitly",
            file=sys.stderr,
        )
        return 2

    if args.format == "all":
        selected = list(EXPORT_SUFFIXES)
    elif args.format == "graph":
        selected = ["mermaid", "graph-json"]
    else:
        selected = [args.format]
    out = Path(args.out).expanduser().resolve()
    try:
        if len(selected) == 1:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(render_export(payload, selected[0]), encoding="utf-8")
            print(out)
            return 0

        out.mkdir(parents=True, exist_ok=True)
        for export_format in selected:
            target = out / f"{path.stem}{EXPORT_SUFFIXES[export_format]}"
            target.write_text(render_export(payload, export_format), encoding="utf-8")
            print(target)
    except (OSError, TypeError, ValueError) as exc:
        print(f"ERROR: cannot export brief: {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_render_brief(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    payload, read_error = _read_payload_for_cli(path)
    if read_error:
        print(f"INVALID: {read_error}", file=sys.stderr)
        return 1
    assert payload is not None
    root = pack_root(args.root)
    errors = validate_brief(payload, root)
    if errors:
        print("INVALID", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if payload["version"] == "2.0":
        namespace = _runtime_script(root, "brief_v2.py")
        renderer = namespace.get("render_brief_v2")
        if not callable(renderer):
            print("ERROR: brief_v2 runtime has no render_brief_v2()", file=sys.stderr)
            return 1
        text = renderer(payload)
    else:
        text = render_brief(payload)
    if args.out:
        out = Path(args.out).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(out)
    else:
        print(text, end="")
    return 0


def cmd_package(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    out_dir = Path(args.out).expanduser().resolve() if args.out else root / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    skills_root = root / "skills" if (root / "skills").is_dir() else root.parent
    count = 0
    for s_name in ["get-things-done", "building-gtd-domain-packs", "gtd-capability-router", "gtd-deliberation"]:
        s_dir = skills_root / s_name
        if not s_dir.is_dir():
            continue
        dest_zip = out_dir / f"{s_name}.zip"
        with zipfile.ZipFile(dest_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(s_dir.rglob("*")):
                if f.is_file() and not f.name.startswith(".DS_Store") and "__pycache__" not in f.parts:
                    zf.write(f, arcname=str(f.relative_to(s_dir)))
        print(f"Built {dest_zip.name} ({dest_zip.stat().st_size:,} bytes)")
        count += 1
    print(f"PASS: packaged {count} standalone skill bundles to {out_dir}")
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    updater_path = skill_dir(root) / "scripts" / "updater.py"
    if not updater_path.is_file():
        print(f"UPDATE ERROR: updater not found: {updater_path}", file=sys.stderr)
        return 1
    namespace = runpy.run_path(str(updater_path), run_name="gtd_updater_runtime")
    run_update = namespace.get("run_update")
    if not callable(run_update):
        print(f"UPDATE ERROR: updater has no run_update(): {updater_path}", file=sys.stderr)
        return 1
    return int(
        run_update(
            pack_root=root,
            channel=args.channel,
            target_path=args.target_path,
            check=args.check,
            force=args.force,
            timeout=args.timeout,
        )
    )


def _get_bridge(root_path: Path) -> Any:
    if ChatgptBridge is None:
        raise RuntimeError("ChatgptBridge module could not be imported")
    return ChatgptBridge(root_path)


def cmd_chatgpt_route(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    bridge = _get_bridge(root)
    if not bridge.is_available():
        print("ERROR: chatgpt-skill Rust engine binary not found. Build it with cargo build in crates/use-chatgpt-engine.", file=sys.stderr)
        return 1

    prompt = args.prompt
    route_data = bridge.route_intent(prompt, format_type=args.format or "json")
    if not route_data.get("success"):
        print(f"ERROR: routing failed: {route_data.get('error')}", file=sys.stderr)
        return 1

    if args.into_brief:
        brief_path = Path(args.into_brief).expanduser().resolve()
        if brief_path.exists():
            payload = read_json(brief_path)
        else:
            payload = blank_brief(prompt[:60], "software")
        enriched = bridge.enrich_brief_with_route(payload, prompt)
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(json.dumps(enriched, indent=2) + "\n", encoding="utf-8")
        print(f"HYDRATED: {brief_path}")
        return 0

    if args.json:
        print(json.dumps(route_data, indent=2))
    else:
        print(f"Domain: {route_data.get('domain')}")
        print("=== Routing Packet ===")
        print(json.dumps(route_data.get("packet", {}), indent=2))
        if route_data.get("dag"):
            print("\n=== Execution DAG ===")
            print(route_data.get("dag"))
    return 0


def cmd_bot_gate(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    bridge = _get_bridge(root)
    if not bridge.is_available():
        print("ERROR: chatgpt-skill Rust engine binary not found.", file=sys.stderr)
        return 1

    bot_data = bridge.inspect_bot_gate(pr=args.pr)
    if not bot_data.get("success"):
        print(f"ERROR: bot-gate failed: {bot_data.get('error')}", file=sys.stderr)
        return 1

    if args.into_brief:
        brief_path = Path(args.into_brief).expanduser().resolve()
        if not brief_path.exists():
            print(f"ERROR: brief does not exist: {brief_path}", file=sys.stderr)
            return 2
        payload = read_json(brief_path)
        enriched = bridge.enrich_brief_with_bot_gate(payload, pr=args.pr)
        brief_path.write_text(json.dumps(enriched, indent=2) + "\n", encoding="utf-8")
        print(f"INGESTED: bot-gate dispositions into {brief_path} ({bot_data.get('actionable_count')} actionable)")
        return 0

    if args.json:
        print(json.dumps(bot_data, indent=2))
    else:
        print(bot_data.get("markdown", ""))
    return 0


def cmd_evidence_ladder(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    bridge = _get_bridge(root)
    path = Path(args.path).expanduser().resolve()
    try:
        payload = read_json(path)
    except Exception as exc:
        print(f"INVALID: cannot read JSON: {exc}", file=sys.stderr)
        return 1

    if args.into_brief:
        enriched = bridge.enrich_brief_with_evidence_ladder(payload)
        path.write_text(json.dumps(enriched, indent=2) + "\n", encoding="utf-8")
        print(f"GRADED: {path}")
        return 0

    evidence_items = payload.get("verification", {}).get("evidence", [])
    eval_res = bridge.evaluate_evidence(evidence_items)
    if args.json:
        print(json.dumps(eval_res, indent=2))
    else:
        print(f"HIGHEST LEVEL: {eval_res.get('highest_level')}")
        print(f"SUFFICIENT FOR DONE: {'YES' if eval_res.get('is_sufficient_for_done') else 'NO'}")
        for item in eval_res.get("evaluated", []):
            print(f"- [{item['level']}] {item['item']}")
    return 0


def cmd_macos_bridge(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    bridge = _get_bridge(root)
    if args.notify:
        ok = bridge.macos_notify(title=args.title or "GTD Notification", message=args.notify)
        if ok:
            print("NOTIFIED")
            return 0
        print("FAILED to notify", file=sys.stderr)
        return 1
    if args.copy:
        ok = bridge.macos_copy(args.copy)
        if ok:
            print("COPIED")
            return 0
        print("FAILED to copy", file=sys.stderr)
        return 1
    if args.paste:
        val = bridge.macos_paste()
        print(val, end="")
        return 0
    print("No macOS action specified (--notify, --copy, or --paste)", file=sys.stderr)
    return 2


def _get_improve_bridge(root_path: Path) -> Any:
    if ImproveBridge is None:
        raise RuntimeError("ImproveBridge module could not be imported")
    return ImproveBridge(root_path)


def cmd_improve_ingest(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    bridge = _get_improve_bridge(root)
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        print(f"ERROR: plan file not found: {path}", file=sys.stderr)
        return 1

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: cannot read plan file: {exc}", file=sys.stderr)
        return 1

    errors = bridge.validate_plan(text)
    if errors and not args.force:
        print("PLAN VALIDATION WARNINGS:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)

    parsed = bridge.parse_plan(text)
    brief = bridge.plan_to_brief(parsed, version=args.version or "1.0", domain=args.domain or "software")

    if args.into_brief:
        brief_path = Path(args.into_brief).expanduser().resolve()
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")
        print(f"INGESTED: {brief_path}")
        return 0

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")
        print(f"GENERATED: {out_path}")
        return 0

    if args.json:
        print(json.dumps(brief, indent=2))
    else:
        print(f"=== Plan Ingestion: {brief.get('title')} ===")
        print(f"Domain: {brief.get('domain')} | Status: {brief.get('status')} | Version: {brief.get('version')}")
        print(f"Workstreams: {len(brief.get('workstreams', []))} | Done Criteria: {len(brief.get('verification', {}).get('success_criteria', brief.get('verification', {}).get('criteria', [])))}")
        print(f"Next Action: {brief.get('next_action')}")
    return 0


def cmd_improve_validate(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    bridge = _get_improve_bridge(root)
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        print(f"ERROR: plan file not found: {path}", file=sys.stderr)
        return 1

    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"ERROR: cannot read plan file: {exc}", file=sys.stderr)
        return 1

    errors = bridge.validate_plan(text)
    if errors:
        print("INVALID", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print("PASS: plan adheres to Improve Senior Advisor and GTD standards")
    return 0


def cmd_improve_plan(args: argparse.Namespace) -> int:
    root = pack_root(args.root)
    bridge = _get_improve_bridge(root)
    scaffold = bridge.scaffold_plan(
        title=args.title,
        category=args.category or "tech-debt",
        priority=args.priority or "P2",
        effort=args.effort or "S",
        risk=args.risk or "LOW",
        in_scope=args.in_scope or None,
    )

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(scaffold, encoding="utf-8")
        print(f"SCAFFOLDED: {out_path}")
        return 0

    print(scaffold, end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gtd", description="Get Things Done skill pack utilities")
    sub = p.add_subparsers(dest="command", required=True)

    x = sub.add_parser("doctor")
    x.add_argument("--root")
    x.set_defaults(func=cmd_doctor)

    x = sub.add_parser("list-domains")
    x.add_argument("--root")
    x.set_defaults(func=cmd_list_domains)

    x = sub.add_parser("new-domain")
    x.add_argument("slug")
    x.add_argument("--name")
    x.add_argument("--output")
    x.add_argument("--root")
    x.add_argument("--force", action="store_true")
    x.set_defaults(func=cmd_new_domain)

    x = sub.add_parser("new-brief")
    x.add_argument("--title", required=True)
    x.add_argument("--domain")
    x.add_argument("--version", choices=["1.0", "2.0"], default="1.0")
    x.add_argument("--out", required=True)
    x.add_argument("--root")
    x.add_argument("--force", action="store_true")
    x.set_defaults(func=cmd_new_brief)

    x = sub.add_parser("validate-brief")
    x.add_argument("path")
    x.add_argument("--root")
    x.set_defaults(func=cmd_validate_brief)

    x = sub.add_parser("assess-brief")
    x.add_argument("path")
    x.add_argument("--json", action="store_true")
    x.add_argument("--require", choices=["valid", "ready", "done"], default="valid")
    x.add_argument("--root")
    x.set_defaults(func=cmd_assess_brief)

    x = sub.add_parser("migrate-brief")
    x.add_argument("path")
    x.add_argument("--out", required=True)
    x.add_argument("--root")
    x.add_argument("--force", action="store_true")
    x.set_defaults(func=cmd_migrate_brief)

    x = sub.add_parser("render-brief")
    x.add_argument("path")
    x.add_argument("--out")
    x.add_argument("--root")
    x.set_defaults(func=cmd_render_brief)

    x = sub.add_parser("export-brief")
    x.add_argument("path")
    x.add_argument("--format", required=True, choices=[*EXPORT_SUFFIXES, "graph", "all"])
    x.add_argument("--out", required=True)
    x.set_defaults(func=cmd_export_brief)

    x = sub.add_parser("package")
    x.add_argument("--out")
    x.add_argument("--root")
    x.set_defaults(func=cmd_package)

    x = sub.add_parser("update", help="refresh installed GTD Skills from the canonical GitHub repository")
    x.add_argument("--channel", choices=["latest", "stable", "main"], default="latest")
    x.add_argument("--target-path", help="Agent Skills root to update; inferred for a normal Skill install")
    x.add_argument("--check", action="store_true", help="check for an update without changing files")
    x.add_argument("--force", action="store_true", help="replace canonical files modified since the last managed update")
    x.add_argument("--timeout", type=float, default=15.0, help="network timeout in seconds")
    x.add_argument("--root", help=argparse.SUPPRESS)
    x.set_defaults(func=cmd_update)

    # Ultra-connected Use-ChatGPT & Rust Engine integration commands
    x = sub.add_parser("chatgpt-route", help="Route intent via Rust engine and generate execution DAG")
    x.add_argument("prompt", help="Natural language prompt or task to route")
    x.add_argument("--into-brief", help="Optional path to Execution Brief to hydrate with routing packet")
    x.add_argument("--format", default="json", choices=["json", "yaml"], help="Routing packet format")
    x.add_argument("--json", action="store_true", help="Print structured JSON result")
    x.add_argument("--root", help="Explicit pack root")
    x.set_defaults(func=cmd_chatgpt_route)

    x = sub.add_parser("bot-gate", help="Inspect PR bot comments and fence actionable items")
    x.add_argument("--pr", type=int, help="Optional PR number")
    x.add_argument("--into-brief", help="Optional path to Execution Brief to ingest actionable items")
    x.add_argument("--json", action="store_true", help="Print structured JSON result")
    x.add_argument("--root", help="Explicit pack root")
    x.set_defaults(func=cmd_bot_gate)

    x = sub.add_parser("evidence-ladder", help="Grade verification evidence against 5-Tier Trust Ladder")
    x.add_argument("path", help="Path to Execution Brief JSON")
    x.add_argument("--into-brief", action="store_true", help="Write graded evidence back into the brief")
    x.add_argument("--json", action="store_true", help="Print structured JSON evaluation")
    x.add_argument("--root", help="Explicit pack root")
    x.set_defaults(func=cmd_evidence_ladder)

    x = sub.add_parser("macos", help="Native macOS notification and clipboard bridge")
    x.add_argument("--notify", help="Notification alert message")
    x.add_argument("--title", default="GTD Alert", help="Notification alert title")
    x.add_argument("--copy", help="Text to copy to clipboard")
    x.add_argument("--paste", action="store_true", help="Print clipboard contents")
    x.add_argument("--root", help="Explicit pack root")
    x.set_defaults(func=cmd_macos_bridge)

    # Improve Codebase Advisor integration commands
    x = sub.add_parser("improve-ingest", help="Ingest an Improve implementation plan into a GTD Execution Brief")
    x.add_argument("path", help="Path to Improve plan markdown file (plans/NNN-*.md)")
    x.add_argument("--into-brief", help="Path to write or hydrate GTD Execution Brief")
    x.add_argument("--out", help="Path to write output Execution Brief JSON")
    x.add_argument("--version", choices=["1.0", "2.0"], default="1.0", help="Execution Brief schema version")
    x.add_argument("--domain", default="software", help="Domain pack for Execution Brief")
    x.add_argument("--force", action="store_true", help="Ingest despite plan validation warnings")
    x.add_argument("--json", action="store_true", help="Print brief JSON to stdout")
    x.add_argument("--root", help="Explicit pack root")
    x.set_defaults(func=cmd_improve_ingest)

    x = sub.add_parser("improve-validate", help="Validate an Improve implementation plan against advisor standards")
    x.add_argument("path", help="Path to Improve plan markdown file")
    x.add_argument("--root", help="Explicit pack root")
    x.set_defaults(func=cmd_improve_validate)

    x = sub.add_parser("improve-plan", help="Scaffold a new self-contained Improve implementation plan")
    x.add_argument("--title", required=True, help="Imperative plan title")
    x.add_argument("--category", default="tech-debt", help="Audit category")
    x.add_argument("--priority", default="P2", choices=["P1", "P2", "P3"], help="Priority level")
    x.add_argument("--effort", default="S", choices=["S", "M", "L"], help="Effort estimate")
    x.add_argument("--risk", default="LOW", choices=["LOW", "MED", "HIGH"], help="Risk level")
    x.add_argument("--in-scope", nargs="*", help="List of in-scope file paths")
    x.add_argument("--out", help="Output file path (e.g. plans/001-slug.md)")
    x.add_argument("--root", help="Explicit pack root")
    x.set_defaults(func=cmd_improve_plan)

    return p



def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
