# Changelog

All notable changes to the ZT Assessment Dashboard are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

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
