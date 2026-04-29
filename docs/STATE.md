# Project State

**Last updated:** 2026-04-29
**Branch:** main (Phase 5 merged at v0.5.0)

## Done

### Phase 1 (v0.1.0)
- Flask app, all 9 SQLAlchemy models, auth, assessment workspace, admin review, Excel export

### Phase 2 (v0.2.0)
- Privacy scrub pipeline + Anthropic API integration + gap finding generation

### Phase 3 (v0.3.0)
- HTMX auto-save, rate limiting, SharePoint integration, DB backup script

### Phase 4 (v0.4.0)
- CISA ZT framework end-to-end, audit log view, sensitive terms management UI

### Phase 5 (v0.5.0)
- spaCy NER Layer 2b: ORG/PERSON/GPE not in token map get auto-assigned tokens (graceful-degrade)
- Customer final report download: `/assessments/{id}/report` after finalization
- Session cookie hardening: Secure + HttpOnly + SameSite=Lax
- HTTPS force-redirect via X-Forwarded-Proto (FORCE_HTTPS env var)
- Structured logging in app factory
- scripts/create_admin.py: bcrypt hash generator for ADMIN_PASSWORD_HASH
- .env.example: full env var documentation
- .github/workflows/ci.yml + deploy.yml: CI + Azure App Service CD
- 147 tests passing

## In Progress
- Nothing

## Blocked
- Nothing

## Next Up (potential future work)
- spaCy NER: consider CIDR notation scrub (10.0.0.0/8 not caught by current IPv4 regex)
- Customer SSO via Azure AD (spec §13, deferred — username/password sufficient for now)
- Per-assessment customer user deduplication (spec §13)
- Engagement Hours sheet in consultant Excel (spec §7.2, optional)
- Scale to Postgres if assessment volume grows past single-user SQLite limits

## Known Issues / Tech Debt
- Admin route `_require_admin()` returns redirect — should be a decorator
- smoke_test.sh uses inline Python thread instead of `flask run` (bash backgrounding issue in container)
- spaCy `en_core_web_sm` is 12MB and must be downloaded separately in CI (handled via direct wheel URL in requirements.txt)
