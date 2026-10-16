use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum BotDisposition {
    CurrentActionable,
    CurrentContext,
    AlreadyFixed,
    StaleAfterNewHead,
    Duplicate,
    FalsePositive,
    NeedsDecision,
}

impl std::fmt::Display for BotDisposition {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::CurrentActionable => write!(f, "CURRENT_ACTIONABLE"),
            Self::CurrentContext => write!(f, "CURRENT_CONTEXT"),
            Self::AlreadyFixed => write!(f, "ALREADY_FIXED"),
            Self::StaleAfterNewHead => write!(f, "STALE_AFTER_NEW_HEAD"),
            Self::Duplicate => write!(f, "DUPLICATE"),
            Self::FalsePositive => write!(f, "FALSE_POSITIVE"),
            Self::NeedsDecision => write!(f, "NEEDS_DECISION"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BotComment {
    pub author: String,
    pub body: String,
    pub target_sha: Option<String>,
    pub disposition: BotDisposition,
    pub justification: String,
}

pub struct BotClassifier;

impl BotClassifier {
    pub fn is_known_bot(author: &str) -> bool {
        let a = author.to_lowercase();
        a.contains("coderabbit")
            || a.contains("bugbot")
            || a.contains("sourcery")
            || a.contains("autofix")
            || a.contains("qlty")
            || a.contains("mergify")
            || a.contains("cubic")
            || a.contains("gitar")
            || a.contains("ecc-tools")
    }

    pub fn classify_comment(
        author: &str,
        body: &str,
        comment_sha: Option<&str>,
        current_head_sha: Option<&str>,
    ) -> (BotDisposition, String) {
        // If the comment points to an older SHA than current HEAD
        if let (Some(c_sha), Some(head_sha)) = (comment_sha, current_head_sha) {
            if c_sha != head_sha {
                return (
                    BotDisposition::StaleAfterNewHead,
                    format!("Comment targets commit {} which is older than current HEAD {}", c_sha, head_sha),
                );
            }
        }

        let b_lower = body.to_lowercase();

        if b_lower.contains("format") || b_lower.contains("style applied") || b_lower.contains("autofix applied") {
            (
                BotDisposition::AlreadyFixed,
                "Automated style/format patch already incorporated".to_string(),
            )
        } else if b_lower.contains("summary") || b_lower.contains("guide") || b_lower.contains("walkthrough") {
            (
                BotDisposition::CurrentContext,
                "Informational overview; no code action required".to_string(),
            )
        } else if b_lower.contains("architecture") || b_lower.contains("design choice") || b_lower.contains("trade-off") {
            (
                BotDisposition::NeedsDecision,
                "Requires engineering sign-off on design decision".to_string(),
            )
        } else if b_lower.contains("bug") || b_lower.contains("vulnerability") || b_lower.contains("leak") || b_lower.contains("error") {
            (
                BotDisposition::CurrentActionable,
                format!("Defect flagged by {}; requires code fix or test refutation", author),
            )
        } else {
            (
                BotDisposition::CurrentContext,
                "General bot comment; context extracted".to_string(),
            )
        }
    }
}
