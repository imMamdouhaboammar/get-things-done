#!/usr/bin/env python3
"""Assess context readiness, decision reversibility, and GTD brief structure for Consult Dad."""

import argparse
import json
import sys
from typing import Dict, Any, List


def score_context_readiness(text: str) -> Dict[str, Any]:
    """Calculate context readiness score (0-8) based on heuristics."""
    score = 0
    breakdown = {}

    # Dimension 1: Specificity of challenge
    specific_indicators = ["offer", "startup", "pivot", "quit", "decide", "co-founder", "salary", "budget", "client", "contract"]
    has_specific = any(ind in text.lower() for ind in specific_indicators)
    breakdown["specificity"] = 2 if has_specific else (1 if len(text.split()) > 10 else 0)
    score += breakdown["specificity"]

    # Dimension 2: Active options
    option_indicators = [" or ", " vs ", "option a", "between", "either"]
    has_options = any(ind in text.lower() for ind in option_indicators)
    breakdown["options"] = 2 if has_options else (1 if "?" in text else 0)
    score += breakdown["options"]

    # Dimension 3: Binding constraints
    constraint_indicators = ["month", "week", "runway", "deadline", "$", "dollar", "penalty", "family", "kids", "savings"]
    has_constraints = any(ind in text.lower() for ind in constraint_indicators)
    breakdown["constraints"] = 2 if has_constraints else (1 if len(text.split()) > 20 else 0)
    score += breakdown["constraints"]

    # Dimension 4: Underlying priority
    priority_indicators = ["want", "love", "scared", "fear", "hate", "value", "growth", "stable", "energy", "excited"]
    has_priority = any(ind in text.lower() for ind in priority_indicators)
    breakdown["priority"] = 2 if has_priority else (1 if "I" in text else 0)
    score += breakdown["priority"]

    recommendation = "Proceed directly to assessment (0 questions required)" if score >= 6 else (
        "Ask exactly ONE high-information clarifying question" if score >= 4 else
        "Ask one foundational context-gathering question"
    )

    return {
        "score": score,
        "max_score": 8,
        "is_ready": score >= 6,
        "breakdown": breakdown,
        "recommendation": recommendation
    }


def classify_reversibility(decision_text: str) -> Dict[str, Any]:
    """Classify whether a decision is Type 1 (irreversible) or Type 2 (reversible)."""
    irreversible_indicators = ["equity", "sell", "quit", "lease", "fire", "lawsuit", "public", "shut down", "kill company"]
    is_type_1 = any(ind in decision_text.lower() for ind in irreversible_indicators)
    
    return {
        "classification": "Type 1 (Irreversible / High Friction)" if is_type_1 else "Type 2 (Reversible / Two-Way Door)",
        "velocity_rule": "Conduct thorough Pre-Mortem & 10/10/10 analysis before commitment" if is_type_1 else "Bias to rapid execution (<48h) and treat outcome as test data"
    }


def validate_brief_schema(brief_data: Dict[str, Any]) -> List[str]:
    """Check required fields in an advisory execution brief."""
    required = ["version", "title", "domain", "status", "intent", "knowledge", "decisions", "next_action"]
    errors = []
    for field in required:
        if field not in brief_data:
            errors.append(f"Missing required field: '{field}'")
    if brief_data.get("domain") not in ["advisory", "consulting"]:
        errors.append(f"Invalid domain '{brief_data.get('domain')}'; expected 'advisory'")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Consult Dad Context Readiness & GTD Brief Assessor")
    parser.add_argument("--text", type=str, help="User input text to evaluate")
    parser.add_argument("--demo", action="store_true", help="Run self-test demo")
    parser.add_argument("--brief", type=str, help="Path to JSON brief to validate")

    args = parser.parse_args()

    if args.demo:
        sample = "I have two job offers. Offer A is a Series A startup with 40% salary bump and 14 months runway. Offer B is enterprise tech with high stability. I love fast work but I'm afraid of startup failure."
        print(json.dumps({
            "sample_input": sample,
            "readiness": score_context_readiness(sample),
            "reversibility": classify_reversibility(sample)
        }, indent=2))
        sys.exit(0)

    if args.text:
        readiness = score_context_readiness(args.text)
        reversibility = classify_reversibility(args.text)
        print(json.dumps({"readiness": readiness, "reversibility": reversibility}, indent=2))
        sys.exit(0)

    if args.brief:
        with open(args.brief, "r") as f:
            data = json.load(f)
        errs = validate_brief_schema(data)
        if errs:
            print(json.dumps({"status": "invalid", "errors": errs}, indent=2))
            sys.exit(1)
        else:
            print(json.dumps({"status": "valid", "title": data.get("title")}, indent=2))
            sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
