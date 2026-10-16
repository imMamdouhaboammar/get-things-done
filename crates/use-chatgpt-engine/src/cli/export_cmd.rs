use anyhow::Result;
use colored::Colorize;
use std::fs;
use std::path::Path;

pub struct ExportCmd;

impl ExportCmd {
    pub fn export_manifests(target_dir: &Path) -> Result<()> {
        println!("{}", "📦 Exporting Multi-Agent Distribution Manifests...".cyan().bold());

        let codex_dir = target_dir.join(".codex-plugin");
        fs::create_dir_all(&codex_dir)?;
        let plugin_json = r#"{
  "name": "use-chatgpt",
  "version": "1.0.0",
  "description": "Modular agentic router and execution engine for orchestrating installed plugins and CLIs.",
  "entrypoint": "skills/use-chatgpt/SKILL.md",
  "author": "Mamdouh Aboammar"
}
"#;
        fs::write(codex_dir.join("plugin.json"), plugin_json)?;
        println!("  {} .codex-plugin/plugin.json", "✓".green());

        let claude_dir = target_dir.join(".claude-plugin");
        fs::create_dir_all(&claude_dir)?;
        let claude_json = r#"{
  "name": "use-chatgpt",
  "version": "1.0.0",
  "description": "Evidence-grounded capability router and open-PR bot gating engine",
  "commands": [
    {
      "name": "use-chatgpt",
      "description": "Route engineering tasks through installed capability graph",
      "exec": "chatgpt-skill route"
    }
  ]
}
"#;
        fs::write(claude_dir.join("manifest.json"), claude_json)?;
        println!("  {} .claude-plugin/manifest.json", "✓".green());

        let agents_dir = target_dir.join(".agents");
        fs::create_dir_all(&agents_dir)?;
        let agents_json = r#"{
  "schema_version": "1.0.0",
  "skills": {
    "use-chatgpt": {
      "path": "skills/use-chatgpt",
      "engine": "crates/use-chatgpt-engine"
    }
  }
}
"#;
        fs::write(agents_dir.join("skills.json"), agents_json)?;
        println!("  {} .agents/skills.json", "✓".green());

        println!("{}", "All manifests generated successfully!".green().bold());
        Ok(())
    }
}
