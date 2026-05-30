"""Coverage Matching — links recommended screenings to insurance reality.

For each recommended screening, says whether the user appears to hold relevant
private coverage and whether it's typically funded by the public basket. This is
the bridge between the health side and the insurance side of the product.
"""
from __future__ import annotations

from app.models import InsurancePolicy
from app.schemas import Finding

# screening key -> (relevant coverage_type or None, funded_by_public_basket?)
_SCREENING_COVERAGE: dict[str, tuple[str | None, bool]] = {
    "colonoscopy": ("surgery", True),
    "mammogram": ("health_basic", True),
    "brca": ("critical_illness", False),
    "cervical": ("health_basic", True),
    "psa": ("health_basic", True),
    "lipid_panel": ("health_basic", True),
    "diabetes": ("health_basic", True),
    "bp_check": ("health_basic", True),
    "skin_check": ("surgery", False),
    "aaa": ("surgery", False),
}

# map a screening Finding title back to its key (titles come from the guideline label)
_TITLE_HINTS = {
    "colorectal": "colonoscopy",
    "breast cancer screening": "mammogram",
    "brca": "brca",
    "cervical": "cervical",
    "prostate": "psa",
    "lipid": "lipid_panel",
    "diabetes": "diabetes",
    "blood pressure": "bp_check",
    "skin": "skin_check",
    "aortic": "aaa",
}


def _key_for(title: str) -> str | None:
    t = title.lower()
    for hint, key in _TITLE_HINTS.items():
        if hint in t:
            return key
    return None


def analyze(screenings: list[Finding], policies: list[InsurancePolicy]) -> list[Finding]:
    held = {p.coverage_type.lower() for p in policies}
    out: list[Finding] = []

    for s in screenings:
        key = _key_for(s.title)
        if not key or key not in _SCREENING_COVERAGE:
            continue
        cov_type, public = _SCREENING_COVERAGE[key]
        has_private = cov_type in held if cov_type else False
        bits = []
        if public:
            bits.append("typically funded by the public basket")
        if cov_type:
            bits.append("private coverage found" if has_private else "no matching private coverage found")
        detail = "; ".join(bits) if bits else "coverage information unavailable."
        out.append(
            Finding(
                title=f"Coverage for: {s.title.replace('Screening to verify: ', '')}",
                detail=detail.capitalize() + ".",
                priority="informational",
                source="coverage_match",
                plain_language=(
                    "Here's how this recommended test lines up with what you're covered for, "
                    "so cost is one less reason to delay."
                ),
            )
        )
    return out
