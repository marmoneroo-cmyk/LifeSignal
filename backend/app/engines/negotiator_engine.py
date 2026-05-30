"""AI Insurance Negotiator — risk-adjusted value assessment of coverage.

Goes past "duplicate/missing" to a value judgement: given the user's age, risk
profile (from the health report) and what they hold, where might they be
over-insured or under-insured? Framed as suggestions to review, not advice.
"""
from __future__ import annotations

from app.data.insurance_reference import coverage_meta
from app.models import InsurancePolicy, User
from app.schemas import Finding, HealthReport


def analyze(user: User, policies: list[InsurancePolicy], report: HealthReport) -> list[Finding]:
    findings: list[Finding] = []
    held = {p.coverage_type.lower() for p in policies}
    total = sum(p.monthly_premium for p in policies)

    # Signal: elevated cardiovascular/metabolic risk + no drugs-outside-basket cover.
    high_risk = any(
        f.priority in ("critical", "high") and f.source in ("risk_engine", "correlation_engine")
        for f in report.findings
    )
    if high_risk and "drugs_outside_basket" not in held:
        findings.append(
            Finding(
                title="Consider expanding medication coverage",
                detail="Your risk profile suggests future medication needs; you have no out-of-basket drug cover.",
                priority="preventive",
                source="negotiator_engine",
                plain_language=(
                    "Given your current risk signals, coverage for medications outside the "
                    "public basket could be worth more to you than it is to the average person."
                ),
            )
        )

    # Signal: critical-illness held but user is young and low-risk -> re-evaluate value.
    if "critical_illness" in held and user.age < 35 and not high_risk:
        findings.append(
            Finding(
                title="Re-evaluate critical-illness value",
                detail="At your age with no elevated risk signals, critical-illness cover may be lower-value.",
                priority="informational",
                source="negotiator_engine",
                plain_language=(
                    "This coverage may not be giving you strong value right now — worth comparing "
                    "the premium against the actual benefit for someone your age and risk."
                ),
            )
        )

    # Signal: long-term-care missing past 45.
    if user.age >= 45 and "long_term_care" not in held:
        findings.append(
            Finding(
                title="Long-term care gap",
                detail="From mid-40s onward, long-term-care cover becomes materially more relevant.",
                priority="preventive",
                source="negotiator_engine",
                plain_language=(
                    "Long-term-care premiums rise with age — reviewing this earlier usually costs less."
                ),
            )
        )

    # Signal: spend concentration (already flagged structurally; here as value lens).
    if total > 0 and len(policies) >= 3:
        findings.append(
            Finding(
                title="Review total insurance spend vs. risk",
                detail=f"You hold {len(policies)} policies (~{total:.0f}/month). Align spend with your actual risk profile.",
                priority="informational",
                source="negotiator_engine",
                plain_language=(
                    "It's worth checking that your overall premium matches your real risks — "
                    "not paying for low-value cover while a high-value gap exists."
                ),
            )
        )

    return findings
