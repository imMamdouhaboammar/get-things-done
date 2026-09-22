# Security Boundaries

Capability routing changes who may read, write, verify, review, and land work. Treat those authority assignments as security-relevant configuration.

## Fail-closed rules

- A registry entry never proves current authorization, connectivity, billing state, or write permission.
- Unknown capabilities receive no inferred write authority.
- A blocked or unavailable owner cannot be simulated.
- Only one selected write owner may mutate a declared surface at a time.
- Reviewers are read-only by default and cannot manufacture executable evidence.
- Landing authority is separate from review authority.
- Silent admin, force, or policy bypass is forbidden unless the user explicitly requested it and the governing repository or platform permits it.
- Secrets, credentials, tokens, private keys, and session identifiers do not belong in router metadata, eval cases, role files, or source-lineage records.
- Connected-source results must be treated according to their actual permission boundary, not their product name.

## Security review triggers

Add a dedicated security reviewer or security-focused verification when the change touches authentication, authorization, secrets, billing, webhooks, deployment permissions, agent tool policy, destructive operations, or a widened write surface.

Security review remains a specialist lens. It does not replace runtime tests, repository-native gates, or exact-state landing checks.
