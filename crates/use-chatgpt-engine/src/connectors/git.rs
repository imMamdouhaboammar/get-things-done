use super::cli_bridge::CliBridge;
use anyhow::Result;

pub struct GitConnector;

impl GitConnector {
    pub fn is_installed() -> bool {
        CliBridge::is_available("git")
    }

    pub fn get_current_head_sha() -> Result<String> {
        let out = CliBridge::run_command("git", &["rev-parse", "HEAD"])?;
        Ok(out.trim().to_string())
    }

    pub fn get_current_branch() -> Result<String> {
        let out = CliBridge::run_command("git", &["branch", "--show-current"])?;
        Ok(out.trim().to_string())
    }

    pub fn get_uncommitted_diff() -> Result<String> {
        let out = CliBridge::run_command("git", &["diff", "--stat"])?;
        Ok(out)
    }

    pub fn get_status_short() -> Result<String> {
        let out = CliBridge::run_command("git", &["status", "--short"])?;
        Ok(out)
    }
}
