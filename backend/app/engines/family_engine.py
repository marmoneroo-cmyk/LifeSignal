"""Family Health Graph Engine.

Aggregates relatives' conditions into hereditary-risk signals and merges them into
the user's effective family-history tags (which the screening engine already
consumes). First-degree relatives weigh more than second-degree.
"""
from __future__ import annotations

from app.models import FamilyMember, User
from app.schemas import Finding

_FIRST_DEGREE = {"father", "mother", "sibling", "brother", "sister", "son", "daughter"}

# condition tag -> (human label, plain-language risk note)
_HEREDITARY = {
    "heart_disease": ("heart disease", "cardiovascular risk"),
    "diabetes": ("diabetes", "metabolic risk"),
    "breast_cancer": ("breast cancer", "breast-cancer risk"),
    "ovarian_cancer": ("ovarian cancer", "ovarian/BRCA risk"),
    "colon_cancer": ("colon cancer", "colorectal-cancer risk"),
    "prostate_cancer": ("prostate cancer", "prostate-cancer risk"),
    "melanoma": ("melanoma", "skin-cancer risk"),
}


def derived_history_tags(members: list[FamilyMember]) -> set[str]:
    """Tags to fold into the user's family_history for screening."""
    tags: set[str] = set()
    for m in members:
        for c in (m.conditions or "").split(","):
            c = c.strip().lower()
            if c in _HEREDITARY:
                tags.add(c)
    return tags


def analyze(user: User, members: list[FamilyMember]) -> list[Finding]:
    findings: list[Finding] = []
    # Count first-degree occurrences per condition.
    counts: dict[str, int] = {}
    first_degree: dict[str, int] = {}
    for m in members:
        is_first = m.relation.strip().lower() in _FIRST_DEGREE
        for c in (m.conditions or "").split(","):
            c = c.strip().lower()
            if c not in _HEREDITARY:
                continue
            counts[c] = counts.get(c, 0) + 1
            if is_first:
                first_degree[c] = first_degree.get(c, 0) + 1

    for cond, total in counts.items():
        label, risk = _HEREDITARY[cond]
        fd = first_degree.get(cond, 0)
        priority = "high" if fd >= 1 else "preventive"
        findings.append(
            Finding(
                title=f"Family history: {label}",
                detail=(
                    f"{total} relative(s) with {label}"
                    + (f", including {fd} first-degree." if fd else ".")
                ),
                priority=priority,
                source="family_engine",
                plain_language=(
                    f"Your family history suggests a higher-than-average {risk}. This can move "
                    "some preventive screenings earlier — worth discussing with a doctor."
                ),
            )
        )
    return findings
