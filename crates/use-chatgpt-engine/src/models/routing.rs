use super::capability::Capability;
use super::stage::LifecycleStage;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Mission {
    pub title: String,
    pub outcome: String,
    pub current_stage: LifecycleStage,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpecialistEntry {
    pub capability: String,
    pub reason: String,
    pub entry_trigger: String,
    pub expected_output: String,
    pub continuation: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RoutingPacket {
    pub mission: Mission,
    pub source_of_truth: Vec<String>,
    pub ownership: Ownership,
    pub specialists: Vec<SpecialistEntry>,
    pub verification_commands: Vec<String>,
    pub primary_reviewer: String,
    pub optional_second_reviewer: Option<String>,
    pub availability_snapshot: Vec<Capability>,
    pub landing_policy: LandingPolicy,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Ownership {
    pub orchestrator: String,
    pub write_owner: String,
    pub landing_owner: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LandingPolicy {
    pub current_head_required: bool,
    pub confirmation_rule: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DagNode {
    pub id: String,
    pub label: String,
    pub stage: LifecycleStage,
    pub tool: String,
    pub write_surface: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DagEdge {
    pub from: String,
    pub to: String,
    pub condition: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionDag {
    pub nodes: Vec<DagNode>,
    pub edges: Vec<DagEdge>,
}

impl ExecutionDag {
    pub fn new() -> Self {
        Self {
            nodes: Vec::new(),
            edges: Vec::new(),
        }
    }

    pub fn add_node(&mut self, node: DagNode) {
        self.nodes.push(node);
    }

    pub fn add_edge(&mut self, from: &str, to: &str, condition: &str) {
        self.edges.push(DagEdge {
            from: from.to_string(),
            to: to.to_string(),
            condition: condition.to_string(),
        });
    }

    pub fn to_mermaid(&self) -> String {
        let mut mermaid = String::from("flowchart TD\n");
        for node in &self.nodes {
            mermaid.push_str(&format!("    {}[\"{}: {}\"]\n", node.id, node.stage, node.label));
        }
        for edge in &self.edges {
            if edge.condition.is_empty() {
                mermaid.push_str(&format!("    {} --> {}\n", edge.from, edge.to));
            } else {
                mermaid.push_str(&format!("    {} -->|\"{}\"| {}\n", edge.from, edge.condition, edge.to));
            }
        }
        mermaid
    }
}
