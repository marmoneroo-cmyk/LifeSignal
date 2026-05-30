"""Reference ranges and metadata for common lab markers.

Ranges are widely-used adult reference intervals for education/decision-support
only. They are intentionally conservative and are NOT a diagnosis. Where a marker
is sex-specific, ranges are split by sex.

Each entry:
  label          human-readable name
  unit           expected unit
  normal         (low, high) normal interval
  borderline     optional (low, high) "watch" band just outside normal; an
                 abnormal-direction value inside this band is flagged "borderline"
  higher_is_risk True if rising values indicate increasing risk (e.g. LDL),
                 False if falling values are the concern (e.g. hemoglobin)
  domain         which Health-Score domain this marker feeds
"""
from __future__ import annotations

# sex key "*" means the same range applies to both sexes.
LAB_REFERENCE: dict[str, dict] = {
    "ldl": {
        "label": "LDL cholesterol",
        "unit": "mg/dL",
        "normal": {"*": (0, 100)},
        "borderline": {"*": (100, 130)},
        "higher_is_risk": True,
        "domain": "cardiovascular",
    },
    "hdl": {
        "label": "HDL cholesterol",
        "unit": "mg/dL",
        "normal": {"male": (40, 200), "female": (50, 200)},
        "higher_is_risk": False,
        "domain": "cardiovascular",
    },
    "triglycerides": {
        "label": "Triglycerides",
        "unit": "mg/dL",
        "normal": {"*": (0, 150)},
        "borderline": {"*": (150, 200)},
        "higher_is_risk": True,
        "domain": "metabolism",
    },
    "glucose_fasting": {
        "label": "Fasting glucose",
        "unit": "mg/dL",
        "normal": {"*": (70, 100)},
        "borderline": {"*": (100, 126)},
        "higher_is_risk": True,
        "domain": "metabolism",
    },
    "hba1c": {
        "label": "HbA1c",
        "unit": "%",
        "normal": {"*": (4.0, 5.7)},
        "borderline": {"*": (5.7, 6.5)},
        "higher_is_risk": True,
        "domain": "metabolism",
    },
    "hemoglobin": {
        "label": "Hemoglobin",
        "unit": "g/dL",
        "normal": {"male": (13.5, 17.5), "female": (12.0, 15.5)},
        "higher_is_risk": False,
        "domain": "blood",
    },
    "ferritin": {
        "label": "Ferritin (iron stores)",
        "unit": "ng/mL",
        "normal": {"male": (30, 400), "female": (15, 200)},
        "higher_is_risk": False,
        "domain": "blood",
    },
    "tsh": {
        "label": "TSH (thyroid)",
        "unit": "mIU/L",
        "normal": {"*": (0.4, 4.0)},
        "higher_is_risk": True,
        "domain": "metabolism",
    },
    "creatinine": {
        "label": "Creatinine (kidney)",
        "unit": "mg/dL",
        "normal": {"male": (0.7, 1.3), "female": (0.6, 1.1)},
        "higher_is_risk": True,
        "domain": "kidney",
    },
    "alt": {
        "label": "ALT (liver)",
        "unit": "U/L",
        "normal": {"*": (7, 56)},
        "higher_is_risk": True,
        "domain": "liver",
    },
    "crp": {
        "label": "CRP (inflammation)",
        "unit": "mg/L",
        "normal": {"*": (0, 3.0)},
        "borderline": {"*": (3.0, 10.0)},
        "higher_is_risk": True,
        "domain": "cardiovascular",
    },
    "vitamin_d": {
        "label": "Vitamin D (25-OH)",
        "unit": "ng/mL",
        "normal": {"*": (30, 100)},
        "higher_is_risk": False,
        "domain": "lifestyle",
    },
    "psa": {
        "label": "PSA (prostate)",
        "unit": "ng/mL",
        "normal": {"male": (0, 4.0)},
        "higher_is_risk": True,
        "domain": "cancer_risk",
    },
    "systolic_bp": {
        "label": "Systolic blood pressure",
        "unit": "mmHg",
        "normal": {"*": (90, 120)},
        "borderline": {"*": (120, 140)},
        "higher_is_risk": True,
        "domain": "cardiovascular",
    },
    "diastolic_bp": {
        "label": "Diastolic blood pressure",
        "unit": "mmHg",
        "normal": {"*": (60, 80)},
        "borderline": {"*": (80, 90)},
        "higher_is_risk": True,
        "domain": "cardiovascular",
    },
    "cholesterol_total": {
        "label": "Total cholesterol",
        "unit": "mg/dL",
        "normal": {"*": (0, 200)},
        "borderline": {"*": (200, 240)},
        "higher_is_risk": True,
        "domain": "cardiovascular",
    },
    "mcv": {
        "label": "MCV (red cell size)",
        "unit": "fL",
        "normal": {"*": (80, 100)},
        "higher_is_risk": True,
        "domain": "blood",
    },
    "mch": {
        "label": "MCH",
        "unit": "pg",
        "normal": {"*": (27, 33)},
        "higher_is_risk": True,
        "domain": "blood",
    },
    "wbc": {
        "label": "White blood cells",
        "unit": "10^3/µL",
        "normal": {"*": (4.0, 11.0)},
        "higher_is_risk": True,
        "domain": "blood",
    },
    "platelets": {
        "label": "Platelets",
        "unit": "10^3/µL",
        "normal": {"*": (150, 400)},
        "higher_is_risk": False,
        "domain": "blood",
    },
    "b12": {
        "label": "Vitamin B12",
        "unit": "pg/mL",
        "normal": {"*": (200, 900)},
        "higher_is_risk": False,
        "domain": "blood",
    },
    "folate": {
        "label": "Folate",
        "unit": "ng/mL",
        "normal": {"*": (3.0, 20.0)},
        "higher_is_risk": False,
        "domain": "blood",
    },
    "iron": {
        "label": "Serum iron",
        "unit": "µg/dL",
        "normal": {"male": (65, 175), "female": (50, 170)},
        "higher_is_risk": False,
        "domain": "blood",
    },
    "ast": {
        "label": "AST (liver)",
        "unit": "U/L",
        "normal": {"*": (8, 48)},
        "higher_is_risk": True,
        "domain": "liver",
    },
    "ggt": {
        "label": "GGT (liver)",
        "unit": "U/L",
        "normal": {"male": (8, 61), "female": (5, 36)},
        "higher_is_risk": True,
        "domain": "liver",
    },
    "bilirubin": {
        "label": "Total bilirubin",
        "unit": "mg/dL",
        "normal": {"*": (0.1, 1.2)},
        "higher_is_risk": True,
        "domain": "liver",
    },
    "albumin": {
        "label": "Albumin",
        "unit": "g/dL",
        "normal": {"*": (3.5, 5.0)},
        "higher_is_risk": False,
        "domain": "liver",
    },
    "egfr": {
        "label": "eGFR (kidney function)",
        "unit": "mL/min/1.73m²",
        "normal": {"*": (90, 200)},
        "borderline": {"*": (60, 90)},
        "higher_is_risk": False,
        "domain": "kidney",
    },
    "uric_acid": {
        "label": "Uric acid",
        "unit": "mg/dL",
        "normal": {"male": (3.4, 7.0), "female": (2.4, 6.0)},
        "higher_is_risk": True,
        "domain": "metabolism",
    },
    "sodium": {
        "label": "Sodium",
        "unit": "mmol/L",
        "normal": {"*": (135, 145)},
        "higher_is_risk": True,
        "domain": "kidney",
    },
    "potassium": {
        "label": "Potassium",
        "unit": "mmol/L",
        "normal": {"*": (3.5, 5.1)},
        "higher_is_risk": True,
        "domain": "kidney",
    },
    "calcium": {
        "label": "Calcium",
        "unit": "mg/dL",
        "normal": {"*": (8.5, 10.5)},
        "higher_is_risk": True,
        "domain": "metabolism",
    },
}


def marker_meta(marker: str) -> dict | None:
    return LAB_REFERENCE.get(marker.lower())


def normal_range(marker: str, sex: str) -> tuple[float, float] | None:
    meta = marker_meta(marker)
    if not meta:
        return None
    ranges = meta["normal"]
    return ranges.get(sex) or ranges.get("*")


def borderline_range(marker: str, sex: str) -> tuple[float, float] | None:
    meta = marker_meta(marker)
    if not meta or "borderline" not in meta:
        return None
    ranges = meta["borderline"]
    return ranges.get(sex) or ranges.get("*")
