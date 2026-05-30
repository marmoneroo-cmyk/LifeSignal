"""Insurance Analysis Engine — Risk-Adjusted Insurance Analysis.

Goes beyond "have it / don't have it":
  - duplicate coverage (paying twice for the same thing)
  - missing critical coverage (gaps)
  - age-relevance (paying for coverage that no longer fits your age)
  - cost concentration (an unusually expensive line)
  - upcoming renewals (handed to the notification engine via findings)
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date

from app.data.insurance_reference import (
    ESSENTIAL_COVERAGE,
    coverage_meta,
)
from app.models import InsurancePolicy, User
from app.schemas import Finding

_RENEWAL_WINDOW_DAYS = 45


def analyze(user: User, policies: list[InsurancePolicy]) -> list[Finding]:
    findings: list[Finding] = []
    by_type: dict[str, list[InsurancePolicy]] = defaultdict(list)
    for p in policies:
        by_type[p.coverage_type.lower()].append(p)

    # 1) Duplicate coverage.
    for ctype, items in by_type.items():
        if len(items) > 1:
            meta = coverage_meta(ctype)
            label = meta["label"] if meta else ctype
            providers = ", ".join(sorted({i.provider for i in items}))
            monthly = sum(i.monthly_premium for i in items)
            findings.append(
                Finding(
                    title=f"Duplicate coverage: {label}",
                    detail=(
                        f"You hold {len(items)} overlapping {label} policies "
                        f"({providers}), costing ~{monthly:.0f}/month combined."
                    ),
                    priority="high",
                    source="insurance_analyzer",
                    plain_language=(
                        f"You appear to be paying more than once for {label.lower()}. "
                        "Consolidating could save money with no loss of cover."
                    ),
                )
            )

    # 2) Missing critical coverage.
    held = set(by_type.keys())
    for ctype in ESSENTIAL_COVERAGE:
        if ctype not in held:
            meta = coverage_meta(ctype)
            label = meta["label"] if meta else ctype
            findings.append(
                Finding(
                    title=f"Missing critical coverage: {label}",
                    detail=f"No {label} policy was found in your uploaded coverage.",
                    priority="high",
                    source="insurance_analyzer",
                    plain_language=(
                        f"You don't seem to have {label.lower()}. This is widely "
                        "considered essential — worth reviewing."
                    ),
                )
            )

    # 3) Age-relevance.
    for ctype, items in by_type.items():
        meta = coverage_meta(ctype)
        if not meta:
            continue
        lo, hi = meta["relevant_ages"]
        if user.age < lo or (hi is not None and user.age > hi):
            label = meta["label"]
            findings.append(
                Finding(
                    title=f"Age relevance: {label}",
                    detail=(
                        f"{label} is typically most relevant for ages "
                        f"{lo}-{hi if hi is not None else '∞'}; you are {user.age}."
                    ),
                    priority="informational",
                    source="insurance_analyzer",
                    plain_language=(
                        f"At your age, {label.lower()} may not give you the value it "
                        "once did. Worth re-checking whether it still fits."
                    ),
                )
            )

    # 4) Cost concentration — flag a single line that dominates spend.
    total = sum(p.monthly_premium for p in policies)
    if total > 0:
        for p in policies:
            if p.monthly_premium >= 0.5 * total and len(policies) > 1:
                meta = coverage_meta(p.coverage_type)
                label = meta["label"] if meta else p.coverage_type
                findings.append(
                    Finding(
                        title=f"High-cost line: {label}",
                        detail=(
                            f"{label} ({p.provider}) is ~{p.monthly_premium:.0f}/month, "
                            f"{p.monthly_premium / total * 100:.0f}% of your premium."
                        ),
                        priority="informational",
                        source="insurance_analyzer",
                        plain_language=(
                            "One policy makes up most of your insurance spend — make "
                            "sure it is risk-adjusted and worth it for you."
                        ),
                    )
                )

    # 5) Upcoming renewals.
    today = date.today()
    for p in policies:
        if p.renewal_date is None:
            continue
        days = (p.renewal_date - today).days
        if 0 <= days <= _RENEWAL_WINDOW_DAYS:
            meta = coverage_meta(p.coverage_type)
            label = meta["label"] if meta else p.coverage_type
            findings.append(
                Finding(
                    title=f"Renewal soon: {label}",
                    detail=f"{label} ({p.provider}) renews in {days} days ({p.renewal_date}).",
                    priority="preventive",
                    source="insurance_analyzer",
                    plain_language=(
                        f"Your {label.lower()} renews soon — a good moment to review "
                        "whether it still matches your needs."
                    ),
                )
            )

    return findings
