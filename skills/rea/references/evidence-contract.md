# REA Evidence Contract & Reconstruction Guidelines

REA enforces an **evidence-first invariant**: reverse engineering output must distinguish hard proof from inference, and reconstructions must be verified against real artifact facts.

## The Evidence Object

REA results include an `evidence` block containing:
- `digest`: SHA-256 hash of the analyzed artifact.
- `locations`: Precise byte offsets, virtual addresses (`0x...`), or AST line ranges.
- `symbols`: Demangled function, method, or selector identifiers.
- `limitations`: Engine-specific boundaries (e.g., whether dynamic dispatch could be fully resolved).
- `unknowns`: Explicit gaps that could not be determined without runtime execution.

## Clean-Room Reconstruction Rules

When recreating a feature observed in a reverse-engineered app:
1. **Never copy decompiled garbage code directly**: Decompiled pseudocode contains artificial variable names (`v12`, `a3`), compiler artifacts, and de-inlined helper loops. Clean it up into idiomatic TypeScript/Rust/Go.
2. **Anchor with Evidence Citations**:
   ```typescript
   // Reconstructed from [Notes.app v1.2]
   // Address: 0x100018f40 (SearchIndex::calculateRelevanceScore)
   // Evidence digest: sha256:4b28f...
   export function calculateRelevanceScore(query: string, document: string): number {
     // Clean, modern implementation preserving exact algorithmic semantics
   }
   ```
3. **Document Unknowns**: If an algorithm relies on a proprietary server endpoint or encrypted key, mark it clearly in an `Unknowns` table rather than inventing fake mock data.
