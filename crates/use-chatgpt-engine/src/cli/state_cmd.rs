use crate::models::LifecycleStage;
use crate::state_machine::StateMachineEngine;
use anyhow::Result;
use colored::Colorize;
use std::path::Path;

pub struct StateCmd;

impl StateCmd {
    pub fn show(state_file: &Path) -> Result<()> {
        let engine = StateMachineEngine::load_or_init(state_file, "Default Mission")?;
        println!("{}", "=== Current Workflow State ===".green().bold());
        println!("  {} {}", "Mission:".yellow(), engine.state.mission_title);
        println!("  {} {}", "Stage:".yellow(), engine.state.current_stage);
        if let Some(ref sha) = engine.state.current_head_sha {
            println!("  {} {}", "Head SHA:".yellow(), sha);
        }
        println!("  {} {}", "Verdict:".yellow(), engine.state.ledger.verdict);
        println!("  {} {}", "Highest Evidence Level:".yellow(), engine.state.ledger.highest_level_attained);

        if !engine.state.history.is_empty() {
            println!("\n{}", "Transition History:".cyan().bold());
            for rec in &engine.state.history {
                println!("  [{}] {} -> {}: {}", rec.timestamp.to_rfc3339(), rec.from, rec.to, rec.proof);
            }
        }
        Ok(())
    }

    pub fn transition(state_file: &Path, target: &str, proof: &str) -> Result<()> {
        let mut engine = StateMachineEngine::load_or_init(state_file, "Default Mission")?;
        let stage = LifecycleStage::from_str_loose(target)
            .ok_or_else(|| anyhow::anyhow!("Unknown lifecycle stage name: '{}'", target))?;

        println!("Attempting transition: {} -> {}...", engine.state.current_stage, stage);
        engine.transition(stage, proof)?;
        println!("{}", "✓ Transition recorded successfully!".green().bold());
        Ok(())
    }
}
