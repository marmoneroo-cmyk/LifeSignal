"""Smart table extractor for structured lab reports.

Israeli health-fund reports (Maccabi, Clalit, Leumit, Meuhedet) are structured
tables — NOT free text. This module detects that structure, extracts every row,
and uses the document's own reference ranges for flagging.

Supported inputs:
  - Excel (.xlsx) via openpyxl
  - PDF text-layer tables via pdfplumber (page.extract_tables())

The extractor is column-name agnostic: it scores each column against known
Hebrew/English header patterns and picks the best match. This means it works
on any layout without needing a hand-crafted format per health fund.
"""
from __future__ import annotations

import io
import re
from datetime import date, datetime
from typing import Any

# ---- Column-header patterns -------------------------------------------------

# Each pattern group: list of lowercase substrings, any of which → match.
_COL_NAME = ["שם", "בדיקה", "name", "test", "פרמטר", "analyte", "מדד"]
_COL_VALUE = ["תוצאה", "ערך", "result", "value", "ריכוז"]
_COL_UNIT = ["יחידה", "unit", "מדידה"]
_COL_REF = ["תקין", "ייחוס", "נורמה", "reference", "normal", "טווח", "range"]
_COL_DATE = ["תאריך", "date", "דגימה", "נדגם"]
_COL_STATUS = ["סטטוס", "status", "פרשנות", "flag"]

_ALL_PATTERNS = [
    ("name",   _COL_NAME),
    ("value",  _COL_VALUE),
    ("unit",   _COL_UNIT),
    ("ref",    _COL_REF),
    ("date",   _COL_DATE),
    ("status", _COL_STATUS),
]

# ---- Reference-range parsing -----------------------------------------------
# Matches "3.5 - 17.5", "< 100", "> 5", "3.5-17.5", "10 – 20" etc.
_RANGE_RE = re.compile(r"(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)")
_LESS_RE  = re.compile(r"<\s*(\d+(?:[.,]\d+)?)")
_MORE_RE  = re.compile(r">\s*(\d+(?:[.,]\d+)?)")
_NUM_RE   = re.compile(r"\d+(?:[.,]\d+)?")


def _to_float(s: str) -> float | None:
    try:
        return float(str(s).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def _parse_ref(raw: str) -> tuple[float | None, float | None]:
    """Return (low, high) from a reference-range string. None = unbounded."""
    s = str(raw or "").strip()
    m = _RANGE_RE.search(s)
    if m:
        return _to_float(m.group(1)), _to_float(m.group(2))
    m = _LESS_RE.search(s)
    if m:
        return None, _to_float(m.group(1))
    m = _MORE_RE.search(s)
    if m:
        return _to_float(m.group(1)), None
    return None, None


def _status_from_ref(value: float, low: float | None, high: float | None) -> str:
    if low is not None and value < low:
        return "low"
    if high is not None and value > high:
        return "high"
    return "normal"


# ---- Column detection -------------------------------------------------------

def _score_header(cell: str, patterns: list[str]) -> int:
    c = str(cell).strip().lower()
    return sum(1 for p in patterns if p in c)


def _detect_columns(headers: list[Any]) -> dict[str, int]:
    """Map role → column-index for the best-scoring header."""
    scores: dict[str, list[tuple[int, int]]] = {role: [] for role, _ in _ALL_PATTERNS}
    for col_idx, h in enumerate(headers):
        for role, patterns in _ALL_PATTERNS:
            s = _score_header(h, patterns)
            if s > 0:
                scores[role].append((s, col_idx))
    return {
        role: max(hits, key=lambda t: t[0])[1]
        for role, hits in scores.items()
        if hits
    }


# ---- Row → LabRow -----------------------------------------------------------

class LabRow:
    __slots__ = ("name", "value", "unit", "ref_low", "ref_high", "status", "taken_on")

    def __init__(
        self,
        name: str,
        value: float,
        unit: str,
        ref_low: float | None,
        ref_high: float | None,
        status: str,
        taken_on: str,
    ) -> None:
        self.name = name
        self.value = value
        self.unit = unit
        self.ref_low = ref_low
        self.ref_high = ref_high
        self.status = status
        self.taken_on = taken_on

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "ref_low": self.ref_low,
            "ref_high": self.ref_high,
            "status": self.status,
            "taken_on": self.taken_on,
        }


