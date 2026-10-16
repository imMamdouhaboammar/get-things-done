use crate::models::{
    AvailabilityState, BlockReason, Capability, DagNode, ExecutionDag, LandingPolicy, LifecycleStage,
    Mission, Ownership, Role, RoutingPacket, SpecialistEntry,
};
use super::classifier::{ClassifiedIntent, IntentDomain};
use super::overlap::OverlapResolver;

pub struct DagBuilder;

impl DagBuilder {
    pub fn build(intent: &ClassifiedIntent) -> (RoutingPacket, ExecutionDag) {
        let (orchestrator, write_owner, primary_reviewer, second_reviewer) = OverlapResolver::resolve_owners(
            false,
            intent.domain == IntentDomain::PullRequestRepair,
            intent.involves_security_boundary,
        );

        let landing_owner = if intent.requires_pr_context {
            "@PR Completion".to_string()
        } else {
            "Repository CI & Branch Policy".to_string()
        };

        let mut specialists = Vec::new();
        if intent.involves_security_boundary {
            specialists.push(SpecialistEntry {
                capability: "@Codex Security".to_string(),
                reason: "Changed trust boundaries require dedicated security analysis".to_string(),
                entry_trigger: "Implementation of auth/secrets complete".to_string(),
                expected_output: "Security findings and remediation".to_string(),
                continuation: "Re-run security test suite".to_string(),
            });
        }

        if let Some(ref lang) = intent.target_language {
            specialists.push(SpecialistEntry {
                capability: "@Context7".to_string(),
                reason: format!("Inspect version-specific {} APIs and conventions", lang),
                entry_trigger: "Prior to writing contract-sensitive code".to_string(),
                expected_output: "Official API examples".to_string(),
                continuation: "Execute implementation".to_string(),
            });
        }

        if intent.involves_ui_ux {
            specialists.push(SpecialistEntry {
                capability: "@Impeccable".to_string(),
                reason: "Inspect accessibility, responsive layout, and interaction states".to_string(),
                entry_trigger: "UI component rendered".to_string(),
                expected_output: "A11y/UI hardening checklist".to_string(),
                continuation: "Apply UI fixes".to_string(),
            });
        }

        let mut verification_commands = Vec::new();
        if let Some(ref lang) = intent.target_language {
            if lang == "rust" {
                verification_commands.push("cargo test".to_string());
                verification_commands.push("cargo check".to_string());
            } else if lang == "typescript" {
                verification_commands.push("bun test".to_string());
                verification_commands.push("bun run typecheck".to_string());
            }
        }
        if verification_commands.is_empty() {
            verification_commands.push("Run targeted unit and regression tests".to_string());
        }

        let mut availability_snapshot = vec![
            Capability {
                name: "@GitHub".to_string(),
                role: Role::Source,
                write_authority: true,
                availability: AvailabilityState::Connected,
                block_reason: BlockReason::None,
                description: "Remote repo source of truth and PR tracking".to_string(),
            },
            Capability {
                name: orchestrator.clone(),
                role: Role::Planner,
                write_authority: false,
                availability: AvailabilityState::Callable,
                block_reason: BlockReason::None,
                description: "Primary lifecycle orchestration".to_string(),
            },
            Capability {
                name: write_owner.clone(),
                role: Role::Executor,
                write_authority: true,
                availability: AvailabilityState::Callable,
                block_reason: BlockReason::None,
                description: "Scoped code modification".to_string(),
            },
            Capability {
                name: primary_reviewer.clone(),
                role: Role::Reviewer,
                write_authority: false,
                availability: AvailabilityState::Callable,
                block_reason: BlockReason::None,
                description: "Independent AI review of meaningful diff".to_string(),
            },
        ];

        if let Some(ref sec) = second_reviewer {
            availability_snapshot.push(Capability {
                name: sec.clone(),
                role: Role::Security,
                write_authority: false,
                availability: AvailabilityState::Callable,
                block_reason: BlockReason::None,
                description: "Dedicated security analysis".to_string(),
            });
        }

        let packet = RoutingPacket {
            mission: Mission {
                title: intent.raw_prompt.clone(),
                outcome: format!("Execute '{}' with verified Level A/B evidence", intent.raw_prompt),
                current_stage: if intent.requires_connected_source {
                    LifecycleStage::Restore
                } else {
                    LifecycleStage::Investigate
                },
            },
            source_of_truth: vec![
                if intent.requires_connected_source { "@GitHub (Live repo & PR state)".to_string() } else { "Local active worktree".to_string() }
            ],
            ownership: Ownership {
                orchestrator: orchestrator.clone(),
                write_owner: write_owner.clone(),
                landing_owner: landing_owner.clone(),
            },
            specialists,
            verification_commands,
            primary_reviewer,
            optional_second_reviewer: second_reviewer,
            availability_snapshot,
            landing_policy: LandingPolicy {
                current_head_required: true,
                confirmation_rule: "Explicit human or CI required-checks verification before merge".to_string(),
            },
        };

        // Construct DAG
        let mut dag = ExecutionDag::new();

        dag.add_node(DagNode {
            id: "node_classify".to_string(),
            label: "Classify Domain & Source of Truth".to_string(),
            stage: LifecycleStage::Classify,
            tool: orchestrator.clone(),
            write_surface: false,
        });

        dag.add_node(DagNode {
            id: "node_restore".to_string(),
            label: "Restore Live State & Reconcile Handoff".to_string(),
            stage: LifecycleStage::Restore,
            tool: "@GitHub".to_string(),
            write_surface: false,
        });

        dag.add_node(DagNode {
            id: "node_investigate".to_string(),
            label: "Investigate Code & External Contracts".to_string(),
            stage: LifecycleStage::Investigate,
            tool: "@Context7 / Workspace".to_string(),
            write_surface: false,
        });

        dag.add_node(DagNode {
            id: "node_plan".to_string(),
            label: "Plan Bounded Scope & Test Plan".to_string(),
            stage: LifecycleStage::Plan,
            tool: orchestrator.clone(),
            write_surface: false,
        });

        dag.add_node(DagNode {
            id: "node_execute".to_string(),
            label: "Implement Changes".to_string(),
            stage: LifecycleStage::Execute,
            tool: write_owner.clone(),
            write_surface: true,
        });

        dag.add_node(DagNode {
            id: "node_verify".to_string(),
            label: "Run Executable Verification (Level B)".to_string(),
            stage: LifecycleStage::Verify,
            tool: "Test Runner / CI".to_string(),
            write_surface: false,
        });

        dag.add_node(DagNode {
            id: "node_review".to_string(),
            label: "Independent Review (Level C)".to_string(),
            stage: LifecycleStage::Review,
            tool: "@CodeRabbit".to_string(),
            write_surface: false,
        });

        dag.add_node(DagNode {
            id: "node_release".to_string(),
            label: "Landing & CI Gate Verification".to_string(),
            stage: LifecycleStage::Release,
            tool: landing_owner,
            write_surface: true,
        });

        // Edges
        dag.add_edge("node_classify", "node_restore", "Domain identified");
        dag.add_edge("node_restore", "node_investigate", "State synchronized");
        dag.add_edge("node_investigate", "node_plan", "Uncertainty resolved");
        dag.add_edge("node_plan", "node_execute", "Scope bounded");
        dag.add_edge("node_execute", "node_verify", "Changes committed");
        dag.add_edge("node_verify", "node_review", "Tests passing");
        dag.add_edge("node_review", "node_release", "Clean review pass");
        dag.add_edge("node_review", "node_execute", "Findings need repair");

        (packet, dag)
    }
}
