use tempfile::NamedTempFile;
use use_chatgpt_engine::models::*;
use use_chatgpt_engine::state_machine::*;

#[test]
fn test_state_machine_flow_and_gating() {
    let tmp = NamedTempFile::new().unwrap();
    let mut engine = StateMachineEngine::load_or_init(tmp.path(), "Test Mission").unwrap();

    assert_eq!(engine.state.current_stage, LifecycleStage::Classify);

    // Transition to Restore
    engine.transition(LifecycleStage::Restore, "Source inspected").unwrap();
    assert_eq!(engine.state.current_stage, LifecycleStage::Restore);

    // Transition to Investigate
    engine.transition(LifecycleStage::Investigate, "Code analyzed").unwrap();

    // Transition to Plan
    engine.transition(LifecycleStage::Plan, "Plan created").unwrap();

    // Transition to Execute
    engine.transition(LifecycleStage::Execute, "Implementation started").unwrap();

    // Attempting to jump directly to Release without Level B verification fails!
    let release_res = engine.transition(LifecycleStage::Release, "Jump to landing");
    assert!(release_res.is_err());
    assert!(release_res.unwrap_err().to_string().contains("Gate Violation"));

    // Now record executable proof Level B
    engine.state.ledger.highest_level_attained = EvidenceLevel::LevelB;

    // Transition to Verify
    engine.transition(LifecycleStage::Verify, "Tests passing").unwrap();

    // Transition to Review
    engine.transition(LifecycleStage::Review, "Review clean").unwrap();

    // Transition to Release now succeeds
    engine.transition(LifecycleStage::Release, "All gates verified").unwrap();
    assert_eq!(engine.state.current_stage, LifecycleStage::Release);
}

#[test]
fn test_bot_commit_invalidates_state() {
    let tmp = NamedTempFile::new().unwrap();
    let mut engine = StateMachineEngine::load_or_init(tmp.path(), "Test Mission").unwrap();

    engine.state.current_head_sha = Some("abc111".to_string());
    engine.state.current_stage = LifecycleStage::Review;

    // Bot authors a commit
    engine.on_bot_commit("def222").unwrap();

    // Must reset to Restore stage to fetch new head
    assert_eq!(engine.state.current_stage, LifecycleStage::Restore);
    assert_eq!(engine.state.current_head_sha.as_deref(), Some("def222"));
    assert_eq!(engine.state.ledger.verdict, CompletionVerdict::Partial);
}
