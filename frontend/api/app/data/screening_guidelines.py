"""Preventive screening guidelines (USPSTF-style, education/decision-support only).

Each guideline is matched against a user profile. These are simplified, widely
cited adult preventive recommendations and are NOT individualized medical advice.

Fields:
  key            stable id
  label          what the screening is
  sex            "male" | "female" | "any"
  min_age        recommended start age
  max_age        recommended stop age (None = no upper bound here)
  interval_years cadence; 0 = one-off / situational
  priority       default priority bucket if it is due/overdue
  triggers       optional list of family-history / lifestyle tags that, if present,
                 make the screening relevant earlier or regardless of age
  why            plain-language reason
"""
from __future__ import annotations

# Region-specific overrides of the default (intl/USPSTF-style) start ages.
# region -> { screening_key: {field: value} }. Applied on top of the base guideline.
REGIONS = ["intl", "il", "us", "eu"]
REGION_LABELS = {"intl": "International", "il": "Israel (MoH)", "us": "USPSTF (US)", "eu": "European"}

REGION_OVERRIDES: dict[str, dict[str, dict]] = {
    "il": {
        # Israeli MoH program: routine mammography from 50 (earlier with risk).
        "mammogram": {"min_age": 50, "interval_years": 2},
        "colonoscopy": {"min_age": 50},
    },
    "us": {
        "mammogram": {"min_age": 40},
        "colonoscopy": {"min_age": 45},
    },
    "eu": {
        "mammogram": {"min_age": 50},
        "cervical": {"interval_years": 5},
    },
}


def guidelines_for(region: str) -> list[dict]:
    """Return guidelines with region overrides applied."""
    region = region if region in REGIONS else "intl"
    overrides = REGION_OVERRIDES.get(region, {})
    out: list[dict] = []
    for g in SCREENING_GUIDELINES:
        merged = {**g, **overrides.get(g["key"], {})}
        out.append(merged)
    return out


SCREENING_GUIDELINES: list[dict] = [
    {
        "key": "colonoscopy",
        "label": "Colorectal cancer screening (colonoscopy / FIT)",
        "sex": "any",
        "min_age": 45,
        "max_age": 75,
        "interval_years": 10,
        "priority": "preventive",
        "triggers": ["colon_cancer"],
        "why": "Colorectal cancer is highly treatable when found early through routine screening.",
    },
    {
        "key": "mammogram",
        "label": "Breast cancer screening (mammogram)",
        "sex": "female",
        "min_age": 40,
        "max_age": 74,
        "interval_years": 2,
        "priority": "preventive",
        "triggers": ["breast_cancer"],
        "why": "Regular mammograms help detect breast cancer before symptoms appear.",
    },
    {
        "key": "brca",
        "label": "BRCA genetic risk evaluation",
        "sex": "female",
        "min_age": 18,
        "max_age": None,
        "interval_years": 0,
        "priority": "preventive",
        "triggers": ["breast_cancer", "ovarian_cancer"],
        "why": "A family history of breast/ovarian cancer can justify genetic counseling.",
    },
    {
        "key": "cervical",
        "label": "Cervical cancer screening (Pap / HPV)",
        "sex": "female",
        "min_age": 21,
        "max_age": 65,
        "interval_years": 3,
        "priority": "preventive",
        "triggers": [],
        "why": "HPV/Pap testing detects pre-cancerous cervical changes early.",
    },
    {
        "key": "psa",
        "label": "Prostate screening discussion (PSA)",
        "sex": "male",
        "min_age": 50,
        "max_age": 70,
        "interval_years": 2,
        "priority": "preventive",
        "triggers": ["prostate_cancer"],
        "why": "Discuss PSA testing with a clinician to weigh benefits and risks.",
    },
    {
        "key": "lipid_panel",
        "label": "Cholesterol / lipid panel",
        "sex": "any",
        "min_age": 35,
        "max_age": None,
        "interval_years": 5,
        "priority": "preventive",
        "triggers": ["heart_disease"],
        "why": "Lipid screening identifies cardiovascular risk that is treatable.",
    },
    {
        "key": "diabetes",
        "label": "Diabetes screening (HbA1c / fasting glucose)",
        "sex": "any",
        "min_age": 35,
        "max_age": 70,
        "interval_years": 3,
        "priority": "preventive",
        "triggers": ["diabetes"],
        "why": "Early detection of high blood sugar prevents long-term complications.",
    },
    {
        "key": "bp_check",
        "label": "Blood pressure check",
        "sex": "any",
        "min_age": 18,
        "max_age": None,
        "interval_years": 1,
        "priority": "preventive",
        "triggers": ["hypertension", "heart_disease"],
        "why": "High blood pressure is common, silent, and treatable.",
    },
    {
        "key": "skin_check",
        "label": "Skin / mole examination",
        "sex": "any",
        "min_age": 18,
        "max_age": None,
        "interval_years": 2,
        "priority": "preventive",
        "triggers": ["melanoma", "skin_cancer"],
        "why": "Periodic skin checks help catch suspicious lesions early.",
    },
    {
        "key": "aaa",
        "label": "Abdominal aortic aneurysm ultrasound",
        "sex": "male",
        "min_age": 65,
        "max_age": 75,
        "interval_years": 0,
        "priority": "preventive",
        "triggers": [],
        "why": "One-time ultrasound is recommended for men 65-75 who have ever smoked.",
    },
]
