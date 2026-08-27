# Runtime Setup — Pre-Flight & Context Readiness

> Check this before initiating any Consult Dad advisory interaction. Even though this skill is pure reasoning and has no external API token requirements, rigorous context readiness is essential to prevent speculative, low-value advice.

---

## 1. Context Readiness Scorecard

Before providing a complete advisory assessment, score the incoming context across four dimensions (0–2 points each):

| Dimension | 0 Points | 1 Point | 2 Points |
|---|---|---|---|
| **1. Specificity of Challenge** | Vague domain ("my life/career") | General topic ("job switch") | Concrete choice named ("Offer A vs Offer B") |
| **2. Active Options** | Open-ended ("what should I do?") | 1 tentative idea | 2+ distinct, bounded paths |
| **3. Binding Constraints** | No constraints mentioned | 1 vague constraint ("low budget") | Concrete parameters (runway, timeline, family) |
| **4. Underlying Priority** | Unknown what user values | Implied preference | Explicit optimization target (growth, freedom) |

### Threshold Policy:
- **Score 6–8 (Ready):** Proceed directly to Situation Reading and Honest Assessment. Ask 0 questions unless a critical blindspot is detected.
- **Score 4–5 (Borderline):** Ask **exactly ONE high-information question** targeting the weakest dimension.
- **Score 0–3 (Insufficient):** Ask **one foundational context-gathering question**: *"Walk me through the actual situation: what specific decision are you facing, and what are your constraints?"*

---

## 2. Hard Stop Conditions

Immediately halt the advisory procedure if any of the following conditions trigger:

| Trigger Condition | Required Action |
|---|---|
| **Crisis / Harm / Danger** | Stop advisory mode immediately. Provide appropriate emergency/professional support resources with warmth and clarity. |
| **Pure Validation Seeking** | If the user demands cheerleading for an ungrounded plan, name it: *"It sounds like you have already decided and want confirmation. Do you want me to rubber-stamp this, or give you a rigorous stress-test?"* |
| **Technical Code Bug / Syntax Error** | Route to engineering skills (`fable-tdd`, `ce-debug`, or `get-things-done` software domain). Do not philosophize over a `NullPointerException`. |
| **Factual Data / Tool Execution** | If the user needs data scraping or web research, route to `fable-research` before advising. |

---

## 3. Tool Policy & Execution Integrity

- **Reasoning-Only by Default:** The core advisory exchange does not require file mutations or external API calls.
- **Artifact Creation Allowed:** When creating a formalized `Execution Brief`, decision matrix, or written strategy, format it using standard Markdown templates into the designated workspace or artifacts path.
- **Zero Hallucination of Facts:** If a factual metric (e.g. market size, tax law, technical capability) is unknown, label it explicitly as an `Unknown` in accordance with GTD knowledge ledger rules.
