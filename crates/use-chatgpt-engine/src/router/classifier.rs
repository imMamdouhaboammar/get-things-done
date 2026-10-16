use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum IntentDomain {
    FeatureImplementation,
    PullRequestRepair,
    BugDebugging,
    CiBuildFix,
    SecurityAudit,
    UiUxHardening,
    SessionContinuation,
    BacklogAudit,
    SkillDevelopment,
    General,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClassifiedIntent {
    pub raw_prompt: String,
    pub domain: IntentDomain,
    pub requires_connected_source: bool,
    pub requires_local_execution: bool,
    pub requires_pr_context: bool,
    pub involves_security_boundary: bool,
    pub involves_ui_ux: bool,
    pub target_language: Option<String>,
}

pub struct IntentClassifier;

impl IntentClassifier {
    pub fn classify(prompt: &str) -> ClassifiedIntent {
        let p_lower = prompt.to_lowercase();

        let mut domain = IntentDomain::General;
        let mut requires_connected_source = false;
        let mut requires_local_execution = false;
        let mut requires_pr_context = false;
        let mut involves_security_boundary = false;
        let mut involves_ui_ux = false;

        // Detect PR context
        if p_lower.contains("pr") || p_lower.contains("pull request") || p_lower.contains("coderabbit") || p_lower.contains("bugbot") || p_lower.contains("sourcery") {
            requires_pr_context = true;
            requires_connected_source = true;
            domain = IntentDomain::PullRequestRepair;
        }

        // Detect CI / Build failure
        if p_lower.contains("ci") || p_lower.contains("build failure") || p_lower.contains("workflow fail") || p_lower.contains("github actions") {
            domain = IntentDomain::CiBuildFix;
            requires_connected_source = true;
            requires_local_execution = true;
        }

        // Detect Security
        if p_lower.contains("security") || p_lower.contains("auth") || p_lower.contains("token") || p_lower.contains("secret") || p_lower.contains("rls") {
            involves_security_boundary = true;
            if domain == IntentDomain::General {
                domain = IntentDomain::SecurityAudit;
            }
        }

        // Detect UI/UX
        if p_lower.contains("ui") || p_lower.contains("ux") || p_lower.contains("frontend") || p_lower.contains("responsive") || p_lower.contains("css") || p_lower.contains("design") {
            involves_ui_ux = true;
            if domain == IntentDomain::General {
                domain = IntentDomain::UiUxHardening;
            }
        }

        // Detect Bug debugging (ensure bugbot in PR does not trigger bug debugging)
        if !requires_pr_context && (p_lower.contains("debug") || (p_lower.contains("bug") && !p_lower.contains("bugbot")) || p_lower.contains("fix error") || p_lower.contains("crash") || p_lower.contains("reproduce")) {
            domain = IntentDomain::BugDebugging;
            requires_local_execution = true;
        }

        // Detect Session Continuation
        if p_lower.contains("continue") || p_lower.contains("resume") || p_lower.contains("handoff") || p_lower.contains("reconcile") {
            domain = IntentDomain::SessionContinuation;
            requires_connected_source = true;
            requires_local_execution = true;
        }

        // Detect Feature Implementation
        if !requires_pr_context && (p_lower.contains("build") || p_lower.contains("implement") || p_lower.contains("feature") || p_lower.contains("create endpoint")) {
            domain = IntentDomain::FeatureImplementation;
            requires_local_execution = true;
        }

        // Detect Skill Development
        if p_lower.contains("skill") || p_lower.contains("plugin") || p_lower.contains("agentic") {
            domain = IntentDomain::SkillDevelopment;
        }

        // Detect language
        let mut target_language = None;
        if p_lower.contains("rust") || p_lower.contains("cargo") {
            target_language = Some("rust".to_string());
            requires_local_execution = true;
        } else if p_lower.contains("typescript") || p_lower.contains("javascript") || p_lower.contains("bun") || p_lower.contains("node") {
            target_language = Some("typescript".to_string());
            requires_local_execution = true;
        } else if p_lower.contains("python") {
            target_language = Some("python".to_string());
            requires_local_execution = true;
        }

        ClassifiedIntent {
            raw_prompt: prompt.to_string(),
            domain,
            requires_connected_source,
            requires_local_execution,
            requires_pr_context,
            involves_security_boundary,
            involves_ui_ux,
            target_language,
        }
    }
}
