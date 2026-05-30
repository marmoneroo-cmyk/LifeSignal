"""Health report + reference-metadata endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.data.insurance_reference import COVERAGE_TYPES
from app.data.lab_reference import LAB_REFERENCE
from app.auth import accessible_profile
from app.config import DISCLAIMER
from app.db import get_db
from app.engines import copilot_engine, narrative_engine, report_engine
from app.engines.translator import translate_report
from app.models import User
from app.schemas import Copilot, HealthReport, Narrative

router = APIRouter(prefix="/api", tags=["report"])


@router.get("/users/{user_id}/report", response_model=HealthReport)
def get_report(lang: str = "he", user: User = Depends(accessible_profile)) -> HealthReport:
    return translate_report(report_engine.generate(user), lang)


@router.get("/users/{user_id}/export")
def export_data(user: User = Depends(accessible_profile)) -> dict:
    """Full data export for the profile (longitudinal portability)."""
    return {
        "profile": {
            "name": user.name,
            "sex": user.sex,
            "birth_date": user.birth_date.isoformat(),
            "region": user.region,
            "smoker": user.smoker,
            "family_history": user.family_history,
        },
        "lab_results": [
            {"marker": r.marker, "value": r.value, "unit": r.unit, "taken_on": r.taken_on.isoformat()}
            for r in user.lab_results
        ],
        "policies": [
            {
                "provider": p.provider,
                "coverage_type": p.coverage_type,
                "monthly_premium": p.monthly_premium,
                "renewal_date": p.renewal_date.isoformat() if p.renewal_date else None,
            }
            for p in user.policies
        ],
        "medications": [{"name": m.name, "dose": m.dose} for m in user.medications],
        "family_members": [
            {"relation": f.relation, "conditions": f.conditions} for f in user.family_members
        ],
    }


@router.get("/users/{user_id}/annual")
def annual_report(user: User = Depends(accessible_profile)) -> dict:
    """Year-over-year comparison of each marker's annual value."""
    from collections import defaultdict

    by_marker_year: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in user.lab_results:
        by_marker_year[r.marker][r.taken_on.year].append(r.value)

    series = []
    for marker, years in by_marker_year.items():
        points = sorted(
            ({"year": y, "value": round(sum(v) / len(v), 2)} for y, v in years.items()),
            key=lambda p: p["year"],
        )
        if len(points) >= 2:
            delta = round(points[-1]["value"] - points[0]["value"], 2)
            series.append({"marker": marker, "points": points, "change": delta})
    return {"years_covered": series, "disclaimer": DISCLAIMER}


@router.get("/users/{user_id}/narrative", response_model=Narrative)
def get_narrative(lang: str = "he", user: User = Depends(accessible_profile)) -> Narrative:
    report = report_engine.generate(user)
    return Narrative(**narrative_engine.narrate(report, lang=lang))


@router.get("/users/{user_id}/copilot", response_model=Copilot)
def get_copilot(lang: str = "he", user: User = Depends(accessible_profile)) -> Copilot:
    report = report_engine.generate(user)
    return Copilot(**copilot_engine.prepare(report, lang=lang))


@router.get("/reference/markers")
def list_markers() -> list[dict]:
    """Marker catalog so the frontend can build the lab-entry form."""
    return [
        {"key": k, "label": v["label"], "unit": v["unit"]}
        for k, v in LAB_REFERENCE.items()
    ]


@router.get("/reference/coverage-types")
def list_coverage_types() -> list[dict]:
    return [
        {"key": k, "label": v["label"], "critical": v["critical"]}
        for k, v in COVERAGE_TYPES.items()
    ]
