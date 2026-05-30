"""Unit normalization for lab markers.

Labs report the same marker in different units (mg/dL vs mmol/L). We normalize
everything to the canonical unit declared in lab_reference before analysis, so
trends and reference comparisons are always apples-to-apples.

Each conversion maps (marker, from_unit) -> factor to multiply by to reach the
canonical unit. Units are compared case-insensitively and whitespace-stripped.
"""
from __future__ import annotations

# marker -> { from_unit(lower): multiply_factor_to_canonical }
CONVERSIONS: dict[str, dict[str, float]] = {
    # mmol/L -> mg/dL
    "glucose_fasting": {"mmol/l": 18.0},
    "ldl": {"mmol/l": 38.67},
    "hdl": {"mmol/l": 38.67},
    "triglycerides": {"mmol/l": 88.57},
    "cholesterol_total": {"mmol/l": 38.67},
    # µmol/L -> mg/dL
    "creatinine": {"umol/l": 0.0113, "µmol/l": 0.0113},
    # g/L -> g/dL
    "hemoglobin": {"g/l": 0.1},
    # pmol/L -> pg/mL (B12)
    "b12": {"pmol/l": 1.355},
}


def _norm(unit: str) -> str:
    return unit.strip().lower().replace(" ", "")


def normalize(marker: str, value: float, unit: str) -> tuple[float, str | None]:
    """Return (canonical_value, applied_from_unit_or_None).

    If no conversion is needed/known, the value is returned unchanged.
    """
    marker = marker.lower()
    table = CONVERSIONS.get(marker)
    if not table or not unit:
        return value, None
    u = _norm(unit)
    # Compare against normalized keys.
    for from_unit, factor in table.items():
        if _norm(from_unit) == u:
            return value * factor, from_unit
    return value, None
