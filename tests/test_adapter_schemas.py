import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = ROOT / "adapters"


def load(name: str) -> dict:
    return json.loads((ADAPTERS / name).read_text(encoding="utf-8"))


def test_registry_conforms_to_published_schema():
    jsonschema.validate(instance=load("registry.json"), schema=load("registry.schema.json"))


def test_companions_conform_to_published_schema():
    jsonschema.validate(instance=load("companions.json"), schema=load("companions.schema.json"))


def test_registries_reference_local_schema_files():
    assert load("registry.json")["$schema"] == "./registry.schema.json"
    assert load("companions.json")["$schema"] == "./companions.schema.json"
