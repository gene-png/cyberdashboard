# ADR 002: Phase 2 Architecture Decisions

**Date:** 2026-04-29

## Decision 1: Word-boundary-safe token replacement

The initial scrub used `re.compile(re.escape(find), re.IGNORECASE)` which matched substrings. For an org named "Test Org", the abbreviation "TO" would incorrectly match "to" inside email addresses (e.g. "admin@testorg.gov" → "admin@tes[ORG_2]rg.gov"), breaking the email regex that runs next. Fixed by using lookahead/lookbehind `(?<![A-Za-z0-9_])` anchors instead of `\b` (which doesn't work well around square brackets and spaces). This ensures tokens only replace standalone words, not substrings.

## Decision 2: spaCy NER deferred

The spec calls for a spaCy NER pass as Layer 2b to catch org/person names not in the token map. This was deferred to Phase 5 because: (a) installing spaCy + a model adds ~500MB to the container, (b) the token map + regex cover the primary vectors, and (c) the spec flags Phase 2 as "test the scrub layer hard" not "implement every layer." The `is_active` flag on SensitiveTerm future-proofs the NER integration path.

## Decision 3: Synchronous AI generation (no HTMX progress)

Phase 2 runs generation synchronously — the admin waits for the HTTP response. For 30–50 gaps this is 30–90 seconds (real API key). A progress indicator via HTMX server-sent events is planned for Phase 3. The current design is correct for the Phase 1 use case of small assessments.

## Decision 4: Placeholder mode when no API key

Rather than failing or skipping, `generate_findings` produces structured placeholder text when `ANTHROPIC_API_KEY` is empty. This lets the full workflow run in dev/test without credentials, and gives admins a usable (if generic) starting point if they choose to generate before configuring the key.

## Decision 5: Prompt injection defense at the boundary

Customer-supplied free text (evidence notes, tool notes) is passed through `_guard_free_text()` before entering the prompt. This strips patterns matching known instruction-override attempts. The Anthropic system prompt also includes explicit instructions to ignore any directive text found in the user message. Defense-in-depth: both the input and the model instruction defend against jailbreak attempts via user-supplied content.
