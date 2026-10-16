use use_chatgpt_engine::models::*;

#[test]
fn test_evidence_trust_ladder_ordering() {
    assert!(EvidenceLevel::LevelA > EvidenceLevel::LevelB);
    assert!(EvidenceLevel::LevelB > EvidenceLevel::LevelC);
    assert!(EvidenceLevel::LevelC > EvidenceLevel::LevelD);
    assert!(EvidenceLevel::LevelD > EvidenceLevel::LevelE);
}

#[test]
fn test_evidence_ledger_rendering() {
    let mut ledger = EvidenceLedger::new("Authentication Feature");
    ledger.source_of_truth_inspected.push("src/auth.rs".to_string());
    ledger.changes_made.push("Added OAuth handler".to_string());
    ledger.tests_executed.push("cargo test auth (4 passed)".to_string());
    ledger.highest_level_attained = EvidenceLevel::LevelB;
    ledger.verdict = CompletionVerdict::Complete;

    let md = ledger.to_markdown();
    assert!(md.contains("Evidence Ledger: Authentication Feature"));
    assert!(md.contains("LEVEL B: EXECUTABLE PROOF"));
    assert!(md.contains("COMPLETE"));
    assert!(md.contains("cargo test auth"));
}
