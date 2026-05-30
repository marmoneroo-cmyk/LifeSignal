"""Unit tests for the individual analysis engines."""
from __future__ import annotations

from datetime import date

from app.data.units import normalize
from app.engines import (
    correlation_engine,
    drug_engine,
    emergency_engine,
    stats_engine,
)
from app.models import LabResult, Medication


def test_unit_normalization_ldl_mmol_to_mgdl():
    value, applied = normalize("ldl", 4.0, "mmol/L")
    assert applied == "mmol/l"
    assert round(value) == 155  # 4.0 * 38.67


def test_unit_normalization_no_change_when_canonical():
    value, applied = normalize("ldl", 130, "mg/dL")
    assert applied is None
    assert value == 130


def test_drug_engine_detects_warfarin_aspirin(demo_user):
    findings = drug_engine.analyze(demo_user.medications)
    titles = " ".join(f.title.lower() for f in findings)
    assert "warfarin" in titles and "aspirin" in titles
    assert any(f.priority == "high" for f in findings)


def test_drug_engine_empty_list():
    assert drug_engine.analyze([]) == []


def test_correlation_detects_iron_deficiency(demo_user):
    findings = correlation_engine.analyze(demo_user, demo_user.lab_results)
    assert any("iron" in f.title.lower() for f in findings)


def test_emergency_detects_high_potassium(demo_user):
    findings = emergency_engine.analyze(demo_user, demo_user.lab_results)
    assert any("potassium" in f.title.lower() for f in findings)
    assert all(f.priority == "critical" for f in findings)


def test_projection_flags_rising_ldl(demo_user):
    findings = stats_engine.projection(demo_user.lab_results)
    assert any("ldl" in f.title.lower() for f in findings)


def test_percentile_within_bounds(demo_user):
    rows = stats_engine.percentiles(demo_user.lab_results)
    for r in rows:
        assert 0 <= r["percentile"] <= 100
