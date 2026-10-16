use crate::models::{CompletionVerdict, EvidenceLedger, EvidenceLevel, LifecycleStage};
use anyhow::{bail, Result};
use chrono::Utc;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowState {
    pub mission_title: String,
    pub current_stage: LifecycleStage,
    pub current_head_sha: Option<String>,
    pub history: Vec<StageTransitionRecord>,
    pub ledger: EvidenceLedger,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StageTransitionRecord {
    pub from: LifecycleStage,
    pub to: LifecycleStage,
    pub timestamp: chrono::DateTime<Utc>,
    pub proof: String,
}

pub struct StateMachineEngine {
    state_file: PathBuf,
    pub state: WorkflowState,
}

impl StateMachineEngine {
    pub fn load_or_init<P: AsRef<Path>>(path: P, mission_title: &str) -> Result<Self> {
        let state_file = path.as_ref().to_path_buf();
        if state_file.exists() {
            let data = fs::read_to_string(&state_file)?;
            if !data.trim().is_empty() {
                let state: WorkflowState = serde_json::from_str(&data)?;
                return Ok(Self { state_file, state });
            }
        }

        let state = WorkflowState {
            mission_title: mission_title.to_string(),
            current_stage: LifecycleStage::Classify,
            current_head_sha: None,
            history: Vec::new(),
            ledger: EvidenceLedger::new(mission_title),
        };
        let engine = Self { state_file, state };
        engine.save()?;
        Ok(engine)
    }

    pub fn save(&self) -> Result<()> {
        if let Some(parent) = self.state_file.parent() {
            fs::create_dir_all(parent)?;
        }
        let data = serde_json::to_string_pretty(&self.state)?;
        fs::write(&self.state_file, data)?;
        Ok(())
    }

    pub fn transition(&mut self, target: LifecycleStage, proof: &str) -> Result<()> {
        // Enforce invariants
        match (self.state.current_stage, target) {
            // Cannot jump to Release without passing verification (Level B or Level A)
            (_, LifecycleStage::Release) => {
                if self.state.ledger.highest_level_attained < EvidenceLevel::LevelB {
                    bail!(
                        "Gate Violation: Cannot transition to STAGE 7: RELEASE without Level B (Executable Proof) or Level A. Current level: {}",
                        self.state.ledger.highest_level_attained
                    );
                }
            }
            // Transitioning from Review back to Execute due to findings invalidates verification
            (LifecycleStage::Review, LifecycleStage::Execute) => {
                self.state.ledger.verdict = CompletionVerdict::Partial;
                eprintln!("[state-machine] Transitioning Review -> Execute: Verification invalidated until tests re-run.");
            }
            _ => {}
        }

        let record = StageTransitionRecord {
            from: self.state.current_stage,
            to: target,
            timestamp: Utc::now(),
            proof: proof.to_string(),
        };

        self.state.history.push(record);
        self.state.current_stage = target;
        self.save()?;
        Ok(())
    }

    /// Handles bot commit detection: forces invalidation of prior head SHA
    pub fn on_bot_commit(&mut self, new_sha: &str) -> Result<()> {
        eprintln!(
            "[state-machine] Bot commit detected: {} replaces previous SHA {:?}. Resetting to STAGE 1: RESTORE.",
            new_sha, self.state.current_head_sha
        );
        self.state.current_head_sha = Some(new_sha.to_string());
        self.state.current_stage = LifecycleStage::Restore;
        self.state.ledger.verdict = CompletionVerdict::Partial;
        self.save()?;
        Ok(())
    }
}
