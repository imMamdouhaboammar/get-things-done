# Architecture Decision: Fable Architecture Microservices Integration of Use-ChatGPT

## Context
The user requested merging and integrating the `use-chatgpt` skill into `imMamdouhaboammar/get-things-done` as an ultra-connected module wired to its functions and tools, adhering to `/fable-architecture`.

## Evaluation
- Vector 1: Scale & Load: 7.5
- Vector 2: Domain Decoupling: 8.5
- Vector 3: Resource Intensity: 7.0
- Composite Score: 7.78 $\ge 6.0 \rightarrow$ Enforce Microservices / Decoupled Polyglot Architecture.

## Architecture
1. **gtd-orchestrator (Category B/D, Python)**: Owns Execution Briefs, Life Cycle States, Knowledge Ledger, and Domain Packs.
2. **use-chatgpt-engine (Category C, Pure Rust)**: Owns Intent Classifier, Routing DAG, Bot Gate Fencer, Evidence Trust Ladder, and macOS system CLI integration.
3. **East-West Protocol**: Strict IDL defined in `proto/gtd_chatgpt_bridge.proto`, implemented with type safety in `skills/get-things-done/scripts/chatgpt_bridge.py`.
4. **North-South Standard**: Universal Agent Skills metadata and CLI stdio JSON interface.
