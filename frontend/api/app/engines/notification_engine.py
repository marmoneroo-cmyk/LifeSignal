"""Notification Engine — turns findings into a non-spammy reminder feed.

Only surfaces things that are actionable now: renewals, worsening trends, and
overdue/critical items. Pure informational items are not pushed as notifications.
"""
from __future__ import annotations

from app.schemas import Finding


def build(all_findings: list[Finding]) -> list[Finding]:
    notifications: list[Finding] = []
    for f in all_findings:
        is_renewal = "Renewal soon" in f.title
        is_trend = "trend" in f.title.lower()
        is_urgent = f.priority in ("critical", "high")
        if is_renewal or is_trend or is_urgent:
            notifications.append(f)
    return notifications
