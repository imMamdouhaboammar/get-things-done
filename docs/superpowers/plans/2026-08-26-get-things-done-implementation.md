# Get Things Done Skill Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a portable two-skill package that converts messy ideas into executable work models, supports domain inheritance, and verifies structured handoffs

**Architecture:** Keep reasoning instructions in concise SKILL.md files and move durable rules, domain packs, schemas, templates, examples, and deterministic helpers into supporting resources

**Tech Stack:** Agent Skills Markdown, JSON Schema 2020-12, Python 3 standard library, pytest

**Spec:** `docs/superpowers/specs/2026-08-26-get-things-done-design.md`

## Global Constraints

- Core behavior remains domain independent
- Domain packs inherit core and cannot weaken core invariants
- Completion requires evidence
- Skill descriptions describe triggering conditions, not workflow summaries
- Never pretend unavailable tool or file access

---

### Task 1: Contract and schema

**Files:**
- Create: `skills/get-things-done/references/core-contract.md`
- Create: `skills/get-things-done/references/domain-pack-spec.md`
- Create: `skills/get-things-done/references/execution-brief.schema.json`

- [ ] Write failing package tests
- [ ] Run and verify RED
- [ ] Implement contract and schema
- [ ] Run focused tests

### Task 2: Runtime skill and domain packs

**Files:**
- Create: `skills/get-things-done/SKILL.md`
- Create: `skills/get-things-done/domains/*.md`
- Create: `skills/get-things-done/templates/execution-brief.md`

- [ ] Keep runtime skill concise
- [ ] Add four domain references
- [ ] Add human-readable brief template

### Task 3: Domain builder

**Files:**
- Create: `skills/building-gtd-domain-packs/SKILL.md`
- Create: `skills/building-gtd-domain-packs/templates/domain-pack-template.md`

- [ ] Implement inheritance-first builder workflow
- [ ] Add reusable domain template

### Task 4: CLI and verification

**Files:**
- Create: `scripts/gtd.py`
- Test: `tests/test_pack.py`

- [ ] Implement doctor, list, scaffold, validate, render
- [ ] Run tests and compile checks

### Task 5: Examples, evals, packaging

**Files:**
- Create: `examples/*.json`
- Create: `evals/*`
- Create: `README.md`
- Create: `install.sh`

- [ ] Add cross-domain examples and pressure cases
- [ ] Add installation helper
- [ ] Package full bundle and individual skill ZIPs
