from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any

EVIDENCE_LEVELS = {"claim": 0, "direct": 1, "independent": 2}
FINISHED_WORKSTREAM_STATES = {"done", "skipped"}
ACTIVE_WORKSTREAM_STATES = {"pending", "ready", "executing", "blocked", "verifying"}


def blank_brief_v2(title: str, domain: str | None) -> dict[str, Any]:
    return {
        "version": "2.0",
        "title": title,
        "domain": domain,
        "mode": "standard",
        "status": "captured",
        "outcome": {"problem": "", "desired_result": "", "actor": None, "acceptance_summary": ""},
        "scope": {"in": [], "out": [], "constraints": []},
        "knowledge": {"facts": [], "assumptions": [], "unknowns": []},
        "authority": {"autonomous_actions": [], "approval_required": [], "approved_actions": []},
        "active_frontier": {"mode": "model", "reason": "", "exit_condition": ""},
        "decisions": [],
        "open_decisions": [],
        "workstreams": [],
        "deliverables": [],
        "risks": [],
        "checkpoints": [],
        "handoffs": [],
        "verification": {"criteria": [], "evidence": []},
        "capabilities": {
            "tools": "unknown",
            "subagents": "unknown",
            "background": "unknown",
            "persistence": "unknown",
            "approvals": "unknown",
        },
        "next_action": {"description": None, "workstream_id": None, "owner": None},
        "blockers": [],
        "terminal_state": "active",
        "domain_data": {},
    }


def _record_id(prefix: str, index: int) -> str:
    return f"{prefix}-{index + 1}"


def _frontier_from_status(status: str) -> str:
    return {
        "clarifying": "clarify",
        "researching": "research",
        "modeling": "model",
        "ready": "execute",
        "executing": "execute",
        "verifying": "verify",
        "done": "verify",
        "blocked": "decide",
    }.get(status, "model")


