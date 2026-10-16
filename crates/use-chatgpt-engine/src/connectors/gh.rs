use super::cli_bridge::CliBridge;
use anyhow::Result;

pub struct GhConnector;

impl GhConnector {
    pub fn is_installed() -> bool {
        CliBridge::is_available("gh")
    }

    pub fn list_open_prs() -> Result<String> {
        CliBridge::run_command("gh", &["pr", "list", "--limit", "10", "--json", "number,title,headRefName"])
    }

    pub fn view_pr_comments(pr_number: u32) -> Result<String> {
        let pr_str = pr_number.to_string();
        CliBridge::run_command("gh", &["pr", "view", &pr_str, "--comments"])
    }

    pub fn view_pr_checks(pr_number: u32) -> Result<String> {
        let pr_str = pr_number.to_string();
        CliBridge::run_command("gh", &["pr", "checks", &pr_str])
    }
}
