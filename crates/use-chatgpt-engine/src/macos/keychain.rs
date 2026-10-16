use anyhow::{bail, Context, Result};
use std::process::Command;

pub struct MacOSKeychain;

impl MacOSKeychain {
    /// Retrieves a password or token stored in macOS Keychain
    pub fn get_password(service: &str, account: &str) -> Result<String> {
        let output = Command::new("/usr/bin/security")
            .arg("find-generic-password")
            .arg("-s")
            .arg(service)
            .arg("-a")
            .arg(account)
            .arg("-w")
            .output()
            .context("Failed to execute /usr/bin/security")?;

        if !output.status.success() {
            bail!("Item not found in macOS Keychain for service '{}', account '{}'", service, account);
        }

        let token = String::from_utf8(output.stdout)
            .context("Invalid UTF-8 token from keychain")?
            .trim()
            .to_string();
        Ok(token)
    }

    /// Stores a password or token into macOS Keychain
    pub fn set_password(service: &str, account: &str, password: &str) -> Result<()> {
        let status = Command::new("/usr/bin/security")
            .arg("add-generic-password")
            .arg("-U")
            .arg("-s")
            .arg(service)
            .arg("-a")
            .arg(account)
            .arg("-w")
            .arg(password)
            .status()
            .context("Failed to update macOS Keychain")?;

        if !status.success() {
            bail!("Failed to set password in macOS Keychain (exit code: {:?})", status.code());
        }
        Ok(())
    }
}
