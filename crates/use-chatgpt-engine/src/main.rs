use clap::{Parser, Subcommand};
use std::path::PathBuf;
use use_chatgpt_engine::cli::*;

#[derive(Parser)]
#[command(name = "chatgpt-skill")]
#[command(author = "Mamdouh Aboammar <imMamdouhaboammar@gmail.com>")]
#[command(version = "1.0.0")]
#[command(about = "Pure Rust agentic routing, state machine, and macOS CLI execution engine", long_about = None)]
struct Cli {
    #[arg(short, long, default_value = ".chatgpt-state.json", global = true)]
    state_file: PathBuf,

    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Classify intent and generate universal routing packet & execution DAG
    Route {
        /// The natural language prompt or task to route
        prompt: String,
        /// Output format (yaml or json)
        #[arg(short, long, default_value = "yaml")]
        format: String,
        /// Display Mermaid execution DAG diagram
        #[arg(long, default_value_t = true)]
        dag: bool,
    },

    /// Manage 8-stage workflow state machine
    State {
        #[command(subcommand)]
        sub: StateSubcommands,
    },

    /// Manage and inspect Evidence Ledger
    Evidence {
        #[command(subcommand)]
        sub: EvidenceSubcommands,
    },

    /// Inspect and classify Open-PR Bot feedback
    BotGate {
        #[command(subcommand)]
        sub: BotGateSubcommands,
    },

    /// Native macOS CLI operations (clipboard, notification, dialog, keychain)
    Macos {
        #[command(subcommand)]
        sub: MacosSubcommands,
    },

    /// Probe connectivity to external CLIs and bridges (git, gh, bun, cargo)
    Connect,

    /// Export multi-agent distribution manifests (.agents, .claude, .codex)
    Export {
        #[arg(short, long, default_value = ".")]
        target_dir: PathBuf,
    },

    /// System and skill package health check
    Doctor {
        #[arg(short, long, default_value = "skills/use-chatgpt")]
        skill_dir: PathBuf,
    },
}

#[derive(Subcommand)]
enum StateSubcommands {
    /// Display current lifecycle stage and transition history
    Show,
    /// Transition to a new lifecycle stage
    Transition {
        /// Target lifecycle stage name (e.g. EXECUTE, VERIFY, RELEASE)
        stage: String,
        /// Proof or rationale for this transition
        #[arg(short, long, default_value = "Verified criteria")]
        proof: String,
    },
}

#[derive(Subcommand)]
enum EvidenceSubcommands {
    /// Initialize a new evidence ledger
    Init {
        mission: String,
    },
    /// Record an entry in the ledger
    Record {
        #[arg(long)]
        source: Option<String>,
        #[arg(long)]
        change: Option<String>,
        #[arg(long)]
        test: Option<String>,
        #[arg(long)]
        runtime: Option<String>,
        #[arg(long)]
        review: Option<String>,
        #[arg(long)]
        bot: Option<String>,
        #[arg(long)]
        level: Option<String>,
        #[arg(long)]
        verdict: Option<String>,
    },
    /// Render markdown evidence ledger
    Show,
}

#[derive(Subcommand)]
enum BotGateSubcommands {
    /// Inspect open PR bot comments and classify dispositions
    Inspect {
        #[arg(short, long)]
        pr: Option<u32>,
    },
}

#[derive(Subcommand)]
enum MacosSubcommands {
    /// Copy text to macOS clipboard (pbcopy)
    Copy {
        text: String,
    },
    /// Paste text from macOS clipboard (pbpaste)
    Paste,
    /// Send macOS Notification Center alert (osascript)
    Notify {
        #[arg(short, long)]
        title: String,
        #[arg(short, long, default_value = "ChatGPT Skill Alert")]
        subtitle: String,
        #[arg(short, long)]
        message: String,
    },
    /// Show macOS modal confirmation dialog (AppleScript)
    Dialog {
        #[arg(short, long)]
        title: String,
        #[arg(short, long)]
        prompt: String,
    },
    /// Open target URL or file with macOS default app
    Open {
        target: String,
    },
    /// Retrieve password/secret from macOS Keychain
    Keychain {
        #[arg(short, long)]
        service: String,
        #[arg(short, long)]
        account: String,
    },
}

fn main() -> anyhow::Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Route { prompt, format, dag } => {
            RouteCmd::execute(&prompt, &format, dag)?;
        }
        Commands::State { sub } => match sub {
            StateSubcommands::Show => {
                StateCmd::show(&cli.state_file)?;
            }
            StateSubcommands::Transition { stage, proof } => {
                StateCmd::transition(&cli.state_file, &stage, &proof)?;
            }
        },
        Commands::Evidence { sub } => match sub {
            EvidenceSubcommands::Init { mission } => {
                EvidenceCmd::init(&cli.state_file, &mission)?;
            }
            EvidenceSubcommands::Record {
                source,
                change,
                test,
                runtime,
                review,
                bot,
                level,
                verdict,
            } => {
                EvidenceCmd::record(
                    &cli.state_file,
                    source,
                    change,
                    test,
                    runtime,
                    review,
                    bot,
                    level,
                    verdict,
                )?;
            }
            EvidenceSubcommands::Show => {
                EvidenceCmd::show(&cli.state_file)?;
            }
        },
        Commands::BotGate { sub } => match sub {
            BotGateSubcommands::Inspect { pr } => {
                BotGateCmd::inspect_pr(pr)?;
            }
        },
        Commands::Macos { sub } => match sub {
            MacosSubcommands::Copy { text } => {
                MacOSCmd::copy(&text)?;
            }
            MacosSubcommands::Paste => {
                MacOSCmd::paste()?;
            }
            MacosSubcommands::Notify {
                title,
                subtitle,
                message,
            } => {
                MacOSCmd::notify(&title, &subtitle, &message)?;
            }
            MacosSubcommands::Dialog { title, prompt } => {
                MacOSCmd::dialog(&title, &prompt)?;
            }
            MacosSubcommands::Open { target } => {
                MacOSCmd::open_target(&target)?;
            }
            MacosSubcommands::Keychain { service, account } => {
                MacOSCmd::keychain_get(&service, &account)?;
            }
        },
        Commands::Connect => {
            ConnectCmd::test_connections()?;
        }
        Commands::Export { target_dir } => {
            ExportCmd::export_manifests(&target_dir)?;
        }
        Commands::Doctor { skill_dir } => {
            DoctorCmd::run(&skill_dir)?;
        }
    }

    Ok(())
}
