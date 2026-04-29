# Plan: Phase 2 — AI Guidance + Scrub Pipeline

## Goal
Add Anthropic-powered gap remediation guidance with a privacy scrub pipeline that ensures no PII/sensitive terms leave the server in plain form.

## Scope
- scrub_service.py: Layer 1 (token map), Layer 2 (regex: IP/MAC/FQDN/email), Layer 3 (rehydrate)
- ai_service.py: prompt builder per spec §6.1, Anthropic API call, system prompt
- report_generator.py: orchestrate all gap findings → scrub → AI → store (serial with delay)
- Severity calculation: gap_size × pillar_weight → low/medium/high/critical
- Admin UI: "Generate AI Findings" button, per-finding "Regenerate" button, stale indicators
- New admin findings view showing all findings with status
- Excel: AI guidance already wired; ensure rehydrated_response flows in
- Tests: test_scrub_service.py (comprehensive), test_ai_service.py (mocked), test_report_generator.py (mocked)

## Out of scope (deferred)
- spaCy NER pass (Layer 2b) — deferred until Phase 5 hardening
- HTMX progress bar (Phase 3)
- SharePoint upload (Phase 3)

## Severity formula
```
gap_size = maturity_order[target] - maturity_order[current]
weight = pillar weight (0.15–0.20 from framework JSON)
score = gap_size × weight × 100

score ≥ 40 → critical
score ≥ 25 → high
score ≥ 10 → medium
else        → low
```

## Files
New:
  app/services/scrub_service.py
  app/services/ai_service.py
  app/services/report_generator.py
  tests/test_scrub_service.py
  tests/test_ai_service.py
  tests/test_report_generator.py

Updated:
  app/routes/admin.py  (generate_findings, regenerate_finding routes)
  app/templates/admin/review.html  (generate button, stale badge)
  app/templates/admin/findings.html  (new template)
