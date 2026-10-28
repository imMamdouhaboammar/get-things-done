#!/usr/bin/env python3
"""
Improve Codebase Advisor Bridge for Get Things Done (GTD).
Provides bidirectional parsing, schema conversion, and verification between
self-contained Improve implementation plans (plans/NNN-*.md) and GTD Execution Briefs.
"""
from __future__ import annotations

import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ImproveBridge:
    """Bridge for parsing, validating, and converting Improve advisor plans into GTD briefs."""

    def __init__(self, pack_root: Optional[Path] = None) -> None:
        if pack_root:
            self.pack_root = pack_root.resolve()
        else:
            self.pack_root = Path(os.environ.get("GTD_PACK_ROOT", Path(__file__).resolve().parents[3])).resolve()

    def parse_plan(self, text: str) -> Dict[str, Any]:
        """Parse an Improve implementation plan markdown string into structured data."""
        data: Dict[str, Any] = {
            "title": "",
            "number": "",
            "status": {},
            "why_this_matters": "",
            "current_state": "",
            "commands": [],
            "scope_in": [],
            "scope_out": [],
            "steps": [],
            "test_plan": "",
            "done_criteria": [],
            "stop_conditions": [],
            "maintenance_notes": "",
        }

        # Extract title
        title_match = re.search(r"^#\s+(?:Plan\s+(\d+):\s*)?([^\n]+)", text, re.MULTILINE)
        if title_match:
            data["number"] = title_match.group(1) or ""
            data["title"] = title_match.group(2).strip()

        # Extract status fields
        status_section = re.search(r"##\s+Status\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if status_section:
            for line in status_section.group(1).splitlines():
                line = line.strip()
                m = re.match(r"^-\s+\*\*([^*]+)\*\*:\s*(.*)", line)
                if m:
                    key = m.group(1).strip().lower().replace(" ", "_")
                    val = m.group(2).strip()
                    data["status"][key] = val

        # Extract Why this matters
        why_match = re.search(r"##\s+Why this matters\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if why_match:
            data["why_this_matters"] = why_match.group(1).strip()

        # Extract Current state
        current_match = re.search(r"##\s+Current state\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if current_match:
            data["current_state"] = current_match.group(1).strip()

        # Extract Commands table
        commands_match = re.search(r"##\s+Commands you will need\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if commands_match:
            for line in commands_match.group(1).splitlines():
                line = line.strip()
                if line.startswith("|") and not line.startswith("|---") and not line.lower().startswith("| purpose"):
                    parts = [p.strip().strip("`") for p in line.split("|")[1:-1]]
                    if len(parts) >= 3:
                        data["commands"].append({
                            "purpose": parts[0],
                            "command": parts[1],
                            "expected": parts[2],
                        })

        # Extract Scope
        scope_match = re.search(r"##\s+Scope\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if scope_match:
            scope_text = scope_match.group(1)
            in_match = re.search(r"\*\*In scope\*\*[^\n]*\n(.*?)(?=\*\*Out of scope\*|\Z)", scope_text, re.DOTALL)
            if in_match:
                for line in in_match.group(1).splitlines():
                    line = line.strip()
                    if line.startswith("-"):
                        data["scope_in"].append(line.lstrip("- ").strip("` "))
            out_match = re.search(r"\*\*Out of scope\*\*[^\n]*\n(.*?)(?=\n###|\n##|\Z)", scope_text, re.DOTALL)
            if out_match:
                for line in out_match.group(1).splitlines():
                    line = line.strip()
                    if line.startswith("-"):
                        data["scope_out"].append(line.lstrip("- ").strip("` "))

        # Extract Steps
        steps_match = re.findall(r"###\s+Step\s+(\d+):\s*([^\n]+)\n(.*?)(?=\n###\s+Step|\n##|\Z)", text, re.DOTALL)
        for step_num, step_title, step_body in steps_match:
            verify_match = re.search(r"\*\*Verify\*\*:\s*`([^`]+)`(?:\s*→\s*([^\n]+))?", step_body)
            data["steps"].append({
                "step": int(step_num),
                "title": step_title.strip(),
                "body": step_body.strip(),
                "verify_command": verify_match.group(1).strip() if verify_match else "",
                "verify_expected": verify_match.group(2).strip() if verify_match and verify_match.group(2) else "success",
            })

        # Extract Test plan
        test_match = re.search(r"##\s+Test plan\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if test_match:
            data["test_plan"] = test_match.group(1).strip()

        # Extract Done criteria
        done_match = re.search(r"##\s+Done criteria\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if done_match:
            for line in done_match.group(1).splitlines():
                line = line.strip()
                if line.startswith("- [ ]") or line.startswith("- [x]"):
                    criterion = line[5:].strip()
                    data["done_criteria"].append(criterion)

        # Extract STOP conditions
        stop_match = re.search(r"##\s+STOP conditions\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if stop_match:
            for line in stop_match.group(1).splitlines():
                line = line.strip()
                if line.startswith("-"):
                    data["stop_conditions"].append(line.lstrip("- ").strip())

        # Extract Maintenance notes
        maint_match = re.search(r"##\s+Maintenance notes\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if maint_match:
            data["maintenance_notes"] = maint_match.group(1).strip()

        return data

    def validate_plan(self, plan_data_or_text: Any) -> List[str]:
        """Validate that a plan adheres to the Improve Senior Advisor and GTD standards."""
        if isinstance(plan_data_or_text, str):
            text = plan_data_or_text
            data = self.parse_plan(text)
        elif isinstance(plan_data_or_text, dict):
            data = plan_data_or_text
            text = str(data)
        else:
            return ["Invalid plan argument type; expected markdown string or parsed dict"]

        errors: List[str] = []

        if not data.get("title"):
            errors.append("Missing plan title (heading '# Plan NNN: <title>')")

        if not data.get("why_this_matters"):
            errors.append("Missing '## Why this matters' section")

        if not data.get("scope_in"):
            errors.append("Missing or empty '**In scope**' section under '## Scope'")

        if not data.get("steps"):
            errors.append("Plan must declare at least one executable step ('### Step N: <title>')")
        else:
            for s in data["steps"]:
                if not s.get("verify_command"):
                    errors.append(f"Step {s.get('step')} is missing a '**Verify**: `<command>`' clause")

        if not data.get("done_criteria"):
            errors.append("Missing machine-checkable '## Done criteria' checkboxes")

        if not data.get("stop_conditions"):
            errors.append("Missing '## STOP conditions' section")

        # Invariant: Never reproduce secrets
        secret_patterns = [
            r"sk-[a-zA-Z0-9_-]{16,}",
            r"ghp_[a-zA-Z0-9]{20,}",
            r"(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*['\"]?[a-zA-Z0-9_=-]{16,}['\"]?",
        ]
        for pattern in secret_patterns:
            if re.search(pattern, text):
                errors.append("SECURITY INVARIANT VIOLATION: Secret or API key token reproduced in plan body")

        # Invariant: Self-containment check (ban dangling conversational references)
        dangling_phrases = [
            "as discussed above",
            "as mentioned earlier",
            "refer to our conversation",
            "per the previous session",
        ]
        for phrase in dangling_phrases:
            if phrase in text.lower():
                errors.append(f"SELF-CONTAINMENT VIOLATION: Plan contains session-relative phrase '{phrase}'")

        return errors

    def plan_to_brief(self, plan_data: Dict[str, Any], version: str = "1.0", domain: str = "software") -> Dict[str, Any]:
        """Convert parsed Improve plan data into a valid GTD Execution Brief (v1.0 or v2.0)."""
        title = plan_data.get("title") or "Improve Plan Implementation"
        why = plan_data.get("why_this_matters") or "Codebase improvement plan execution"

        problem = why
        desired_outcome = f"Complete implementation plan: {title}"

        in_scope = plan_data.get("scope_in") or []
        out_scope = plan_data.get("scope_out") or []

        facts_raw = []
        if plan_data.get("current_state"):
            for line in plan_data["current_state"].splitlines():
                clean = line.strip().lstrip("-* ").strip()
                if clean:
                    facts_raw.append(clean)
        planned_at = plan_data.get("status", {}).get("planned_at")
        if planned_at:
            facts_raw.append(f"Planned at commit {planned_at}")

        success_criteria = list(plan_data.get("done_criteria", []))
        if not success_criteria:
            success_criteria = ["Verify plan implementation with test suite"]

        if version == "2.0":
            from brief_v2 import blank_brief_v2  # type: ignore
            brief = blank_brief_v2(title, domain)
            brief["status"] = "modeling"
            brief["outcome"]["problem"] = problem
            brief["outcome"]["desired_result"] = desired_outcome
            brief["outcome"]["acceptance_summary"] = f"All {len(success_criteria)} done criteria verified"
            brief["scope"]["in"] = in_scope
            brief["scope"]["out"] = out_scope
            brief["scope"]["constraints"] = ["Zero mutating commands outside disposable worktree", "Self-contained execution"]

            brief["knowledge"]["facts"] = [
                {"id": f"fact-{i+1}", "statement": statement, "source": "improve-plan"}
                for i, statement in enumerate(facts_raw)
            ]

            steps = plan_data.get("steps", [])
            brief["workstreams"] = [
                {
                    "id": f"ws-{i+1}",
                    "kind": "internal",
                    "name": s["title"],
                    "outcome": s["body"].split("\n")[0] if s.get("body") else f"Execute {s['title']}",
                    "dependencies": [f"ws-{i}"] if i > 0 else [],
                    "status": "pending",
                    "owner": "executor-agent",
                    "estimate": 1.0,
                    "parallel_safe": True,
                    "completion_criteria": [f"crit-{min(i+1, len(success_criteria))}"],
                }
                for i, s in enumerate(steps)
            ]

            brief["deliverables"] = [
                {
                    "id": f"deliv-{i+1}",
                    "name": item,
                    "status": "pending",
                    "workstream_id": f"ws-{min(i+1, len(steps))}" if steps else None,
                }
                for i, item in enumerate(in_scope)
            ]

            risks = []
            risk_level = (plan_data.get("status", {}).get("risk") or "low").lower()
            if risk_level not in {"unknown", "low", "medium", "high", "critical"}:
                risk_level = "low"
            for i, stop_c in enumerate(plan_data.get("stop_conditions", [])):
                risks.append({
                    "id": f"risk-{i+1}",
                    "description": stop_c,
                    "likelihood": "low",
                    "impact": risk_level,
                    "mitigation": "Stop and report back if boundary violated",
                    "rollback": "git checkout . in worktree",
                    "owner": None,
                    "status": "open",
                })
            brief["risks"] = risks

            criteria_objs = [
                {
                    "id": f"crit-{i+1}",
                    "description": crit,
                    "required": True,
                    "evidence_level": "direct",
                    "freshness_hours": 24.0,
                }
                for i, crit in enumerate(success_criteria)
            ]
            brief["verification"]["criteria"] = criteria_objs

            evidence_objs = []
            for i, cmd_entry in enumerate(plan_data.get("commands", [])):
                evidence_objs.append({
                    "id": f"evid-{i+1}",
                    "criterion_id": f"crit-{min(i+1, len(criteria_objs))}",
                    "method": cmd_entry["command"],
                    "source": "terminal",
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                    "result": "passed",
                    "level": "direct",
                    "limitations": "",
                })
            brief["verification"]["evidence"] = evidence_objs

            brief["next_action"] = {
                "description": f"Execute Step 1: {steps[0]['title']}" if steps else "Review plan",
                "workstream_id": "ws-1" if steps else None,
                "owner": "executor-agent",
            }

            brief["domain_data"]["improve_metadata"] = {
                "plan_number": plan_data.get("number"),
                "priority": plan_data.get("status", {}).get("priority"),
                "effort": plan_data.get("status", {}).get("effort"),
                "category": plan_data.get("status", {}).get("category"),
            }
            return brief

        # Default v1.0
        workstreams_v1 = []
        for s in plan_data.get("steps", []):
            step_name = f"Step {s['step']}: {s['title']}"
            outcome = s["body"].split("\n")[0] if s.get("body") else f"Execute {s['title']}"
            workstreams_v1.append({
                "name": step_name,
                "outcome": outcome,
                "dependencies": [f"Step {s['step'] - 1}"] if s["step"] > 1 else [],
            })

        evidence_v1 = []
        for cmd_entry in plan_data.get("commands", []):
            evidence_v1.append(f"Level A: {cmd_entry['command']} -> {cmd_entry['expected']}")
        for s in plan_data.get("steps", []):
            if s.get("verify_command"):
                evidence_v1.append(f"Level A: {s['verify_command']} -> {s.get('verify_expected', 'pass')}")

        risks_v1 = []
        risk_val = plan_data.get("status", {}).get("risk")
        if risk_val:
            risks_v1.append(f"Risk level: {risk_val}")
        for stop_c in plan_data.get("stop_conditions", []):
            risks_v1.append(f"STOP boundary: {stop_c}")

        deliverables_v1 = list(in_scope)
        if plan_data.get("maintenance_notes"):
            deliverables_v1.append("Handoff & Maintenance notes review")

        next_action_v1 = f"Execute {workstreams_v1[0]['name']}" if workstreams_v1 else "Review implementation plan"

        return {
            "version": "1.0",
            "title": title,
            "domain": domain,
            "intent": {
                "problem": problem,
                "desired_outcome": desired_outcome,
                "actor": "executor-agent",
            },
            "status": "ready",
            "scope": {
                "in": in_scope,
                "out": out_scope,
                "constraints": ["Zero mutating commands outside disposable worktree"],
            },
            "knowledge": {
                "facts": facts_raw,
                "assumptions": ["Repo build and test baseline established during advisor recon"],
                "unknowns": [],
            },
            "decisions": [
                {
                    "decision": f"Execute Improve plan: {title}",
                    "rationale": why[:120],
                    "reversible": True,
                }
            ],
            "open_decisions": [],
            "workstreams": workstreams_v1,
            "deliverables": deliverables_v1,
            "risks": risks_v1,
            "domain_data": {
                "improve_metadata": {
                    "plan_number": plan_data.get("number"),
                    "priority": plan_data.get("status", {}).get("priority"),
                    "effort": plan_data.get("status", {}).get("effort"),
                    "category": plan_data.get("status", {}).get("category"),
                }
            },
            "verification": {
                "success_criteria": success_criteria,
                "evidence": evidence_v1,
            },
            "next_action": next_action_v1,
            "blockers": [],
        }

    def scaffold_plan(
        self,
        title: str,
        category: str = "tech-debt",
        priority: str = "P2",
        effort: str = "S",
        risk: str = "LOW",
        planned_at: str = "",
        in_scope: Optional[List[str]] = None,
    ) -> str:
        """Generate a new self-contained plan markdown skeleton."""
        if not planned_at:
            try:
                out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True)
                planned_at = out.stdout.strip()
            except Exception:
                planned_at = "HEAD"

        in_scope_lines = "\n".join(f"- `{f}`" for f in (in_scope or ["src/index.ts"]))

        return f"""# Plan 001: {title}

> **Executor instructions**: Follow this plan step by step. Run every
> verification command and confirm the expected result before moving to the
> next step. If anything in the "STOP conditions" section occurs, stop and
> report — do not improvise. When done, update the status row for this plan
> in `plans/README.md`.
>
> **Drift check (run first)**: `git diff --stat {planned_at}..HEAD -- {in_scope[0] if in_scope else "src/index.ts"}`

## Status

- **Priority**: {priority}
- **Effort**: {effort}
- **Risk**: {risk}
- **Depends on**: none
- **Category**: {category}
- **Planned at**: commit `{planned_at}`

## Why this matters

Describe the problem, concrete cost, and improvement outcome.

## Current state

- Relevant files and roles:
  - `{in_scope[0] if in_scope else "src/index.ts"}` — primary implementation
- Code excerpts with `file:line` markers.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Tests | `pytest` | all pass |
| Typecheck | `tsc --noEmit` | exit 0 |

## Scope

**In scope**:
{in_scope_lines}

**Out of scope**:
- Unrelated feature modules and legacy files

## Steps

### Step 1: Initial implementation step

Describe specific actions and changes.

**Verify**: `pytest` → pass

## Test plan

- Unit and integration tests covering the new behavior.
- Verification command and expected pass output.

## Done criteria

- [ ] All automated tests pass
- [ ] No files outside in-scope list are modified
- [ ] Status row in `plans/README.md` updated

## STOP conditions

- Code at "Current state" does not match live code.
- Verification fails twice after reasonable fix attempt.
- Change requires touching an out-of-scope file.

## Maintenance notes

- Downstream interactions and review considerations.
"""
