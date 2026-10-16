use use_chatgpt_engine::bot_gate::*;

#[test]
fn test_known_bot_recognition() {
    assert!(BotClassifier::is_known_bot("coderabbitai[bot]"));
    assert!(BotClassifier::is_known_bot("cursor-bugbot"));
    assert!(BotClassifier::is_known_bot("sourcery-ai"));
    assert!(BotClassifier::is_known_bot("autofix-ci"));
    assert!(!BotClassifier::is_known_bot("john_doe_developer"));
}

#[test]
fn test_comment_disposition_classification() {
    // Current actionable finding on current head
    let (disp, _) = BotClassifier::classify_comment(
        "coderabbitai",
        "Potential memory leak in connection pool buffer",
        Some("head123"),
        Some("head123"),
    );
    assert_eq!(disp, BotDisposition::CurrentActionable);

    // Stale comment on older head
    let (disp, _) = BotClassifier::classify_comment(
        "coderabbitai",
        "Potential memory leak in connection pool buffer",
        Some("older000"),
        Some("head123"),
    );
    assert_eq!(disp, BotDisposition::StaleAfterNewHead);

    // Already fixed formatting
    let (disp, _) = BotClassifier::classify_comment(
        "autofix.ci",
        "Autofix applied: rustfmt formatting rules",
        Some("head123"),
        Some("head123"),
    );
    assert_eq!(disp, BotDisposition::AlreadyFixed);

    // Informational summary
    let (disp, _) = BotClassifier::classify_comment(
        "sourcery-ai",
        "Here is the Pull Request walkthrough and summary guide",
        Some("head123"),
        Some("head123"),
    );
    assert_eq!(disp, BotDisposition::CurrentContext);
}

#[test]
fn test_bot_fencer_processing() {
    let raw = vec![
        ("coderabbitai", "Buffer overflow vulnerability detected", Some("sha_new")),
        ("sourcery-ai", "Refactor loop", Some("sha_old")),
        ("random_user", "Looks good to me!", None),
    ];

    let comments = BotFencer::process_comments(raw, Some("sha_new"));
    assert_eq!(comments.len(), 2); // random_user is not a bot
    assert_eq!(comments[0].disposition, BotDisposition::CurrentActionable);
    assert_eq!(comments[1].disposition, BotDisposition::StaleAfterNewHead);

    let report = BotFencer::format_report(&comments);
    assert!(report.contains("**Actionable Items Requiring Fix**: 1"));
    assert!(report.contains("CURRENT_ACTIONABLE"));
    assert!(report.contains("STALE_AFTER_NEW_HEAD"));
}
