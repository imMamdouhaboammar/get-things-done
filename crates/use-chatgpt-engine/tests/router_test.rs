use use_chatgpt_engine::models::*;
use use_chatgpt_engine::router::*;

#[test]
fn test_classify_feature_with_rust() {
    let prompt = "Build a user authentication microservice in Rust with cargo test";
    let intent = IntentClassifier::classify(prompt);

    assert_eq!(intent.domain, IntentDomain::FeatureImplementation);
    assert_eq!(intent.target_language.as_deref(), Some("rust"));
    assert!(intent.requires_local_execution);
    assert!(intent.involves_security_boundary);
}

#[test]
fn test_classify_pr_repair() {
    let prompt = "Inspect PR #42 and fix CodeRabbit and Bugbot review feedback";
    let intent = IntentClassifier::classify(prompt);

    assert_eq!(intent.domain, IntentDomain::PullRequestRepair);
    assert!(intent.requires_pr_context);
    assert!(intent.requires_connected_source);
}

#[test]
fn test_precedence_order() {
    let mut caps = vec![
        Capability::new("Reviewer", Role::Reviewer, false, "Code review"),
        Capability::new("Source", Role::Source, false, "GitHub source"),
        Capability::new("Executor", Role::Executor, true, "Local editor"),
        Capability::new("Landing", Role::Landing, true, "PR Completion"),
    ];

    PrecedenceEngine::sort_by_precedence(&mut caps);

    assert_eq!(caps[0].role, Role::Source);
    assert_eq!(caps[1].role, Role::Executor);
    assert_eq!(caps[2].role, Role::Reviewer);
    assert_eq!(caps[3].role, Role::Landing);
}

#[test]
fn test_dag_builder_generation() {
    let prompt = "Implement payment integration in TypeScript with unit tests";
    let intent = IntentClassifier::classify(prompt);
    let (packet, dag) = DagBuilder::build(&intent);

    assert!(!packet.ownership.orchestrator.is_empty());
    assert!(!packet.ownership.write_owner.is_empty());
    assert_eq!(packet.ownership.write_owner, "Codex Engineering Guardrails code-work");
    assert!(!dag.nodes.is_empty());
    assert!(!dag.edges.is_empty());

    let mermaid = dag.to_mermaid();
    assert!(mermaid.starts_with("flowchart TD"));
    assert!(mermaid.contains("node_classify"));
    assert!(mermaid.contains("node_verify"));
}
