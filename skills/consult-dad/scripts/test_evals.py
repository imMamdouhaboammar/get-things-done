#!/usr/bin/env python3
"""Validate the evaluation scenarios for Consult Dad."""

import json
import sys
from pathlib import Path


def validate_scenarios(scenarios_path: Path) -> bool:
    if not scenarios_path.exists():
        print(f"Error: Scenarios file not found at {scenarios_path}")
        return False

    with open(scenarios_path, "r") as f:
        scenarios = json.load(f)

    if not isinstance(scenarios, list):
        print("Error: Scenarios must be a JSON list")
        return False

    print(f"Loaded {len(scenarios)} evaluation scenarios.")
    should_trigger = [s for s in scenarios if s.get("category") == "should-trigger"]
    should_not = [s for s in scenarios if s.get("category") == "should-not-trigger"]
    behavioral = [s for s in scenarios if s.get("category") == "behavioral"]

    print(f"- Should-trigger: {len(should_trigger)}")
    print(f"- Should-not-trigger: {len(should_not)}")
    print(f"- Behavioral: {len(behavioral)}")

    errors = []
    for s in scenarios:
        sid = s.get("id", "UNKNOWN")
        if not s.get("description"):
            errors.append(f"Scenario {sid} missing description")
        if not s.get("given") or not s.get("given", {}).get("intent"):
            errors.append(f"Scenario {sid} missing given.intent")
        if not s.get("expected"):
            errors.append(f"Scenario {sid} missing expected block")

    if errors:
        print(f"Validation FAILED with {len(errors)} errors:")
        for err in errors:
            print(f"  ❌ {err}")
        return False

    print("✅ All evaluation scenarios are structurally valid and complete.")
    return True


if __name__ == "__main__":
    path = Path(__file__).parent.parent / "evals" / "scenarios.json"
    success = validate_scenarios(path)
    sys.exit(0 if success else 1)
