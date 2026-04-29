# Plan: Phase 4 — CISA ZT UI Parity + Audit Views + Sensitive Terms UI

## Scope

### 1. CISA ZT framework UI parity
The CISA ZT JSON fixture already exists. What's missing:
- New assessment wizard already lets you pick `cisa_zt` — but the framework selector
  currently only shows DoD ZT as usable. No functional gap — `load_framework("cisa_zt")`
  works fine. Need to verify all routes handle cisa maturity states correctly.
- CISA maturity states: `traditional | initial | advanced | optimal`
  DoD maturity states: `not_met | partial | target | advanced`
  The templates use `framework.maturity_states` and `framework.maturity_labels` dynamically
  — they already work. The key gap is that the Excel service's `_compute_pillar_stats`
  uses a hardcoded `maturity_order` dict; must come from the framework JSON.
- Add CISA ZT end-to-end test covering a full assessment cycle.
- Fix any hardcoded DoD-specific state references.

### 2. Audit log view (admin)
- New route: `GET /admin/assessments/{id}/audit`
- Shows full audit_log table for the assessment, newest first
- Columns: timestamp, username, action, target_type, target_id, before, after
- Linked from admin review page

### 3. Sensitive terms UI (admin)
- New route: `GET/POST /admin/assessments/{id}/terms`
- Shows current sensitive_term table; admin can add new terms (user_added source)
  and deactivate existing ones
- Important for privacy: admin adds codenames, subsidiary names, hostnames
  before generating findings
- Linked from admin review page

### 4. Reopen-for-revision stale marking
Already implemented — customer edits mark findings stale via HTMX and the
pillar POST route. Verify with a test.

### 5. Minor: expose CISA ZT in new-assessment form label (already works)

## Files

New:
  app/templates/admin/audit.html
  app/templates/admin/terms.html
  tests/test_cisa_framework.py
  tests/test_admin_views.py

Updated:
  app/routes/admin.py        (audit route, terms routes)
  app/services/excel_service.py   (fix hardcoded maturity_order → framework JSON)
  app/templates/admin/review.html (links to audit + terms)
