"""Calendar export — generates an .ics file for recommended preventive screenings.

The endpoint streams a standard RFC 5545 iCalendar feed the user can import
into Google Calendar / Apple Calendar / Outlook so screening reminders show up
alongside their normal calendar. No external email/push needed.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Response

from app.auth import accessible_profile
from app.engines import report_engine
from app.engines.translator import translate_report
from app.models import User

router = APIRouter(tags=["calendar"])


def _ics_escape(text: str) -> str:
    """Escape iCalendar TEXT values per RFC 5545."""
    return (text.replace("\\", "\\\\")
                .replace(";", r"\;")
                .replace(",", r"\,")
                .replace("\n", r"\n"))


def _build_ics(events: list[dict], user_name: str) -> str:
    """Build a minimal RFC 5545-compliant iCalendar feed."""
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//LifeSignal//Preventive Screenings//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:LifeSignal — {_ics_escape(user_name)}",
    ]
    for ev in events:
        dt = ev["date"].strftime("%Y%m%d")
        # 1-day all-day event: DTSTART (incl) / DTEND (excl, next day).
        end = (ev["date"] + timedelta(days=1)).strftime("%Y%m%d")
        lines += [
            "BEGIN:VEVENT",
            f"UID:{ev['uid']}@lifesignal",
            f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART;VALUE=DATE:{dt}",
            f"DTEND;VALUE=DATE:{end}",
            f"SUMMARY:{_ics_escape(ev['summary'])}",
            f"DESCRIPTION:{_ics_escape(ev['description'])}",
            "BEGIN:VALARM",
            "ACTION:DISPLAY",
            "TRIGGER:-P7D",  # remind 7 days before
            f"DESCRIPTION:{_ics_escape(ev['summary'])}",
            "END:VALARM",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    # CRLF line endings per spec; line-folding is left to clients (our lines are short).
    return "\r\n".join(lines) + "\r\n"


@router.get("/api/users/{user_id}/screenings.ics")
def screenings_ics(
    lang: str = "he",
    user: User = Depends(accessible_profile),
) -> Response:
    """Return an .ics file with one event per recommended screening.

    Events are scheduled 30 days from today by default — a gentle nudge that
    is far enough out to plan and close enough not to be forgotten.
    """
    report = translate_report(report_engine.generate(user), lang)
    base_date = date.today() + timedelta(days=30)
    events: list[dict] = []
    for idx, finding in enumerate(report.missing_screenings):
        # Stagger by a few days so they don't all collapse onto one calendar day.
        when = base_date + timedelta(days=idx * 3)
        events.append({
            "uid": f"{user.id}-screening-{idx}",
            "date": when,
            "summary": finding.title,
            "description": finding.plain_language or finding.detail,
        })

    body = _build_ics(events, user.name)
    return Response(
        content=body,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=lifesignal-screenings.ics",
        },
    )
