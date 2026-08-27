import json
from pathlib import Path
import pytest
import jsonschema

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import scripts.adapters as adapters

COMPANIONS_SCHEMA = json.loads((ROOT / "adapters" / "companions.schema.json").read_text(encoding="utf-8"))
COMPANIONS_DATA = json.loads((ROOT / "adapters" / "companions.json").read_text(encoding="utf-8"))


def test_all_companions_comply_with_schema():
    jsonschema.validate(instance=COMPANIONS_DATA, schema=COMPANIONS_SCHEMA)


@pytest.mark.parametrize("companion_id", [
    "plugin-autopilot",
    "plugin-eval",
    "superpowers",
    "armorcodex",
    "context7",
])
def test_companion_declares_mature_contract_fields(companion_id):
    companion = adapters.companions_by_id()[companion_id]
    assert isinstance(companion["inputs"], list) and len(companion["inputs"]) > 0
    assert isinstance(companion["outputs"], list) and len(companion["outputs"]) > 0
    assert isinstance(companion["evidence_contract"], str) and len(companion["evidence_contract"]) > 10
    assert isinstance(companion["failure_policy"], str) and len(companion["failure_policy"]) > 5
    assert isinstance(companion["authority_boundary"], str) and len(companion["authority_boundary"]) > 10
    assert "no-runtime-dependency" in companion["guardrails"] or "gtd-remains-domain-independent" in companion["guardrails"]


def test_companion_cannot_own_gtd_core():
    for companion in COMPANIONS_DATA["companions"]:
        assert companion["ownership"]["gtd"] == "execution-contract"
        assert companion["ownership"]["companion"] != "execution-contract"
        assert "manifest" not in companion
        assert "export" not in companion
        assert "project_path" not in companion


def test_interop_matrix_includes_mature_fields():
    matrix = adapters.interop_matrix()
    for companion_id in ["plugin-autopilot", "plugin-eval", "superpowers", "armorcodex", "context7"]:
        entry = matrix[companion_id]
        assert "inputs" in entry and len(entry["inputs"]) > 0
        assert "outputs" in entry and len(entry["outputs"]) > 0
        assert "failure_policy" in entry and len(entry["failure_policy"]) > 0
        assert "authority_boundary" in entry and len(entry["authority_boundary"]) > 0
