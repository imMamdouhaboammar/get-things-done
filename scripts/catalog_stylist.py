#!/usr/bin/env python3
"""Skill Catalog Stylist — Automated visual identity & asset generator for GTD Skill Pack."""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import NamedTuple

import yaml


class SkillStyling(NamedTuple):
    name: str
    display_name: str
    short_description: str
    default_prompt: str
    brand_color: str
    gradient_start: str
    gradient_end: str
    accent_color: str
    categories: list[str]


CATALOG_CONFIG: dict[str, SkillStyling] = {
    "get-things-done": SkillStyling(
        name="get-things-done",
        display_name="Get Things Done",
        short_description="Convert messy, unclear ideas into verifiable, executable work models and action.",
        default_prompt="Turn this idea into an executable work model with clear facts, decisions, and actions:",
        brand_color="#2563EB",
        gradient_start="#2563EB",
        gradient_end="#0F172A",
        accent_color="#38BDF8",
        categories=["productivity", "project-management", "workflow-automation"],
    ),
    "building-gtd-domain-packs": SkillStyling(
        name="building-gtd-domain-packs",
        display_name="GTD Domain Pack Builder",
        short_description="Build domain-specific GTD extensions without forking the core contract.",
        default_prompt="Help me design a new domain pack extension for Get Things Done:",
        brand_color="#059669",
        gradient_start="#10B981",
        gradient_end="#064E3B",
        accent_color="#6EE7B7",
        categories=["developer-tools", "productivity"],
    ),
}


def build_gtd_large_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" fill="none">
  <defs>
    <linearGradient id="bgGradGTD" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563EB" />
      <stop offset="50%" stop-color="#1D4ED8" />
      <stop offset="100%" stop-color="#0F172A" />
    </linearGradient>
    <linearGradient id="vectorGradGTD" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="60%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#0284C7" />
    </linearGradient>
    <linearGradient id="checkGradGTD" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#FFFFFF" />
    </linearGradient>
    <radialGradient id="glowGTD" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#2563EB" stop-opacity="0" />
    </radialGradient>
    <filter id="dropShadowGTD" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#0284C7" flood-opacity="0.45" />
    </filter>
  </defs>

  <!-- Base Squircle -->
  <rect x="40" y="40" width="432" height="432" rx="96" fill="url(#bgGradGTD)" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="4" />
  <circle cx="256" cy="256" r="180" fill="url(#glowGTD)" />

  <!-- Precision Reticle & Geometry -->
  <circle cx="256" cy="256" r="150" stroke="#38BDF8" stroke-opacity="0.25" stroke-width="2" stroke-dasharray="8 8" />
  <circle cx="256" cy="256" r="110" stroke="#FFFFFF" stroke-opacity="0.15" stroke-width="1.5" />
  
  <!-- Outer Crosshair Notches -->
  <line x1="256" y1="76" x2="256" y2="96" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" />
  <line x1="256" y1="416" x2="256" y2="436" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" />
  <line x1="76" y1="256" x2="96" y2="256" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" />
  <line x1="416" y1="256" x2="436" y2="256" stroke="#38BDF8" stroke-width="3" stroke-linecap="round" />

  <!-- Four Quadrant Distinction Nodes (Fact, Assumption, Decision, Unknown) -->
  <circle cx="160" cy="160" r="5" fill="#38BDF8" fill-opacity="0.8" />
  <circle cx="352" cy="160" r="5" fill="#38BDF8" fill-opacity="0.8" />
  <circle cx="160" cy="352" r="5" fill="#38BDF8" fill-opacity="0.8" />
  <circle cx="352" cy="352" r="5" fill="#38BDF8" fill-opacity="0.8" />

  <!-- Central Dynamic Vector & Verified Checkmark Glyph -->
  <g filter="url(#dropShadowGTD)">
    <!-- Dynamic Forward Arrow Track -->
    <path d="M150 256 H290 M230 196 L290 256 L230 316" stroke="url(#vectorGradGTD)" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" />
    
    <!-- Bold Completion Checkmark -->
    <path d="M210 270 L260 320 L370 180" stroke="url(#checkGradGTD)" stroke-width="26" stroke-linecap="round" stroke-linejoin="round" />
  </g>

  <!-- Nexus Core Diamond -->
  <polygon points="256,128 266,138 256,148 246,138" fill="#FFFFFF" />
  <polygon points="256,364 266,374 256,384 246,374" fill="#38BDF8" />
