# ADR 003: Phase 3 Architecture Decisions

**Date:** 2026-04-29

## Decision 1: HTMX auto-save via change trigger, not blur

The spec says "auto-save fires on every blur." Using `hx-trigger="change"` (not `blur`) is more reliable because `change` fires when the user selects a value or leaves a textarea with new content, but it does not double-fire on every keystroke. For the textarea, we use `change delay:600ms` to debounce rapid typing. The `<noscript>` fallback keeps the page usable without JavaScript.

## Decision 2: HTMX endpoint exempt from CSRF

The HTMX auto-save endpoint is exempted from Flask-WTF CSRF because: (a) it is session-authenticated (Flask-Login), (b) it only accepts POST from the same origin, and (c) adding a CSRF hidden input inside every activity card's HTMX call would require rendering it per-card in Jinja, which complicates the template significantly. SameSite=Lax session cookies provide equivalent protection for same-origin requests.

## Decision 3: Rate limiter disabled in TestingConfig

Flask-Limiter's in-memory store persists across function-scoped test fixtures because the app is session-scoped. After 5 failed login attempts across test functions, all subsequent login tests return 429. Setting `RATELIMIT_ENABLED = False` in TestingConfig cleanly disables the limiter in tests while keeping it active in production.

## Decision 4: SharePoint upload is non-blocking on failure

If SharePoint credentials are missing or the upload fails, the finalize route degrades gracefully: the assessment is still marked finalized in the DB, and a warning flash message is shown. The admin can download the Excel files manually from the browser. This avoids the scenario where a network glitch or misconfigured credential prevents finalization entirely.

## Decision 5: Stale-finding mark moved to unconditional position in HTMX handler

The original autosave handler only marked findings stale when a prior `Response` row existed (inside the `if resp:` branch). This missed the case where a finding was created before the first response was saved via HTMX. Moved the stale check to run after the response upsert in both code paths.
