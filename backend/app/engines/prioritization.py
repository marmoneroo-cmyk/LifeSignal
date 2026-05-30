"""Prioritization Engine — order findings so the user sees what matters first."""
from __future__ import annotations

from app.schemas import Finding

PRIORITY_RANK = {"critical": 0, "high": 1, "preventive": 2, "informational": 3}


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(findings, key=lambda f: PRIORITY_RANK.get(f.priority, 99))


def top_priorities(findings: list[Finding], limit: int = 3) -> list[Finding]:
    """The '3 most important things for your health right now' surface."""
    actionable = [f for f in findings if f.priority in ("critical", "high")]
    ranked = sort_findings(actionable) or sort_findings(findings)
    return ranked[:limit]
