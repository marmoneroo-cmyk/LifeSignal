"""Claim Eligibility Engine.

Given the user's coverage and recommended/likely medical activities, surfaces
reimbursements they may be entitled to claim. Conservative ("you may be eligible
— check your policy terms"), never a guarantee.
"""
from __future__ import annotations

from app.data.insurance_reference import coverage_meta
from app.models import InsurancePolicy, User
from app.schemas import Finding, HealthReport

# coverage_type -> (claimable activity description)
_CLAIMABLE: dict[str, str] = {
    "surgery": "private specialist consultations and elective procedures",
    "drugs_outside_basket": "medications prescribed outside the public basket",
    "dental": "dental treatments and cleanings",
    "health_basic": "ambulatory visits, imaging and tests within the plan",
    "travel": "medical expenses incurred while traveling",
}


def analyze(user: User, policies: list[InsurancePolicy], report: HealthReport) -> list[Finding]:
    findings: list[Finding] = []
    held = {p.coverage_type.lower(): p for p in policies}

    # If a recommended screening maps to a coverage the user holds, flag a possible claim.
    recommended_keywords = " ".join(s.title.lower() for s in report.missing_screenings)
    if held.get("surgery") and ("colorectal" in recommended_keywords or "skin" in recommended_keywords):
        findings.append(
            Finding(
                title="Possible claim: specialist / procedure cover",
                detail="A recommended screening may be claimable under your private surgery/specialist cover.",
                priority="informational",
                source="claim_engine",
                plain_language=(
                    "If you go ahead with a recommended specialist test, you may be able to claim it — "
                    "check the terms and keep receipts."
                ),
            )
        )

    # Medications + out-of-basket cover -> possible drug claim.
    if held.get("drugs_outside_basket") and report.drug_interactions is not None:
        findings.append(
            Finding(
                title="Possible claim: out-of-basket medications",
                detail="You hold cover for medications outside the public basket.",
                priority="informational",
                source="claim_engine",
                plain_language=(
                    "If a doctor prescribes a medication outside the public basket, your policy "
                    "may reimburse part of the cost — worth confirming before you pay out of pocket."
                ),
            )
        )

    # Generic: list what each held policy may let them claim.
    for ctype, policy in held.items():
        activity = _CLAIMABLE.get(ctype)
        if not activity:
            continue
        meta = coverage_meta(ctype)
        label = meta["label"] if meta else ctype
        findings.append(
            Finding(
                title=f"Claimable under {label}",
                detail=f"This policy may reimburse: {activity}.",
                priority="informational",
                source="claim_engine",
                plain_language=f"Your {label.lower()} may cover {activity} — check terms before paying.",
            )
        )

    return findings
