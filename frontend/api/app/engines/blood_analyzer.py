"""Blood Test Analysis Engine.

Detects:
  - abnormal / borderline markers vs. sex-specific reference ranges
  - longitudinal trends across repeated tests ("the thing most doctors miss")
Returns plain-language Findings and structured MarkerTrend series for charts.
"""
from __future__ import annotations

from collections import defaultdict

from app.data.lab_reference import (
    borderline_range,
    marker_meta,
    normal_range,
)
from app.models import LabResult, User
from app.schemas import Finding, MarkerTrend, TrendPoint

# A change of at least this fraction across the series counts as a real trend.
_TREND_THRESHOLD = 0.10


def _classify(marker: str, value: float, sex: str) -> str:
    rng = normal_range(marker, sex)
    if not rng:
        return "normal"
    low, high = rng
    if low <= value <= high:
        return "normal"
    meta = marker_meta(marker)
    higher_is_risk = meta["higher_is_risk"] if meta else True
    # A value on the "safe" side of the range is not a concern.
    if higher_is_risk and value < low:
        return "normal"
    if not higher_is_risk and value > high:
        return "normal"
    bord = borderline_range(marker, sex)
    if bord and bord[0] <= value <= bord[1]:
        return "borderline"
    return "abnormal"


def _direction(points: list[TrendPoint]) -> str:
    if len(points) < 2:
        return "stable"
    first, last = points[0].value, points[-1].value
    if first == 0:
        return "stable"
    change = (last - first) / abs(first)
    if change > _TREND_THRESHOLD:
        return "rising"
    if change < -_TREND_THRESHOLD:
        return "falling"
    return "stable"


def _plain_language(marker: str, status: str, label: str) -> str:
    phrases = {
        ("hba1c", "borderline"): "Your average blood sugar is starting to creep up.",
        ("hba1c", "abnormal"): "Your average blood sugar is in a range worth discussing with a doctor.",
        ("ldl", "borderline"): "Your 'bad' cholesterol is a little above the ideal target.",
        ("ldl", "abnormal"): "Your 'bad' cholesterol is high enough to discuss with a doctor.",
        ("hemoglobin", "abnormal"): "Your red blood cell level is lower than expected, which can cause fatigue.",
        ("ferritin", "abnormal"): "Your iron stores look low.",
        ("vitamin_d", "abnormal"): "Your vitamin D level is below the recommended range.",
        ("tsh", "abnormal"): "Your thyroid hormone signal is outside the usual range.",
    }
    generic = {
        "borderline": f"{label} is slightly outside the ideal range.",
        "abnormal": f"{label} is outside the usual range and worth a closer look.",
    }
    return phrases.get((marker, status), generic.get(status, ""))


def build_trends(user: User, results: list[LabResult]) -> list[MarkerTrend]:
    by_marker: dict[str, list[LabResult]] = defaultdict(list)
    for r in results:
        by_marker[r.marker.lower()].append(r)

    trends: list[MarkerTrend] = []
    for marker, rows in by_marker.items():
        meta = marker_meta(marker)
        if not meta:
            continue
        rows.sort(key=lambda r: r.taken_on)
        points = [TrendPoint(taken_on=r.taken_on, value=r.value) for r in rows]
        latest_status = _classify(marker, rows[-1].value, user.sex)
        trends.append(
            MarkerTrend(
                marker=marker,
                label=meta["label"],
                unit=meta["unit"],
                points=points,
                direction=_direction(points),
                status=latest_status,
            )
        )
    trends.sort(key=lambda t: {"abnormal": 0, "borderline": 1, "normal": 2}[t.status])
    return trends


def analyze(user: User, results: list[LabResult]) -> tuple[list[Finding], list[MarkerTrend]]:
    trends = build_trends(user, results)
    findings: list[Finding] = []

    for t in trends:
        meta = marker_meta(t.marker)
        label = t.label
        latest = t.points[-1].value

        # 1) Static abnormality on the most recent value.
        if t.status in ("abnormal", "borderline"):
            priority = "high" if t.status == "abnormal" else "preventive"
            findings.append(
                Finding(
                    title=f"{label}: {t.status}",
                    detail=f"Most recent value {latest} {t.unit} is {t.status} for your profile.",
                    priority=priority,
                    source="blood_analyzer",
                    plain_language=_plain_language(t.marker, t.status, label),
                )
            )

        # 2) Longitudinal trend in the risk direction across >= 3 tests.
        higher_is_risk = meta["higher_is_risk"] if meta else True
        worsening = (t.direction == "rising" and higher_is_risk) or (
            t.direction == "falling" and not higher_is_risk
        )
        if len(t.points) >= 3 and worsening:
            findings.append(
                Finding(
                    title=f"{label}: {t.direction} trend over {len(t.points)} tests",
                    detail=(
                        f"{label} has been {t.direction} across your last "
                        f"{len(t.points)} results — a longitudinal pattern worth reviewing."
                    ),
                    priority="high" if t.status != "normal" else "preventive",
                    source="blood_analyzer",
                    plain_language=(
                        f"Over time, your {label.lower()} keeps moving in the wrong "
                        "direction. Trends like this are easy to miss in single visits."
                    ),
                )
            )

    return findings, trends
