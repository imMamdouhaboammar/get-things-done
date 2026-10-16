use crate::macos::{MacOSClipboard, MacOSDialog, MacOSKeychain, MacOSNotify, MacOSSystem};
use anyhow::Result;
use colored::Colorize;

pub struct MacOSCmd;

impl MacOSCmd {
    pub fn copy(text: &str) -> Result<()> {
        MacOSClipboard::copy(text)?;
        println!("{}", "✓ Copied text to macOS clipboard (pbcopy)".green().bold());
        Ok(())
    }

    pub fn paste() -> Result<()> {
        let text = MacOSClipboard::paste()?;
        println!("{}", text);
        Ok(())
    }

    pub fn notify(title: &str, subtitle: &str, message: &str) -> Result<()> {
        MacOSNotify::send(title, subtitle, message)?;
        println!("{}", "✓ Dispatched macOS Notification Center alert (osascript)".green().bold());
        Ok(())
    }

    pub fn dialog(title: &str, prompt: &str) -> Result<()> {
        println!("Prompting macOS confirmation dialog...");
        let approved = MacOSDialog::confirm(title, prompt)?;
        if approved {
            println!("{}", "✓ User approved dialog.".green().bold());
        } else {
            println!("{}", "✗ User cancelled dialog.".red().bold());
        }
        Ok(())
    }

    pub fn open_target(target: &str) -> Result<()> {
        MacOSSystem::open_target(target)?;
        println!("Opened target '{}' via macOS open", target);
        Ok(())
    }

    pub fn keychain_get(service: &str, account: &str) -> Result<()> {
        let secret = MacOSKeychain::get_password(service, account)?;
        println!("Keychain Secret for {}@{}: [REDACTED {} chars]", service, account, secret.len());
        Ok(())
    }
}
