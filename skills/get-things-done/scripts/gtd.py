#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import sys
import zipfile
from decimal import Decimal
from pathlib import Path
from typing import Any

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


def validate_brief(payload: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["brief must be a JSON object"]
    for key in REQUIRED_TOP:
        if key not in payload:
            errors.append(f"missing required field: {key}")
    if errors:
        return errors
    if payload.get("version") != "1.0":
        errors.append("version must be 1.0")
    if not isinstance(payload.get("title"), str) or not payload["title"].strip():
        errors.append("title must be a non-empty string")
    if payload.get("status") not in STATUSES:
        errors.append(f"status must be one of: {', '.join(sorted(STATUSES))}")
    if payload.get("domain") is not None and not isinstance(payload.get("domain"), str):
        errors.append("domain must be a string or null")
    for parent, keys in NESTED_REQUIRED.items():
        obj = payload.get(parent)
        if not isinstance(obj, dict):
            errors.append(f"{parent} must be an object")
            continue
        for key in keys:
            if key not in obj:
                errors.append(f"missing required field: {parent}.{key}")
    for key in ("decisions", "open_decisions", "workstreams", "deliverables", "risks", "blockers"):
        if key in payload and not isinstance(payload.get(key), list):
            errors.append(f"{key} must be an array")
    return errors


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
    """Return deterministic structural gaps for the core Definition of Done."""
    gaps: list[str] = []
    verification = payload.get("verification") if isinstance(payload.get("verification"), dict) else {}

    if not payload.get("deliverables"):
        gaps.append("deliverables are empty")
    if not verification.get("success_criteria"):
        gaps.append("success criteria are empty")
    if not verification.get("evidence"):
        gaps.append("verification evidence is empty")
    if payload.get("open_decisions"):
        gaps.append("blocking decisions remain open")
    if payload.get("blockers"):
        gaps.append("blockers remain")
    return gaps


def assess_brief(payload: dict[str, Any]) -> dict[str, Any]:
    ready_gaps = readiness_gaps(payload)
    completion_gaps = done_gaps(payload)
    return {
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
        skill / "templates/execution-brief.md",
    ]
    builder = root / "skills/building-gtd-domain-packs/SKILL.md"
    if (root / "skills").is_dir():
        required.append(builder)
    missing = [str(p.relative_to(root)) for p in required if not p.exists()]
    try:
        schema = read_json(references_dir(root) / "execution-brief.schema.json")
        schema_ok = schema.get("title") == "Execution Brief v1"
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
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(blank_brief(args.title, args.domain), indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


def cmd_validate_brief(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    try:
        payload = read_json(path)
    except Exception as exc:
        print(f"INVALID: cannot read JSON: {exc}")
        return 1
    errors = validate_brief(payload)
    if args.root and payload.get("domain"):
        domain_path = domains_dir(pack_root(args.root)) / f"{payload['domain']}.md"
        if not domain_path.exists():
            errors.append(f"domain pack not found: {payload['domain']}")
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID")
    return 0


def cmd_assess_brief(args: argparse.Namespace) -> int:
    path = Path(args.path).expanduser().resolve()
    try:
        payload = read_json(path)
    except Exception as exc:
        print(f"INVALID: cannot read JSON: {exc}")
        return 1
    errors = validate_brief(payload)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    assessment = assess_brief(payload)
    if args.json:
        print(json.dumps(assessment, indent=2))
    else:
        print(f"READY: {'YES' if assessment['ready'] else 'NO'}")
        for gap in assessment["ready_gaps"]:
            print(f"- ready gap: {gap}")
        print(f"DONE: {'YES' if assessment['done'] else 'NO'}")
        for gap in assessment["done_gaps"]:
            print(f"- done gap: {gap}")
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
    payload = read_json(path)
    errors = validate_brief(payload)
    if errors:
        print("INVALID", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
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
    for s_name in ["get-things-done", "building-gtd-domain-packs"]:
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
    x.add_argument("--out", required=True)
    x.add_argument("--force", action="store_true")
    x.set_defaults(func=cmd_new_brief)

    x = sub.add_parser("validate-brief")
    x.add_argument("path")
    x.add_argument("--root")
    x.set_defaults(func=cmd_validate_brief)

    x = sub.add_parser("assess-brief")
    x.add_argument("path")
    x.add_argument("--json", action="store_true")
    x.set_defaults(func=cmd_assess_brief)

    x = sub.add_parser("render-brief")
    x.add_argument("path")
    x.add_argument("--out")
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
    return p


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
