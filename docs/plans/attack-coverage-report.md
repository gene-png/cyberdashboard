# Plan: ATT&CK Coverage Report (v0.7.0)

- **Purpose**: Generate a 5-sheet Excel report mapping each finalized tool in an assessment to MITRE ATT&CK Enterprise techniques, classifying coverage gaps as Full / Detect Only / Prevent Only / Single Tool / None.
- **Components**: Three new DB models (`MitreTechnique`, `AttackCoverageRun`, `CoverageReport`), two services (`attack_mapper` for LLM calls + fingerprint caching, `attack_coverage_excel` for workbook generation), three admin routes (view page, generate POST, download), one Jinja template, and `scripts/seed_mitre.py` for one-time ATT&CK data loading.
- **Approach**: Per-tool API calls are expensive — cache results in `AttackCoverageRun` by `(tool_id, sha256-fingerprint-of-metadata)`. Only re-call the LLM when tool metadata or confirmed activity mappings change. Only tools with `mapping_status=active` are included; `pending_review` tools are listed as excluded in the Methodology sheet.
- **Testing**: Pure-unit tests for `classify_gap_status`, fingerprint determinism, JSON parsing/validation, cache behaviour, and the Excel builder (sheet count, content assertions). Route tests use mocks for the LLM call and `current_app.config`.
