#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import jsonschema


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def schema(name: str) -> dict[str, Any]:
    return json.loads((skill_dir() / "references" / name).read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate(path: Path, schema_name: str) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema(schema_name), format_checker=jsonschema.FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(payload), key=lambda e: list(e.path))]


def cmd_new_problem(args: argparse.Namespace) -> int:
    payload = {
        "version": "1.0",
        "title": args.title,
        "status": "contemplating",
        "original_request": args.request,
        "desired_outcome": args.outcome or args.request,
        "proposed_solution": args.proposed_solution,
        "current_framing": args.request,
        "freshness_context": {
            "status": "blocked",
            "searched_at": None,
            "search_scope": "",
            "queries": [],
            "sources": [],
            "freshness_findings": [],
            "stale_or_changed_claims": [],
            "freshness_gaps": ["Current-date search has not been performed yet."]
        },
        "assumptions": [],
        "evidence": [],
        "contradictions": [],
        "alternative_framings": [],
        "second_order_effects": [],
        "candidate_directions": [],
        "recommended_direction": None,
        "rejected_directions": [],
        "open_decisions": [],
        "direction_gate": {
            "requires_user_decision": True,
            "status": "pending",
            "decision": None
        },
        "contemplation_exit": {
            "reason": "Deliberation has not reached sufficiency.",
            "remaining_uncertainty": [],
            "next_artifact": "problem-model"
        }
    }
    write_json(Path(args.out), payload)
    print(f"CREATED {args.out}")
    return 0


def cmd_validate_problem(args: argparse.Namespace) -> int:
    errors = validate(Path(args.path), "problem-model.schema.json")
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID problem model")
    return 0


def cmd_new_backlog(args: argparse.Namespace) -> int:
    payload = {
        "version": "1.0",
        "title": args.title,
        "approved_direction": args.direction,
        "source_problem_model": args.problem_model,
        "source_execution_brief": args.execution_brief,
        "epics": [],
        "decision_log": [{"decision": args.direction, "reason": "Approved Direction Gate", "source": args.problem_model}],
        "risks": [],
        "next_action": args.next_action
    }
    write_json(Path(args.out), payload)
    print(f"CREATED {args.out}")
    return 0


def cmd_validate_backlog(args: argparse.Namespace) -> int:
    errors = validate(Path(args.path), "backlog.schema.json")
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID backlog")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gtd-deliberation")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("new-problem-model")
    p.add_argument("--title", required=True)
    p.add_argument("--request", required=True)
    p.add_argument("--outcome")
    p.add_argument("--proposed-solution")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_new_problem)

    p = sub.add_parser("validate-problem-model")
    p.add_argument("path")
    p.set_defaults(func=cmd_validate_problem)

    p = sub.add_parser("new-backlog")
    p.add_argument("--title", required=True)
    p.add_argument("--direction", required=True)
    p.add_argument("--problem-model", required=True)
    p.add_argument("--execution-brief")
    p.add_argument("--next-action", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_new_backlog)

    p = sub.add_parser("validate-backlog")
    p.add_argument("path")
    p.set_defaults(func=cmd_validate_backlog)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
