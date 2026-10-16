use anyhow::{Context, Result};
use std::process::Command;

pub struct MacOSNotify;

impl MacOSNotify {
    /// Displays a native macOS Notification Center banner using AppleScript
    pub fn send(title: &str, subtitle: &str, message: &str) -> Result<()> {
        let script = format!(
            "display notification \"{}\" with title \"{}\" subtitle \"{}\" sound name \"Glass\"",
            escape_applescript(message),
            escape_applescript(title),
            escape_applescript(subtitle)
        );

        let output = Command::new("osascript")
            .arg("-e")
            .arg(&script)
            .output()
            .context("Failed to execute osascript for notification")?;

        if !output.status.success() {
            let err = String::from_utf8_lossy(&output.stderr);
            anyhow::bail!("osascript notification failed: {}", err);
        }
        Ok(())
    }
}

fn escape_applescript(s: &str) -> String {
    s.replace('\\', "\\\\").replace('\"', "\\\"")
}
