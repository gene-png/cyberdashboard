# Plan: Phase 5 — Hardening

## Scope

### 1. spaCy NER scrub (Layer 2b — spec §6.2)
The spec requires a third sub-layer in the outbound scrub: any ORG/PERSON/GPE
entities spaCy finds that are NOT already in the token map get a fresh token and
are added to the assessment's sensitive_term table. This runs between Layer 1
(token map) and Layer 2 (regex).

Graceful-degrade: if spaCy or `en_core_web_sm` is unavailable, log a warning
and skip NER — the other layers still run. This avoids hard failures on deploy.

### 2. Session cookie hardening (spec §11)
Add to Config: `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`,
`SESSION_COOKIE_SAMESITE="Lax"`. Enabled only in production (not TestingConfig).

### 3. HTTPS force-redirect (spec §11)
`before_request` hook in the app factory: if `X-Forwarded-Proto: http` and
not testing/debug, redirect to `https://`. Azure App Service terminates TLS
and sets this header.

### 4. Customer final report download (spec §5.6)
After finalization, customer can download their Excel. Add:
- Route: `GET /assessments/{id}/report` → `send_file` customer Excel
- Workspace sidebar: "Final Report" link when `assessment.status == 'finalized'`

### 5. GitHub Actions CI/CD
- `.github/workflows/ci.yml` — runs pytest on every push and PR
- `.github/workflows/deploy.yml` — deploys to Azure App Service on semver tag push

### 6. Utility scripts
- `scripts/create_admin.py` — prints bcrypt hash for a given password (for setting ADMIN_PASSWORD_HASH env var)
- `.env.example` — documents all required env vars with placeholder values

### 7. Structured logging
Configure Python's logging module in the app factory with a structured format
(timestamp, level, logger, message). Replaces ad-hoc print statements.

## Files

New:
  .github/workflows/ci.yml
  .github/workflows/deploy.yml
  .env.example
  scripts/create_admin.py
  tests/test_phase5.py

Updated:
  app/__init__.py          (HTTPS redirect hook, logging setup)
  app/config.py            (session cookie settings)
  app/services/scrub_service.py  (NER layer)
  app/routes/assessment.py (final report route)
  app/templates/assessment/workspace.html  (Final Report link)
  requirements.txt         (add spacy)
