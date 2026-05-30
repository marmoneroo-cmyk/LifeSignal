"""Shared fixtures: an in-memory demo user exercising every engine."""
from __future__ import annotations

from datetime import date

import pytest

from app.models import FamilyMember, InsurancePolicy, LabResult, Medication, User


@pytest.fixture
def demo_user() -> User:
    user = User(
        id=1,
        name="Test User",
        sex="male",
        birth_date=date(1983, 4, 12),
        smoker=False,
        family_history="heart_disease",
    )
    user.lab_results = [
        LabResult(marker="ldl", value=118, unit="mg/dL", taken_on=date(2022, 2, 1)),
        LabResult(marker="ldl", value=138, unit="mg/dL", taken_on=date(2023, 2, 1)),
        LabResult(marker="ldl", value=162, unit="mg/dL", taken_on=date(2024, 2, 1)),
        LabResult(marker="hba1c", value=5.9, unit="%", taken_on=date(2024, 2, 1)),
        LabResult(marker="potassium", value=6.4, unit="mmol/L", taken_on=date(2024, 2, 1)),
        LabResult(marker="hemoglobin", value=11.5, unit="g/dL", taken_on=date(2024, 2, 1)),
        LabResult(marker="mcv", value=74, unit="fL", taken_on=date(2024, 2, 1)),
        LabResult(marker="ferritin", value=12, unit="ng/mL", taken_on=date(2024, 2, 1)),
    ]
    user.policies = [
        InsurancePolicy(provider="A", coverage_type="health_basic", monthly_premium=90),
        InsurancePolicy(provider="B", coverage_type="health_basic", monthly_premium=75),
    ]
    user.medications = [
        Medication(name="warfarin", dose="5mg"),
        Medication(name="aspirin", dose="100mg"),
    ]
    user.family_members = [
        FamilyMember(relation="father", conditions="heart_disease"),
    ]
    return user
