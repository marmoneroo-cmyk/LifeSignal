"""Parser for the Apple Health export.zip / export.xml.

Apple's HealthKit lets users export all their data via Health app →
profile → Export All Health Data. The export is a ZIP whose `export.xml`
file contains <Record> elements like:

    <Record type="HKQuantityTypeIdentifierBloodPressureSystolic"
            sourceName="Watch" startDate="2025-01-15 08:13:00 +0200"
            value="125" unit="mmHg"/>

We map a small set of clinically relevant types to our canonical markers.
Latest sample per (marker, day) wins to avoid creating dozens of duplicates.
"""
from __future__ import annotations

import io
import re
import zipfile
from collections import defaultdict
from datetime import date, datetime

from app.data.units import normalize

# HealthKit type → our canonical marker key.
TYPE_MAP: dict[str, str] = {
    "HKQuantityTypeIdentifierBloodPressureSystolic":  "systolic_bp",
    "HKQuantityTypeIdentifierBloodPressureDiastolic": "diastolic_bp",
    "HKQuantityTypeIdentifierBloodGlucose":           "glucose_fasting",
    "HKQuantityTypeIdentifierBodyMassIndex":          "bmi",
    "HKQuantityTypeIdentifierHeartRate":              "resting_hr",
    "HKQuantityTypeIdentifierOxygenSaturation":       "spo2",
}

_RECORD = re.compile(
    r'<Record\s+([^>]+?)/>',
    re.IGNORECASE,
)
_ATTR = re.compile(r'(\w+)="([^"]*)"')


def _attrs(blob: str) -> dict[str, str]:
    return {m.group(1): m.group(2) for m in _ATTR.finditer(blob)}


def _read_xml(data: bytes) -> str:
    """Accept either a raw XML payload or a ZIP that contains export.xml."""
    if data[:2] == b"PK":  # ZIP magic
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            name = next((n for n in zf.namelist() if n.endswith("export.xml")), None)
            if not name:
                raise ValueError("export.xml not found in zip")
            return zf.read(name).decode("utf-8", errors="ignore")
    return data.decode("utf-8", errors="ignore")


def parse(data: bytes, max_records: int = 5000) -> list[dict]:
    """Return up to `max_records` recent samples mapped to our canonical markers.

    De-duplicates to one value per (marker, day) — the most recent timestamp wins.
    """
    text = _read_xml(data)
    seen: dict[tuple[str, date], tuple[datetime, float, str]] = {}

    for n, m in enumerate(_RECORD.finditer(text)):
        if n >= max_records:
            break
        a = _attrs(m.group(1))
        kind = a.get("type", "")
        marker = TYPE_MAP.get(kind)
        if not marker:
            continue
        raw_value = a.get("value")
        if not raw_value:
            continue
        try:
            value = float(raw_value)
        except ValueError:
            continue
        unit = a.get("unit", "")
        start = a.get("startDate") or a.get("creationDate") or ""
        # Apple's date format: "2025-01-15 08:13:00 +0200"
        try:
            taken_dt = datetime.strptime(start[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        day = taken_dt.date()
        key = (marker, day)
        if key not in seen or seen[key][0] < taken_dt:
            value_canonical, _ = normalize(marker, value, unit)
            seen[key] = (taken_dt, value_canonical, unit)

    out: list[dict] = []
    for (marker, day), (_, value, unit) in sorted(seen.items()):
        out.append({"marker": marker, "value": value, "unit": unit, "taken_on": day.isoformat()})
    return out
