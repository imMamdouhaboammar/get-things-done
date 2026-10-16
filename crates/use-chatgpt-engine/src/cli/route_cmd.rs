use crate::router::{DagBuilder, IntentClassifier};
use anyhow::Result;
use colored::Colorize;

pub struct RouteCmd;

impl RouteCmd {
    pub fn execute(prompt: &str, format: &str, show_dag: bool) -> Result<()> {
        println!("{}", "⚡ Analyzing Intent & Routing Capabilities...".cyan().bold());
        let intent = IntentClassifier::classify(prompt);

        println!("  {} {:?}", "Classified Domain:".yellow(), intent.domain);
        if let Some(ref l) = intent.target_language {
            println!("  {} {}", "Target Language:".yellow(), l);
        }
        println!("  {} {}", "Connected Source Needed:".yellow(), intent.requires_connected_source);
        println!("  {} {}", "Local Execution Needed:".yellow(), intent.requires_local_execution);
        println!("  {} {}", "Security Boundary:".yellow(), intent.involves_security_boundary);

        let (packet, dag) = DagBuilder::build(&intent);

        println!("\n{}", "=== Universal Routing Packet ===".green().bold());
        if format == "json" {
            println!("{}", serde_json::to_string_pretty(&packet)?);
        } else {
            println!("{}", serde_yaml::to_string(&packet)?);
        }

        if show_dag {
            println!("\n{}", "=== Execution DAG (Mermaid) ===".blue().bold());
            println!("```mermaid\n{}```", dag.to_mermaid());
        }

        Ok(())
    }
}
