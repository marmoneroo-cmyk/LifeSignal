"""Risk Engine + Health Score.

Produces a 0-100 Health Score broken down by domain (cardiovascular, metabolism,
etc.) from the latest lab values, plus coarse risk findings. The score is a
decision-support signal, not a medical grade.
"""
from __future__ import annotations

from app.data.lab_reference import LAB_REFERENCE, marker_meta, normal_range
from app.models import LabResult, User
from app.schemas import Finding, ScoreComponent

# Domains shown on the dashboard even if we have no data for them yet.
DOMAINS = [
    "cardiovascular",
    "metabolism",
    "blood",
    "kidney",
    "liver",
    "cancer_risk",
    "lifestyle",
]

_DOMAIN_LABELS = {
    "cardiovascular": "Heart & vessels",
    "metabolism": "Metabolism",
    "blood": "Blood",
    "kidney": "Kidneys",
    "liver": "Liver",
    "cancer_risk": "Cancer risk markers",
    "lifestyle": "Lifestyle",
}


def _latest_by_marker(results: list[LabResult]) -> dict[str, LabResult]:
    latest: dict[str, LabResult] = {}
    for r in results:
        key = r.marker.lower()
        if key not in latest or r.taken_on > latest[key].taken_on:
            latest[key] = r
    return latest


def _marker_penalty(marker: str, value: float, sex: str) -> int:
    """0 (perfect) .. 40 (badly out of range) penalty for one marker."""
    rng = normal_range(marker, sex)
    if not rng:
        return 0
    low, high = rng
    if low <= value <= high:
        return 0
    meta = marker_meta(marker)
    higher_is_risk = meta["higher_is_risk"] if meta else True
    if higher_is_risk:
        if value < low:
            return 0
        overshoot = (value - high) / (high if high else 1)
    else:
        if value > high:
            return 0
        overshoot = (low - value) / (low if low else 1)
    return min(40, int(overshoot * 100))


def score(user: User, results: list[LabResult]) -> tuple[int, list[ScoreComponent], list[Finding]]:
    latest = _latest_by_marker(results)
    findings: list[Finding] = []
    components: list[ScoreComponent] = []

    # Group markers by domain.
    domain_markers: dict[str, list[str]] = {d: [] for d in DOMAINS}
    for marker, meta in LAB_REFERENCE.items():
        domain_markers.setdefault(meta["domain"], []).append(marker)

    domain_scores: list[int] = []
    for domain in DOMAINS:
        markers = domain_markers.get(domain, [])
        measured = [m for m in markers if m in latest]
        if not measured:
            components.append(
                ScoreComponent(domain=_DOMAIN_LABELS[domain], score=-1, note="No data yet")
            )
            continue
        penalties = [_marker_penalty(m, latest[m].value, user.sex) for m in measured]
        domain_score = max(0, 100 - max(penalties))  # worst marker drives the domain
        components.append(
            ScoreComponent(
                domain=_DOMAIN_LABELS[domain],
                score=domain_score,
                note=f"{len(measured)} marker(s) measured",
            )
        )
        domain_scores.append(domain_score)

    # Lifestyle adjustment for smoking (no lab needed).
    overall = round(sum(domain_scores) / len(domain_scores)) if domain_scores else 70
    if user.smoker:
        overall = max(0, overall - 10)
        findings.append(
            Finding(
                title="Smoking raises multiple risks",
                detail="Smoking increases cardiovascular and cancer risk across the board.",
                priority="high",
                source="risk_engine",
                plain_language="Stopping smoking is the single highest-impact change for your health score.",
            )
        )

    # Composite cardiovascular flag if several heart markers are off together.
    cv_markers = ["ldl", "triglycerides", "crp", "systolic_bp"]
    cv_hits = [m for m in cv_markers if m in latest and _marker_penalty(m, latest[m].value, user.sex) > 0]
    if len(cv_hits) >= 2:
        findings.append(
            Finding(
                title="Cardiovascular risk above average for your age",
                detail=f"Multiple heart-related markers are elevated together: {', '.join(cv_hits)}.",
                priority="high",
                source="risk_engine",
                plain_language=(
                    "Several heart-risk signals are raised at once. This is worth "
                    "discussing with a doctor and reviewing preventive steps."
                ),
            )
        )

    return overall, components, findings
