"""Chat engine — answer free-form questions grounded in the user's own data.

Builds a compact context block from the user's profile, labs, policies,
medications and family graph, then asks Claude (with prompt caching on the
system prompt). Without an API key, returns a deterministic fallback that
echoes the most relevant data the question seems to ask about — so the chat
surface still works without credentials.
"""
from __future__ import annotations

from datetime import date

from app.config import DISCLAIMER, get_settings
from app.models import User

SYSTEM_PROMPT = """You are LifeSignal, a health-intelligence assistant grounded
in the user's OWN uploaded medical data. You are NOT a doctor.

Rules:
- Answer only from the patient context provided. If the data does not answer
  the question, say so plainly — do not invent.
- Never diagnose, never claim certainty.
- Use simple, calm language. Encourage consulting a physician when relevant.
- For Hebrew questions, reply in Hebrew. For English, reply in English.
- Be concise (2-5 short paragraphs unless the user asks for more).
- When you reference a lab value or policy, name it specifically so the user
  can verify it against their own data.

You may be asked questions like:
- "What changed in my labs over the last year?"
- "האם הביטוח שלי מכסה קולונוסקופיה?"
- "Why is my LDL trending up?"
"""


def _build_context(user: User) -> str:
    parts: list[str] = []
    parts.append(f"Patient: {user.sex}, age {user.age}, region={user.region}.")
    if user.smoker:
        parts.append("Smoker: yes.")
    if user.family_history:
        parts.append(f"Family history tags: {user.family_history}")

    # Family graph
    if user.family_members:
        parts.append("\nFamily members:")
        for m in user.family_members:
            parts.append(f"  - {m.relation}: {m.conditions or 'no conditions listed'}")

    # Labs — group by marker and show chronological values
    if user.lab_results:
        by_marker: dict[str, list] = {}
        for r in user.lab_results:
            by_marker.setdefault(r.marker, []).append(r)
        parts.append("\nLab results (chronological):")
        for marker, rows in by_marker.items():
            rows.sort(key=lambda r: r.taken_on)
            series = ", ".join(f"{r.taken_on}: {r.value} {r.unit}" for r in rows)
            parts.append(f"  - {marker}: {series}")

    # Policies
    if user.policies:
        parts.append("\nInsurance policies held:")
        for p in user.policies:
            renew = f", renews {p.renewal_date}" if p.renewal_date else ""
            parts.append(f"  - {p.coverage_type} ({p.provider}), {p.monthly_premium}/month{renew}")

    # Medications
    if user.medications:
        parts.append("\nMedications:")
        for m in user.medications:
            parts.append(f"  - {m.name} {m.dose}")

    if len(parts) <= 2:
        parts.append("\n(No medical data uploaded yet.)")

    return "\n".join(parts)


def _fallback_answer(question: str, user: User) -> str:
    """Deterministic answer when no API key is configured."""
    q = question.lower()
    he = any(ord(c) > 1487 and ord(c) < 1515 for c in question)  # Hebrew chars

    # Try to surface the most relevant data
    if user.lab_results and any(k in q for k in ("ldl", "כולסטרול", "cholesterol", "סוכר", "hba1c", "ויטמין", "vitamin")):
        relevant = [r for r in user.lab_results
                    if any(k in r.marker for k in ("ldl", "hba1c", "vitamin", "hdl"))]
        if relevant:
            relevant.sort(key=lambda r: r.taken_on)
            lines = [f"{r.marker.upper()}: {r.value} {r.unit} ({r.taken_on})" for r in relevant[-6:]]
            if he:
                return ("הנה הערכים הרלוונטיים מהנתונים שלך:\n" + "\n".join(lines) +
                        "\n\n(תשובה מבוססת-כללים. הגדר ANTHROPIC_API_KEY לתשובות חכמות יותר.)")
            return ("Here are the relevant values from your data:\n" + "\n".join(lines) +
                    "\n\n(Rule-based answer. Set ANTHROPIC_API_KEY for smarter responses.)")

    if user.policies and any(k in q for k in ("policy", "insurance", "ביטוח", "פוליסה", "כיסוי", "coverage")):
        lines = [f"{p.coverage_type} — {p.provider}, {p.monthly_premium}/mo" for p in user.policies]
        if he:
            return "הפוליסות שלך:\n" + "\n".join(lines) + "\n\n(הגדר ANTHROPIC_API_KEY לניתוח חכם יותר.)"
        return "Your policies:\n" + "\n".join(lines) + "\n\n(Set ANTHROPIC_API_KEY for smarter analysis.)"

    if he:
        return ("אני עובד עכשיו במצב מבוסס-כללים (ללא Claude API). "
                "אני יודע לענות על שאלות שמתייחסות ישירות לנתונים שלך — נסה לשאול על "
                "מרקר ספציפי (LDL, ויטמין D), על הביטוחים, או על תרופות. "
                "להפעלה מלאה: הגדר ANTHROPIC_API_KEY בקובץ backend/.env.")
    return ("I'm in rule-based mode (no Claude API). I can answer questions that "
            "directly reference your data — try asking about a specific marker (LDL, vitamin D), "
            "your insurance, or your medications. To enable full chat: set "
            "ANTHROPIC_API_KEY in backend/.env.")


def ask(user: User, question: str) -> dict:
    settings = get_settings()
    context = _build_context(user)

    if not settings.anthropic_api_key:
        return {
            "answer": _fallback_answer(question, user),
            "generated_by": "rule_based",
            "model": None,
            "disclaimer": DISCLAIMER,
        }

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=800,
            system=[
                {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}
            ],
            messages=[
                {"role": "user", "content": f"Patient context:\n{context}\n\nQuestion: {question}"},
            ],
        )
        text = "".join(b.text for b in message.content if b.type == "text").strip()
        return {
            "answer": text,
            "generated_by": "claude",
            "model": settings.anthropic_model,
            "disclaimer": DISCLAIMER,
        }
    except Exception:
        return {
            "answer": _fallback_answer(question, user),
            "generated_by": "rule_based_fallback",
            "model": None,
            "disclaimer": DISCLAIMER,
        }
