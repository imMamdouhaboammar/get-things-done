use crate::models::{CompletionVerdict, EvidenceLevel};
use crate::state_machine::StateMachineEngine;
use anyhow::Result;
use colored::Colorize;
use std::path::Path;

pub struct EvidenceCmd;

impl EvidenceCmd {
    pub fn init(state_file: &Path, mission_title: &str) -> Result<()> {
        let engine = StateMachineEngine::load_or_init(state_file, mission_title)?;
        println!("{} for mission: '{}'", "✓ Initialized Evidence Ledger".green().bold(), engine.state.mission_title);
        Ok(())
    }

    pub fn record(
        state_file: &Path,
        source: Option<String>,
        change: Option<String>,
        test: Option<String>,
        runtime: Option<String>,
        review: Option<String>,
        bot: Option<String>,
        level: Option<String>,
        verdict: Option<String>,
    ) -> Result<()> {
        let mut engine = StateMachineEngine::load_or_init(state_file, "Default Mission")?;

        if let Some(s) = source {
            engine.state.ledger.source_of_truth_inspected.push(s);
        }
        if let Some(c) = change {
            engine.state.ledger.changes_made.push(c);
        }
        if let Some(t) = test {
            engine.state.ledger.tests_executed.push(t);
            if engine.state.ledger.highest_level_attained < EvidenceLevel::LevelB {
                engine.state.ledger.highest_level_attained = EvidenceLevel::LevelB;
            }
        }
        if let Some(r) = runtime {
            engine.state.ledger.runtime_checks.push(r);
            engine.state.ledger.highest_level_attained = EvidenceLevel::LevelA;
        }
        if let Some(rv) = review {
            engine.state.ledger.review_evidence.push(rv);
            if engine.state.ledger.highest_level_attained < EvidenceLevel::LevelC {
                engine.state.ledger.highest_level_attained = EvidenceLevel::LevelC;
            }
        }
        if let Some(b) = bot {
            engine.state.ledger.open_pr_bot_context.push(b);
        }
        if let Some(lvl_str) = level {
            let upper = lvl_str.to_uppercase();
            if upper.contains('A') {
                engine.state.ledger.highest_level_attained = EvidenceLevel::LevelA;
            } else if upper.contains('B') {
                engine.state.ledger.highest_level_attained = EvidenceLevel::LevelB;
            } else if upper.contains('C') {
                engine.state.ledger.highest_level_attained = EvidenceLevel::LevelC;
            } else if upper.contains('D') {
                engine.state.ledger.highest_level_attained = EvidenceLevel::LevelD;
            } else {
                engine.state.ledger.highest_level_attained = EvidenceLevel::LevelE;
            }
        }
        if let Some(v_str) = verdict {
            let upper = v_str.to_uppercase();
            if upper.contains("COMPLETE_WITH_FOLLOWUPS") {
                engine.state.ledger.verdict = CompletionVerdict::CompleteWithFollowups;
            } else if upper.contains("COMPLETE") {
                engine.state.ledger.verdict = CompletionVerdict::Complete;
            } else if upper.contains("PARTIAL") {
                engine.state.ledger.verdict = CompletionVerdict::Partial;
            } else if upper.contains("BLOCKED") {
                engine.state.ledger.verdict = CompletionVerdict::Blocked;
            } else {
                engine.state.ledger.verdict = CompletionVerdict::NotStarted;
            }
        }

        engine.state.ledger.updated_at = chrono::Utc::now();
        engine.save()?;

        println!("{}", "✓ Evidence ledger updated!".green().bold());
        println!("\n{}", engine.state.ledger.to_markdown());
        Ok(())
    }

    pub fn show(state_file: &Path) -> Result<()> {
        let engine = StateMachineEngine::load_or_init(state_file, "Default Mission")?;
        println!("{}", engine.state.ledger.to_markdown());
        Ok(())
    }
}
