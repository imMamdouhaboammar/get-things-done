use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PromptContract {
    pub outcome: String,
    pub success_criteria: Vec<String>,
    pub source_of_truth: Vec<String>,
    pub in_scope: Vec<String>,
    pub out_of_scope: Vec<String>,
    pub allowed_permissions: Vec<String>,
    pub confirmation_required_permissions: Vec<String>,
    pub write_owner: String,
    pub tool_bindings: std::collections::HashMap<String, String>,
    pub evidence_required: Vec<String>,
    pub stop_conditions: Vec<String>,
}

impl Default for PromptContract {
    fn default() -> Self {
        Self {
            outcome: String::new(),
            success_criteria: Vec::new(),
            source_of_truth: Vec::new(),
            in_scope: Vec::new(),
            out_of_scope: Vec::new(),
            allowed_permissions: vec!["read_files".into(), "edit_workspace_files".into(), "run_tests".into()],
            confirmation_required_permissions: vec!["push_branch".into(), "merge_pr".into(), "mutate_production".into()],
            write_owner: "Codex Engineering Guardrails code-work".into(),
            tool_bindings: std::collections::HashMap::new(),
            evidence_required: vec!["clean_test_suite".into(), "verified_diff".into()],
            stop_conditions: vec!["COMPLETE".into(), "BLOCKED".into(), "AUTHORITY_REQUIRED".into()],
        }
    }
}
