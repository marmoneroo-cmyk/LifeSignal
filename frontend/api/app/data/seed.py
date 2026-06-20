"""Seed a demo profile so the dashboard is meaningful on first run.

Run:  python -m app.data.seed
Creates the doc's example case: a 42-year-old man with a rising LDL trend, high
BMI-adjacent metabolic markers, a family history of heart disease, plus a couple
of insurance policies including a duplicate — so every engine has something to say.
"""
from __future__ import annotations

from datetime import date

from app.auth import hash_password
from app.db import Base, SessionLocal, engine
from app.models import FamilyMember, InsurancePolicy, LabResult, Medication, User


def run() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.name == "Demo User").first()
        if existing:
            print(f"Demo user already exists (id={existing.id}).")
            return

        # No email/password — this profile is purely seed data for the engines;
        # real users register via the UI.
        user = User(
            name="Demo User",
            sex="male",
            birth_date=date(1983, 4, 12),  # ~42
            smoker=False,
            family_history="heart_disease,colon_cancer",
            region="il",
        )
        db.add(user)
        db.flush()

        # Rising LDL over 3 years (the longitudinal-trend showcase).
        labs = [
            ("ldl", 118, date(2022, 2, 1)),
            ("ldl", 138, date(2023, 2, 1)),
            ("ldl", 162, date(2024, 2, 1)),
            ("hba1c", 5.6, date(2023, 2, 1)),
            ("hba1c", 5.9, date(2024, 2, 1)),
            ("triglycerides", 180, date(2024, 2, 1)),
            ("crp", 4.2, date(2024, 2, 1)),
            ("systolic_bp", 132, date(2024, 2, 1)),
            ("hemoglobin", 15.1, date(2024, 2, 1)),
            ("vitamin_d", 22, date(2024, 2, 1)),
        ]
        for marker, value, taken in labs:
            db.add(LabResult(user_id=user.id, marker=marker, value=value, taken_on=taken))

        # Two basic-health policies = duplicate; missing disability + drugs cover.
        policies = [
            ("Provider A", "health_basic", 90, date(2026, 6, 20)),
            ("Provider B", "health_basic", 75, None),
            ("Provider A", "critical_illness", 40, None),
            ("Provider C", "dental", 25, None),
        ]
        for provider, ctype, premium, renewal in policies:
            db.add(
                InsurancePolicy(
                    user_id=user.id,
                    provider=provider,
                    coverage_type=ctype,
                    monthly_premium=premium,
                    renewal_date=renewal,
                )
            )

        # Medications: clopidogrel + omeprazole (moderate) and + aspirin (moderate).
        meds = [("clopidogrel", "75 mg"), ("aspirin", "100 mg"), ("omeprazole", "20 mg")]
        for name, dose in meds:
            db.add(Medication(user_id=user.id, name=name, dose=dose))

        # Family graph: first-degree heart disease, second-degree colon cancer.
        family = [
            ("father", "heart_disease"),
            ("grandparent", "colon_cancer"),
        ]
        for relation, conditions in family:
            db.add(FamilyMember(user_id=user.id, relation=relation, conditions=conditions))

        db.commit()
        print(
            f"Seeded demo user id={user.id}: {len(labs)} labs, {len(policies)} policies, "
            f"{len(meds)} medications, {len(family)} family members."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
