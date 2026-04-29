# Changelog

All notable changes to the ZT Assessment Dashboard are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.3.0] — 2026-04-29

### Added
- HTMX auto-save: per-activity `change` trigger POSTs to `/htmx/assessments/{id}/response/{activity_id}`; returns inline "Saved" indicator with CSS fade-out; no page reload required
- `<noscript>` fallback form on pillar page for no-JS environments
- Rate limiting via Flask-Limiter: 5 POST attempts / 15 min on `/login`; 10 / min on finding regenerate endpoint
- SharePoint service (`sharepoint_service.py`): Graph API client-credentials auth, folder creation, file upload, `upload_assessment_outputs`, `backup_database`
- Finalize route now builds both Excel files and uploads to SharePoint (no-op with warning if credentials not configured)
- Response snapshot JSON and audit CSVs uploaded alongside Excel on finalization
- `scripts/backup_db.py`: nightly DB backup to SharePoint `/Backups/{date}/`, prunes backups older than 30 days
- Admin session countdown timer in navbar (warns at 3 min remaining, shows "expired" at 0)
- `RATELIMIT_ENABLED = False` in TestingConfig to prevent rate-limiter interference with tests
- 25 new tests (test_htmx, test_sharepoint_service) — 102 total passing

## [0.2.0] — 2026-04-29

### Added
- Privacy scrub pipeline (scrub_service.py): Layer 1 token map (org name + variants, usernames, user-defined terms), Layer 2 regex (IPv4, IPv6, MAC, FQDN, email), Layer 3 rehydration with unknown-token warning
- `seed_token_map()`: idempotent seeding of sensitive_term table on assessment creation/generation
- Prompt injection defense in `ai_service.py`: strips instruction-override patterns from evidence notes and tool notes before they enter the AI prompt
- `build_prompt()`: full spec §6.1 prompt structure (framework, pillar, activity, intent, current/target state, evidence, tools, 4-part task)
- `call_anthropic()`: Anthropic API client with model, token counts, and duration logging
- `generate_findings()`: orchestrates all gaps → scrub → AI → store serially; marks no-gap findings stale; logs to ai_call_log and audit_log
- `regenerate_finding()`: per-finding regeneration, updates existing row in place
- Severity formula: gap_size × pillar_weight × 100 → critical/high/medium/low
- Placeholder AI response when ANTHROPIC_API_KEY is not set (enables testing without credentials)
- Admin "AI Findings" page with finding cards, stale indicators, per-finding Regenerate button
- "Generate AI Findings" button in admin review and findings views
- 50 new tests (test_scrub_service, test_ai_service, test_report_generator) — 77 total passing

## [0.1.0] — 2026-04-29

### Added
- Phase 1 skeleton: full Flask application with SQLAlchemy ORM
- Nine database models: Assessment, User, ToolInventory, Response, AdminScore, GapFinding, SensitiveTerm, AuditLog, AICallLog
- Framework JSON fixtures for DoD Zero Trust Reference Architecture (7 pillars, 33 activities) and CISA ZT Maturity Model 2.0 (5 pillars, 17 activities)
- Auth: Flask-Login customer login, logout, admin password gate with 15-minute session timeout
- Dashboard: assessment list view for admin, auto-redirect to workspace for customer users
- New assessment wizard (admin-only): creates assessment + customer credentials
- Assessment workspace: overview with per-pillar progress summary
- Tool inventory: add/delete tools, auto-flip status to in_progress on first edit
- Pillar response forms: current state, target state, evidence notes; saves to DB with audit log entries; marks gap findings stale on edit
- Submit flow: submit assessment → awaiting_review status, locks customer edits
- Admin review: per-pillar admin scoring, gap summary, consultant recommendations
- Admin finalize / reopen flows with audit log entries
- Excel export: customer report (Executive Summary, Gap Register, per-pillar sheets, Tool Inventory, Methodology) and consultant report (all customer sheets + Admin Notes, AI Call Log, Audit Log)
- Privacy scrub service foundation (token-map structure in DB)
- pytest suite: 27 tests covering models, auth, assessment routes, Excel generation
- Smoke test script (scripts/smoke_test.sh): boots server, checks all key routes
- CSRF protection (Flask-WTF) on all forms
- Input sanitization with bleach on all customer free-text fields