</svg>"""


def build_gtd_small_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 512 512" fill="none">
  <defs>
    <linearGradient id="bgGradGTDSmall" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#0F172A" />
    </linearGradient>
    <linearGradient id="glyphGradGTDSmall" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="100%" stop-color="#38BDF8" />
    </linearGradient>
  </defs>

  <!-- Squircle Base -->
  <rect x="40" y="40" width="432" height="432" rx="96" fill="url(#bgGradGTDSmall)" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="6" />

  <!-- Bold High-Contrast Execution Glyph -->
  <path d="M140 256 H270 M210 196 L270 256 L210 316" stroke="#38BDF8" stroke-width="32" stroke-linecap="round" stroke-linejoin="round" opacity="0.8" />
  <path d="M210 270 L265 325 L375 175" stroke="#FFFFFF" stroke-width="38" stroke-linecap="round" stroke-linejoin="round" />
  
  <circle cx="256" cy="256" r="160" stroke="#38BDF8" stroke-opacity="0.3" stroke-width="6" stroke-dasharray="16 16" />
</svg>"""


def build_builder_large_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512" fill="none">
  <defs>
    <linearGradient id="bgGradBuilder" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10B981" />
      <stop offset="50%" stop-color="#059669" />
      <stop offset="100%" stop-color="#064E3B" />
    </linearGradient>
    <linearGradient id="topFaceGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6EE7B7" />
      <stop offset="100%" stop-color="#34D399" />
    </linearGradient>
    <linearGradient id="leftFaceGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#059669" />
      <stop offset="100%" stop-color="#047857" />
    </linearGradient>
    <linearGradient id="rightFaceGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#047857" />
      <stop offset="100%" stop-color="#065F46" />
    </linearGradient>
    <radialGradient id="glowBuilder" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#34D399" stop-opacity="0.3" />
      <stop offset="100%" stop-color="#059669" stop-opacity="0" />
    </radialGradient>
    <filter id="dropShadowBuilder" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#047857" flood-opacity="0.4" />
    </filter>
  </defs>

  <!-- Base Squircle -->
  <rect x="40" y="40" width="432" height="432" rx="96" fill="url(#bgGradBuilder)" stroke="#FFFFFF" stroke-opacity="0.18" stroke-width="4" />
  <circle cx="256" cy="256" r="180" fill="url(#glowBuilder)" />

  <!-- Blueprint Architectural Grid Lines -->
  <g opacity="0.22" stroke="#6EE7B7" stroke-width="1.5">
    <line x1="120" y1="180" x2="392" y2="336" stroke-dasharray="6 6" />
    <line x1="392" y1="180" x2="120" y2="336" stroke-dasharray="6 6" />
    <line x1="256" y1="100" x2="256" y2="412" stroke-dasharray="6 6" />
    <circle cx="256" cy="256" r="140" fill="none" stroke-width="1" />
  </g>

  <!-- 3D Isometric Domain Architecture Stack -->
  <g filter="url(#dropShadowBuilder)">
    <!-- Layer 1: Core Foundation Base Plate (Inherited GTD Contract) -->
    <g transform="translate(0, 70)">
      <polygon points="256,230 360,170 256,110 152,170" fill="#047857" stroke="#6EE7B7" stroke-width="2" stroke-opacity="0.6" />
      <polygon points="152,170 256,230 256,255 152,195" fill="#065F46" />
      <polygon points="256,230 360,170 360,195 256,255" fill="#064E3B" />
    </g>

    <!-- Layer 2: Domain Extension Tier (Vocabulary & Rules) -->
    <g transform="translate(0, 10)">
      <polygon points="256,215 345,165 256,115 167,165" fill="url(#topFaceGrad)" stroke="#FFFFFF" stroke-width="2.5" stroke-opacity="0.8" />
      <polygon points="167,165 256,215 256,242 167,192" fill="url(#leftFaceGrad)" />
      <polygon points="256,215 345,165 345,192 256,242" fill="url(#rightFaceGrad)" />
    </g>

    <!-- Layer 3: Floating Modular Plugin Block / Diamond Nexus -->
    <g transform="translate(0, -55)">
      <polygon points="256,190 320,150 256,110 192,150" fill="#FFFFFF" stroke="#6EE7B7" stroke-width="3" />
      <polygon points="192,150 256,190 256,215 192,175" fill="#34D399" />
      <polygon points="256,190 320,150 320,175 256,215" fill="#10B981" />
      
      <!-- Center Core Pulse -->
      <circle cx="256" cy="150" r="8" fill="#059669" />
      <circle cx="256" cy="150" r="4" fill="#FFFFFF" />
    </g>
  </g>

  <!-- Architectural Corner Nodes -->
  <circle cx="152" cy="240" r="4" fill="#6EE7B7" />
  <circle cx="360" cy="240" r="4" fill="#6EE7B7" />
  <circle cx="256" cy="95" r="5" fill="#FFFFFF" />
