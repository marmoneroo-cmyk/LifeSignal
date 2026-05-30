"""Emergency Detection Engine.

Flags values in a danger zone that warrant prompt medical attention. It NEVER
names a diagnosis (no "heart attack") — it says "seek prompt medical evaluation".
These thresholds are deliberately conservative red-lines, not diagnostic cutoffs.
"""
from __future__ import annotations

from app.models import LabResult, User
from app.schemas import Finding

# marker -> (comparator, threshold, message). comparator: ">" or "<".
_RED_LINES: dict[str, tuple[str, float, str]] = {
    "systolic_bp": (">", 180, "Very high systolic blood pressure"),
    "diastolic_bp": (">", 120, "Very high diastolic blood pressure"),
    "glucose_fasting": (">", 300, "Very high blood glucose"),
    "potassium": (">", 6.0, "Very high potassium"),
    "sodium": ("<", 125, "Very low sodium"),
    "hemoglobin": ("<", 7.0, "Very low hemoglobin"),
    "egfr": ("<", 30, "Very low kidney function (eGFR)"),
    "platelets": ("<", 50, "Very low platelets"),
}


def _latest(results: list[LabResult]) -> dict[str, float]:
    out: dict[str, tuple] = {}
    for r in results:
        k = r.marker.lower()
        if k not in out or r.taken_on > out[k][0]:
            out[k] = (r.taken_on, r.value)
    return {k: val for k, (_, val) in out.items()}


def analyze(user: User, results: list[LabResult]) -> list[Finding]:
    v = _latest(results)
    findings: list[Finding] = []

    for marker, (cmp, threshold, label) in _RED_LINES.items():
        if marker not in v:
            continue
        value = v[marker]
        breached = (cmp == ">" and value > threshold) or (cmp == "<" and value < threshold)
        if not breached:
            continue
        findings.append(
            Finding(
                title=f"Urgent: {label}",
                detail=f"{label} ({value}). This value is in a range that warrants prompt evaluation.",
                priority="critical",
                source="emergency_engine",
                plain_language=(
                    "One of your readings is in a range that we recommend having checked "
                    "promptly by a medical professional. If you feel unwell, seek urgent care."
                ),
            )
        )

    return findings
