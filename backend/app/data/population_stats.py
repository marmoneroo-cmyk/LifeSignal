"""Simplified population distributions for percentile comparison.

Approximate adult mean / standard deviation per marker, used only to give the
user a rough "where do I sit vs others" sense. These are illustrative reference
values, not a validated epidemiological model.
"""
from __future__ import annotations

# marker -> (mean, sd)
POPULATION: dict[str, tuple[float, float]] = {
    "ldl": (110, 30),
    "hdl": (52, 14),
    "triglycerides": (120, 60),
    "glucose_fasting": (92, 12),
    "hba1c": (5.4, 0.5),
    "cholesterol_total": (190, 35),
    "systolic_bp": (122, 14),
    "diastolic_bp": (78, 9),
    "bmi": (26, 4.5),
    "uric_acid": (5.2, 1.3),
    "crp": (1.8, 1.6),
    "vitamin_d": (28, 10),
}