</svg>"""


def build_builder_small_svg() -> str:
    return """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 512 512" fill="none">
  <defs>
    <linearGradient id="bgGradBuilderSmall" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10B981" />
      <stop offset="100%" stop-color="#064E3B" />
    </linearGradient>
  </defs>

  <!-- Base Squircle -->
  <rect x="40" y="40" width="432" height="432" rx="96" fill="url(#bgGradBuilderSmall)" stroke="#FFFFFF" stroke-opacity="0.25" stroke-width="6" />

  <!-- Bold Simplified Isometric Modular Stack -->
  <!-- Base Tier -->
  <polygon points="256,360 380,290 256,220 132,290" fill="#047857" stroke="#6EE7B7" stroke-width="6" />
  <polygon points="132,290 256,360 256,395 132,325" fill="#065F46" />
  <polygon points="256,360 380,290 380,325 256,395" fill="#064E3B" />

  <!-- Top Floating Prism -->
  <polygon points="256,230 350,175 256,120 162,175" fill="#FFFFFF" stroke="#6EE7B7" stroke-width="6" />
  <polygon points="162,175 256,230 256,270 162,215" fill="#34D399" />
  <polygon points="256,230 350,175 350,215 256,270" fill="#10B981" />

  <circle cx="256" cy="175" r="14" fill="#064E3B" />
  <circle cx="256" cy="175" r="7" fill="#FFFFFF" />
