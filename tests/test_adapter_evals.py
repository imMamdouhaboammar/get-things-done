import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_adapter_evals_cover_every_registered_adapter_once():
    registry = json.loads((ROOT / "adapters/registry.json").read_text(encoding="utf-8"))
    cases = read_jsonl(ROOT / "evals/adapter-cases.jsonl")
    registered = {item["id"] for item in registry["adapters"]}
    evaluated = [item["adapter"] for item in cases]
    assert set(evaluated) == registered
    assert len(evaluated) == len(set(evaluated))


def test_companion_evals_cover_every_registered_companion_once():
    registry = json.loads((ROOT / "adapters/companions.json").read_text(encoding="utf-8"))
    cases = read_jsonl(ROOT / "evals/interop-cases.jsonl")
    registered = {item["id"] for item in registry["companions"]}
    evaluated = [item["companion"] for item in cases]
    assert set(evaluated) == registered
    assert len(evaluated) == len(set(evaluated))


def test_eval_cases_have_unique_ids_and_nonempty_expectations():
    cases = read_jsonl(ROOT / "evals/adapter-cases.jsonl") + read_jsonl(ROOT / "evals/interop-cases.jsonl")
    ids = [item["id"] for item in cases]
    assert len(ids) == len(set(ids))
    assert all(item.get("expected") for item in cases)
