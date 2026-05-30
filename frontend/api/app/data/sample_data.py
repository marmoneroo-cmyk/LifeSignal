"""Sample-data seeder for an EXISTING profile.

Loads realistic demo health data (labs trending over 3 years, insurance with a
duplicate, medications with a flagged interaction, family history) into a target
profile so a new user can explore the full app instantly.

Separate from app/data/seed.py — that creates the initial demo *account*. This
populates ANY logged-in profile on demand from the onboarding flow.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models import FamilyMember, InsurancePolicy, LabResult, Medication, User


def populate(db: Session, user: User) -> dict:
    """Add sample data to the given user. Skips categories already populated."""
    added = {"labs": 0, "policies": 0, "medications": 0, "family": 0}

    # Labs — 3-year trend showing rising LDL + worsening A1c
    if not user.lab_results:
        labs = [
            ("ldl", 118, "mg/dL", date(2023, 2, 1)),
            ("ldl", 138, "mg/dL", date(2024, 2, 1)),
            ("ldl", 162, "mg/dL", date(2025, 2, 1)),
            ("hba1c", 5.4, "%", date(2023, 2, 1)),
            ("hba1c", 5.7, "%", date(2024, 2, 1)),
            ("hba1c", 5.9, "%", date(2025, 2, 1)),
            ("triglycerides", 180, "mg/dL", date(2025, 2, 1)),
            ("crp", 4.2, "mg/L", date(2025, 2, 1)),
            ("systolic_bp", 132, "mmHg", date(2025, 2, 1)),
            ("hemoglobin", 15.1, "g/dL", date(2025, 2, 1)),
            ("vitamin_d", 22, "ng/mL", date(2025, 2, 1)),
            ("hdl", 42, "mg/dL", date(2025, 2, 1)),
        ]
        for marker, value, unit, taken in labs:
            db.add(LabResult(user_id=user.id, marker=marker, value=value, unit=unit, taken_on=taken))
        added["labs"] = len(labs)

    # Policies — duplicate basic health, missing disability + drug cover
    if not user.policies:
        policies = [
            ("פוליסה א", "health_basic", 90, date(2026, 6, 20)),
            ("פוליסה ב", "health_basic", 75, None),
            ("פוליסה א", "critical_illness", 40, None),
            ("דנט-קר", "dental", 25, None),
        ]
        for provider, ctype, premium, renewal in policies:
            db.add(InsurancePolicy(
                user_id=user.id, provider=provider, coverage_type=ctype,
                monthly_premium=premium, renewal_date=renewal,
            ))
        added["policies"] = len(policies)

    # Medications — triggers two interactions
    if not user.medications:
        meds = [("clopidogrel", "75 mg"), ("aspirin", "100 mg"), ("omeprazole", "20 mg")]
        for name, dose in meds:
            db.add(Medication(user_id=user.id, name=name, dose=dose))
        added["medications"] = len(meds)

    # Family history — triggers earlier screenings
    if not user.family_members:
        family = [
            ("father", "heart_disease"),
            ("grandparent", "colon_cancer"),
        ]
        for relation, conditions in family:
            db.add(FamilyMember(user_id=user.id, relation=relation, conditions=conditions))
        added["family"] = len(family)

    db.commit()
    return added