</svg>"""


def build_openai_manifest(styling: SkillStyling) -> str:
    data = {
        "schema_version": "v1",
        "name": styling.name,
        "display_name": styling.display_name,
        "short_description": styling.short_description,
        "default_prompt": styling.default_prompt,
        "brand_color": styling.brand_color,
        "categories": styling.categories,
    }
    return yaml.dump(data, sort_keys=False, allow_unicode=True, width=1000)


def generate_all_assets(root: Path) -> None:
    skills_root = root / "skills"
    
    # 1. get-things-done
    gtd_dir = skills_root / "get-things-done"
    (gtd_dir / "assets").mkdir(parents=True, exist_ok=True)
    (gtd_dir / "agents").mkdir(parents=True, exist_ok=True)
    
    (gtd_dir / "assets" / "large-logo.svg").write_text(build_gtd_large_svg(), encoding="utf-8")
    (gtd_dir / "assets" / "small-logo.svg").write_text(build_gtd_small_svg(), encoding="utf-8")
    (gtd_dir / "agents" / "openai.yaml").write_text(build_openai_manifest(CATALOG_CONFIG["get-things-done"]), encoding="utf-8")
    
    # 2. building-gtd-domain-packs
    builder_dir = skills_root / "building-gtd-domain-packs"
    (builder_dir / "assets").mkdir(parents=True, exist_ok=True)
    (builder_dir / "agents").mkdir(parents=True, exist_ok=True)
    
    (builder_dir / "assets" / "large-logo.svg").write_text(build_builder_large_svg(), encoding="utf-8")
    (builder_dir / "assets" / "small-logo.svg").write_text(build_builder_small_svg(), encoding="utf-8")
    (builder_dir / "agents" / "openai.yaml").write_text(build_openai_manifest(CATALOG_CONFIG["building-gtd-domain-packs"]), encoding="utf-8")
    
    print(f"Generated brand assets & openai.yaml manifests for {len(CATALOG_CONFIG)} skills.")


def validate_catalog_assets(root: Path) -> list[str]:
    errors: list[str] = []
    skills_root = root / "skills"
    
    for skill_name, styling in CATALOG_CONFIG.items():
        skill_dir = skills_root / skill_name
        if not skill_dir.is_dir():
            errors.append(f"Skill directory not found: {skill_dir}")
            continue
            
        small_logo = skill_dir / "assets" / "small-logo.svg"
        large_logo = skill_dir / "assets" / "large-logo.svg"
        manifest = skill_dir / "agents" / "openai.yaml"
        skill_md = skill_dir / "SKILL.md"
        
        # Check files existence
        for p, desc in [(small_logo, "small-logo.svg"), (large_logo, "large-logo.svg"), (manifest, "agents/openai.yaml"), (skill_md, "SKILL.md")]:
            if not p.exists():
                errors.append(f"[{skill_name}] missing {desc} at {p}")
        
        # Validate SVGs
        for svg_path, exp_size in [(small_logo, 128), (large_logo, 512)]:
            if svg_path.exists():
                try:
                    tree = ET.fromstring(svg_path.read_text(encoding="utf-8"))
                    w = int(tree.attrib.get("width", 0))
                    h = int(tree.attrib.get("height", 0))
                    viewbox = tree.attrib.get("viewBox", "")
                    if w != h or w < 48:
                        errors.append(f"[{skill_name}] {svg_path.name} must be square with size >= 48 (got {w}x{h})")
                    if viewbox != "0 0 512 512":
                        errors.append(f"[{skill_name}] {svg_path.name} viewBox must be '0 0 512 512' (got '{viewbox}')")
                except Exception as e:
                    errors.append(f"[{skill_name}] {svg_path.name} invalid XML: {e}")
        
        # Validate manifest
        if manifest.exists():
            try:
                data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    errors.append(f"[{skill_name}] openai.yaml must be a YAML mapping")
                else:
                    disp = data.get("display_name", "")
                    if not disp or len(disp) > 40:
                        errors.append(f"[{skill_name}] display_name must be 1..40 chars (got {len(disp)})")
                    short_desc = data.get("short_description", "")
                    if not short_desc or len(short_desc) > 80:
                        errors.append(f"[{skill_name}] short_description must be 1..80 chars (got {len(short_desc)})")
                    prompt = data.get("default_prompt", "")
                    if not prompt or len(prompt) > 128 or "\n" in prompt:
                        errors.append(f"[{skill_name}] default_prompt must be single-line <= 128 chars (got {len(prompt)})")
                    brand = data.get("brand_color", "")
                    if not (brand.startswith("#") and len(brand) == 7 and all(c in "0123456789ABCDEFabcdef" for c in brand[1:])):
                        errors.append(f"[{skill_name}] brand_color must be valid #RRGGBB hex (got '{brand}')")
                    if brand.upper() != styling.brand_color.upper():
                        errors.append(f"[{skill_name}] brand_color {brand} does not match palette {styling.brand_color}")
            except Exception as e:
                errors.append(f"[{skill_name}] openai.yaml parsing error: {e}")
                
        # Validate SKILL.md frontmatter
        if skill_md.exists():
            content = skill_md.read_text(encoding="utf-8")
            if not content.startswith("---\n"):
                errors.append(f"[{skill_name}] SKILL.md missing frontmatter header")
            parts = content.split("---", 2)
            if len(parts) < 3:
                errors.append(f"[{skill_name}] SKILL.md malformed frontmatter")
            else:
                fm = yaml.safe_load(parts[1])
                if not isinstance(fm, dict):
                    errors.append(f"[{skill_name}] SKILL.md frontmatter must be YAML dict")
                else:
                    if fm.get("name") != skill_name:
                        errors.append(f"[{skill_name}] SKILL.md name mismatch: {fm.get('name')}")
                    desc = fm.get("description", "")
                    if not desc.startswith("Use when"):
                        errors.append(f"[{skill_name}] SKILL.md description must start with 'Use when'")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill Catalog Stylist utility")
    parser.add_argument("--root", default=".", help="Root of get-things-done repository")
    parser.add_argument("--generate", action="store_true", help="Generate or regenerate all SVG assets and manifests")
    parser.add_argument("--validate", action="store_true", help="Validate all catalog assets against store invariants")
    args = parser.parse_args()

    root = Path(args.root).resolve()

    if args.generate or not args.validate:
        generate_all_assets(root)

    if args.validate or not args.generate:
        errors = validate_catalog_assets(root)
        if errors:
            print("Validation FAILED with errors:")
            for err in errors:
                print(f"  ❌ {err}")
            return 1
        print("✅ All skill catalog assets, SVGs, and manifests passed 100% store preflight validation!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
