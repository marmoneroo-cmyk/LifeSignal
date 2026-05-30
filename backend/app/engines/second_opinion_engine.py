"""Second Opinion Engine.

For high-priority findings, suggests *additional* directions of inquiry a patient
could raise with their doctor — never an alternative diagnosis, always framed as
"questions worth exploring". Supportive, not a replacement for a physician.
"""
from __future__ import annotations

from app.schemas import Finding, HealthReport

# Maps a finding 'source'/keyword to extra avenues to discuss.
_AVENUES: dict[str, list[str]] = {
    "iron": [
        "Ask whether the cause of low iron has been investigated (diet, blood loss, absorption).",
        "Ask if a ferritin + reticulocyte panel would clarify the picture.",
    ],
    "cardiovascular": [
        "Ask whether a coronary risk calculator (e.g. ASCVD) applies to you.",
        "Ask if a one-time lipoprotein(a) test is worthwhile given family history.",
    ],
    "metabolic": [
        "Ask whether a repeat fasting glucose or oral glucose tolerance test is indicated.",
        "Ask about a structured lifestyle program before considering medication.",
    ],
    "liver": [
        "Ask whether a liver ultrasound or a fatty-liver evaluation is appropriate.",
    ],
    "kidney": [
        "Ask whether a urine albumin test should accompany the eGFR.",
    ],
    "thyroid": [
        "Ask whether free T4 / antibodies should be checked alongside TSH.",
    ],
}


def _avenues_for(finding: Finding) -> list[str]:
    blob = (finding.title + " " + finding.detail).lower()
    out: list[str] = []
    for key, items in _AVENUES.items():
        if key in blob:
            out.extend(items)
    return out


def analyze(report: HealthReport) -> list[Finding]:
    seen: set[str] = set()
    findings: list[Finding] = []
    for f in report.top_priorities + report.findings:
        for avenue in _avenues_for(f):
            if avenue in seen:
                continue
            seen.add(avenue)
            findings.append(
                Finding(
                    title="Worth exploring with your doctor",
                    detail=avenue,
                    priority="informational",
                    source="second_opinion_engine",
                    plain_language=avenue,
                )
            )
    return findings[:6]
