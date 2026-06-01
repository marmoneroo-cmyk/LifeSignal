"use client";

import { use, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useT } from "@/lib/i18n";
import { MarkerChart } from "@/components/MarkerChart";
import type { Finding, HealthReport } from "@/lib/types";

interface PageProps {
  params: Promise<{ token: string }>;
}

/**
 * Print-optimized view of a shared report.
 *
 * Designed for clinicians: A4 layout, no navigation, no interactive widgets,
 * black-on-white styling, page-break-friendly section ordering. Triggers the
 * browser print dialog automatically once the report is loaded (one shot per
 * page load) so "open link → save as PDF" is a one-click flow.
 *
 * Auth is bypassed for /share/* (handled by AuthGate's PUBLIC_PREFIXES);
 * the unguessable URL token is the only credential.
 */
export default function SharedReportPrintPage({ params }: PageProps) {
  const { token } = use(params);
  const { lang } = useT();
  const he = lang === "he";

  const [report, setReport] = useState<HealthReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [autoPrinted, setAutoPrinted] = useState(false);

  useEffect(() => {
    api
      .viewSharedReport(token, lang)
      .then(setReport)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, [token, lang]);

  // Open the browser print dialog once the report has rendered. One shot only.
  useEffect(() => {
    if (!report || autoPrinted) return;
    setAutoPrinted(true);
    // Small delay so the DOM finishes layout (charts, etc.) before printing.
    const t = setTimeout(() => window.print(), 600);
    return () => clearTimeout(t);
  }, [report, autoPrinted]);

  if (error) {
    return (
      <div className="mx-auto max-w-md px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-slate-800">
          {he ? "הקישור אינו זמין" : "Link unavailable"}
        </h1>
        <p className="mt-2 text-sm text-slate-500">{error}</p>
      </div>
    );
  }
  if (!report) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-400">
        {he ? "טוען…" : "Loading…"}
      </div>
    );
  }

  const issued = new Date().toLocaleDateString(he ? "he-IL" : "en-US", {
    day: "2-digit", month: "long", year: "numeric",
  });

  return (
    <div className="print-page mx-auto max-w-3xl bg-white p-8 text-slate-900 print:p-0 print:max-w-none">
      {/* Print-only manual button — hidden on screen by being inside print:hidden inverted */}
      <div className="print:hidden mb-4 flex items-center justify-between border-b border-slate-200 pb-3">
        <span className="text-xs text-slate-500">
          {he
            ? "תיבת ההדפסה אמורה להיפתח אוטומטית. אם לא — לחץ על הכפתור."
            : "The print dialog should open automatically. If not — click the button."}
        </span>
        <button
          onClick={() => window.print()}
          className="rounded-lg bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-700"
        >
          {he ? "הדפסה / שמירה כ-PDF" : "Print / Save as PDF"}
        </button>
      </div>

      {/* Header */}
      <header className="mb-6 border-b-2 border-slate-900 pb-4">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-bold">
              {he ? "דוח אינטליגנציה בריאותית" : "Health Intelligence Report"}
            </h1>
            <p className="mt-1 text-sm text-slate-600">
              {he ? "נוצר ע״י" : "Produced by"} LifeSignal · {issued}
            </p>
          </div>
          <div className="text-end text-xs text-slate-500">
            <p>
              <strong>{report.user.name}</strong>
            </p>
            <p>
              {report.user.sex === "male" ? (he ? "זכר" : "Male") : (he ? "נקבה" : "Female")} ·{" "}
              {he ? "גיל" : "age"} {report.user.age}
            </p>
            <p>
              {he ? "ציון בריאות:" : "Health score:"} <strong>{report.health_score}/100</strong>
            </p>
          </div>
        </div>
      </header>

      {/* Emergency banner — prominent on print */}
      {report.emergency_alerts.length > 0 && (
        <section className="mb-6 break-inside-avoid border-2 border-red-700 p-3">
          <h2 className="text-base font-bold text-red-800">
            ⚠ {he ? "מומלצת בדיקה רפואית בהקדם" : "Prompt medical evaluation recommended"}
          </h2>
          <ul className="mt-2 ms-5 list-disc text-sm">
            {report.emergency_alerts.map((a, i) => (
              <li key={i}>{a.plain_language || a.detail}</li>
            ))}
          </ul>
        </section>
      )}

      <PrintSection title={he ? "3 הדברים החשובים ביותר" : "Top priorities"} items={report.top_priorities} />

      {/* Lab markers as a compact table — print-friendly */}
      {report.trends.length > 0 && (
        <section className="mb-6 break-inside-avoid">
          <h2 className="mb-2 border-b border-slate-300 pb-1 text-base font-bold">
            {he ? "מרקרים אחרונים" : "Latest lab markers"}
          </h2>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-300 text-start text-xs uppercase text-slate-500">
                <th className="py-1 text-start font-semibold">{he ? "בדיקה" : "Marker"}</th>
                <th className="py-1 text-start font-semibold">{he ? "ערך אחרון" : "Latest"}</th>
                <th className="py-1 text-start font-semibold">{he ? "תאריך" : "Date"}</th>
                <th className="py-1 text-start font-semibold">{he ? "טווח תקין" : "Normal range"}</th>
                <th className="py-1 text-start font-semibold">{he ? "מגמה" : "Trend"}</th>
                <th className="py-1 text-start font-semibold">{he ? "סטטוס" : "Status"}</th>
              </tr>
            </thead>
            <tbody>
              {report.trends.map((tr) => {
                const last = tr.points[tr.points.length - 1];
                const ref =
                  tr.ref_low !== undefined && tr.ref_low !== null
                    ? `${tr.ref_low}–${tr.ref_high ?? "∞"}`
                    : "—";
                const statusColor =
                  tr.status === "abnormal" ? "text-red-700 font-semibold" :
                  tr.status === "borderline" ? "text-orange-700" : "";
                return (
                  <tr key={tr.marker} className="border-b border-slate-100">
                    <td className="py-1 pe-2">{tr.label}</td>
                    <td className="py-1 pe-2">
                      {last?.value} {tr.unit}
                    </td>
                    <td className="py-1 pe-2 text-slate-500">{last?.taken_on}</td>
                    <td className="py-1 pe-2 text-slate-500">{ref} {tr.unit}</td>
                    <td className="py-1 pe-2">{tr.direction}</td>
                    <td className={`py-1 ${statusColor}`}>{tr.status}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </section>
      )}

      {/* Trend charts — only markers with ≥2 data points, in a 2-column grid */}
      {report.trends.some((t) => t.points.length >= 2) && (
        <section className="mb-6 break-inside-avoid">
          <h2 className="mb-2 border-b border-slate-300 pb-1 text-base font-bold">
            {he ? "מגמות לאורך זמן" : "Trends over time"}
          </h2>
          <div className="grid grid-cols-2 gap-3">
            {report.trends.filter((t) => t.points.length >= 2).map((tr) => (
              <div key={tr.marker} className="break-inside-avoid rounded border border-slate-200 p-2">
                <p className="mb-1 truncate text-xs font-semibold">{tr.label}</p>
                <MarkerChart
                  label={tr.label}
                  unit={tr.unit}
                  points={tr.points}
                  status={tr.status}
                  refLow={tr.ref_low}
                  refHigh={tr.ref_high}
                />
              </div>
            ))}
          </div>
        </section>
      )}

      <PrintSection title={he ? "סיכונים וממצאים" : "Risks & findings"} items={report.findings} />
      <PrintSection title={he ? "אינטראקציות תרופתיות" : "Drug interactions"} items={report.drug_interactions} />
      <PrintSection title={he ? "היסטוריה משפחתית" : "Family history & inherited risk"} items={report.family_insights} />
      <PrintSection title={he ? "בדיקות מונעות מומלצות" : "Recommended preventive screenings"} items={report.missing_screenings} />
      <PrintSection title={he ? "תובנות ביטוח" : "Insurance insights"} items={report.insurance_insights} />

      {/* Footer — disclaimer always on the last page */}
      <footer className="mt-8 border-t-2 border-slate-900 pt-3 text-xs text-slate-700 print:fixed print:bottom-0 print:start-0 print:end-0 print:bg-white">
        <p className="font-semibold">{he ? "כתב הוויתור הרפואי" : "Medical disclaimer"}</p>
        <p className="mt-1">{report.disclaimer}</p>
        <p className="mt-2 text-slate-400">
          {he ? "נוצר ע״י" : "Generated by"} LifeSignal — life-signal-one.vercel.app
        </p>
      </footer>

      {/* Print-only stylesheet — A4 margins, hide screen-only chrome, force B/W feel */}
      <style jsx global>{`
        @media print {
          @page { size: A4; margin: 16mm; }
          html, body { background: white !important; }
          .print-page { padding: 0 !important; max-width: none !important; }
          /* Hide everything else from the app shell if it leaked in. */
          aside, nav[role="navigation"] { display: none !important; }
        }
      `}</style>
    </div>
  );
}

/**
 * Compact print section: title + bullet list of findings. Hides itself if empty
 * so the printout doesn't waste paper on "Nothing found." pages.
 */
function PrintSection({ title, items }: { title: string; items: Finding[] }) {
  if (items.length === 0) return null;
  return (
    <section className="mb-5 break-inside-avoid">
      <h2 className="mb-2 border-b border-slate-300 pb-1 text-base font-bold">{title}</h2>
      <ul className="space-y-2 text-sm">
        {items.map((f, i) => (
          <li key={i}>
            <p className="font-semibold">
              {f.title}
              <span className="ms-2 text-xs uppercase text-slate-500">[{f.priority}]</span>
            </p>
            {f.plain_language && <p className="text-slate-700">{f.plain_language}</p>}
            {f.detail && f.detail !== f.plain_language && (
              <p className="text-xs text-slate-500">{f.detail}</p>
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
