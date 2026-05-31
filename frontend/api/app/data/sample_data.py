"""Sample-data seeder for an EXISTING profile.

Loads realistic demo health data into a target profile so a new user can explore
the full app instantly. Multiple personas are available — each emphasizes a
different aspect of the engine (rising LDL, prediabetes cluster, pediatric
growth tracking, geriatric polypharmacy).

Separate from `seed.py` (which creates the initial demo *account*). This one
populates ANY logged-in profile via the onboarding flow.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models import FamilyMember, InsurancePolicy, LabResult, Medication, User

# ---- Persona definitions ---------------------------------------------------
# Each persona: labs (marker, value, unit, date), policies, meds, family.

PERSONAS: dict[str, dict] = {
    # Recommended default — exercises most engines.
    "midlife_male": {
        "label_he": "גבר בגיל העמידה (LDL עולה, סיכון לב)",
        "label_en": "Midlife male (rising LDL, cardiac risk)",
        "labs": [
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
        ],
        "policies": [
            ("פוליסה א", "health_basic", 90, date(2026, 6, 20)),
            ("פוליסה ב", "health_basic", 75, None),
            ("פוליסה א", "critical_illness", 40, None),
            ("דנט-קר", "dental", 25, None),
        ],
        "medications": [("clopidogrel", "75 mg"), ("aspirin", "100 mg"), ("omeprazole", "20 mg")],
        "family": [("father", "heart_disease"), ("grandparent", "colon_cancer")],
    },

    # Iron-deficiency anemia pattern + thyroid + low vit D — common in women.
    "young_female": {
        "label_he": "אישה צעירה (אנמיה מחוסר ברזל)",
        "label_en": "Young female (iron-deficiency anemia)",
        "labs": [
            ("hemoglobin", 11.2, "g/dL", date(2025, 2, 1)),
            ("ferritin", 8, "ng/mL", date(2025, 2, 1)),
            ("iron", 32, "µg/dL", date(2025, 2, 1)),
            ("mcv", 74, "fL", date(2025, 2, 1)),
            ("tsh", 4.8, "mIU/L", date(2025, 2, 1)),
            ("vitamin_d", 18, "ng/mL", date(2025, 2, 1)),
            ("b12", 240, "pg/mL", date(2025, 2, 1)),
            ("ldl", 95, "mg/dL", date(2025, 2, 1)),
        ],
        "policies": [
            ("פוליסה ג", "health_basic", 70, None),
            ("פוליסה ג", "drugs_outside_basket", 50, None),
        ],
        "medications": [("levothyroxine", "50 mcg"), ("omeprazole", "20 mg")],
        "family": [("mother", "breast_cancer")],
    },

    # Polypharmacy + reduced kidney function — typical 70+ profile.
    "senior": {
        "label_he": "מבוגר/ת (פוליפרמציה + תפקוד כליות מופחת)",
        "label_en": "Senior (polypharmacy + reduced kidney function)",
        "labs": [
            ("creatinine", 1.6, "mg/dL", date(2025, 2, 1)),
            ("egfr", 48, "mL/min/1.73m²", date(2025, 2, 1)),
            ("potassium", 5.4, "mmol/L", date(2025, 2, 1)),
            ("hba1c", 7.2, "%", date(2025, 2, 1)),
            ("ldl", 145, "mg/dL", date(2025, 2, 1)),
            ("systolic_bp", 152, "mmHg", date(2025, 2, 1)),
            ("hemoglobin", 12.4, "g/dL", date(2025, 2, 1)),
            ("vitamin_d", 20, "ng/mL", date(2025, 2, 1)),
        ],
        "policies": [
            ("פוליסה ד", "health_basic", 110, None),
            ("פוליסה ד", "long_term_care", 180, date(2026, 12, 1)),
            ("פוליסה ה", "drugs_outside_basket", 95, None),
        ],
        "medications": [
            ("warfarin", "5 mg"), ("aspirin", "100 mg"),       # high-severity interaction
            ("lisinopril", "10 mg"), ("metformin", "1000 mg"),
            ("simvastatin", "20 mg"), ("atorvastatin", "20 mg"),  # duplicate class
        ],
        "family": [("sibling", "heart_disease")],
    },

    # Pediatric — light data, mainly for growth/preventive UX demo.
    "child": {
        "label_he": "ילד/ה (מעקב בסיסי)",
        "label_en": "Child (routine pediatric tracking)",
        "labs": [
            ("hemoglobin", 12.8, "g/dL", date(2025, 1, 15)),
            ("ferritin", 25, "ng/mL", date(2025, 1, 15)),
            ("vitamin_d", 28, "ng/mL", date(2025, 1, 15)),
        ],
        "policies": [
            ("פוליסה ו", "health_basic", 35, None),
        ],
        "medications": [],
        "family": [],
    },
}


def populate(db: Session, user: User, persona: str = "midlife_male") -> dict:
    """Add sample data to the given user. Skips categories already populated."""
    profile = PERSONAS.get(persona, PERSONAS["midlife_male"])
    added = {"labs": 0, "policies": 0, "medications": 0, "family": 0}

    if not user.lab_results:
        for marker, value, unit, taken in profile["labs"]:
            db.add(LabResult(user_id=user.id, marker=marker, value=value, unit=unit, taken_on=taken))
        added["labs"] = len(profile["labs"])

    if not user.policies:
        for provider, ctype, premium, renewal in profile["policies"]:
            db.add(InsurancePolicy(
                user_id=user.id, provider=provider, coverage_type=ctype,
                monthly_premium=premium, renewal_date=renewal,
            ))
        added["policies"] = len(profile["policies"])

    if not user.medications:
        for name, dose in profile["medications"]:
            db.add(Medication(user_id=user.id, name=name, dose=dose))
        added["medications"] = len(profile["medications"])

    if not user.family_members:
        for relation, conditions in profile["family"]:
            db.add(FamilyMember(user_id=user.id, relation=relation, conditions=conditions))
        added["family"] = len(profile["family"])

    db.commit()
    return added


def list_personas(lang: str = "he") -> list[dict]:
    """List available personas for the onboarding picker."""
    key = "label_he" if lang == "he" else "label_en"
    return [{"key": k, "label": v[key]} for k, v in PERSONAS.items()]
