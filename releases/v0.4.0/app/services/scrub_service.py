"""
Privacy scrub pipeline — three layers per spec §6.2.

Layer 1: Per-assessment token map (DB-backed SensitiveTerm table).
Layer 2: Regex pass — IPv4, IPv6, MAC addresses, FQDNs, email addresses.
Layer 3: Inbound rehydrate — reverse the token map, warn on unknown tokens.

spaCy NER (Layer 2b) is deferred to Phase 5.
"""
import re
import logging
from typing import Optional

from ..extensions import db
from ..models import SensitiveTerm

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Vendor/product allowlist — these pass through unscrubbed.
# Add to this list rather than bloating the token map.
# ---------------------------------------------------------------------------
VENDOR_ALLOWLIST: frozenset[str] = frozenset(
    [
        "microsoft", "azure", "defender", "entra", "intune", "sentinel",
        "crowdstrike", "falcon", "palo alto", "prisma", "cortex",
        "splunk", "elastic", "okta", "ping identity", "sailpoint",
        "cyberark", "beyond trust", "beyondtrust", "thycotic", "delinea",
        "cisco", "duo", "secureworks", "mandiant", "google", "chronicle",
        "aws", "amazon", "tenable", "qualys", "rapid7", "veracode",
        "checkmarx", "snyk", "fortinet", "zscaler", "netskope",
        "illumio", "guardicore", "vmware", "carbon black",
    ]
)

# ---------------------------------------------------------------------------
# Regex patterns for Layer 2
# ---------------------------------------------------------------------------
_RE_IPV4 = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b"
)
_RE_IPV6 = re.compile(
    r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b"
    r"|\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b"
    r"|\b::(?:[0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4}\b"
)
_RE_MAC = re.compile(
    r"\b(?:[0-9a-fA-F]{2}[:\-]){5}[0-9a-fA-F]{2}\b"
)
_RE_EMAIL = re.compile(
    r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b"
)
# FQDN pattern — must contain at least one dot and not be a standalone word.
# Intentionally conservative to avoid over-scrubbing tool names.
_RE_FQDN = re.compile(
    r"\b(?:[a-zA-Z0-9\-]+\.){2,}(?:com|org|net|gov|mil|edu|io|us|co)\b"
)

# Token type prefixes
_IP_PREFIX = "IP"
_IPV6_PREFIX = "IPV6"
_MAC_PREFIX = "MAC"
_HOST_PREFIX = "HOST"
_EMAIL_PREFIX = "EMAIL"

# Pattern used to detect leftover unknown tokens in AI response
_RE_UNKNOWN_TOKEN = re.compile(r"\[UNKNOWN_[A-Z0-9_]+\]")


def _next_token_num(existing_tokens: list[str], prefix: str) -> int:
    """Return the next integer suffix for a given token prefix."""
    highest = 0
    pattern = re.compile(rf"^\[{re.escape(prefix)}_(\d+)\]$")
    for t in existing_tokens:
        m = pattern.match(t)
        if m:
            highest = max(highest, int(m.group(1)))
    return highest + 1


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def seed_token_map(assessment_id: str, org_name: str, usernames: list[str], extra_terms: list[str] | None = None) -> None:
    """
    Seed the sensitive_term table for a new assessment.

    Idempotent: skips terms that are already mapped.
    """
    existing = {st.term for st in SensitiveTerm.query.filter_by(assessment_id=assessment_id).all()}
    existing_replacements = [
        st.replacement_token
        for st in SensitiveTerm.query.filter_by(assessment_id=assessment_id).all()
    ]

    def _add(term: str, prefix: str) -> None:
        if not term or term in existing:
            return
        n = _next_token_num(existing_replacements, prefix)
        token = f"[{prefix}_{n}]"
        st = SensitiveTerm(
            assessment_id=assessment_id,
            term=term,
            replacement_token=token,
            source="auto",
        )
        db.session.add(st)
        existing.add(term)
        existing_replacements.append(token)

    # Org name and common abbreviations
    _add(org_name, "ORG")
    # Simple initials abbreviation: "Acme Federal Agency" → "AFA"
    words = [w for w in org_name.split() if w]
    if len(words) > 1:
        initials = "".join(w[0].upper() for w in words)
        _add(initials, "ORG")
    # First two words as a shorter name
    if len(words) >= 2:
        short = " ".join(words[:2])
        if short != org_name:
            _add(short, "ORG")

    # Usernames → PERSON tokens
    for uname in usernames:
        if uname:
            _add(uname, "PERSON")

    # Extra user-supplied terms
    for term in (extra_terms or []):
        if term:
            _add(term, "PROGRAM")

    db.session.commit()


