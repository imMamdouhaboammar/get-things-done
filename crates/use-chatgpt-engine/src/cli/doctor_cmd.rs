use crate::connectors::CliBridge;
use anyhow::Result;
use colored::Colorize;
use std::path::Path;

pub struct DoctorCmd;

impl DoctorCmd {
    pub fn run(skill_dir: &Path) -> Result<()> {
        println!("{}", "🩺 Running System & Skill Health Check...".cyan().bold());

        let mut all_green = true;

        // 1. Check Skill root
        let skill_md = skill_dir.join("SKILL.md");
        if skill_md.exists() {
            println!("  {} SKILL.md found", "✓".green());
        } else {
            println!("  {} SKILL.md missing at {:?}", "✗".red(), skill_md);
            all_green = false;
        }

        // 2. Check references
        let refs = [
            "operating-contract.md",
            "plugin-role-model.md",
            "execution-surfaces.md",
            "open-pr-bot-gate.md",
            "evidence-trust-ladder.md",
            "capability-graph.md",
            "workflow-state-machine.md",
            "agentic-recipes.md",
            "prompt-contracts.md",
        ];
        for r in refs {
            if skill_dir.join("references").join(r).exists() {
                println!("  {} reference: {}", "✓".green(), r);
            } else {
                println!("  {} reference missing: {}", "✗".red(), r);
                all_green = false;
            }
        }

        // 3. Check CLI tools
        let tools = ["git", "gh", "bun", "cargo", "osascript", "pbcopy"];
        for t in tools {
            if CliBridge::is_available(t) {
                println!("  {} tool: {}", "✓".green(), t);
            } else {
                println!("  {} tool not in PATH: {}", "⚠".yellow(), t);
            }
        }

        if all_green {
            println!("\n{}", "🎉 System and Skill Package are 100% Healthy!".green().bold());
        } else {
            println!("\n{}", "⚠ One or more checks failed. Review warnings above.".yellow().bold());
        }

        Ok(())
    }
}
