# Plan: Phase 3 — Polish + SharePoint

## Scope

1. **HTMX auto-save** — per-activity blur saves to a HTMX partial endpoint; "Saved ✓" confirmation; no page reload
2. **Rate limiting** — Flask-Limiter: 5 attempts/15 min on login; 10/min on regenerate endpoint
3. **SharePoint service** — `sharepoint_service.py`: Graph API client (client credentials), folder create, file upload
4. **Finalize → SharePoint** — on finalize: generate both Excel files, upload to SharePoint folder, store response snapshot JSON
5. **DB backup script** — `scripts/backup_db.py`: uploads `assessments.db` to SharePoint `/Backups/{date}/`, retains 30 days
6. **Admin password gate UX** — show remaining time, inline re-prompt before timeout drops a form

## Files

New:
  app/services/sharepoint_service.py
  app/routes/htmx.py
  app/templates/partials/response_row.html
  app/templates/partials/save_indicator.html
  scripts/backup_db.py
  tests/test_sharepoint_service.py
  tests/test_htmx.py

Updated:
  app/__init__.py                 (register htmx_bp, init limiter)
  app/extensions.py               (add limiter)
  app/routes/auth.py              (rate-limit login)
  app/routes/admin.py             (rate-limit regenerate, call SharePoint on finalize)
  app/routes/assessment.py        (keep manual save for fallback)
  app/templates/assessment/pillar.html  (add HTMX attrs, save indicator)
  app/templates/base.html         (add htmx.min.js, admin timeout JS)
  requirements.txt                (pin flask-limiter already in)

## SharePoint folder layout (per spec §8.2)
```
ZT Assessments/
└── {OrgName}_{date}/
    ├── inputs/responses_snapshot.json
    ├── outputs/customer_report.xlsx
    ├── outputs/consultant_report.xlsx
    ├── audit/ai_call_log.csv
    └── audit/audit_log.csv
```

## HTMX auto-save flow
1. Activity `<select>` and `<textarea>` have `hx-post`, `hx-trigger="change delay:400ms"`,
   `hx-target="#save-{activity_id}"`, `hx-swap="innerHTML"`
2. POST to `/htmx/assessments/{id}/response/{activity_id}` with current+target+notes
3. Returns `<span class="save-ok">Saved</span>` (fades out via CSS) or error span
4. Pillar page still has a manual "Save All" form as fallback (no JS = works too)

## Rate limiting
- Login: 5/15 minutes per IP
- Admin regenerate: 10/minute per IP (prevents accidental cost runaway per spec §11)
- Storage: in-memory (default) — acceptable for single-instance deployment
