"""Free-text drug search via the NIH RxNorm REST API.

RxNorm is an authoritative US drug nomenclature maintained by the NIH. The
RxNav web service is FREE, requires no API key, and returns canonical names
for brand/generic queries. We use it as an autocomplete source so users can
type "Lipitor" and get the canonical "atorvastatin".

Docs: https://rxnav.nlm.nih.gov/RxNormAPIs.html
"""
from __future__ import annotations

import urllib.parse
import urllib.request

from fastapi import APIRouter, Depends, HTTPException

from app.auth import current_user
from app.data.drug_interactions import DRUG_ALIASES
from app.models import User

router = APIRouter(prefix="/api/drugs", tags=["drugs"])

_RXNAV = "https://rxnav.nlm.nih.gov/REST"
_HEADERS = {"User-Agent": "LifeSignal/1.0 (decision-support)"}
_TIMEOUT = 5  # seconds — keep snappy on serverless cold start


def _http_get(url: str) -> dict:
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        import json
        return json.loads(resp.read().decode("utf-8"))


@router.get("/search")
def search(q: str, _account: User = Depends(current_user)) -> dict:
    """Look up a brand/generic name. Returns canonical RxNorm name + RxCUI ID."""
    if len(q.strip()) < 2:
        return {"query": q, "matches": [], "known_aliases": []}

    # First: check if it matches a known alias in our local interaction KB.
    q_lc = q.strip().lower()
    known: list[str] = []
    for key, aliases in DRUG_ALIASES.items():
        if any(a in q_lc or q_lc in a for a in aliases):
            known.append(key)

    matches: list[dict] = []
    try:
        # RxNorm's approximateTerm endpoint handles typos + brand→generic mapping.
        url = f"{_RXNAV}/approximateTerm.json?term={urllib.parse.quote(q)}&maxEntries=8"
        data = _http_get(url)
        for cand in (data.get("approximateGroup", {}) or {}).get("candidate", []) or []:
            matches.append({
                "rxcui": cand.get("rxcui"),
                "name": cand.get("score") and cand.get("name") or cand.get("name"),
                "score": cand.get("score"),
            })
    except Exception:
        # Network blip → empty matches, but local-alias matches still returned.
        pass

    return {"query": q, "matches": matches, "known_aliases": known}


@router.get("/interactions/{rxcui}")
def interactions(rxcui: str, _account: User = Depends(current_user)) -> dict:
    """Look up drug-drug interactions via RxNav's interaction API.

    Note: as of Jan 2024, NIH retired their bundled interaction source. The
    endpoint still exists for documentation purposes but may return empty.
    The app's primary interaction logic uses the local curated KB.
    """
    try:
        url = f"{_RXNAV}/interaction/interaction.json?rxcui={rxcui}"
        return _http_get(url)
    except Exception as exc:
        raise HTTPException(503, f"RxNav unavailable: {exc}")
