"""Parser for raw 23andMe genotype files.

The user downloads their raw data from 23andMe → Account → Browse Raw Data.
The resulting file is a tab-separated text with rows like:

    # rsid    chromosome  position  genotype
    rs53576   3           8804371   AA

We scan for a small curated set of clinically discussed SNPs and surface the
genotype only — never an interpretation. This is research-information, NOT
medical genetics. Real interpretation needs board-certified counseling.

Disclaimer is enforced at the API + UI layer.
"""
from __future__ import annotations

import io
import zipfile

# Curated SNPs that show up commonly in lay-press health writing. We report the
# raw genotype only and let the user discuss with a clinician. Risk text is
# deliberately framed as "discussed in the literature" — never as causation.
NOTABLE_SNPS: dict[str, dict] = {
    "rs53576":  {"gene": "OXTR",   "topic_he": "אוקסיטוצין/אמפתיה", "topic_en": "oxytocin/empathy"},
    "rs1801133":{"gene": "MTHFR",  "topic_he": "מטבוליזם של חומצה פולית", "topic_en": "folate metabolism"},
    "rs7903146":{"gene": "TCF7L2", "topic_he": "סיכון לסוכרת סוג 2", "topic_en": "type-2 diabetes risk"},
    "rs429358": {"gene": "APOE",   "topic_he": "סיכון אלצהיימר", "topic_en": "Alzheimer's-disease risk"},
    "rs7412":   {"gene": "APOE",   "topic_he": "סיכון אלצהיימר", "topic_en": "Alzheimer's-disease risk"},
    "rs1799971":{"gene": "OPRM1",  "topic_he": "תגובה למשככי כאב אופיואידים", "topic_en": "opioid analgesic response"},
    "rs4988235":{"gene": "MCM6",   "topic_he": "סבילות ללקטוז", "topic_en": "lactose tolerance"},
    "rs1799971":{"gene": "OPRM1",  "topic_he": "תגובה אופיואידית", "topic_en": "opioid response"},
    "rs1042713":{"gene": "ADRB2",  "topic_he": "תגובה למרחיבי סימפונות", "topic_en": "bronchodilator response"},
    "rs1799752":{"gene": "ACE",    "topic_he": "מערכת רנין-אנגיוטנסין", "topic_en": "ACE / blood pressure"},
}


def _read_text(data: bytes) -> str:
    """Accept plain .txt or a .zip containing one .txt file."""
    if data[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            name = next((n for n in zf.namelist() if n.endswith(".txt")), None)
            if not name:
                raise ValueError("No .txt file inside the zip")
            return zf.read(name).decode("utf-8", errors="ignore")
    return data.decode("utf-8", errors="ignore")


def parse(data: bytes, lang: str = "he") -> dict:
    """Return found notable SNPs + their genotypes from the 23andMe export."""
    text = _read_text(data)
    found: list[dict] = []
    total = 0

    for raw in text.splitlines():
        if not raw or raw.startswith("#"):
            continue
        total += 1
        # 23andMe rows are tab-separated: rsid \t chromosome \t position \t genotype
        parts = raw.split("\t")
        if len(parts) < 4:
            continue
        rsid, _chrom, _pos, genotype = parts[0], parts[1], parts[2], parts[3]
        meta = NOTABLE_SNPS.get(rsid)
        if not meta:
            continue
        found.append({
            "rsid": rsid,
            "gene": meta["gene"],
            "topic": meta["topic_he" if lang == "he" else "topic_en"],
            "genotype": genotype,
        })

    return {"total_rows_scanned": total, "notable": found}
