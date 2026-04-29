# Plan: Phase 1 Skeleton

## Goal
Ship a working Flask app that covers the entire assessment lifecycle end-to-end without AI or SharePoint. Usable for real assessments.

## Scope
- Flask app factory + blueprints
- SQLAlchemy models (all 9 tables)
- Framework JSON for DoD ZT only
- Auth: Flask-Login customer login + admin password gate
- Dashboard: list assessments
- Assessment workspace: tool inventory, current state, target state, submit
- Admin review: view responses, admin scoring
- Excel export (customer + consultant) — no AI guidance yet, no SharePoint
- pytest suite covering models + routes

## Out of scope (Phase 2+)
- Anthropic API / scrub pipeline
- HTMX auto-save (manual form submit for now)
- SharePoint upload
- CISA ZT framework
- Rate limiting
- spaCy NER

## Structure
```
app/
  __init__.py         # app factory
  config.py
  extensions.py       # db, login_manager, etc.
  models/
  services/
    framework_loader.py
    excel_service.py
  routes/
    auth.py
    dashboard.py
    assessment.py
    admin.py
  templates/
  static/
data/frameworks/
  dod_zt.json
tests/
  conftest.py
  test_models.py
  test_auth.py
  test_assessment.py
  test_excel_service.py
scripts/
  smoke_test.sh
```

## Steps
1. requirements.txt + install
2. Framework JSON (DoD ZT)
3. Models
4. App factory + config
5. Auth routes + templates
6. Dashboard routes + templates
7. Assessment workspace routes + templates
8. Admin routes + templates
9. Excel service
10. Tests
11. Smoke test script
