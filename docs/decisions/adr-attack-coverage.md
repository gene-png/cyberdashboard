# ADR: MITRE ATT&CK Coverage Report Design

**Date:** 2026-04-29
**Status:** Accepted
**Feature:** feat/attack-coverage-report

## Context

We need to show how well the tools in a Zero Trust assessment cover the MITRE ATT&CK Enterprise technique catalogue — both for internal gap analysis and for leadership-level reporting.

## Decisions

### 1. Generated Excel report, not a live in-app view

An Excel snapshot is easier to share with leadership and auditors without granting them system access. It serves as a point-in-time artefact that can be attached to a review meeting, signed off, and stored in a document management system. Live in-app views are valuable for internal analysts but out of scope for the audit trail use-case.

### 2. Finalized tools only (mapping_status = "active")

Tools with `pending_review` mappings have not been verified by a consultant. Including them would introduce unverified data into the gap classification. Excluded tools are listed by name in the report's Methodology sheet so auditors know the boundary.

### 3. Fingerprint-based caching of LLM results

Anthropic API calls are non-trivial in cost and latency (~$0.01–0.05 per tool depending on technique catalogue size). Tool metadata (name, vendor, category, notes) and confirmed activity IDs rarely change between report runs. A SHA-256 fingerprint of these fields lets us skip the API call when nothing has changed and serve the cached `AttackCoverageRun.response_payload` instead. Cache is invalidated automatically whenever the fingerprint changes.

### 4. Gap classification scheme

| Status | Condition |
|---|---|
| Full | At least one detect tool AND at least one prevent tool |
| Detect Only | Detect coverage present; no prevent tool |
| Prevent Only | Prevent coverage present; no detect tool |
| Single Tool | Exactly one unique tool covers the technique (any coverage type) |
| None | No tool covers the technique |

"Full" requires both detect AND prevent because a tool that only blocks without alerting (or only alerts without blocking) represents a meaningful operational gap. "Single Tool" is a separate category because single-point-of-failure coverage is flagged differently from complete absence.
