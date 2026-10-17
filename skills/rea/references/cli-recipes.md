# REA CLI Command Recipes

Practical command-line examples for common reverse engineering scenarios using `rea` (or `bunx rea-agents`).

## 1. Electron & JavaScript Analysis

Inspect an Electron ASAR or unpacked application directory:
```bash
# Analyze full application structure, imports, and IPC boundaries
rea analyze-javascript-application /path/to/app.asar --json > app-analysis.json

# Trace specific feature seed through the application graph
rea trace-application-feature /path/to/app.asar --seed "searchNotes" --json

# Extract and recover human-readable source from bundle
rea recover-javascript-sources /path/to/bundle.js --out ./recovered-src
```

## 2. Native Binary Inspection & Decompilation

Analyze a compiled Mach-O, ELF, or Windows PE binary:
```bash
# Inspect binary headers, architectures, and layout (offline, no engine required)
rea inspect-binary-layout /path/to/binary --json

# Search procedures and strings
rea search /path/to/binary --query "validateLicense" --json

# Analyze function at specific symbol or address
rea function /path/to/binary --target "validateLicense" --json

# Trace native value flow and dependencies
rea trace /path/to/binary --address 0x100003a20 --json
```

## 3. Android APK Analysis

Inspect APK manifest, classes, and method logic:
```bash
# Decode manifest and package inventory without running APK
rea inspect-android-package /path/to/app.apk --json

# Search class inventory
rea search-android-classes /path/to/app.apk --query "AuthManager" --json

# Decompile specific method
rea inspect-android-method /path/to/app.apk --class "com.example.AuthManager" --method "login" --json
```

## 4. Web Network & Session Captures

Analyze HAR or mitmproxy files for API reverse engineering:
```bash
# Inspect API requests, headers, and payload structures
rea inspect-web-network-capture /path/to/traffic.har --json

# Trace script imports and sourcemap resolutions
rea trace-web-module-imports /path/to/index.html --json
```

## 5. System Health & Diagnostics

Check provider configuration and installed engines:
```bash
# Doctor check
rea doctor

# List available engines
rea providers

# Check MCP server stdio status
rea mcp --check
```
