# LifeSignal — Personal Health Intelligence (MVP)

A **Clinical Decision Support System**, built from the product vision in
[`readme.txt`](readme.txt). It is **not** a diagnostic tool — it surfaces trends,
gaps, and preventive opportunities from a person's own lab + insurance data, and
always defers to a physician.

> _This system does not provide a medical diagnosis and should not replace
> consultation with qualified healthcare professionals._

This is **Stage 1 (the doc's recommended MVP): Insurance + Blood Analysis**, with a
deterministic, rule-based engine (no AI API key required) so it runs anywhere.

## What it does today

| Engine | Output |
|--------|--------|
| **Blood Test Analyzer** | Abnormal/borderline markers vs. sex-specific ranges + **longitudinal trends** across repeated tests ("the thing doctors miss") |
| **Insurance Analyzer** | Duplicate coverage, missing critical coverage, age-relevance, cost concentration, upcoming renewals |
| **Preventive Screening Engine** | Age/sex/family-history-driven screening recommendations (USPSTF-style) |
| **Risk Engine + Health Score** | 0–100 score broken down by domain (heart, metabolism, kidney…) |
| **Prioritization** | "3 most important things right now" |
| **Notification Engine** | Non-spammy reminder feed |
| **Document Intake (PDF)** | Upload a blood-test/insurance **PDF** → text extracted & parsed into marker/coverage candidates (English + Hebrew aliases) for you to review before saving |
| **Narrative Engine** | Plain-language **Executive Health Summary** (Hebrew or English). Uses **Claude** when `ANTHROPIC_API_KEY` is set (with prompt caching); falls back to a deterministic rule-based summary otherwise |
| **Drug Interaction Engine** | Pairwise interactions + duplicate-class therapy from your medication list (curated KB, English + Hebrew drug names) |
| **Cross-Correlation Engine** | Multi-marker *patterns* (iron-deficiency anemia, prediabetes cluster, liver-enzyme group, reduced kidney function) — not single values |
| **Emergency Detection** | Conservative red-line values → "seek prompt medical evaluation" (never a diagnosis) |
| **Family Health Graph** | Relatives' conditions → hereditary-risk signals that bring screenings earlier |
| **Stats Engine** | Population **percentiles** + conditional **future-risk projections** of worsening trends |
| **Coverage Matching** | Links each recommended screening to your private coverage + public-basket funding |
| **Medical Copilot** | Pre-visit questions + "what changed since last time" (Hebrew/English) |
| **Unit Normalization** | Converts mmol/L↔mg/dL etc. to canonical units at intake |
| **Second Opinion Engine** | Extra avenues of inquiry to raise with a doctor (supportive, never alternative diagnoses) |
| **Insurance Negotiator** | Risk-adjusted value review — where you may be over- or under-insured |
| **Claim Eligibility** | Reimbursements you may be entitled to claim under held cover |
| **Region Guidelines** | Screening start-ages by region (International / Israel MoH / USPSTF / EU) |
| **Year-over-Year** | Annual comparison of each marker, with deltas |
| **Auth + Family Accounts** | Local JWT login; one account manages multiple profiles (self + dependents) with per-profile authorization |
| **Policy Clause Extraction** | Pulls deductibles / ceilings / exclusions from policy PDFs |
| **Export / Print** | JSON data export + print-to-PDF report; multi-file PDF upload |
| **Safety Eval Harness** | `pytest` suite (18 tests) asserting the system never diagnoses, always carries the disclaimer, is deterministic, and that auth/JWT behave correctly |

## Architecture (as specified in the doc)

- **Frontend:** Next.js (App Router) + Tailwind + shadcn-style UI
- **Backend:** Python **FastAPI**
- **Database:** **PostgreSQL** — set `DATABASE_URL`; otherwise falls back to a local
  **SQLite** file so it runs with zero setup.
- **AI:** rule-based now; the engine layer is isolated so Claude/OCR modules can be
  added behind the same interfaces later.

```
backend/   FastAPI + rule engines + clinical reference data
frontend/  Next.js dashboard, report, timeline, intake forms
```

## Run it

### 1. Backend (terminal 1)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.data.seed          # creates a demo profile (man, 42)
uvicorn app.main:app --reload    # http://localhost:8000  (docs at /docs)
```

Run the safety + engine test suite:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q   # 18 tests: safety evals + engine + auth units
```

To use PostgreSQL instead of SQLite, copy `.env.example` to `.env` and set
`DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/health_intel`.

### 2. Frontend (terminal 2)

```powershell
cd frontend
npm install
npm run dev                      # http://localhost:3000
```

Open **http://localhost:3000** and **log in** with the seeded demo account:

> **email:** `demo@demo.com`  **password:** `demo1234`

Or register a new account. Use the profile switcher (top-left) to add **family
profiles** (e.g. children) and switch between them. Use **Upload PDF** to drop in
a blood-test or insurance PDF (values extracted for review before saving), or
**Add Lab Results** / **Add Insurance** / **Medications** / **Family History** to
enter data manually, then watch the analysis update. The **Health Report** has
**Print / PDF** and **Export** buttons.

> The Document Intake module reads **text-layer PDFs** (digitally generated).
> Scanned/photographed documents need true OCR (Azure / Google Document AI) — a
> documented future module.

## Safety & scope

Every report carries the legal disclaimer. The engines never diagnose, never claim
certainty, and always frame findings as "worth reviewing with a doctor." Image
analysis, OCR, drug-interaction, and family-graph modules from the vision doc are
intentionally **out of scope** for this MVP and are noted as future work.

## Roadmap (from `readme.txt`)

**Done:** ✅ PDF intake · ✅ Claude narration · ✅ drug interactions · ✅ family
graph · ✅ emergency detection · ✅ cross-correlations · ✅ percentiles &
projections · ✅ coverage matching · ✅ medical copilot · ✅ unit normalization ·
✅ safety eval harness · ✅ second opinion · ✅ insurance negotiator · ✅ claim
eligibility · ✅ region guidelines · ✅ year-over-year · ✅ auth + family accounts ·
✅ policy clause extraction · ✅ data export / print-to-PDF / multi-file upload.

**Deferred — require third-party credentials** (interfaces stubbed in
[`app/integrations/`](backend/app/integrations/), not faked):
- **OCR for scanned docs** — Azure / Google Document AI ([ocr_provider.py](backend/app/integrations/ocr_provider.py))
- **Wearables** — Apple Health / Google Fit OAuth ([wearables.py](backend/app/integrations/wearables.py))
- **Guideline RAG** — embeddings + vector store ([guidelines_rag.py](backend/app/integrations/guidelines_rag.py))
- Image risk detection · kupot/FHIR integration · SMS/email channels · real auth (Clerk/Auth0)

To enable AI narration: copy `backend/.env.example` to `backend/.env` and set
`ANTHROPIC_API_KEY`. Without it, the summary is generated by a rule-based fallback.
