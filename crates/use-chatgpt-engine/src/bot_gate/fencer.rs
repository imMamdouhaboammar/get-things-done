use super::classifier::{BotClassifier, BotComment, BotDisposition};

pub struct BotFencer;

impl BotFencer {
    pub fn process_comments(
        raw_comments: Vec<(&str, &str, Option<&str>)>,
        current_head_sha: Option<&str>,
    ) -> Vec<BotComment> {
        let mut results = Vec::new();
        for (author, body, comment_sha) in raw_comments {
            if BotClassifier::is_known_bot(author) {
                let (disposition, justification) = BotClassifier::classify_comment(
                    author,
                    body,
                    comment_sha,
                    current_head_sha,
                );
                results.push(BotComment {
                    author: author.to_string(),
                    body: body.to_string(),
                    target_sha: comment_sha.map(|s| s.to_string()),
                    disposition,
                    justification,
                });
            }
        }
        results
    }

    pub fn format_report(comments: &[BotComment]) -> String {
        let mut report = String::from("### Open-PR Bot Context Report\n\n");
        if comments.is_empty() {
            report.push_str("No active GitHub App / bot comments detected.\n");
            return report;
        }

        report.push_str("| Author | Target SHA | Disposition | Justification |\n");
        report.push_str("| :--- | :--- | :--- | :--- |\n");
        for c in comments {
            report.push_str(&format!(
                "| `{}` | `{}` | **{}** | {} |\n",
                c.author,
                c.target_sha.as_deref().unwrap_or("unspecified"),
                c.disposition,
                c.justification
            ));
        }

        let actionable_count = comments.iter().filter(|c| c.disposition == BotDisposition::CurrentActionable).count();
        report.push_str(&format!("\n**Actionable Items Requiring Fix**: {}\n", actionable_count));
        report
    }
}
