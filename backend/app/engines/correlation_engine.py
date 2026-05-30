"""Lab Cross-Correlation Engine.

Single markers in isolation miss patterns. This engine looks at combinations of
the latest values to surface recognizable clinical *patterns* (still framed as
"worth a closer look", never a diagnosis).
"""
from __future__ import annotations

from app.models import LabResult, User
from app.schemas import Finding


def _latest(results: list[LabResult]) -> dict[str, float]:
    out: dict[str, tuple] = {}
    for r in results:
        k = r.marker.lower()
        if k not in out or r.taken_on > out[k][0]:
            out[k] = (r.taken_on, r.value)
    return {k: v for k, (_, v) in out.items()}


def analyze(user: User, results: list[LabResult]) -> list[Finding]:
    v = _latest(results)
    findings: list[Finding] = []

    def has(m: str) -> bool:
        return m in v

    # Iron-deficiency anemia pattern: low hemoglobin + low MCV + low ferritin.
    low_hgb = has("hemoglobin") and v["hemoglobin"] < (13.5 if user.sex == "male" else 12.0)
    low_mcv = has("mcv") and v["mcv"] < 80
    low_ferritin = has("ferritin") and v["ferritin"] < (30 if user.sex == "male" else 15)
    if low_hgb and (low_mcv or low_ferritin):
        findings.append(
            Finding(
                title="Pattern: possible iron-deficiency anemia",
                detail="Low hemoglobin together with low MCV/ferritin is a recognizable pattern.",
                priority="high",
                source="correlation_engine",
                plain_language=(
                    "Several blood markers point to low iron together — this combination is "
                    "worth raising with a doctor, as it has treatable causes."
                ),
            )
        )

    # Prediabetes / metabolic pattern: borderline HbA1c + high triglycerides + high fasting glucose.
    pre_a1c = has("hba1c") and v["hba1c"] >= 5.7
    high_trig = has("triglycerides") and v["triglycerides"] >= 150
    high_glu = has("glucose_fasting") and v["glucose_fasting"] >= 100
    if pre_a1c and (high_trig or high_glu):
        findings.append(
            Finding(
                title="Pattern: metabolic / prediabetes signals",
                detail="Raised HbA1c with high triglycerides/glucose is a metabolic-risk cluster.",
                priority="high",
                source="correlation_engine",
                plain_language=(
                    "A few markers related to blood sugar and fats are raised together. "
                    "Lifestyle changes are often very effective at this stage — worth discussing."
                ),
            )
        )

    # Liver-stress pattern: ALT + AST + GGT elevated.
    elevated = sum(
        1
        for m, hi in (("alt", 56), ("ast", 48), ("ggt", 61))
        if has(m) and v[m] > hi
    )
    if elevated >= 2:
        findings.append(
            Finding(
                title="Pattern: liver enzymes elevated together",
                detail="Two or more liver enzymes above range together suggests reviewing liver health.",
                priority="preventive",
                source="correlation_engine",
                plain_language="A few liver-related values are raised together — worth a follow-up check.",
            )
        )

    # Kidney pattern: high creatinine + low eGFR.
    if has("creatinine") and has("egfr") and v["egfr"] < 60:
        findings.append(
            Finding(
                title="Pattern: reduced kidney function",
                detail="Low eGFR with raised creatinine warrants kidney-function follow-up.",
                priority="high",
                source="correlation_engine",
                plain_language="Kidney-function markers suggest a follow-up with your doctor is sensible.",
            )
        )

    return findings
