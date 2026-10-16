use anyhow::{Context, Result};
use std::process::Command;

pub struct MacOSDialog;

impl MacOSDialog {
    /// Displays a native modal confirmation dialog on macOS.
    /// Returns true if user clicked OK, false if user cancelled.
    pub fn confirm(title: &str, prompt: &str) -> Result<bool> {
        let script = format!(
            "display dialog \"{}\" with title \"{}\" buttons {{\"Cancel\", \"Approve\"}} default button \"Approve\" with icon caution",
            escape_applescript(prompt),
            escape_applescript(title)
        );

        let output = Command::new("osascript")
            .arg("-e")
            .arg(&script)
            .output()
            .context("Failed to execute osascript dialog")?;

        if output.status.success() {
            let res = String::from_utf8_lossy(&output.stdout);
            Ok(res.contains("button returned:Approve"))
        } else {
            // User clicked cancel or dismissed dialog
            Ok(false)
        }
    }
}

fn escape_applescript(s: &str) -> String {
    s.replace('\\', "\\\\").replace('\"', "\\\"")
}
