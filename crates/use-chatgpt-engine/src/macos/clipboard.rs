use anyhow::{Context, Result};
use std::io::Write;
use std::process::{Command, Stdio};

pub struct MacOSClipboard;

impl MacOSClipboard {
    /// Copies text to macOS system clipboard using pbcopy
    pub fn copy(text: &str) -> Result<()> {
        let mut child = Command::new("pbcopy")
            .stdin(Stdio::piped())
            .spawn()
            .context("Failed to spawn pbcopy")?;

        if let Some(mut stdin) = child.stdin.take() {
            stdin.write_all(text.as_bytes())?;
        }

        let status = child.wait()?;
        if !status.success() {
            anyhow::bail!("pbcopy exited with non-zero status: {:?}", status.code());
        }
        Ok(())
    }

    /// Reads text from macOS system clipboard using pbpaste
    pub fn paste() -> Result<String> {
        let output = Command::new("pbpaste")
            .output()
            .context("Failed to execute pbpaste")?;

        if !output.status.success() {
            anyhow::bail!("pbpaste exited with non-zero status: {:?}", output.status.code());
        }

        let text = String::from_utf8(output.stdout)
            .context("Clipboard content is not valid UTF-8")?;
        Ok(text)
    }
}
