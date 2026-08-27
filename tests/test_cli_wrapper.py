import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "gtd.py"


def load_wrapper():
    spec = importlib.util.spec_from_file_location("gtd_wrapper", WRAPPER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_wrapper_import_is_side_effect_free():
    module = load_wrapper()
    assert callable(module.main)


def test_wrapper_points_at_canonical_cli():
    module = load_wrapper()
    assert module.CANONICAL == ROOT / "skills" / "get-things-done" / "scripts" / "gtd.py"
    assert module.CANONICAL.is_file()
