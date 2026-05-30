"""Insurance coverage reference for risk-adjusted policy analysis.

Defines the canonical coverage types the analyzer understands, whether each is
considered critical, and a coarse age band where it is most relevant. This drives
duplicate detection, gap detection, and age-relevance flags.
"""
from __future__ import annotations

# critical: a gap here is flagged "high"; otherwise "informational"/"preventive".
# relevant_ages: (min_age, max_age|None) where this coverage matters most.
COVERAGE_TYPES: dict[str, dict] = {
    "health_basic": {
        "label": "Basic health / ambulatory",
        "critical": True,
        "relevant_ages": (0, None),
    },
    "critical_illness": {
        "label": "Critical illness",
        "critical": True,
        "relevant_ages": (30, 65),
    },
    "disability": {
        "label": "Loss of working capacity (disability)",
        "critical": True,
        "relevant_ages": (25, 67),
    },
    "long_term_care": {
        "label": "Long-term care (nursing)",
        "critical": True,
        "relevant_ages": (45, None),
    },
    "drugs_outside_basket": {
        "label": "Medications outside the national basket",
        "critical": True,
        "relevant_ages": (0, None),
    },
    "surgery": {
        "label": "Private surgery / specialist",
        "critical": False,
        "relevant_ages": (0, None),
    },
    "dental": {
        "label": "Dental",
        "critical": False,
        "relevant_ages": (0, None),
    },
    "travel": {
        "label": "Travel insurance",
        "critical": False,
        "relevant_ages": (0, None),
    },
}

# Coverage every adult should generally hold; absence is a critical gap.
ESSENTIAL_COVERAGE = [
    "health_basic",
    "disability",
    "drugs_outside_basket",
]


def coverage_meta(coverage_type: str) -> dict | None:
    return COVERAGE_TYPES.get(coverage_type.lower())
