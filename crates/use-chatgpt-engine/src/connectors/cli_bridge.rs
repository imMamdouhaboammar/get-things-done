use anyhow::{bail, Context, Result};
use std::process::{Command, Stdio};

pub struct CliBridge;

impl CliBridge {
    pub fn run_command(program: &str, args: &[&str]) -> Result<String> {
        let output = Command::new(program)
            .args(args)
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .output()
            .with_context(|| format!("Failed to execute command: {} {:?}", program, args))?;

        if !output.status.success() {
            let err = String::from_utf8_lossy(&output.stderr);
            bail!("Command '{} {:?}' failed (exit code {:?}):\n{}", program, args, output.status.code(), err);
        }

        let out = String::from_utf8_lossy(&output.stdout).to_string();
        Ok(out)
    }

    pub fn is_available(program: &str) -> bool {
        which::which(program).is_ok()
    }
}
