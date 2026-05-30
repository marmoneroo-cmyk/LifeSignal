"""Report Engine — assembles the Executive Health Report from all sub-engines.

Orchestration layer the API calls. Runs every engine, merges findings, folds the
family graph into the screening profile, computes the score, prioritizes, and
attaches the legal disclaimer.
"""
from __future__ import annotations

from app.config import DISCLAIMER
from app.engines import (
    blood_analyzer,
    claim_engine,
    correlation_engine,
    coverage_match,
    drug_engine,
    emergency_engine,
    family_engine,
    insurance_analyzer,
    negotiator_engine,
    notification_engine,
    prioritization,
    risk_engine,
    screening_engine,
    second_opinion_engine,
    stats_engine,
)
from app.models import User
from app.schemas import Finding, HealthReport, Percentile, UserOut


def _user_with_family_history(user: User, family_tags: set[str]) -> User:
    """Non-mutating copy of the user with family tags merged into history."""
    existing = {h.strip().lower() for h in (user.family_history or "").split(",") if h.strip()}
    merged = existing | family_tags
    clone = User(
        name=user.name,
        sex=user.sex,
        birth_date=user.birth_date,
        smoker=user.smoker,
        family_history=",".join(sorted(merged)),
        region=user.region,
    )
    return clone


def generate(user: User) -> HealthReport:
    labs = list(user.lab_results)
    policies = list(user.policies)
    medications = list(user.medications)
    family = list(user.family_members)

    blood_findings, trends = blood_analyzer.analyze(user, labs)
    correlation_findings = correlation_engine.analyze(user, labs)
    emergency_findings = emergency_engine.analyze(user, labs)
    insurance_findings = insurance_analyzer.analyze(user, policies)
    drug_findings = drug_engine.analyze(medications)
    family_findings = family_engine.analyze(user, family)
    projection_findings = stats_engine.projection(labs)
    percentile_rows = [Percentile(**p) for p in stats_engine.percentiles(labs)]

    # Family graph feeds the preventive-screening profile.
    family_tags = family_engine.derived_history_tags(family)
    screening_user = _user_with_family_history(user, family_tags)
    screening_findings = screening_engine.recommend(screening_user, region=user.region or "intl")
    coverage_findings = coverage_match.analyze(screening_findings, policies)

    health_score, components, risk_findings = risk_engine.score(user, labs)

    all_findings: list[Finding] = (
        emergency_findings
        + blood_findings
        + correlation_findings
        + risk_findings
        + drug_findings
        + family_findings
        + insurance_findings
        + screening_findings
        + projection_findings
    )
    ordered = prioritization.sort_findings(all_findings)

    report = HealthReport(
        user=UserOut.model_validate({**user.__dict__, "age": user.age}),
        health_score=health_score,
        score_components=components,
        top_priorities=prioritization.top_priorities(all_findings),
        findings=ordered,
        trends=trends,
        missing_screenings=prioritization.sort_findings(screening_findings),
        insurance_insights=prioritization.sort_findings(insurance_findings),
        notifications=prioritization.sort_findings(notification_engine.build(all_findings)),
        emergency_alerts=emergency_findings,
        drug_interactions=prioritization.sort_findings(drug_findings),
        family_insights=prioritization.sort_findings(family_findings),
        coverage_matches=coverage_findings,
        projections=projection_findings,
        percentiles=percentile_rows,
        disclaimer=DISCLAIMER,
    )

    # Engines that consume the assembled report.
    report.second_opinions = second_opinion_engine.analyze(report)
    report.insurance_negotiation = negotiator_engine.analyze(user, policies, report)
    report.claim_opportunities = claim_engine.analyze(user, policies, report)
    return report
