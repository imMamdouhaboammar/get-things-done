use anyhow::{bail, Context, Result};
use std::process::Command;

pub struct MacOSSystem;

impl MacOSSystem {
    /// Opens a URL or file path using the default macOS handler
    pub fn open_target(target: &str) -> Result<()> {
        let status = Command::new("open")
            .arg(target)
            .status()
            .context("Failed to run open command")?;

        if !status.success() {
            bail!("open command failed with status: {:?}", status.code());
        }
        Ok(())
    }

    /// Checks if a CLI tool is available in PATH
    pub fn which_cli(cli_name: &str) -> bool {
        which::which(cli_name).is_ok()
    }
}
