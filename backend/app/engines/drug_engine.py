"""Drug Interaction Engine.

Checks the user's medication list for pairwise interactions and duplicate-class
therapy. Findings are framed as "discuss with your pharmacist/doctor" — never as
instructions to start/stop a medication.
"""
from __future__ import annotations

from itertools import combinations

from app.data.drug_interactions import (
    DUPLICATE_CLASSES,
    INTERACTIONS,
    drug_meta_label,
)
from app.models import Medication
from app.schemas import Finding


def _interaction_lookup() -> dict[frozenset[str], tuple[str, str]]:
    table: dict[frozenset[str], tuple[str, str]] = {}
    for a, b, severity, note in INTERACTIONS:
        table[frozenset({a, b})] = (severity, note)
    return table


def analyze(medications: list[Medication]) -> list[Finding]:
    keys = sorted({m.name.lower() for m in medications})
    findings: list[Finding] = []
    table = _interaction_lookup()

    for a, b in combinations(keys, 2):
        hit = table.get(frozenset({a, b}))
        if not hit:
            continue
        severity, note = hit
        findings.append(
            Finding(
                title=f"Interaction: {drug_meta_label(a)} + {drug_meta_label(b)}",
                detail=note,
                priority="high" if severity == "high" else "preventive",
                source="drug_engine",
                plain_language=(
                    f"Taking {drug_meta_label(a)} and {drug_meta_label(b)} together "
                    "is worth reviewing with your pharmacist or doctor."
                ),
            )
        )

    key_set = set(keys)
    for dup in DUPLICATE_CLASSES:
        if dup.issubset(key_set):
            names = " + ".join(drug_meta_label(d) for d in sorted(dup))
            findings.append(
                Finding(
                    title=f"Possible duplicate therapy: {names}",
                    detail="These belong to the same drug class and may be redundant together.",
                    priority="high",
                    source="drug_engine",
                    plain_language=(
                        "You may be taking two medicines that do the same job — worth confirming this is intended."
                    ),
                )
            )

    return findings
