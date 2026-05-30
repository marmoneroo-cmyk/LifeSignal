"""Medical Copilot — prepare the user for a doctor visit.

Generates a focused list of questions to ask and what changed since last time,
derived from the report's findings and trends. Pure rule-based (deterministic);
the Narrative Engine can optionally rephrase these with Claude.
"""
from __future__ import annotations

from app.schemas import HealthReport


def prepare(report: HealthReport, lang: str = "en") -> dict:
    he = lang == "he"
    questions: list[str] = []
    changes: list[str] = []

    for f in report.top_priorities:
        if he:
            questions.append(f"לגבי \"{f.title}\" — מה כדאי לבדוק או לעשות עכשיו?")
        else:
            questions.append(f'Regarding "{f.title}" — what should I check or do now?')

    worsening = [t for t in report.trends if t.status in ("abnormal", "borderline")]
    for t in worsening[:4]:
        latest = t.points[-1].value if t.points else "?"
        if he:
            changes.append(f"{t.label}: כעת {latest} {t.unit} ({t.direction}).")
            questions.append(f"האם המגמה ב{t.label} דורשת בדיקה נוספת?")
        else:
            changes.append(f"{t.label}: now {latest} {t.unit} ({t.direction}).")
            questions.append(f"Does my {t.label} trend need further testing?")

    if report.missing_screenings:
        first = report.missing_screenings[0].title.replace("Screening to verify: ", "")
        if he:
            questions.append(f"האם הגיע הזמן ל: {first}?")
        else:
            questions.append(f"Is it time for: {first}?")

    # De-duplicate while preserving order.
    seen: set[str] = set()
    questions = [q for q in questions if not (q in seen or seen.add(q))]

    return {
        "questions": questions[:8],
        "changes_since_last": changes,
        "disclaimer": report.disclaimer,
    }
