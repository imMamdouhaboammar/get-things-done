# GTD Action Bridge — Connecting Advisory Insights to Execution

> The defining principle of Getting Things Done is: **Your idea is not a task yet.** An advisory session that ends in "good advice" without an executable next action violates this principle. This reference specifies how Consult Dad seamlessly translates advisory conclusions into rigorous GTD artifacts and workflows.

---

## 1. Mapping Advisory Dialogue to GTD Knowledge Ledgers

During any consultation, decompose user input and advisor synthesis into the four canonical GTD categories:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        GTD KNOWLEDGE LEDGER                            │
├─────────────┬──────────────────────────────────────────────────────────┤
│ Fact        │ Verified data: "User has $50k savings, 2 months runway"   │
├─────────────┼──────────────────────────────────────────────────────────┤
│ Assumption  │ Explicit working hypothesis: "Customer CAC will stay <$50"│
├─────────────┼──────────────────────────────────────────────────────────┤
│ Decision    │ Selected choice: "Pursue Option A; defer Option B"        │
├─────────────┼──────────────────────────────────────────────────────────┤
│ Unknown     │ Unresolved variable: "Will supplier deliver by October?" │
└─────────────┴──────────────────────────────────────────────────────────┘
```

### Advisory Ledger Invariants:
1. **Never treat an unverified fear or assumption as a Fact.** If the user says *"I can't raise prices because customers will revolt"*, categorize that as an **Assumption**, not a Fact.
2. **Transform blocking Unknowns into Research/Validation actions.** If the core decision depends on an Unknown (e.g. competitor pricing), the immediate next action is to verify that fact.
3. **Decisions must be explicit and dated.** Record the chosen direction and the specific rationale.

---

## 2. The Advisory Definition of Ready (DoR)

An advisory outcome passes the Definition of Ready only when all of the following conditions are met:

- [ ] **Core Objective is Clear:** The real problem (not just the symptom) is identified.
- [ ] **Load-Bearing Trade-off is Named:** The primary sacrifice or constraint is acknowledged.
- [ ] **Reversibility is Classified:** Type 1 (irreversible) vs. Type 2 (reversible).
- [ ] **Concrete Recommendation Delivered:** Unhedged stance with 2–3 reasons.
- [ ] **Primary Risk & Mitigation Explicit:** What can go wrong and how to absorb it.
- [ ] **At least 1 Next Action exists:** Formatted as an immediate, physical, time-bounded verb.

---

## 3. Formulating the Next Action Sequence

Every Consult Dad session concludes with 1–3 ordered next moves. To be GTD-compliant, every action must:

1. Start with an **imperative physical verb** (e.g., *Draft, Call, Schedule, Review, Deploy, Calculate*).
2. Avoid passive or rubber verbs (e.g., *Think about, Consider, Plan to, Feel out*).
3. Have a clear completion signal (how the user knows it is done).
4. Be time-bounded (e.g., *Today, Before Friday 5 PM, Within 48 hours*).

### Example Transformation:
- ❌ *"Think more about your relationship with your co-founder."*
- ✅ *"Schedule a 45-minute private breakfast with your co-founder for Thursday morning to discuss equity realignment using the draft agenda."*

---

## 4. Generating a GTD Execution Brief

When the user asks for a structured plan or when handing off to an execution agent/workflow, emit an **Advisory Execution Brief** conforming to `references/execution-brief.schema.json`.

```json
{
  "version": "1.0",
  "title": "Startup Runway Extension & Customer Validation",
  "domain": "advisory",
  "status": "ready",
  "intent": {
    "problem": "Company has 2 months runway; user is debating quitting job vs pivoting product",
    "desired_outcome": "Validate paying customer demand before making irreversible career leap",
    "actor": "Founder"
  },
  "scope": {
    "in": ["5 paying customer interviews", "Pricing elasticity test", "Runway calculation"],
    "out": ["Full product rebuild", "Quitting day job immediately"],
    "constraints": ["Must be completed within 7 calendar days"]
  },
  "knowledge": {
    "facts": [
      "Current paying customers = 12 total, 5 organically paying for core workflow",
      "Liquid personal savings = $15,000"
    ],
    "assumptions": [
      "The 5 organic paying customers represent an identifiable repeatable niche"
    ],
    "unknowns": [
      "Will the 5 customers pay $99/mo instead of $19/mo?"
    ]
  },
  "decisions": [
    "Defer quitting employment until customer interviews validate willingness to pay",
    "Focus 100% of engineering bandwidth exclusively on the core workflow of the 5 organic users"
  ],
  "open_decisions": [],
  "workstreams": [
    {
      "name": "Customer Interviews",
      "deliverable": "Interview transcript summary & pricing validation",
      "owner": "Founder",
      "status": "ready"
    }
  ],
  "verification": {
    "success_criteria": [
      "5/5 customer calls completed by Friday",
      "Common pain trigger documented in customer's exact words"
    ],
    "evidence": []
  },
  "next_action": "Email the 5 organic paying customers today with a calendar link offering a $50 Amazon gift card for a 20-minute feedback call."
}
```
