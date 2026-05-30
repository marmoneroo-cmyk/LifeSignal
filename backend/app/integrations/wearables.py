"""Wearable / health-platform connectors (Apple Health, Google Fit).

Continuous data (heart rate, sleep, steps, SpO2, BP) is the product's long-term
moat. These require OAuth apps and user consent, so they are interface-only here.

Status: NOT ACTIVE — requires OAuth client credentials.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass
class WearableSample:
    metric: str  # "resting_hr" | "sleep_hours" | "steps" | "spo2" | "systolic_bp"
    value: float
    taken_on: date


class WearableConnector(Protocol):
    def fetch(self, since: date) -> list[WearableSample]:
        """Pull samples since a date for the authenticated user."""
        ...


class AppleHealthConnector:
    """Apple Health ingests via a HealthKit export (XML) or an iOS companion app.

    To implement: accept an exported `export.xml`, parse <Record> elements, and
    map HKQuantityTypeIdentifier* to WearableSample.metric values.
    """

    def fetch(self, since: date) -> list[WearableSample]:  # noqa: ARG002
        raise NotImplementedError(
            "Apple Health connector requires a HealthKit export or companion app. "
            "Not configured."
        )


class GoogleFitConnector:
    """Google Fit via the Fitness REST API (OAuth 2.0).

    To implement: set GOOGLE_FIT_CLIENT_ID/SECRET, complete OAuth, call
    users.dataset.aggregate, map data types to WearableSample.
    """

    def fetch(self, since: date) -> list[WearableSample]:  # noqa: ARG002
        raise NotImplementedError(
            "Google Fit connector requires OAuth client credentials. Not configured."
        )
