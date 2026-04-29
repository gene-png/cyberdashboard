# Plan: Phase 6 — Excel Mapping, Workspace UX & AI Tool Mapping

## Status: Draft
## Date: 2026-04-29

---

## Scope

### 1. Gap Register Excel — Priority & Related Tools columns
- Add `Priority` column (integer: 1=critical, 2=high, 3=medium, 4=low) to Gap model and Gap Register sheet.
- Add `Related Tools` column: pipe-separated tool names whose active mappings include that activity.
- Populate via join on `ToolActivityMapping` at export time.

### 2. Executive Summary Excel — Top 5 Priority Gaps callout
- Below the pillar score table, insert a "Top 5 Priority Gaps" block.
- Sorted by Priority asc, then pillar. Pull from Gap table filtered by assessment.

### 3. Customer workspace — Additional Sensitive Terms
- Add `<textarea>` to `assessment_overview.html` (overview page).
- POST to `/assessments/<id>/terms` (not the admin route).
- Creates `SensitiveTerm` rows with `source='user_added'`.
- Admin `/admin` route remains unchanged.

### 4. Workspace resume — redirect to current step
- On `GET /assessments/<id>`: if `assessment.current_step` is set, redirect to that pillar page.
- `?overview=1` query param bypasses the redirect.
- Update all "Back to Overview" links to include `?overview=1`.

### 5. AI generation progress indicator (JS-only)
- On Generate AI Findings form submit: show a loading overlay with elapsed-seconds counter.
- Disable the submit button for the duration.
- No server changes. Pure JS in `assessment.html` (or shared `main.js`).

### 6. AI-derived Tool Activity Mapping (full feature)
See `docs/decisions/adr-tool-mapping-ai.md` for rationale.

**New DB models:**
- `ToolActivityMapping(id, tool_id, activity_id, confidence, rationale, is_active)`
- `MappingSuggestionsLog(id, tool_id, prompt, raw_response, created_at)`
- `MappingChange(id, tool_id, admin_user, change_type, before_json, after_json, changed_at)`

**Updated model:**
- `ToolInventory` gains `mapping_status` (enum: pending/active/skipped) and `mappings_finalized_at`, `mappings_finalized_by`.

**New service:** `app/services/mapping_suggester.py`
- Builds structured prompt from tool name/description + framework activities.
- Calls Claude API, parses JSON response.
- Graceful-degrade: returns empty suggestions on failure.

**New admin routes + template:**
- `GET/POST /admin/tools/<id>/mapping` — review/finalize mapping page.
- Template: `admin_tool_mapping.html` — checkboxes pre-populated from AI suggestions, confidence badges, rationale tooltips.

**Excel — Tool Inventory Mapping sheet:**
- Activity linkage table per tool.
- Redundancy panel: activities covered by 3+ tools.
- Underutilization panel: tools with <2 active mappings.

**`inventory.html` updates:**
- Mapping status badge per tool.
- Link to mapping review page.

### 7. SharePoint README.txt
- On SharePoint export, upload `README.txt` to the folder describing contents.

---

## Files Modified / Created

| Path | Change |
|------|--------|
| `app/models.py` | Add ToolActivityMapping, MappingSuggestionsLog, MappingChange; update ToolInventory |
| `app/services/mapping_suggester.py` | New — AI mapping service |
| `app/routes/admin.py` | Add mapping review routes |
| `app/routes/assessments.py` | Add /terms route; add current_step redirect |
| `app/templates/admin_tool_mapping.html` | New — mapping review UI |
| `app/templates/assessment_overview.html` | Add sensitive terms textarea; update Back links |
| `app/templates/inventory.html` | Add mapping status badge + review link |
| `app/static/js/main.js` | AI generation progress overlay |
| `app/services/excel_exporter.py` | Priority + Related Tools cols; Top 5 gaps; Mapping sheet |
| `app/services/sharepoint.py` | Upload README.txt |
| `tests/test_tool_mapping.py` | New — mapping service + routes tests |
| `tests/test_excel_export.py` | Extended — new columns and sheets |
| `migrations/` | New migration for schema changes |
