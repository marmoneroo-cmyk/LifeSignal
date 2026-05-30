"""Preventive Screening Engine — the 'what you are NOT doing' engine.

Matches the user's age / sex / family history against preventive guidelines and
reports screenings that are recommended for them, marking those they appear to be
missing. (Without a documented 'done' date we treat an eligible screening as a
recommendation to verify — clearly framed, never alarmist.)
"""
from __future__ import annotations

from app.data.screening_guidelines import guidelines_for
from app.models import User
from app.schemas import Finding


def _applies(g: dict, user: User, history: set[str]) -> bool:
    if g["sex"] != "any" and g["sex"] != user.sex:
        return False
    triggered = bool(set(g["triggers"]) & history)
    if user.age < g["min_age"] and not triggered:
        return False
    if g["max_age"] is not None and user.age > g["max_age"] and not triggered:
        return False
    return True


def recommend(user: User, region: str = "intl") -> list[Finding]:
    history = {h.strip().lower() for h in (user.family_history or "").split(",") if h.strip()}
    findings: list[Finding] = []

    for g in guidelines_for(region):
        if not _applies(g, user, history):
            continue
        triggered_by = sorted(set(g["triggers"]) & history)
        priority = "high" if triggered_by else g["priority"]
        cadence = (
            "one-time" if g["interval_years"] == 0
            else f"every {g['interval_years']} year(s)"
        )
        detail = f"Recommended for your profile ({cadence})."
        if triggered_by:
            detail += f" Elevated relevance due to family history: {', '.join(triggered_by)}."
        findings.append(
            Finding(
                title=f"Screening to verify: {g['label']}",
                detail=detail,
                priority=priority,
                source="screening_engine",
                plain_language=g["why"],
            )
        )

    return findings
