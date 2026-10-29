# REA Target Routing Matrix

Map any reverse-engineering target to its canonical entrypoint, tools, and CLI fallback.

## Target Matrix

| Target Type | File Formats / Artifacts | Primary Entrypoint | MCP Tools | CLI Command Equivalent | Engine Needed |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Electron & JavaScript** | `.asar`, extracted app dirs, `.js`, bundles | `analyze_javascript_application` | `trace_application_feature`, `trace_javascript_semantics`, `inspect_electron_page` | `rea analyze-javascript-application <path> --json` | **None** (pure AST / static) |
| **Native Executable** | Mach-O (`.app`, bin), ELF, Windows PE (`.exe`, `.dll`) | `open_binary` | `binary_overview`, `search_procedures`, `search_strings`, `analyze_function`, `xrefs` | `rea open-binary <path>`, `rea inspect <path>`, `rea function <addr>` | Hopper, Ghidra, or IDA (if deep decompile); None for layout |
| **Android APK** | `.apk`, `.aab` | `inspect_android_package` | `search_android_classes`, `inspect_android_class`, `inspect_android_method`, `trace_android_references` | `rea inspect-android-package <apk>` | JADX / Java |
| **App Archives** | `.zip`, `.ipa`, `.dmg`, `.msix` | `open_binary` | `inspect_artifact`, `extract_artifact`, `project_apple_application_graph` | `rea inspect-artifact <archive>` | Native archive extractors |
| **Managed .NET** | C# / .NET PE CLI assemblies | `inspect_managed_artifact` | `inspect_managed_members`, `inspect_managed_native_boundaries`, `project_managed_application_graph` | `rea inspect-managed-artifact <dll>` | None (metadata reader) |
| **Firmware Image** | Flash dumps, bin images | `inspect_firmware_regions` | `inspect_firmware_regions`, `extract_firmware` | `rea inspect-firmware-regions <bin>` | Binwalk / Unblob |
| **Web & Network** | `.har`, mitmproxy flow logs | `inspect_web_network_capture` | `inspect_web_network_capture`, `trace_web_module_imports`, `trace_web_source_location` | `rea inspect-web-network-capture <har>` | None |
| **Offline EVM** | Smart contract bytecode | `inspect_evm_interface` | `inspect_evm_interface` | `rea inspect-evm-interface <hex>` | None |
| **Linux Core Dump** | ELF core dumps | `inspect_recorded_crash` | `inspect_recorded_crash` | `rea inspect-recorded-crash <core>` | LLDB / GDB |

## Availability & Session Rules

1. **Active-Target vs Target-Free**:
   - **Active-Target**: Native decompilation (`analyze_function`, `procedure_assembly`, `procedure_callers`, `xrefs`) requires an active session via `open_binary`.
   - **Target-Free**: `analyze_javascript_application`, `inspect_android_package`, `inspect_firmware_regions`, `inspect_evm_interface`, and `inspect_web_network_capture` take an explicit path argument and do not require `open_binary`.
2. **Provider Checks**:
   - Check available providers with `providers` (MCP) or `rea providers` (CLI).
   - If Hopper or Ghidra is missing, fall back to `inspect_binary_layout` or static inspection rather than aborting.
