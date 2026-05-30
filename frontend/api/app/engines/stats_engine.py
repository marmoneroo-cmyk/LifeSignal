"""Statistical comparison + future-risk projection.

- percentile(): where the user's latest value sits vs a population distribution.
- projection(): naive linear extrapolation of a worsening trend to a future date,
  framed conditionally ("if the current trend continues…").
Both are decision-support signals, explicitly approximate.
"""
from __future__ import annotations

import math
from datetime import date

from app.data.lab_reference import marker_meta
from app.data.population_stats import POPULATION
from app.models import LabResult
from app.schemas import Finding


def _normal_cdf(z: float) -> float:
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def percentiles(results: list[LabResult]) -> list[dict]:
    latest: dict[str, tuple] = {}
    for r in results:
        k = r.marker.lower()
        if k not in latest or r.taken_on > latest[k][0]:
            latest[k] = (r.taken_on, r.value)

    out: list[dict] = []
    for marker, (_, value) in latest.items():
        stats = POPULATION.get(marker)
        meta = marker_meta(marker)
        if not stats or not meta:
            continue
        mean, sd = stats
        if sd <= 0:
            continue
        pct = round(_normal_cdf((value - mean) / sd) * 100)
        out.append(
            {
                "marker": marker,
                "label": meta["label"],
                "value": value,
                "percentile": pct,
                "higher_is_risk": meta["higher_is_risk"],
            }
        )
    out.sort(key=lambda d: abs(d["percentile"] - 50), reverse=True)
    return out


def projection(results: list[LabResult]) -> list[Finding]:
    """Project markers with >= 3 points and a clear risk-direction slope."""
    series: dict[str, list[LabResult]] = {}
    for r in results:
        series.setdefault(r.marker.lower(), []).append(r)

    findings: list[Finding] = []
    for marker, rows in series.items():
        if len(rows) < 3:
            continue
        meta = marker_meta(marker)
        if not meta:
            continue
        rows.sort(key=lambda r: r.taken_on)
        # x = years since first sample; least-squares slope.
        x0 = rows[0].taken_on
        xs = [(r.taken_on - x0).days / 365.25 for r in rows]
        ys = [r.value for r in rows]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        denom = sum((x - mx) ** 2 for x in xs)
        if denom == 0:
            continue
        slope = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / denom
        worsening = (slope > 0 and meta["higher_is_risk"]) or (slope < 0 and not meta["higher_is_risk"])
        if not worsening or abs(slope) < 1e-6:
            continue
        projected = round(my + slope * (xs[-1] - mx + 2), 1)  # ~2 years past latest
        findings.append(
            Finding(
                title=f"Projection: {meta['label']}",
                detail=f"If the current trend continues, {meta['label']} could reach ~{projected} {meta['unit']} in ~2 years.",
                priority="preventive",
                source="stats_engine",
                plain_language=(
                    f"At the current pace, your {meta['label'].lower()} may keep moving in the "
                    "wrong direction. Acting now is usually easier than later."
                ),
            )
        )
    return findings