def scrub(assessment_id: str, text: str) -> str:
    """
    Scrub sensitive content from *text* before sending to the AI.

    Applies Layer 1 (token map) then Layer 2 (regex patterns).
    """
    if not text:
        return text

    # Layer 1 — token map (longest-first to avoid partial replacements)
    terms = (
        SensitiveTerm.query
        .filter_by(assessment_id=assessment_id, is_active=True)
        .all()
    )
    # Sort by term length descending so longer matches replace first
    terms_sorted = sorted(terms, key=lambda t: len(t.term), reverse=True)
    for st in terms_sorted:
        text = _case_insensitive_replace(text, st.term, st.replacement_token)

    # Layer 2 — regex patterns (order matters: email before FQDN to avoid
    # the @ being swallowed as part of a hostname match)
    text, _ = _apply_regex_scrub(text, _RE_EMAIL, _EMAIL_PREFIX)
    text, _ = _apply_regex_scrub(text, _RE_IPV4, _IP_PREFIX)
    text, _ = _apply_regex_scrub(text, _RE_IPV6, _IPV6_PREFIX)
    text, _ = _apply_regex_scrub(text, _RE_MAC, _MAC_PREFIX)
    text, _ = _apply_regex_scrub(text, _RE_FQDN, _HOST_PREFIX)

    return text


def rehydrate(assessment_id: str, text: str) -> str:
    """
    Reverse the token map in an AI response.

    Warns (but does not raise) if unknown [TOKEN] patterns remain.
    """
    if not text:
        return text

    terms = (
        SensitiveTerm.query
        .filter_by(assessment_id=assessment_id, is_active=True)
        .all()
    )
    # Reverse map: replacement_token → term
    for st in terms:
        text = text.replace(st.replacement_token, st.term)

    # Sanity check: warn if any [UNKNOWN_*] patterns remain
    unknowns = _RE_UNKNOWN_TOKEN.findall(text)
    if unknowns:
        logger.warning(
            "Rehydrate found unknown tokens in assessment %s: %s",
            assessment_id,
            unknowns,
        )

    return text


def get_token_map(assessment_id: str) -> dict[str, str]:
    """Return {term: replacement_token} for all active terms in this assessment."""
    terms = SensitiveTerm.query.filter_by(assessment_id=assessment_id, is_active=True).all()
    return {st.term: st.replacement_token for st in terms}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _case_insensitive_replace(text: str, find: str, replace: str) -> str:
    """
    Replace all case-insensitive occurrences of *find* with *replace*.

    Uses word boundaries so short abbreviations like "TO" don't match
    inside longer words like "testorg".
    """
    # \b doesn't anchor well around punctuation in multi-word phrases with spaces,
    # so we use lookahead/lookbehind to require a non-word character (or start/end)
    # on both sides.
    boundary = r"(?<![A-Za-z0-9_])"
    pattern = re.compile(boundary + re.escape(find) + r"(?![A-Za-z0-9_])", re.IGNORECASE)
    return pattern.sub(replace, text)


def _apply_regex_scrub(text: str, pattern: re.Pattern, prefix: str) -> tuple[str, list[str]]:
    """
    Replace all matches of *pattern* with sequential [PREFIX_N] tokens.

    Preserves previously substituted tokens by skipping already-bracketed content.
    Returns (scrubbed_text, list_of_new_tokens).
    """
    new_tokens: list[str] = []
    counter = [1]

    def _replacer(m: re.Match) -> str:
        token = f"[{prefix}_{counter[0]}]"
        counter[0] += 1
        new_tokens.append(token)
        return token

    text = pattern.sub(_replacer, text)
    return text, new_tokens