def migrate_v1_to_v2(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("version") != "1.0":
        raise ValueError("migration requires an Execution Brief with version 1.0")

    migrated = blank_brief_v2(str(payload.get("title", "Untitled")), payload.get("domain"))
    status = str(payload.get("status", "captured"))
    intent = payload.get("intent", {})
    criteria = list(payload.get("verification", {}).get("success_criteria", []))
    migrated.update(
        {
            "status": status,
            "outcome": {
                "problem": str(intent.get("problem", "")),
                "desired_result": str(intent.get("desired_outcome", "")),
                "actor": intent.get("actor"),
                "acceptance_summary": "; ".join(str(item) for item in criteria),
            },
            "scope": payload.get("scope", {"in": [], "out": [], "constraints": []}),
            "authority": {"autonomous_actions": [], "approval_required": [], "approved_actions": []},
            "active_frontier": {
                "mode": _frontier_from_status(status),
                "reason": f"Migrated from v1 status: {status}",
                "exit_condition": "Reassess this brief under the GTD v2 contract",
            },
            "domain_data": payload.get("domain_data", {}),
        }
    )

    knowledge = payload.get("knowledge", {})
    migrated["knowledge"] = {
        "facts": [
            {"id": _record_id("fact", index), "statement": str(value), "source": "migrated:v1"}
            for index, value in enumerate(knowledge.get("facts", []))
        ],
        "assumptions": [
            {
                "id": _record_id("assumption", index),
                "statement": str(value),
                "risk": "unknown",
                "expires_at": None,
            }
            for index, value in enumerate(knowledge.get("assumptions", []))
        ],
        "unknowns": [
            {
                "id": _record_id("unknown", index),
                "statement": str(value),
                "blocking": False,
                "owner": None,
            }
            for index, value in enumerate(knowledge.get("unknowns", []))
        ],
    }
    migrated["decisions"] = [
        {
            "id": _record_id("decision", index),
            "decision": str(value.get("decision", "")),
            "rationale": str(value.get("rationale", "")),
            "reversible": bool(value.get("reversible", False)),
            "owner": None,
            "status": "decided",
        }
        for index, value in enumerate(payload.get("decisions", []))
    ]
    migrated["open_decisions"] = [
        {
            "id": _record_id("open-decision", index),
            "question": str(value),
            "owner": None,
            "blocking": True,
        }
        for index, value in enumerate(payload.get("open_decisions", []))
    ]

    legacy_workstreams = list(payload.get("workstreams", []))
    name_to_id: dict[str, str] = {}
    workstreams: list[dict[str, Any]] = []
    for index, value in enumerate(legacy_workstreams):
        workstream_id = _record_id("workstream", index)
        name = str(value.get("name", f"Workstream {index + 1}"))
        name_to_id.setdefault(name.strip().casefold(), workstream_id)
        workstreams.append(
            {
                "id": workstream_id,
                "kind": "internal",
                "name": name,
                "outcome": str(value.get("outcome", "")),
                "dependencies": [],
                "status": "done" if status == "done" else "pending",
                "owner": None,
                "estimate": 1,
                "completion_criteria": [],
            }
        )

    external_ids: dict[str, str] = {}
    for index, value in enumerate(legacy_workstreams):
        dependencies: list[str] = []
        for dependency in value.get("dependencies", []):
            label = str(dependency)
            normalized = label.strip().casefold()
            dependency_id = name_to_id.get(normalized)
            if dependency_id is None:
                dependency_id = external_ids.get(normalized)
                if dependency_id is None:
                    dependency_id = _record_id("external-dependency", len(external_ids))
                    external_ids[normalized] = dependency_id
                    workstreams.append(
                        {
                            "id": dependency_id,
                            "kind": "external",
                            "name": label,
                            "outcome": "External dependency carried forward from Execution Brief v1",
                            "dependencies": [],
                            "status": "blocked",
                            "owner": None,
                            "estimate": 0,
                            "completion_criteria": [],
                        }
                    )
            dependencies.append(dependency_id)
        workstreams[index]["dependencies"] = dependencies
    migrated["workstreams"] = workstreams

    migrated["deliverables"] = [
        {
            "id": _record_id("deliverable", index),
            "name": str(value),
            "status": "done" if status == "done" else "pending",
            "workstream_id": None,
        }
        for index, value in enumerate(payload.get("deliverables", []))
    ]
    migrated["risks"] = [
        {
            "id": _record_id("risk", index),
            "description": str(value),
            "likelihood": "unknown",
            "impact": "unknown",
            "mitigation": "",
            "rollback": None,
            "owner": None,
            "status": "open",
        }
        for index, value in enumerate(payload.get("risks", []))
    ]
    migrated["verification"] = {
        "criteria": [
            {
                "id": _record_id("criterion", index),
                "description": str(value),
                "required": True,
                "evidence_level": "direct",
                "freshness_hours": None,
            }
            for index, value in enumerate(criteria)
        ],
        "evidence": [
            {
                "id": _record_id("evidence", index),
                "criterion_id": None,
                "method": "legacy-record",
                "source": str(value),
                "observed_at": None,
                "result": "inconclusive",
                "level": "claim",
                "limitations": "Migrated from unlinked v1 evidence; relink and re-verify before completion",
            }
            for index, value in enumerate(payload.get("verification", {}).get("evidence", []))
        ],
    }
    migrated["next_action"] = {
        "description": payload.get("next_action"),
        "workstream_id": None,
        "owner": None,
    }
    migrated["blockers"] = [
        {
            "id": _record_id("blocker", index),
            "description": str(value),
            "owner": None,
            "resolution": None,
        }
        for index, value in enumerate(payload.get("blockers", []))
    ]
    migrated["terminal_state"] = "blocked" if status == "blocked" else "unverified" if status == "done" else "active"
    return migrated


def _duplicate_ids(items: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for item in items:
        item_id = str(item.get("id", ""))
        if item_id in seen and item_id not in duplicates:
            duplicates.append(item_id)
        seen.add(item_id)
    return duplicates


def plan_brief_v2(payload: dict[str, Any]) -> dict[str, Any]:
    workstreams = list(payload.get("workstreams", []))
    order = [str(item.get("id", "")) for item in workstreams]
    by_id = {str(item.get("id", "")): item for item in workstreams}
    duplicates = _duplicate_ids(workstreams)
    missing_dependencies: list[dict[str, str]] = []
    indegree = {item_id: 0 for item_id in order}
    dependents: dict[str, list[str]] = {item_id: [] for item_id in order}

    for workstream in workstreams:
        workstream_id = str(workstream.get("id", ""))
        for dependency in workstream.get("dependencies", []):
            dependency_id = str(dependency)
            if dependency_id not in by_id:
                missing_dependencies.append({"workstream": workstream_id, "dependency": dependency_id})
                continue
            indegree[workstream_id] += 1
            dependents[dependency_id].append(workstream_id)

    queue = deque(item_id for item_id in order if indegree[item_id] == 0)
    topological_order: list[str] = []
    while queue:
        item_id = queue.popleft()
        topological_order.append(item_id)
        for dependent in dependents[item_id]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)
    cycle_nodes = [item_id for item_id in order if indegree[item_id] > 0]

    distances: dict[str, float] = {}
    predecessor: dict[str, str | None] = {}
    for item_id in topological_order:
        item = by_id[item_id]
        estimate = float(item.get("estimate", 0))
        valid_dependencies = [dep for dep in item.get("dependencies", []) if dep in distances]
        if valid_dependencies:
            best_dependency = max(valid_dependencies, key=lambda dep: distances[dep])
            distances[item_id] = distances[best_dependency] + estimate
            predecessor[item_id] = best_dependency
        else:
            distances[item_id] = estimate
            predecessor[item_id] = None

    critical_path: list[str] = []
    critical_path_estimate = 0.0
    if distances and not cycle_nodes:
        cursor: str | None = max(order, key=lambda item_id: distances[item_id])
        critical_path_estimate = distances[cursor]
        while cursor is not None:
            critical_path.append(cursor)
            cursor = predecessor[cursor]
        critical_path.reverse()

    ready_workstreams: list[str] = []
    blocked_workstreams: list[str] = []
    for workstream in workstreams:
        workstream_id = str(workstream.get("id", ""))
        if workstream.get("status") not in {"pending", "ready", "blocked"}:
            continue
        dependencies = list(workstream.get("dependencies", []))
        if any(dependency not in by_id for dependency in dependencies):
            blocked_workstreams.append(workstream_id)
            continue
        dependencies_done = all(by_id[dependency].get("status") in FINISHED_WORKSTREAM_STATES for dependency in dependencies)
        if dependencies_done and workstream.get("kind") != "external":
            ready_workstreams.append(workstream_id)
        else:
            blocked_workstreams.append(workstream_id)

    return {
        "topological_order": topological_order,
        "critical_path": critical_path,
        "critical_path_estimate": critical_path_estimate,
        "ready_workstreams": ready_workstreams,
        "blocked_workstreams": blocked_workstreams,
        "missing_dependencies": missing_dependencies,
        "duplicate_workstream_ids": duplicates,
        "cycle_nodes": cycle_nodes,
    }


def _nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def readiness_gaps_v2(payload: dict[str, Any]) -> list[str]:
    gaps: list[str] = []
    outcome = payload.get("outcome", {})
    scope = payload.get("scope", {})
    frontier = payload.get("active_frontier", {})
    verification = payload.get("verification", {})
    next_action = payload.get("next_action", {})

    if not _nonempty_text(outcome.get("desired_result")):
        gaps.append("desired outcome is empty")
    if payload.get("mode") != "fast" and not scope.get("in"):
        gaps.append("in-scope work is empty")
    if any(item.get("blocking") for item in payload.get("knowledge", {}).get("unknowns", [])):
        gaps.append("blocking unknowns remain")
    if any(item.get("blocking") for item in payload.get("open_decisions", [])):
        gaps.append("blocking decisions remain open")
    if payload.get("blockers"):
        gaps.append("blockers remain")
    if not verification.get("criteria"):
        gaps.append("success criteria are empty")
    if not _nonempty_text(next_action.get("description")):
        gaps.append("next executable action is missing")
    if not _nonempty_text(frontier.get("reason")):
        gaps.append("active frontier reason is empty")
    if not _nonempty_text(frontier.get("exit_condition")):
        gaps.append("active frontier exit condition is empty")

    plan = plan_brief_v2(payload)
    if plan["duplicate_workstream_ids"]:
        gaps.append("duplicate workstream ids: " + ", ".join(plan["duplicate_workstream_ids"]))
    if plan["missing_dependencies"]:
        refs = [f"{item['workstream']}->{item['dependency']}" for item in plan["missing_dependencies"]]
        gaps.append("missing workstream dependencies: " + ", ".join(refs))
    if plan["cycle_nodes"]:
        gaps.append("workstream dependency cycle: " + ", ".join(plan["cycle_nodes"]))

    criterion_ids = {item.get("id") for item in verification.get("criteria", [])}
    for workstream in payload.get("workstreams", []):
        unknown_criteria = [item for item in workstream.get("completion_criteria", []) if item not in criterion_ids]
        if unknown_criteria:
            gaps.append(f"workstream {workstream.get('id')} references unknown criteria: {', '.join(unknown_criteria)}")

    workstream_ids = {item.get("id") for item in payload.get("workstreams", [])}
    next_workstream = next_action.get("workstream_id")
    if next_workstream is not None and next_workstream not in workstream_ids:
        gaps.append(f"next action references unknown workstream: {next_workstream}")

    if payload.get("mode") == "high-assurance":
        authority = payload.get("authority", {})
        pending = [
            item for item in authority.get("approval_required", []) if item not in authority.get("approved_actions", [])
        ]
        if pending:
            gaps.append("required approvals are missing: " + ", ".join(pending))
        if pending and payload.get("capabilities", {}).get("approvals") == "unavailable":
            gaps.append("approval capability is unavailable")
        for risk in payload.get("risks", []):
            if risk.get("impact") not in {"high", "critical"} or risk.get("status") in {"accepted", "closed"}:
                continue
            if not _nonempty_text(risk.get("mitigation")):
                gaps.append(f"high-impact risk lacks mitigation: {risk.get('id')}")
            if not _nonempty_text(risk.get("rollback")):
                gaps.append(f"high-impact risk lacks rollback: {risk.get('id')}")
    return gaps


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def evidence_coverage_v2(payload: dict[str, Any], now: datetime | None = None) -> list[dict[str, Any]]:
    current_time = now or datetime.now(timezone.utc)
    evidence = payload.get("verification", {}).get("evidence", [])
    coverage: list[dict[str, Any]] = []
    for criterion in payload.get("verification", {}).get("criteria", []):
        criterion_id = criterion.get("id")
        linked = [item for item in evidence if item.get("criterion_id") == criterion_id]
        linked.sort(key=lambda item: _parse_time(item.get("observed_at")) or datetime.min.replace(tzinfo=timezone.utc))
        latest = linked[-1] if linked else None
        sufficient = False
        reason = "no linked evidence"
        if latest is not None:
            required_level = EVIDENCE_LEVELS.get(str(criterion.get("evidence_level")), 99)
            actual_level = EVIDENCE_LEVELS.get(str(latest.get("level")), -1)
            observed_at = _parse_time(latest.get("observed_at"))
            if latest.get("result") != "passed":
                reason = f"latest evidence result is {latest.get('result')}"
            elif actual_level < required_level:
                reason = f"evidence level {latest.get('level')} is below {criterion.get('evidence_level')}"
            elif observed_at is None:
                reason = "evidence timestamp is missing"
            elif criterion.get("freshness_hours") is not None:
                age_hours = (current_time - observed_at).total_seconds() / 3600
                if age_hours > float(criterion["freshness_hours"]):
                    reason = "evidence is stale"
                else:
                    sufficient = True
                    reason = "covered"
            else:
                sufficient = True
                reason = "covered"
        coverage.append(
            {
                "criterion_id": criterion_id,
                "required": bool(criterion.get("required")),
                "covered": sufficient,
                "reason": reason,
                "evidence_id": latest.get("id") if latest else None,
            }
        )
    return coverage


def done_gaps_v2(payload: dict[str, Any], now: datetime | None = None) -> list[str]:
    gaps: list[str] = []
    deliverables = payload.get("deliverables", [])
    verification = payload.get("verification", {})
    criteria = verification.get("criteria", [])
    evidence = verification.get("evidence", [])

    if not deliverables:
        gaps.append("deliverables are empty")
    elif any(item.get("status") not in {"done", "accepted"} for item in deliverables):
        gaps.append("deliverables are incomplete")
    if not criteria:
        gaps.append("success criteria are empty")
    if not evidence:
        gaps.append("verification evidence is empty")

    for item in evidence_coverage_v2(payload, now):
        if item["required"] and not item["covered"]:
            gaps.append(f"criterion {item['criterion_id']} is not verified: {item['reason']}")

    criterion_ids = {item.get("id") for item in criteria}
    for item in evidence:
        criterion_id = item.get("criterion_id")
        if criterion_id is None:
            gaps.append(f"evidence {item.get('id')} is not linked to a criterion")
        elif criterion_id not in criterion_ids:
            gaps.append(f"evidence {item.get('id')} references unknown criterion: {criterion_id}")

    unfinished = [
        item.get("id")
        for item in payload.get("workstreams", [])
        if item.get("status") in ACTIVE_WORKSTREAM_STATES
    ]
    if unfinished:
        gaps.append("workstreams are incomplete: " + ", ".join(str(item) for item in unfinished))
    if any(item.get("blocking") for item in payload.get("open_decisions", [])):
        gaps.append("blocking decisions remain open")
    if payload.get("blockers"):
        gaps.append("blockers remain")
    if any(item.get("status") == "failed" for item in payload.get("handoffs", [])):
        gaps.append("failed handoffs remain")
    if any(
        item.get("impact") in {"high", "critical"} and item.get("status") == "open"
        for item in payload.get("risks", [])
    ):
        gaps.append("high-impact risks remain open")
    if payload.get("terminal_state") != "verified_complete":
        gaps.append("terminal state is not verified_complete")
    return gaps


def assess_brief_v2(payload: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    ready_gaps = readiness_gaps_v2(payload)
    completion_gaps = done_gaps_v2(payload, now)
    return {
        "version": "2.0",
        "mode": payload.get("mode"),
        "ready": not ready_gaps,
        "done": not completion_gaps,
        "ready_gaps": ready_gaps,
        "done_gaps": completion_gaps,
        "evidence_coverage": evidence_coverage_v2(payload, now),
        "plan": plan_brief_v2(payload),
    }


def _bullets(items: list[Any], formatter=lambda item: str(item)) -> str:
    return "\n".join(f"- {formatter(item)}" for item in items) if items else "- None recorded"


def render_brief_v2(payload: dict[str, Any]) -> str:
    outcome = payload["outcome"]
    frontier = payload["active_frontier"]
    authority = payload["authority"]
    verification = payload["verification"]
    plan = plan_brief_v2(payload)
    parts = [
        f"# Execution Brief v2: {payload['title']}",
        "",
        "## Operating profile",
        f"- Mode: {payload['mode']}",
        f"- Status: {payload['status']}",
        f"- Terminal state: {payload['terminal_state']}",
        f"- Domain: {payload.get('domain')}",
        "",
        "## Outcome contract",
        f"- Problem: {outcome.get('problem', '')}",
        f"- Desired result: {outcome.get('desired_result', '')}",
        f"- Actor: {outcome.get('actor')}",
        f"- Acceptance summary: {outcome.get('acceptance_summary', '')}",
        "",
        "## Active frontier",
        f"- Mode: {frontier.get('mode')}",
        f"- Reason: {frontier.get('reason', '')}",
        f"- Exit condition: {frontier.get('exit_condition', '')}",
        "",
        "## Scope",
        "### In",
        _bullets(payload["scope"].get("in", [])),
        "### Out",
        _bullets(payload["scope"].get("out", [])),
        "### Constraints",
        _bullets(payload["scope"].get("constraints", [])),
        "",
        "## Authority",
        "### Autonomous actions",
        _bullets(authority.get("autonomous_actions", [])),
        "### Approval required",
        _bullets(authority.get("approval_required", [])),
        "### Approved actions",
        _bullets(authority.get("approved_actions", [])),
        "",
        "## Workstreams",
        "| ID | Kind | Workstream | Status | Dependencies | Owner | Estimate |",
        "|---|---|---|---|---|---|---|",
    ]
    workstream_rows = [
        f"| {item['id']} | {item['kind']} | {item['name']} | {item['status']} | "
        f"{', '.join(item['dependencies'])} | {item.get('owner')} | {item.get('estimate', 0)} |"
        for item in payload.get("workstreams", [])
    ]
    parts.extend(workstream_rows or ["| None | | | | | | |"])
    parts.extend(
        [
            "",
            "### Critical path",
            f"- {' -> '.join(plan['critical_path']) or 'Not available'}",
            f"- Estimated effort: {plan['critical_path_estimate']}",
            "",
            "## Risks and rollback",
            _bullets(
                payload.get("risks", []),
                lambda item: f"{item['id']}: {item['description']} "
                f"(impact={item['impact']}, status={item['status']}, rollback={item.get('rollback')})",
            ),
            "",
            "## Checkpoints",
            _bullets(
                payload.get("checkpoints", []),
                lambda item: f"{item['id']}: {item['status']} — {item['summary']} — resume: {item['resume_action']}",
            ),
            "",
            "## Handoffs",
            _bullets(
                payload.get("handoffs", []),
                lambda item: f"{item['id']}: {item.get('from')} -> {item.get('to')} "
                f"({item['status']}) — {item['scope']}",
            ),
            "",
            "## Verification criteria",
            _bullets(
                verification.get("criteria", []),
                lambda item: f"{item['id']}: {item['description']} "
                f"(required={item['required']}, level={item['evidence_level']})",
            ),
            "",
            "## Evidence",
            _bullets(
                verification.get("evidence", []),
                lambda item: f"{item['id']} -> {item.get('criterion_id')}: {item['result']} "
                f"via {item['method']} ({item.get('observed_at')})",
            ),
            "",
            "## Blockers",
            _bullets(payload.get("blockers", []), lambda item: f"{item['id']}: {item['description']}"),
            "",
            "## Next executable action",
            f"- {payload.get('next_action', {}).get('description') or 'Not set'}",
            "",
        ]
    )
    return "\n".join(parts)
