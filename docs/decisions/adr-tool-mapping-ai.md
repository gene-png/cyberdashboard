# ADR-001: AI-Derived Tool-to-Activity Mapping with Mandatory Admin Review

## Status
Accepted

## Date
2026-04-29

---

## Context

The Tool Inventory Mapping Excel sheet (spec §7.1) requires each tool to be mapped to the framework activities it supports. With 50+ activities per framework, three options were evaluated:

**(a) Manual admin mapping**
Admin selects applicable activities per tool via checkboxes. Accurate but cognitively heavy and time-consuming; prone to omissions on large inventories.

**(b) Category heuristic**
Derive mappings from the tool's category (e.g., "IAM" → Identity pillar activities). Fast to implement, but tool categories don't cleanly align to framework pillars and produce coarse, unreliable results.

**(c) AI-derived with mandatory admin review**
Claude suggests mappings (activity_id, confidence, rationale) via a structured JSON prompt. Admin reviews suggestions on a dedicated page before any mapping becomes active. Combines speed with accuracy and preserves human authority over the final record.

---

## Decision

**Option (c).** Claude generates mapping suggestions via a structured prompt that includes the tool name, description, and the full list of framework activities. The response is a JSON array of `{activity_id, confidence, rationale}` objects. These are stored in `MappingSuggestionsLog` and pre-populate checkboxes on the admin mapping review page. No mapping is marked active until an admin finalizes the review. Re-run is available if the tool description changes.

---

## Consequences

- **Cost:** ~$0.01 per tool at Sonnet pricing. Acceptable for 5–20 tools per engagement.
- **Audit trail:** `MappingSuggestionsLog` preserves the raw LLM prompt and response. `MappingChange` records every post-finalization edit with before/after JSON.
- **Trust:** Rationale field shown alongside each checkbox improves admin confidence in accepting or rejecting suggestions.
- **Graceful degrade:** If `ANTHROPIC_API_KEY` is absent or the API call fails, the mapping page opens with all checkboxes unchecked and a warning banner. Admin can finalize mappings manually with no data loss.
- **Re-run:** Allowed when `ToolInventory.mapping_status` is not `active`, or explicitly triggered by admin.

---

## Analysis Thresholds (configurable via app config)

| Metric | Default threshold |
|--------|-------------------|
| Redundancy | 3 tools per activity |
| Underutilization | < 2 active mappings per tool |

Only tools with `mapping_status = 'active'` appear in redundancy and underutilization analysis.

---

## Fallback Behavior

1. `ANTHROPIC_API_KEY` absent → skip API call, open review page blank with banner: "AI suggestions unavailable — map activities manually."
2. API call fails (timeout, rate limit, bad response) → same banner, log error to `MappingSuggestionsLog.raw_response`.
3. Malformed JSON response → attempt partial parse; log raw response; fall back to empty suggestions.
