#!/usr/bin/env python3
"""
East-West IPC Bridge connecting Get Things Done (Python) to Use-ChatGPT Rust Engine.
Defined under fable-architecture (microservices_manifest.toon & proto/gtd_chatgpt_bridge.proto).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class ChatgptBridge:
    """Typed IPC Client interfacing with the Pure Rust `chatgpt-skill` binary."""

    def __init__(self, pack_root: Optional[Path] = None, binary_path: Optional[Path] = None) -> None:
        if pack_root:
            self.pack_root = pack_root.resolve()
        else:
            self.pack_root = Path(os.environ.get("GTD_PACK_ROOT", Path(__file__).resolve().parents[3])).resolve()
        
        self.explicit_binary = binary_path
        self._binary_cache: Optional[Path] = None

    def find_binary(self) -> Optional[Path]:
        """Locate the chatgpt-skill binary across canonical release and system locations."""
        if self.explicit_binary and self.explicit_binary.is_file() and os.access(self.explicit_binary, os.X_OK):
            return self.explicit_binary

        if self._binary_cache and self._binary_cache.is_file():
            return self._binary_cache

        env_bin = os.environ.get("CHATGPT_SKILL_BIN")
        if env_bin:
            p = Path(env_bin).expanduser().resolve()
            if p.is_file() and os.access(p, os.X_OK):
                self._binary_cache = p
                return p

        candidates = [
            self.pack_root / "crates" / "use-chatgpt-engine" / "target" / "release" / "chatgpt-skill",
            self.pack_root / "crates" / "use-chatgpt-engine" / "target" / "debug" / "chatgpt-skill",
            Path.home() / ".local" / "bin" / "chatgpt-skill",
            Path.home() / ".cargo" / "bin" / "chatgpt-skill",
            Path("/usr/local/bin/chatgpt-skill"),
        ]

        for cand in candidates:
            if cand.is_file() and os.access(cand, os.X_OK):
                self._binary_cache = cand
                return cand

        system_which = shutil.which("chatgpt-skill")
        if system_which:
            p = Path(system_which).resolve()
            self._binary_cache = p
            return p

        return None

    def is_available(self) -> bool:
        return self.find_binary() is not None

    def _run_cli(self, args: List[str]) -> subprocess.CompletedProcess[str]:
        bin_path = self.find_binary()
        if not bin_path:
            raise FileNotFoundError(
                "chatgpt-skill binary not found. Build it with `cargo build --release` in crates/use-chatgpt-engine."
            )
        cmd = [str(bin_path)] + args
        return subprocess.run(cmd, capture_output=True, text=True, check=False)

    def route_intent(self, prompt: str, format_type: str = "json") -> Dict[str, Any]:
        """Classify intent and extract universal routing packet & DAG via Rust engine."""
        res = self._run_cli(["route", prompt, "--format", format_type])
        if res.returncode != 0:
            return {
                "success": False,
                "error": res.stderr.strip() or f"exit code {res.returncode}",
                "domain": "Unknown",
                "packet": {},
                "dag": "",
            }

        stdout = res.stdout
        domain_match = re.search(r"Classified Domain:\s*([A-Za-z0-9_]+)", stdout)
        domain = domain_match.group(1) if domain_match else "GeneralSoftware"

        packet: Dict[str, Any] = {}
        # Extract JSON packet between headers or directly
        if "=== Universal Routing Packet ===" in stdout:
            after_header = stdout.split("=== Universal Routing Packet ===")[1]
            if "=== Execution DAG" in after_header:
                json_part = after_header.split("=== Execution DAG")[0].strip()
            else:
                json_part = after_header.strip()
            try:
                packet = json.loads(json_part)
            except json.JSONDecodeError:
                pass

        dag_mermaid = ""
        if "```mermaid" in stdout:
            dag_mermaid = stdout.split("```mermaid")[1].split("```")[0].strip()

        return {
            "success": True,
            "domain": domain,
            "packet": packet,
            "dag": dag_mermaid,
            "raw": stdout,
        }

    def inspect_bot_gate(self, pr: Optional[int] = None, state_file: Optional[str] = None) -> Dict[str, Any]:
        """Inspect PR bot review context using Bot Gate Fencer (BOT != NOISE, BOT != TRUTH)."""
        args = ["bot-gate", "inspect"]
        if pr is not None:
            args.extend(["--pr", str(pr)])
        if state_file:
            args.extend(["--state-file", state_file])

        res = self._run_cli(args)
        if res.returncode != 0:
            return {
                "success": False,
                "error": res.stderr.strip() or f"exit code {res.returncode}",
                "comments": [],
                "actionable_count": 0,
                "current_head": "",
                "markdown": "",
            }

        stdout = res.stdout
        head_match = re.search(r"Current Local Git HEAD:\s*([a-f0-9]+)", stdout)
        head = head_match.group(1) if head_match else ""

        comments: List[Dict[str, str]] = []
        table_lines = [line.strip() for line in stdout.splitlines() if line.strip().startswith("| `")]
        for line in table_lines:
            cols = [col.strip().strip("`*") for col in line.strip("|").split("|")]
            if len(cols) >= 4:
                comments.append({
                    "author": cols[0],
                    "target_sha": cols[1],
                    "disposition": cols[2],
                    "justification": cols[3],
                })

        actionable_match = re.search(r"Actionable Items Requiring Fix\*:\s*(\d+)", stdout)
        actionable_count = int(actionable_match.group(1)) if actionable_match else sum(
            1 for c in comments if c["disposition"] == "CURRENT_ACTIONABLE"
        )

        return {
            "success": True,
            "current_head": head,
            "comments": comments,
            "actionable_count": actionable_count,
            "markdown": stdout,
        }

    @staticmethod
    def classify_evidence_level(evidence_str: str) -> str:
        """Classify an evidence statement against the 5-Tier Evidence Trust Ladder."""
        s = evidence_str.lower()
        if "level a" in s or any(k in s for k in ["pytest", "cargo test", "test passed", "exit code 0", "sha256", "checksum", "deterministic"]):
            return "LEVEL A: MACHINE PROOF"
        if "level b" in s or any(k in s for k in ["integration", "e2e", "curl", "api response", "browser verification", "live endpoint"]):
            return "LEVEL B: INTEGRATION PROOF"
        if "level c" in s or any(k in s for k in ["cli output", "command output", "log output", "terminal trace", "subprocess"]):
            return "LEVEL C: OBSERVED RUNTIME"
        if "level d" in s or any(k in s for k in ["inspected", "diff checked", "schema validated", "code inspection", "manual check"]):
            return "LEVEL D: STATIC INSPECTION"
        return "LEVEL E: CONTEXT / ASSERTION"

    def evaluate_evidence(self, items: List[str]) -> Dict[str, Any]:
        """Evaluate a list of evidence items against the Trust Ladder."""
        evaluated = []
        rank_order = {
            "LEVEL A: MACHINE PROOF": 5,
            "LEVEL B: INTEGRATION PROOF": 4,
            "LEVEL C: OBSERVED RUNTIME": 3,
            "LEVEL D: STATIC INSPECTION": 2,
            "LEVEL E: CONTEXT / ASSERTION": 1,
        }
        highest_rank = 0
        highest_level = "LEVEL E: CONTEXT / ASSERTION"

        for item in items:
            level = self.classify_evidence_level(item)
            rank = rank_order.get(level, 1)
            if rank > highest_rank:
                highest_rank = rank
                highest_level = level
            evaluated.append({"item": item, "level": level})

        return {
            "evaluated": evaluated,
            "highest_level": highest_level,
            "is_sufficient_for_done": highest_rank >= 3,
        }

    def macos_notify(self, title: str, message: str, subtitle: str = "GTD Alert") -> bool:
        """Trigger native macOS notification alert."""
        if self.is_available():
            res = self._run_cli(["macos", "notify", "--title", title, "--subtitle", subtitle, "--message", message])
            if res.returncode == 0:
                return True
        # Fallback to AppleScript osascript if binary unavailable
        if sys.platform == "darwin":
            script = f'display notification "{message}" with title "{title}" subtitle "{subtitle}"'
            proc = subprocess.run(["osascript", "-e", script], capture_output=True, check=False)
            return proc.returncode == 0
        return False

    def macos_copy(self, text: str) -> bool:
        """Copy text to macOS clipboard (pbcopy)."""
        if self.is_available():
            res = self._run_cli(["macos", "copy", text])
            if res.returncode == 0:
                return True
        if sys.platform == "darwin" and shutil.which("pbcopy"):
            p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
            p.communicate(input=text)
            return p.returncode == 0
        return False

    def macos_paste(self) -> str:
        """Paste text from macOS clipboard (pbpaste)."""
        if self.is_available():
            res = self._run_cli(["macos", "paste"])
            if res.returncode == 0:
                return res.stdout
        if sys.platform == "darwin" and shutil.which("pbpaste"):
            res = subprocess.run(["pbpaste"], capture_output=True, text=True, check=False)
            return res.stdout
        return ""

    def enrich_brief_with_route(self, brief: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Ultra-connected: Hydrate a GTD Execution Brief from chatgpt-skill routing."""
        route_data = self.route_intent(prompt)
        if not route_data.get("success"):
            return brief

        packet = route_data.get("packet", {})
        mission = packet.get("mission", {})

        if not brief.get("title") or brief["title"] == "Untitled":
            brief["title"] = mission.get("title") or prompt[:60]

        if not brief["intent"].get("problem"):
            brief["intent"]["problem"] = prompt
        if not brief["intent"].get("desired_outcome"):
            brief["intent"]["desired_outcome"] = mission.get("outcome") or f"Resolve: {prompt}"
        if not brief.get("domain"):
            brief["domain"] = "software"

        # Hydrate Knowledge Facts
        existing_facts = set(brief["knowledge"].get("facts", []))
        for source in packet.get("source_of_truth", []):
            fact_str = f"Source of truth: {source}"
            if fact_str not in existing_facts:
                brief["knowledge"]["facts"].append(fact_str)

        for av in packet.get("availability_snapshot", []):
            fact_str = f"Role '{av.get('role')}': {av.get('name')} [{av.get('availability')}]"
            if fact_str not in existing_facts:
                brief["knowledge"]["facts"].append(fact_str)

        # Hydrate Workstreams from specialists & DAG
        existing_streams = {w.get("name") for w in brief.get("workstreams", []) if isinstance(w, dict)}
        for sp in packet.get("specialists", []):
            c_name = sp.get("capability")
            if c_name and c_name not in existing_streams:
                brief["workstreams"].append({
                    "name": c_name,
                    "outcome": sp.get("expected_output", ""),
                    "dependencies": [sp.get("entry_trigger", "ready")],
                })

        # Hydrate Deliverables
        if not brief.get("deliverables"):
            brief["deliverables"] = [mission.get("outcome", f"Deliverable for: {prompt}")]

        # Hydrate Verification Criteria & Evidence seams
        verif_cmds = packet.get("verification_commands", [])
        existing_criteria = set(brief["verification"].get("success_criteria", []))
        for cmd in verif_cmds:
            if cmd not in existing_criteria:
                brief["verification"]["success_criteria"].append(cmd)

        if not brief["verification"].get("evidence"):
            brief["verification"]["evidence"] = [
                f"[LEVEL B] Automated verification for: {cmd}" for cmd in verif_cmds
            ] or ["[LEVEL A] Verification test run output"]

        # Next action
        if not brief.get("next_action"):
            brief["next_action"] = f"Execute Stage {mission.get('current_stage', 'INVESTIGATE')} for: {prompt}"

        # Domain metadata
        if "domain_data" not in brief or not isinstance(brief["domain_data"], dict):
            brief["domain_data"] = {}
        brief["domain_data"]["chatgpt_routing"] = {
            "classified_domain": route_data.get("domain"),
            "ownership": packet.get("ownership"),
            "landing_policy": packet.get("landing_policy"),
            "dag_mermaid": route_data.get("dag"),
        }

        return brief

    def enrich_brief_with_bot_gate(self, brief: Dict[str, Any], pr: Optional[int] = None) -> Dict[str, Any]:
        """Ultra-connected: Ingest PR bot reviews into Brief blockers, risks, and facts."""
        bot_data = self.inspect_bot_gate(pr)
        if not bot_data.get("success"):
            return brief

        existing_blockers = set(brief.get("blockers", []))
        existing_facts = set(brief["knowledge"].get("facts", []))
        existing_risks = set(brief.get("risks", []))

        head = bot_data.get("current_head", "unknown")
        brief["knowledge"]["facts"].append(f"PR Bot inspection evaluated at Git HEAD {head}")

        for comment in bot_data.get("comments", []):
            author = comment.get("author")
            disp = comment.get("disposition")
            just = comment.get("justification")
            entry = f"[{author}] {just}"

            if disp == "CURRENT_ACTIONABLE":
                if entry not in existing_blockers:
                    brief["blockers"].append(entry)
            elif disp == "STALE_AFTER_NEW_HEAD":
                stale_fact = f"Stale review skipped ({author}): {just}"
                if stale_fact not in existing_facts:
                    brief["knowledge"]["facts"].append(stale_fact)
            elif disp == "ALREADY_FIXED":
                fixed_fact = f"Review item resolved ({author}): {just}"
                if fixed_fact not in existing_facts:
                    brief["knowledge"]["facts"].append(fixed_fact)
            else:
                if entry not in existing_risks:
                    brief["risks"].append(entry)

        if "domain_data" not in brief or not isinstance(brief["domain_data"], dict):
            brief["domain_data"] = {}
        brief["domain_data"]["bot_gate"] = {
            "inspected_head": head,
            "actionable_count": bot_data.get("actionable_count", 0),
            "dispositions": bot_data.get("comments", []),
        }

        return brief

    def enrich_brief_with_evidence_ladder(self, brief: Dict[str, Any]) -> Dict[str, Any]:
        """Ultra-connected: Grade verification evidence against the 5-Tier Trust Ladder."""
        evidence_items = brief.get("verification", {}).get("evidence", [])
        if not evidence_items:
            return brief

        eval_res = self.evaluate_evidence(evidence_items)
        graded_evidence = []
        for item_eval in eval_res.get("evaluated", []):
            item = item_eval["item"]
            level = item_eval["level"]
            if not item.startswith("[LEVEL "):
                graded_evidence.append(f"[{level}] {item}")
            else:
                graded_evidence.append(item)

        brief["verification"]["evidence"] = graded_evidence
        if "domain_data" not in brief or not isinstance(brief["domain_data"], dict):
            brief["domain_data"] = {}
        brief["domain_data"]["evidence_grade"] = {
            "highest_level": eval_res.get("highest_level"),
            "is_sufficient_for_done": eval_res.get("is_sufficient_for_done"),
        }
        return brief
