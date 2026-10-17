# Example: Electron ASAR Feature Extraction & Clean-Room Reconstruction

This example demonstrates how `/rea` investigates an obfuscated Electron ASAR package, extracts the internal token verification logic, and produces a clean-room implementation with verifiable evidence.

## 1. Intent & Scope

* **User Intent**: "Deconstruct how token refresh is handled inside the desktop app bundle, show the evidence, and implement an equivalent clean-room module."
* **Target Artifact**: `release-darwin-x64/app.asar` (SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`)

## 2. Analysis Pathway & Discovery

Using target-free AST inspection:
```bash
rea analyze-javascript-application ./release-darwin-x64/app.asar --json
```

Identified module boundaries:
* `lib/auth/token-refresh.js`
* Key symbol: `verifyAndRefreshToken(sessionToken, refreshEndpoint)`

## 3. Evidence Ledger

```json
{
  "target": "release-darwin-x64/app.asar",
  "digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "locations": [
    "lib/auth/token-refresh.js:L42-L88"
  ],
  "symbols": [
    "verifyAndRefreshToken",
    "calculateBackoffDelay"
  ],
  "limitations": "Static AST analysis; server private key omitted from bundle as expected.",
  "unknowns": [
    "Remote token revocation endpoint rate-limit policy"
  ]
}
```

## 4. Clean-Room Implementation

```typescript
/**
 * Feature Reconstruction: Token Refresh Flow
 * Reverse-Engineered from: Desktop Client (release-darwin-x64/app.asar)
 * Evidence Digest: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
 * Location: lib/auth/token-refresh.js:L42-L88
 */

export interface RefreshResult {
  accessToken: string;
  expiresInSeconds: number;
}

export async function refreshSessionToken(
  refreshToken: string,
  endpoint: string
): Promise<RefreshResult> {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Client-Intent': 'refresh-token',
    },
    body: JSON.stringify({ token: refreshToken }),
  });

  if (!response.ok) {
    throw new Error(`Token refresh failed with HTTP status ${response.status}`);
  }

  const payload = await response.json();
  return {
    accessToken: payload.access_token,
    expiresInSeconds: payload.expires_in,
  };
}
```
