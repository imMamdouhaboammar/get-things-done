# Example: Crisis Scope Cut — Emergency Project Deadline Triage

## The Situation

**User says:**
"We are 10 days away from a critical product launch for our enterprise anchor client. Our engineering lead just informed me that our scheduled feature list is only 60% complete, and if we try to ship everything, QA will fail and the entire deployment will crash. If we slip the date, we face a $50k SLA penalty. I am completely overwhelmed and panicking."

---

## Step 1: Pre-Flight & Advisory Mode

Context readiness score is 8/8. Mode 4 (Acknowledge and Redirect) + Mode 3 (Honest Pushback on shipping broken software).

---

## Step 2: Honest Assessment (Direct + Warm)

**What I see:**
Take a deep breath. Panicking burns cognitive energy you need for triage. The $50k SLA penalty is bad, but deploying broken software that corrupts your client's production data is catastrophic and can cost you the entire contract and your reputation. You are not going to ship 100% of the scope in 10 days, and pretending you can is the single biggest threat to this company.

**The real question:**
Not *"how do we miraculously finish 4 weeks of work in 10 days?"* — but *"what is the irreducible 40% of this system that delivers the core value the client actually needs on Day 1?"*

**GTD Knowledge Ledger:**
- **Fact:** 10 days until contractual delivery; 60% of codebase complete.
- **Fact:** Full scope cannot be stabilized by the deadline without severe bugs.
- **Fact:** Client signed up primarily for automated reporting, not the secondary dashboard widgets.
- **Assumption:** Client will accept a phased delivery if the core reporting engine works flawlessly.
- **Decision:** Ruthlessly cut 50% of the scope; freeze new feature code immediately.

**The framework (Constraint Reframe & Pre-Mortem):**
- *The Pre-Mortem:* If you try to ship everything, the system goes down during client onboarding, data is lost, and the client terminates for cause.
- *The Solution:* Freeze all secondary features today. Dedicate 100% of the remaining 10 days exclusively to hardening and QA-testing the core reporting pipeline.

**My take:**
Cut scope immediately. Call the client executive tomorrow. Do not apologize meekly; present it as a professional engineering decision:
*"We are deploying Phase 1 on schedule with the core reporting engine you need for billing. To guarantee 99.99% data integrity, we are rolling out the secondary visualization widgets in Phase 2 two weeks later at no extra charge."*

**The primary risk & mitigation:**
The risk is client pushback. Mitigate this by demonstrating that their primary business workflow is 100% functional and tested before they ask.

**GTD Action Bridge (Next Moves):**
1. **[Today 2 PM]:** Convene an emergency 30-minute scope triage: tag every non-core ticket as `Phase 2 - Post-Launch` and lock the branch.
2. **[Tomorrow 9 AM]:** Conduct end-to-end integration testing on the core reporting engine.
3. **[Tomorrow 2 PM]:** Call the client stakeholder with the proactive phased rollout plan.

---

## Step 3: Closing Ownership Transfer

"Calm execution wins crises. Are you ready to lock that scope cut right now?"
