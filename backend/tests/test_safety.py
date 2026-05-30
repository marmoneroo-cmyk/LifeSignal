"""Safety evals — the report must never behave like a diagnostic device.

These guard the product's core legal/clinical promise. If any of these fail, the
build should be considered unsafe to ship.
"""
from __future__ import annotations

from app.config import DISCLAIMER
from app.engines import report_engine

# Phrases that would imply a diagnosis or false certainty. Case-insensitive.
BANNED_PHRASES = [
    "you have cancer",
    "you have diabetes",
    "this is a heart attack",
    "you are having a stroke",
    "diagnosis is",
    "we diagnose",
    "definitely",
    "certainly have",
    "guaranteed",
]


def _all_text(report) -> str:
    parts: list[str] = [report.disclaimer]
    buckets = [
        report.findings,
        report.top_priorities,
        report.emergency_alerts,
        report.drug_interactions,
        report.family_insights,
        report.missing_screenings,
        report.insurance_insights,
        report.coverage_matches,
        report.projections,
        report.second_opinions,
        report.insurance_negotiation,
        report.claim_opportunities,
    ]
    for b in buckets:
        for f in b:
            parts.append(f.title)
            parts.append(f.detail)
            parts.append(f.plain_language)
    return "\n".join(parts).lower()


def test_disclaimer_always_present(demo_user):
    report = report_engine.generate(demo_user)
    assert report.disclaimer == DISCLAIMER
    assert report.disclaimer.strip()


def test_no_diagnostic_language(demo_user):
    text = _all_text(report_engine.generate(demo_user))
    for phrase in BANNED_PHRASES:
        assert phrase not in text, f"Banned diagnostic phrase surfaced: {phrase!r}"


def test_emergency_is_advisory_not_diagnostic(demo_user):
    report = report_engine.generate(demo_user)
    # The danger-zone potassium should trigger a critical, advisory alert.
    assert report.emergency_alerts, "Expected an emergency alert for K=6.4"
    for f in report.emergency_alerts:
        assert f.priority == "critical"
        blob = (f.detail + f.plain_language).lower()
        assert "evaluation" in blob or "urgent" in blob or "promptly" in blob


def test_every_finding_has_valid_priority(demo_user):
    report = report_engine.generate(demo_user)
    valid = {"critical", "high", "preventive", "informational"}
    for f in report.findings:
        assert f.priority in valid


def test_report_is_deterministic(demo_user):
    a = report_engine.generate(demo_user)
    b = report_engine.generate(demo_user)
    assert a.health_score == b.health_score
    assert [f.title for f in a.findings] == [f.title for f in b.findings]
