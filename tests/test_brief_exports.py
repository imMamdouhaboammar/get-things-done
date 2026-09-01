import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "gtd.py"
EXAMPLE = ROOT / "examples" / "software-brief.json"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_export_all_writes_every_supported_format(tmp_path):
    out = tmp_path / "exports"

    result = run_cli("export-brief", str(EXAMPLE), "--format", "all", "--out", str(out))

    assert result.returncode == 0, result.stdout + result.stderr
    expected = {
        "software-brief.md",
        "software-brief.json",
        "software-brief.toon",
        "software-brief.mmd",
        "software-brief.graph.json",
    }
    assert {path.name for path in out.iterdir()} == expected
    assert json.loads((out / "software-brief.json").read_text(encoding="utf-8")) == json.loads(
        EXAMPLE.read_text(encoding="utf-8")
    )
    assert (
        (out / "software-brief.md")
        .read_text(encoding="utf-8")
        .startswith("# Execution Brief: Brand-aware agent review layer")
    )


def test_toon_export_uses_standard_compact_shapes(tmp_path):
    out = tmp_path / "brief.toon"

    result = run_cli("export-brief", str(EXAMPLE), "--format", "toon", "--out", str(out))

    assert result.returncode == 0, result.stdout + result.stderr
    text = out.read_text(encoding="utf-8")
    assert 'version: "1.0"' in text
    assert "decisions[1]{decision,rationale,reversible}:" in text
    assert "workstreams[2]:" in text
    assert "dependencies: []" in text
    assert not text.endswith("\n")


def test_relational_graph_preserves_workstream_dependencies(tmp_path):
    out = tmp_path / "graph"

    result = run_cli("export-brief", str(EXAMPLE), "--format", "graph", "--out", str(out))

    assert result.returncode == 0, result.stdout + result.stderr
    graph = json.loads((out / "software-brief.graph.json").read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in graph["nodes"]}
    dependency_edges = [edge for edge in graph["edges"] if edge["relation"] == "depends_on"]
    assert graph["directed"] is True
    assert nodes["workstream:0"]["label"] == "Brand contract"
    assert nodes["workstream:1"]["label"] == "Review layer"
    assert dependency_edges == [{"source": "workstream:1", "target": "workstream:0", "relation": "depends_on"}]

    mermaid = (out / "software-brief.mmd").read_text(encoding="utf-8")
    assert mermaid.startswith("flowchart LR\n")
    assert "Brand contract" in mermaid
    assert "Review layer" in mermaid
    assert "-->|depends_on|" in mermaid


def test_mermaid_export_escapes_labels(tmp_path):
    payload = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    payload["title"] = 'Plan "A"\nnext line'
    source = tmp_path / "quoted.json"
    source.write_text(json.dumps(payload), encoding="utf-8")
    out = tmp_path / "quoted.mmd"

    result = run_cli("export-brief", str(source), "--format", "mermaid", "--out", str(out))

    assert result.returncode == 0, result.stdout + result.stderr
    mermaid = out.read_text(encoding="utf-8")
    assert 'n0["Plan &quot;A&quot;<br/>next line"]' in mermaid


def test_export_rejects_invalid_brief_before_writing(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text('{"title": "Incomplete"}', encoding="utf-8")
    out = tmp_path / "invalid.toon"

    result = run_cli("export-brief", str(invalid), "--format", "toon", "--out", str(out))

    assert result.returncode == 1
    assert "INVALID" in result.stderr
    assert not out.exists()
