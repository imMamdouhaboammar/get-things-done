use crate::models::{Capability, Role};

pub struct PrecedenceEngine;

impl PrecedenceEngine {
    pub fn precedence_score(role: &Role) -> u32 {
        match role {
            Role::Source => 1,
            Role::Contract => 2,
            Role::Planner => 3,
            Role::Executor => 4,
            Role::Verifier => 5,
            Role::Reviewer => 6,
            Role::Security => 7,
            Role::RuntimeQa => 8,
            Role::Readiness => 9,
            Role::Landing => 10,
            Role::Handoff => 11,
        }
    }

    pub fn sort_by_precedence(capabilities: &mut [Capability]) {
        capabilities.sort_by_key(|c| Self::precedence_score(&c.role));
    }
}
