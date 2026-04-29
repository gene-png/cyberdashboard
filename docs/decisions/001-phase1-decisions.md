# ADR 001: Phase 1 Architecture Decisions

**Date:** 2026-04-29

## Decision 1: Admin gate as session unlock, not role

The spec calls for an "admin password gate" as a session-level unlock on top of the normal login system, not a separate admin user role. This allows the consultant to log in as a customer and walk them through assessment entry without exposing admin views. The gate is implemented as `is_admin_unlocked()` checking a session timestamp with a 15-minute timeout.

## Decision 2: Pillar responses as form POSTs, not HTMX auto-save

Phase 1 uses explicit form submission per pillar rather than HTMX auto-save. HTMX auto-save is spec'd for Phase 3. This keeps Phase 1 simpler and avoids partial-save race conditions.

## Decision 3: Excel sheet titles sanitized with regex

openpyxl forbids `[\\/*?\[\]:]` in worksheet titles. "Network/Environment" (DoD ZT pillar name) contains `/`, which would raise `ValueError`. We replace invalid chars with `_` before creating sheets. The test asserts "Network_Environment" as the expected sheet title.

## Decision 4: Framework data loaded at request time with in-memory cache

`framework_loader.py` reads JSON from disk on first request per framework ID and caches in a module-level dict. This avoids DB storage of framework data (spec says file-based) while keeping subsequent requests fast. Cache is cleared on process restart, which is the right behavior when a framework file is updated.

## Decision 5: Consultant Excel built by copying customer Excel

Rather than building the consultant report from scratch, `build_consultant_excel` builds the customer report first, then copies all sheets into a new workbook and appends admin-only sheets. This avoids duplication and ensures the customer and consultant reports have identical presentation for shared sheets. Uses `copy.copy()` instead of the deprecated `.copy()` method on openpyxl style objects.
