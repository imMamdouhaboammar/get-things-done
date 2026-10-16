use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum EvidenceLevel {
    /// Level E: Context, previous session memory, or hypotheses
    LevelE = 0,
    /// Level D: External primary documentation or standards
    LevelD = 1,
    /// Level C: Independent AI or static code review
    LevelC = 2,
    /// Level B: Executable proof (tests, compiler, CI runs)
    LevelB = 3,
    /// Level A: Direct current state (live filesystem, DB, running UI)
    LevelA = 4,
}

impl std::fmt::Display for EvidenceLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::LevelA => write!(f, "LEVEL A: DIRECT CURRENT STATE"),
            Self::LevelB => write!(f, "LEVEL B: EXECUTABLE PROOF"),
            Self::LevelC => write!(f, "LEVEL C: INDEPENDENT REVIEW"),
            Self::LevelD => write!(f, "LEVEL D: EXTERNAL CONTRACT"),
            Self::LevelE => write!(f, "LEVEL E: CONTEXT / MEMORY / INFERENCE"),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum CompletionVerdict {
    Complete,
    CompleteWithFollowups,
    Partial,
    Blocked,
    NotStarted,
}

impl std::fmt::Display for CompletionVerdict {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Complete => write!(f, "COMPLETE"),
            Self::CompleteWithFollowups => write!(f, "COMPLETE_WITH_FOLLOWUPS"),
            Self::Partial => write!(f, "PARTIAL"),
            Self::Blocked => write!(f, "BLOCKED"),
            Self::NotStarted => write!(f, "NOT_STARTED"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidenceLedger {
    pub mission_title: String,
    pub source_of_truth_inspected: Vec<String>,
    pub changes_made: Vec<String>,
    pub tests_executed: Vec<String>,
    pub runtime_checks: Vec<String>,
    pub review_evidence: Vec<String>,
    pub open_pr_bot_context: Vec<String>,
    pub known_limitations: Vec<String>,
    pub highest_level_attained: EvidenceLevel,
    pub verdict: CompletionVerdict,
    pub updated_at: DateTime<Utc>,
}

impl EvidenceLedger {
    pub fn new(mission_title: &str) -> Self {
        Self {
            mission_title: mission_title.to_string(),
            source_of_truth_inspected: Vec::new(),
            changes_made: Vec::new(),
            tests_executed: Vec::new(),
            runtime_checks: Vec::new(),
            review_evidence: Vec::new(),
            open_pr_bot_context: Vec::new(),
            known_limitations: Vec::new(),
            highest_level_attained: EvidenceLevel::LevelE,
            verdict: CompletionVerdict::NotStarted,
            updated_at: Utc::now(),
        }
    }

    pub fn to_markdown(&self) -> String {
        format!(
            "### Evidence Ledger: {}\n\n\
            - **Source of Truth Inspected**:\n  {}\n\
            - **Changes Made**:\n  {}\n\
            - **Tests Executed**:\n  {}\n\
            - **Runtime Checks**:\n  {}\n\
            - **Review Evidence**:\n  {}\n\
            - **Open-PR Bot Context**:\n  {}\n\
            - **Known Limitations**:\n  {}\n\
            - **Highest Evidence Level Attained**: {}\n\
            - **Final Verdict**: **{}**\n\
            - **Timestamp**: {}\n",
            self.mission_title,
            if self.source_of_truth_inspected.is_empty() { "None recorded".to_string() } else { self.source_of_truth_inspected.join("\n  ") },
            if self.changes_made.is_empty() { "None".to_string() } else { self.changes_made.join("\n  ") },
            if self.tests_executed.is_empty() { "None executed".to_string() } else { self.tests_executed.join("\n  ") },
            if self.runtime_checks.is_empty() { "None executed".to_string() } else { self.runtime_checks.join("\n  ") },
            if self.review_evidence.is_empty() { "None recorded".to_string() } else { self.review_evidence.join("\n  ") },
            if self.open_pr_bot_context.is_empty() { "None inspected".to_string() } else { self.open_pr_bot_context.join("\n  ") },
            if self.known_limitations.is_empty() { "None".to_string() } else { self.known_limitations.join("\n  ") },
            self.highest_level_attained,
            self.verdict,
            self.updated_at.to_rfc3339()
        )
    }
}