def _rows_from_table(
    table: list[list[Any]],
    default_date: str,
) -> list[LabRow]:
    """Extract LabRow objects from a 2-D table (list of lists)."""
    if not table or len(table) < 2:
        return []

    # Try the first non-empty row as the header.
    header_idx = 0
    for i, row in enumerate(table):
        if any(c and str(c).strip() for c in row):
            header_idx = i
            break

    headers = [str(c or "").strip() for c in table[header_idx]]
    cols = _detect_columns(headers)

    if "name" not in cols or "value" not in cols:
        return []

    rows: list[LabRow] = []
    for row in table[header_idx + 1:]:
        if len(row) <= max(cols.values()):
            continue
        name_cell  = str(row[cols["name"]]  or "").strip()
        value_cell = str(row[cols["value"]] or "").strip()

        if not name_cell or not value_cell:
            continue
        value = _to_float(value_cell)
        if value is None:
            continue

        unit = str(row[cols["unit"]] or "").strip() if "unit" in cols else ""

        ref_low, ref_high = None, None
        if "ref" in cols:
            ref_low, ref_high = _parse_ref(str(row[cols["ref"]] or ""))

        doc_status = str(row[cols["status"]] or "").strip().lower() if "status" in cols else ""
        if doc_status in ("גבוה", "high", "h", "↑"):
            status = "high"
        elif doc_status in ("נמוך", "low", "l", "↓"):
            status = "low"
        elif ref_low is not None or ref_high is not None:
            status = _status_from_ref(value, ref_low, ref_high)
        else:
            status = "normal"

        taken_on = default_date
        if "date" in cols:
            d = str(row[cols["date"]] or "").strip()
            parsed = _try_parse_date(d)
            if parsed:
                taken_on = parsed

        rows.append(LabRow(name_cell, value, unit, ref_low, ref_high, status, taken_on))

    return rows


def _try_parse_date(s: str) -> str | None:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return None


# ---- Excel extractor --------------------------------------------------------

def extract_from_excel(data: bytes) -> list[LabRow]:
    import openpyxl  # optional dependency

    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
    all_rows: list[LabRow] = []
    today = date.today().isoformat()

    for ws in wb.worksheets:
        table = [[cell.value for cell in row] for row in ws.iter_rows()]
        all_rows.extend(_rows_from_table(table, today))

    return all_rows


# ---- PDF table extractor ----------------------------------------------------

def extract_from_pdf_tables(data: bytes) -> list[LabRow]:
    import pdfplumber

    all_rows: list[LabRow] = []
    today = date.today().isoformat()

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in (tables or []):
                all_rows.extend(_rows_from_table(table, today))

    return all_rows


# ---- Public API -------------------------------------------------------------

def extract(data: bytes, filename: str) -> dict:
    """Entry point: detect format, extract, return structured result."""
    fn = filename.lower()
    rows: list[LabRow] = []
    warnings: list[str] = []

    try:
        if fn.endswith((".xlsx", ".xls", ".ods")):
            rows = extract_from_excel(data)
            source = "excel"
        else:
            # PDF: try table extraction first, fall back to text regex (existing parser).
            rows = extract_from_pdf_tables(data)
            source = "pdf_table"
            if not rows:
                warnings.append(
                    "לא זוהתה טבלה מובנית ב-PDF. נסה לייצא מהמעבדה כ-Excel, "
                    "או השתמש ב-PDF דיגיטלי (לא סרוק)."
                )
    except ImportError as e:
        warnings.append(f"חסרה תלות: {e}. הרץ pip install -r requirements.txt.")
        rows = []
        source = "error"
    except Exception as e:
        warnings.append(f"שגיאה בקריאת הקובץ: {e}")
        rows = []
        source = "error"

    abnormal = [r for r in rows if r.status in ("high", "low")]

    return {
        "source": source,
        "total_rows": len(rows),
        "rows": [r.to_dict() for r in rows],
        "abnormal": [r.to_dict() for r in abnormal],
        "warnings": warnings,
    }
