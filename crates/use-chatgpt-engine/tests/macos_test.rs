use use_chatgpt_engine::macos::*;

#[test]
fn test_macos_system_cli_detection() {
    // Basic system commands that should exist on any macOS installation
    assert!(MacOSSystem::which_cli("sh"));
    assert!(MacOSSystem::which_cli("echo"));
}

#[test]
fn test_macos_clipboard_roundtrip() {
    let test_str = "use-chatgpt-engine-test-clipboard-12345";
    // Only run if pbcopy and pbpaste exist
    if MacOSSystem::which_cli("pbcopy") && MacOSSystem::which_cli("pbpaste") {
        let copy_res = MacOSClipboard::copy(test_str);
        if copy_res.is_ok() {
            let pasted = MacOSClipboard::paste().unwrap();
            assert_eq!(pasted.trim(), test_str);
        }
    }
}
