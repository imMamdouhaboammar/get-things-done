use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum LifecycleStage {
    Classify = 0,
    Restore = 1,
    Investigate = 2,
    Plan = 3,
    Execute = 4,
    Verify = 5,
    Review = 6,
    Release = 7,
    Handoff = 8,
}

impl std::fmt::Display for LifecycleStage {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Classify => write!(f, "STAGE 0: CLASSIFY"),
            Self::Restore => write!(f, "STAGE 1: RESTORE"),
            Self::Investigate => write!(f, "STAGE 2: INVESTIGATE"),
            Self::Plan => write!(f, "STAGE 3: PLAN"),
            Self::Execute => write!(f, "STAGE 4: EXECUTE"),
            Self::Verify => write!(f, "STAGE 5: VERIFY"),
            Self::Review => write!(f, "STAGE 6: REVIEW"),
            Self::Release => write!(f, "STAGE 7: RELEASE"),
            Self::Handoff => write!(f, "STAGE 8: HANDOFF"),
        }
    }
}

impl LifecycleStage {
    pub fn from_str_loose(s: &str) -> Option<Self> {
        let upper = s.trim().to_uppercase();
        if upper.contains("CLASSIFY") {
            Some(Self::Classify)
        } else if upper.contains("RESTORE") {
            Some(Self::Restore)
        } else if upper.contains("INVESTIGATE") {
            Some(Self::Investigate)
        } else if upper.contains("PLAN") {
            Some(Self::Plan)
        } else if upper.contains("EXECUTE") {
            Some(Self::Execute)
        } else if upper.contains("VERIFY") {
            Some(Self::Verify)
        } else if upper.contains("REVIEW") {
            Some(Self::Review)
        } else if upper.contains("RELEASE") || upper.contains("CLOSE") || upper.contains("LAND") {
            Some(Self::Release)
        } else if upper.contains("HANDOFF") {
            Some(Self::Handoff)
        } else {
            None
        }
    }

    pub fn next(&self) -> Option<Self> {
        match self {
            Self::Classify => Some(Self::Restore),
            Self::Restore => Some(Self::Investigate),
            Self::Investigate => Some(Self::Plan),
            Self::Plan => Some(Self::Execute),
            Self::Execute => Some(Self::Verify),
            Self::Verify => Some(Self::Review),
            Self::Review => Some(Self::Release),
            Self::Release => Some(Self::Handoff),
            Self::Handoff => None,
        }
    }
}
