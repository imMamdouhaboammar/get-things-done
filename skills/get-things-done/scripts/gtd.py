#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
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
    decision_rows = "\n".join(
        f"| {d.get('decision','')} | {d.get('rationale','')} | {d.get('reversible','')} |" for d in decisions
    ) or "| None | | |"
    work_rows = "\n".join(
        f"| {w.get('name','')} | {w.get('outcome','')} | {', '.join(w.get('dependencies', []))} |" for w in workstreams
    ) or "| None | | |"
    parts = [
        f"# Execution Brief: {payload['title']}",
        "",
        "## Outcome",
        f"- Problem: {intent.get('problem','')}",
        f"- Desired outcome: {intent.get('desired_outcome','')}",
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
