"""Aliases for mapping free-text PDF content to canonical markers / coverage keys.

Used by the PDF parser to recognise lab markers and insurance coverage lines in
both English and Hebrew. Matching is case-insensitive and accent-naive. These are
heuristics for text-layer PDFs — clearly best-effort, always reviewed by the user
before anything is saved.
"""
from __future__ import annotations

# canonical marker key -> list of textual aliases (lowercased) that may appear.
MARKER_ALIASES: dict[str, list[str]] = {
    # --- Lipids ---
    "ldl": ["ldl", "ldl-c", "ldl cholesterol", "כולסטרול ldl", "כולסטרול רע",
            "ליפופרוטאין בצפיפות נמוכה", "low density"],
    "hdl": ["hdl", "hdl-c", "hdl cholesterol", "כולסטרול hdl", "כולסטרול טוב",
            "ליפופרוטאין בצפיפות גבוהה", "high density"],
    "triglycerides": ["triglycerides", "trig", "tg", "טריגליצרידים", "טריגליצרידים"],
    "cholesterol_total": ["total cholesterol", "כולסטרול כללי", "כולסטרול סה״כ",
                          "cholesterol total", "כולסטרול"],
    "glucose_fasting": ["fasting glucose", "glucose", "glu", "גלוקוז", "סוכר בצום",
                        "סוכר", "גלוקוזה"],
    "hba1c": ["hba1c", "hb a1c", "a1c", "המוגלובין מסוכרר", "סוכר ממוצע",
              "hemoglobin a1c", "glycated"],
    "hemoglobin": ["hemoglobin", "hgb", "hb", "המוגלובין", "המוגלובין"],
    "ferritin": ["ferritin", "פריטין", "פריטין (אחסון ברזל)"],
    "iron": ["serum iron", "iron", "ברזל", "ברזל בסרום", "fe"],
    "mcv": ["mcv", "נפח גופיף ממוצע", "mean corpuscular"],
    "wbc": ["wbc", "white blood", "ספירת לויקוציטים", "לויקוציטים", "כדוריות לבנות"],
    "platelets": ["platelets", "plt", "טסיות", "טרומבוציטים"],
    "b12": ["b12", "vitamin b12", "ויטמין b12", "קובלמין", "cobalamin"],
    "folate": ["folate", "folic acid", "חומצה פולית", "פולאט"],
    "tsh": ["tsh", "thyroid stimulating", "בלוטת התריס", "טירוטרופין",
            "ת.ש.ה", "תפקוד בלוטת התריס"],
    "vitamin_d": ["vitamin d", "25-oh", "25 oh", "ויטמין d", "ויטמין די",
                  "25 hydroxyvitamin", "25(oh)d"],
    "creatinine": ["creatinine", "creat", "קריאטינין", "קריאטינין בסרום"],
    "egfr": ["egfr", "gfr", "סינון כליות", "קצב סינון גלומרולרי", "estimated gfr"],
    "uric_acid": ["uric acid", "urate", "חומצה אורית", "אורט"],
    "sodium": ["sodium", "na", "נתרן"],
    "potassium": ["potassium", "k", "אשלגן"],
    "alt": ["alt", "sgpt", "alanine", "אלט", "אלנין אמינוטרנספראז"],
    "ast": ["ast", "sgot", "aspartate", "אסט", "אספרטט אמינוטרנספראז"],
    "ggt": ["ggt", "gamma gt", "גמא גלוטמיל"],
    "bilirubin": ["bilirubin", "bili", "בילירובין"],
    "albumin": ["albumin", "אלבומין"],
    "crp": ["crp", "c-reactive", "חלבון מגיב c", "c reactive protein",
            "חלבון c מגיב"],
    "psa": ["psa", "prostate specific", "פסא", "אנטיגן ספציפי לערמונית"],
    "systolic_bp": ["systolic", "blood pressure", "bp", "לחץ דם סיסטולי", "לחץ דם"],
}

# canonical coverage key -> list of textual aliases (lowercased).
COVERAGE_ALIASES: dict[str, list[str]] = {
    "health_basic": ["ambulatory", "health basic", "basic health", "בריאות בסיסי", "אמבולטורי"],
    "critical_illness": ["critical illness", "מחלות קשות"],
    "disability": ["disability", "loss of working", "אובדן כושר עבודה", "אכ\"ע"],
    "long_term_care": ["long term care", "nursing", "סיעוד", "סיעודי"],
    "drugs_outside_basket": ["outside basket", "medications", "תרופות מחוץ לסל", "תרופות"],
    "surgery": ["surgery", "surgical", "ניתוחים", "ניתוח"],
    "dental": ["dental", "שיניים"],
    "travel": ["travel", "נסיעות לחו\"ל", "ביטוח נסיעות"],
}
