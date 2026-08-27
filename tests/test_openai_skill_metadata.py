from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("get-things-done", "building-gtd-domain-packs")


def test_openai_skill_interfaces_match_current_shape_and_assets_exist():
    for skill_name in SKILLS:
        skill_dir = ROOT / "skills" / skill_name
        data = yaml.safe_load((skill_dir / "agents/openai.yaml").read_text(encoding="utf-8"))
        interface = data.get("interface")
        assert isinstance(interface, dict)
        assert 25 <= len(interface["short_description"]) <= 64
        assert interface["default_prompt"].startswith(f"Use ${skill_name}")
        for key in ("icon_small", "icon_large"):
            value = interface[key]
            assert value.startswith("./assets/")
            assert (skill_dir / value[2:]).is_file()
        policy = data.get("policy")
        assert policy == {"allow_implicit_invocation": True}
