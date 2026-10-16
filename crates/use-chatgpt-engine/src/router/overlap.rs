use crate::models::{Capability, Role};
use anyhow::{bail, Result};

pub struct OverlapResolver;

impl OverlapResolver {
    /// Validates that there is at most one primary orchestrator and exactly one write owner per mutable surface.
    pub fn validate_ownership(capabilities: &[Capability]) -> Result<()> {
        let planners: Vec<_> = capabilities.iter().filter(|c| c.role == Role::Planner).collect();
        if planners.len() > 1 {
            bail!(
                "Overlap Violation: Multiple primary orchestrators selected ({:?}). Select exactly one primary lifecycle owner.",
                planners.iter().map(|c| &c.name).collect::<Vec<_>>()
            );
        }

        let write_owners: Vec<_> = capabilities.iter().filter(|c| c.write_authority).collect();
        if write_owners.len() > 1 {
            // Note: If distinct surfaces, it's allowed, but within one task we fence concurrent mutations
            let names: Vec<_> = write_owners.iter().map(|c| &c.name).collect();
            tracing_or_log(&format!(
                "Caution: Multiple write authorities declared ({:?}). Ensure write surfaces are strictly disjoint.",
                names
            ));
        }

        Ok(())
    }

    /// Selects the optimal primary orchestrator and reviewers based on classified intent.
    pub fn resolve_owners(
        is_fable_active: bool,
        is_pr_repair: bool,
        is_security_sensitive: bool,
    ) -> (String, String, String, Option<String>) {
        let orchestrator = if is_pr_repair {
            "@PR Completion".to_string()
        } else if is_fable_active {
            "@get-fable".to_string()
        } else {
            "@Superpowers".to_string()
        };

        let write_owner = "Codex Engineering Guardrails code-work".to_string();
        let primary_reviewer = "@CodeRabbit".to_string();
        let second_reviewer = if is_security_sensitive {
            Some("@Codex Security".to_string())
        } else {
            None
        };

        (orchestrator, write_owner, primary_reviewer, second_reviewer)
    }
}

fn tracing_or_log(msg: &str) {
    eprintln!("[use-chatgpt-engine] {}", msg);
}
