"""Narrative Engine — turns a HealthReport into a plain-language summary.

Uses Claude when an API key is configured (with prompt caching on the static
system prompt to cut cost), and otherwise falls back to a deterministic,
rule-based summary so the feature always works with zero setup.

Safety: the system prompt encodes the product's SYSTEM ROLE — never diagnose,
never claim certainty, avoid fear-inducing language, always defer to a physician.
"""
from __future__ import annotations

from app.config import DISCLAIMER, get_settings
from app.schemas import Finding, HealthReport

# Static system prompt -> cached via cache_control to reduce repeat-call cost.
SYSTEM_PROMPT = """You are an advanced health-intelligence assistant.
Your role is NOT to diagnose diseases or replace physicians. You:
- Explain medical data in clear, simple language a non-expert understands.
- Highlight the most important, potentially life-saving preventive opportunities.
- Clearly distinguish information from diagnosis, and never claim certainty.
- Encourage consulting a physician when appropriate.
- Avoid fear-inducing or alarmist language; be calm, factual, and supportive.
- Prioritize what matters: lead with the few things that matter most.

Write a short executive summary (~150-220 words) with: a one-line overall read,
then the 2-4 most important things to act on, then a brief encouraging close.
Do not invent data beyond what you are given. Do not output a diagnosis."""

_LANG_INSTRUCTION = {
    "he": "Write the entire summary in clear, simple Hebrew.",
    "en": "Write the entire summary in clear, simple English.",
}


def _facts_block(report: HealthReport) -> str:
    lines: list[str] = [
        f"Patient: {report.user.sex}, age {report.user.age}.",
        f"Overall health score: {report.health_score}/100.",
        "",
        "Top priorities:",
    ]
    for f in report.top_priorities or [Finding(title="None", detail="", priority="informational", source="")]:
        lines.append(f"- [{f.priority}] {f.title}: {f.plain_language or f.detail}")

    lines.append("")
    lines.append("Notable lab trends:")
    for t in report.trends[:6]:
        latest = t.points[-1].value if t.points else "?"
        lines.append(f"- {t.label}: latest {latest} {t.unit}, {t.direction}, status {t.status}.")

    lines.append("")
    lines.append("Insurance insights:")
    for f in report.insurance_insights[:5]:
        lines.append(f"- [{f.priority}] {f.title}")

    lines.append("")
    lines.append("Recommended screenings to verify:")
    for f in report.missing_screenings[:5]:
        lines.append(f"- {f.title}")

    return "\n".join(lines)


def _rule_based(report: HealthReport, lang: str) -> str:
    """Deterministic fallback summary — no API key needed."""
    he = lang == "he"
    parts: list[str] = []

    if he:
        parts.append(
            f"בסך הכול ציון הבריאות שלך הוא {report.health_score} מתוך 100. "
            "להלן הדברים החשובים ביותר כרגע, בשפה פשוטה:"
        )
    else:
        parts.append(
            f"Your overall health score is {report.health_score} out of 100. "
            "Here are the most important things right now, in plain language:"
        )

    for f in report.top_priorities:
        text = f.plain_language or f.detail
        parts.append(f"• {text}")

    trends_worsening = [t for t in report.trends if t.status in ("abnormal", "borderline")]
    if trends_worsening:
        t = trends_worsening[0]
        if he:
            parts.append(
                f"• שים לב למגמה ב{t.label} — כדאי לעקוב ולשוחח עם רופא בהזדמנות."
            )
        else:
            parts.append(
                f"• Keep an eye on your {t.label} trend — worth tracking and raising with a doctor."
            )

    if report.insurance_insights:
        if he:
            parts.append(
                "• בתחום הביטוח זוהו נקודות לבדיקה (כפילויות או חוסרים) — שווה לעבור עליהן כדי לא לשלם על מה שלא צריך."
            )
        else:
            parts.append(
                "• On insurance, we found items worth reviewing (duplicates or gaps) so you don't pay for what you don't need."
            )

    if he:
        parts.append(
            "אלה אינם אבחנות — הם נועדו לעזור לך לשאול את השאלות הנכונות ולתעדף בדיקות מונעות יחד עם הרופא/ה שלך."
        )
    else:
        parts.append(
            "These are not diagnoses — they help you ask the right questions and prioritize preventive care with your doctor."
        )

    return "\n".join(parts)


def narrate(report: HealthReport, lang: str = "he") -> dict:
    lang = lang if lang in _LANG_INSTRUCTION else "he"
    settings = get_settings()

    if not settings.anthropic_api_key:
        return {
            "text": _rule_based(report, lang),
            "generated_by": "rule_based",
            "model": None,
            "disclaimer": DISCLAIMER,
        }

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        user_content = f"{_LANG_INSTRUCTION[lang]}\n\nHere is the patient's report:\n\n{_facts_block(report)}"
        message = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=700,
            system=[
                {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
            ],
            messages=[{"role": "user", "content": user_content}],
        )
        text = "".join(block.text for block in message.content if block.type == "text")
        return {
            "text": text.strip(),
            "generated_by": "claude",
            "model": settings.anthropic_model,
            "disclaimer": DISCLAIMER,
        }
    except Exception:
        # Any failure (no package, network, auth) degrades gracefully.
        return {
            "text": _rule_based(report, lang),
            "generated_by": "rule_based_fallback",
            "model": None,
            "disclaimer": DISCLAIMER,
        }
