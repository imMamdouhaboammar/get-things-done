use crate::connectors::{CliBridge, GhConnector, GitConnector};
use anyhow::Result;
use colored::Colorize;

pub struct ConnectCmd;

impl ConnectCmd {
    pub fn test_connections() -> Result<()> {
        println!("{}", "🔌 Probing External CLIs & Bridges...".cyan().bold());

        let git_ok = GitConnector::is_installed();
        let gh_ok = GhConnector::is_installed();
        let bun_ok = CliBridge::is_available("bun");
        let cargo_ok = CliBridge::is_available("cargo");
        let osascript_ok = CliBridge::is_available("osascript");
        let pbcopy_ok = CliBridge::is_available("pbcopy");
        let security_ok = CliBridge::is_available("/usr/bin/security");

        print_status("Git CLI (git)", git_ok);
        print_status("GitHub CLI (gh)", gh_ok);
        print_status("Bun Runtime (bun)", bun_ok);
        print_status("Cargo / Rust (cargo)", cargo_ok);
        print_status("macOS AppleScript (osascript)", osascript_ok);
        print_status("macOS Clipboard (pbcopy / pbpaste)", pbcopy_ok);
        print_status("macOS Keychain (/usr/bin/security)", security_ok);

        if git_ok {
            if let Ok(branch) = GitConnector::get_current_branch() {
                println!("  {} Current Git Branch: {}", "•".cyan(), branch);
            }
            if let Ok(sha) = GitConnector::get_current_head_sha() {
                println!("  {} Current HEAD SHA: {}", "•".cyan(), sha);
            }
        }

        println!("\n{}", "Connectivity probe complete.".green().bold());
        Ok(())
    }
}

fn print_status(name: &str, ok: bool) {
    if ok {
        println!("  {} {}", "✓".green().bold(), name);
    } else {
        println!("  {} {} (not found in PATH)", "✗".red().bold(), name);
    }
}
