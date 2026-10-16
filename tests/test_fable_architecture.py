from pathlib import Path
import json
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_microservices_manifest_exists_and_conforms_to_fable_architecture():
    manifest_path = ROOT / "microservices_manifest.toon"
    assert manifest_path.is_file(), "microservices_manifest.toon must exist"

    text = manifest_path.read_text(encoding="utf-8")
    assert "architecture_manifest:" in text
    assert "verdict, allow_monolith, scale_score, domain_score, resource_score, composite_score" in text
    assert "microservices, false" in text

    # Parse evaluation numbers
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    eval_line = None
    for i, line in enumerate(lines):
        if "architecture_manifest:" in line and i + 1 < len(lines):
            eval_line = lines[i + 1]
            break
    assert eval_line is not None
    parts = [p.strip() for p in eval_line.split(",")]
    assert parts[0] == "microservices"
    assert parts[1] == "false"
    scale_score = float(parts[2])
    domain_score = float(parts[3])
    resource_score = float(parts[4])
    composite_score = float(parts[5])

    assert scale_score >= 7.0
    assert domain_score >= 7.0
    assert resource_score >= 7.0
    assert composite_score >= 6.0

    # Verify communication standards
    assert "communication_standards:" in text
    assert "North-South" in text
    assert "East-West" in text
    assert "proto/gtd_chatgpt_bridge.proto" in text

    # Verify services table
    assert "services [2]:" in text
    assert "gtd-orchestrator" in text
    assert "use-chatgpt-engine" in text
    assert "Rust" in text
    assert "Python" in text


def test_east_west_proto_contract_exists_and_defines_rpc():
    proto_path = ROOT / "proto" / "gtd_chatgpt_bridge.proto"
    assert proto_path.is_file(), "proto/gtd_chatgpt_bridge.proto must exist"

    content = proto_path.read_text(encoding="utf-8")
    assert 'syntax = "proto3";' in content
    assert "service GtdChatgptBridge" in content
    assert "rpc RouteIntent" in content
    assert "rpc InspectBotGate" in content
    assert "rpc EvaluateEvidence" in content
    assert "rpc ExecuteMacosAction" in content
    assert "message RoutingPacket" in content
    assert "message BotGateInspectResponse" in content
    assert "message EvidenceEvaluateResponse" in content


def test_rust_engine_crate_structure():
    crate_dir = ROOT / "crates" / "use-chatgpt-engine"
    assert (crate_dir / "Cargo.toml").is_file()
    assert (crate_dir / "src/main.rs").is_file()
    assert (crate_dir / "src/lib.rs").is_file()
    assert (crate_dir / "src/router/classifier.rs").is_file()
    assert (crate_dir / "src/router/dag.rs").is_file()
    assert (crate_dir / "src/bot_gate/fencer.rs").is_file()
    assert (crate_dir / "src/macos/notify.rs").is_file()


def test_companion_registry_declares_fable_transport():
    companions_path = ROOT / "adapters" / "companions.json"
    data = json.loads(companions_path.read_text(encoding="utf-8"))
    chatgpt_comp = next((c for c in data["companions"] if c["id"] == "use-chatgpt"), None)
    assert chatgpt_comp is not None
    assert chatgpt_comp["transport"] == "East-West CLI/IPC"
    assert "bot-is-neither-noise-nor-truth" in chatgpt_comp["guardrails"]
    assert "no-runtime-dependency" in chatgpt_comp["guardrails"]
