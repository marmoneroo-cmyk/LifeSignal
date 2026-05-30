"""Document Intake + Medical-text parsing (rule-based, local).

Extracts the text layer from an uploaded PDF and heuristically pulls out:
  - lab markers + values (mapped to canonical keys via aliases)
  - insurance coverage lines + monthly premiums

Scope: text-layer PDFs. Scanned/image-only PDFs need true OCR (Azure / Google
Document AI) — a documented future module. Output is always returned as *candidates*
for the user to review and confirm; nothing is auto-trusted.
"""
from __future__ import annotations

import io
import re
from datetime import date

from app.data.aliases import COVERAGE_ALIASES, MARKER_ALIASES
from app.data.insurance_reference import coverage_meta
from app.data.lab_reference import marker_meta

# A number like 162, 5.7, 1,234.5  (commas as thousand separators tolerated).
_NUMBER = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)(?![\w.])")
_DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "ymd"),
    (re.compile(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b"), "dmy"),
]


def extract_text(data: bytes) -> str:
    """Extract concatenated text from a PDF's text layer."""
    import pdfplumber  # imported lazily so the rest of the app runs without it

    chunks: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            chunks.append(page.extract_text() or "")
    return "\n".join(chunks)


def _to_float(raw: str) -> float | None:
    try:
        return float(raw.replace(",", ""))
    except ValueError:
        return None


def _find_date(text: str) -> date | None:
    for pattern, kind in _DATE_PATTERNS:
        m = pattern.search(text)
        if not m:
            continue
        try:
            if kind == "ymd":
                y, mo, d = (int(g) for g in m.groups())
            else:
                d, mo, y = (int(g) for g in m.groups())
            return date(y, mo, d)
        except ValueError:
            continue
    return None


def _match_alias(line_lc: str, alias_map: dict[str, list[str]]) -> str | None:
    """Return the canonical key whose alias best matches the line (longest alias)."""
    best_key, best_len = None, 0
    for key, aliases in alias_map.items():
        for alias in aliases:
            if alias in line_lc and len(alias) > best_len:
                best_key, best_len = key, len(alias)
    return best_key


def parse_labs(text: str) -> list[dict]:
    report_date = _find_date(text) or date.today()
    seen: set[str] = set()
    out: list[dict] = []

    for line in text.splitlines():
        line_lc = line.lower()
        marker = _match_alias(line_lc, MARKER_ALIASES)
        if not marker or marker in seen:
            continue
        nums = _NUMBER.findall(line)
        if not nums:
            continue
        value = _to_float(nums[0])
        if value is None:
            continue
        meta = marker_meta(marker)
        seen.add(marker)
        out.append(
            {
                "marker": marker,
                "label": meta["label"] if meta else marker,
                "value": value,
                "unit": meta["unit"] if meta else "",
                "taken_on": report_date.isoformat(),
                "source_line": line.strip()[:120],
            }
        )
    return out


# Clause cue-words (English + Hebrew) -> which field they populate.
_DEDUCTIBLE_CUES = ("deductible", "co-pay", "copay", "השתתפות עצמית", "השתתפות")
_CEILING_CUES = ("ceiling", "maximum", "max benefit", "up to", "תקרה", "עד לסך")
_EXCLUSION_CUES = ("exclusion", "not covered", "excluded", "החרגה", "לא מכוסה", "אינו מכוסה")


def _scan_clauses(lines: list[str]) -> dict:
    """Best-effort scan for deductible / ceiling amounts and exclusion notes."""
    deductible, ceiling = 0.0, 0.0
    exclusions: list[str] = []
    for line in lines:
        lc = line.lower()
        nums = [n for n in (_to_float(x) for x in _NUMBER.findall(line)) if n is not None]
        if any(c in lc for c in _DEDUCTIBLE_CUES) and nums:
            deductible = max(deductible, max(nums))
        if any(c in lc for c in _CEILING_CUES) and nums:
            ceiling = max(ceiling, max(nums))
        if any(c in lc for c in _EXCLUSION_CUES):
            exclusions.append(line.strip()[:80])
    return {"deductible": deductible, "ceiling": ceiling, "exclusions": "; ".join(exclusions[:5])}


def parse_policies(text: str) -> list[dict]:
    seen: set[str] = set()
    out: list[dict] = []
    lines = text.splitlines()
    clauses = _scan_clauses(lines)  # document-level clause scan

    for line in lines:
        line_lc = line.lower()
        ctype = _match_alias(line_lc, COVERAGE_ALIASES)
        if not ctype or ctype in seen:
            continue
        # A premium is the number nearest a currency / "per month" cue, else first number.
        premium = 0.0
        nums = [n for n in (_to_float(x) for x in _NUMBER.findall(line)) if n is not None]
        if nums:
            premium = nums[-1] if any(c in line for c in ("₪", "$", "month", "לחודש")) else nums[0]
        meta = coverage_meta(ctype)
        seen.add(ctype)
        out.append(
            {
                "provider": "(from document)",
                "coverage_type": ctype,
                "label": meta["label"] if meta else ctype,
                "monthly_premium": premium,
                "renewal_date": (_find_date(line) or None) and _find_date(line).isoformat(),
                "deductible": clauses["deductible"],
                "ceiling": clauses["ceiling"],
                "exclusions": clauses["exclusions"],
                "source_line": line.strip()[:120],
            }
        )
    return out


def parse(data: bytes, kind: str) -> dict:
    """kind: 'lab' | 'insurance' | 'auto'. Returns candidate labs + policies."""
    text = extract_text(data)
    labs = parse_labs(text) if kind in ("lab", "auto") else []
    policies = parse_policies(text) if kind in ("insurance", "auto") else []
    warnings: list[str] = []
    if not text.strip():
        warnings.append(
            "No text layer found. This looks like a scanned image — OCR (a future "
            "module) is required. Try a digitally-generated PDF."
        )
    if text.strip() and not labs and not policies:
        warnings.append("Text was read but no known markers or coverage lines were recognised.")
    return {
        "kind": kind,
        "text_chars": len(text),
        "labs": labs,
        "policies": policies,
        "warnings": warnings,
    }
