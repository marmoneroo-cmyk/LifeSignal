"""Curated drug-interaction knowledge base (education/decision-support only).

A small, widely-documented set of clinically notable interactions and cautions.
NOT exhaustive and NOT a substitute for a pharmacist or physician. A production
build would back this with RxNorm + DrugBank / a licensed interaction API.

Drugs are referenced by canonical lowercase keys. `DRUG_ALIASES` maps free-text
(brand names, Hebrew) to those keys for the PDF/manual intake.
"""
from __future__ import annotations

DRUG_ALIASES: dict[str, list[str]] = {
    "warfarin": ["warfarin", "coumadin", "קומדין", "ורפרין"],
    "aspirin": ["aspirin", "asa", "acetylsalicylic", "אספירין", "אקמולי לא"],
    "ibuprofen": ["ibuprofen", "advil", "nurofen", "איבופרופן", "נורופן"],
    "atorvastatin": ["atorvastatin", "lipitor", "ליפיטור", "אטורבסטטין"],
    "simvastatin": ["simvastatin", "zocor", "סימבסטטין"],
    "metformin": ["metformin", "glucophage", "מטפורמין"],
    "lisinopril": ["lisinopril", "ליסינופריל"],
    "amlodipine": ["amlodipine", "norvasc", "אמלודיפין"],
    "omeprazole": ["omeprazole", "omepradex", "אומפרזול"],
    "clopidogrel": ["clopidogrel", "plavix", "פלביקס"],
    "levothyroxine": ["levothyroxine", "eltroxin", "אלטרוקסין"],
    "ssri": ["ssri", "fluoxetine", "sertraline", "cipralex", "escitalopram", "ציפרלקס"],
    "vitamin_k": ["vitamin k", "ויטמין k"],
    "st_johns_wort": ["st john", "hypericum", "פרע מחורר"],
    "grapefruit": ["grapefruit", "אשכולית"],
    "potassium_supplement": ["potassium supplement", "תוסף אשלגן"],
}

# Each rule: (drug_a, drug_b, severity, note). severity: high | moderate.
INTERACTIONS: list[tuple[str, str, str, str]] = [
    ("warfarin", "aspirin", "high", "Combined blood-thinning sharply raises bleeding risk."),
    ("warfarin", "ibuprofen", "high", "NSAIDs with warfarin increase bleeding risk."),
    ("warfarin", "vitamin_k", "moderate", "Vitamin K can reduce warfarin's effect; keep intake consistent."),
    ("warfarin", "st_johns_wort", "high", "St John's Wort can dangerously reduce warfarin levels."),
    ("clopidogrel", "omeprazole", "moderate", "Omeprazole may reduce clopidogrel effectiveness."),
    ("clopidogrel", "aspirin", "moderate", "Dual antiplatelet therapy increases bleeding risk; often intentional but monitor."),
    ("atorvastatin", "grapefruit", "moderate", "Grapefruit raises statin levels and side-effect risk."),
    ("simvastatin", "grapefruit", "high", "Grapefruit substantially raises simvastatin toxicity risk."),
    ("simvastatin", "atorvastatin", "high", "Two statins together is usually duplicate therapy."),
    ("lisinopril", "potassium_supplement", "high", "ACE inhibitors plus potassium can cause dangerous high potassium."),
    ("lisinopril", "ibuprofen", "moderate", "NSAIDs can reduce ACE-inhibitor effect and stress the kidneys."),
    ("ssri", "aspirin", "moderate", "SSRIs with aspirin modestly increase bleeding risk."),
    ("ssri", "ibuprofen", "moderate", "SSRIs with NSAIDs increase GI bleeding risk."),
    ("levothyroxine", "omeprazole", "moderate", "Stomach-acid reducers can lower levothyroxine absorption."),
]

# Drugs that are duplicate-class if taken together (same therapeutic class).
DUPLICATE_CLASSES: list[set[str]] = [
    {"atorvastatin", "simvastatin"},
    {"ibuprofen", "aspirin"},  # both NSAID/antiplatelet overlap — flag for review
]


def drug_meta_label(key: str) -> str:
    return key.replace("_", " ").title()
