use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Role {
    Source,
    Contract,
    Planner,
    Executor,
    Verifier,
    Reviewer,
    Security,
    RuntimeQa,
    Readiness,
    Landing,
    Handoff,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum AvailabilityState {
    Callable,
    Connected,
    InstalledButNotCallableHere,
    KnownNameUnresolved,
    Unavailable,
    Blocked,
}

impl std::fmt::Display for AvailabilityState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Callable => write!(f, "CALLABLE"),
            Self::Connected => write!(f, "CONNECTED"),
            Self::InstalledButNotCallableHere => write!(f, "INSTALLED_BUT_NOT_CALLABLE_HERE"),
            Self::KnownNameUnresolved => write!(f, "KNOWN_NAME_UNRESOLVED"),
            Self::Unavailable => write!(f, "UNAVAILABLE"),
            Self::Blocked => write!(f, "BLOCKED"),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BlockReason {
    ReviewRateLimited,
    BillingBlocked,
    AuthMissing,
    DeviceOffline,
    PermissionDenied,
    None,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Capability {
    pub name: String,
    pub role: Role,
    pub write_authority: bool,
    pub availability: AvailabilityState,
    pub block_reason: BlockReason,
    pub description: String,
}

impl Capability {
    pub fn new(name: &str, role: Role, write_authority: bool, description: &str) -> Self {
        Self {
            name: name.to_string(),
            role,
            write_authority,
            availability: AvailabilityState::Callable,
            block_reason: BlockReason::None,
            description: description.to_string(),
        }
    }
}
