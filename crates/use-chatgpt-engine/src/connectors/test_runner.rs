use super::cli_bridge::CliBridge;
use anyhow::Result;

pub struct TestRunner;

impl TestRunner {
    pub fn run_cargo_test(filter: Option<&str>) -> Result<(bool, String)> {
        let mut args = vec!["test"];
        if let Some(f) = filter {
            args.push(f);
        }

        match CliBridge::run_command("cargo", &args) {
            Ok(out) => Ok((true, out)),
            Err(e) => Ok((false, e.to_string())),
        }
    }

    pub fn run_bun_test(filter: Option<&str>) -> Result<(bool, String)> {
        let mut args = vec!["test"];
        if let Some(f) = filter {
            args.push(f);
        }

        match CliBridge::run_command("bun", &args) {
            Ok(out) => Ok((true, out)),
            Err(e) => Ok((false, e.to_string())),
        }
    }
}
