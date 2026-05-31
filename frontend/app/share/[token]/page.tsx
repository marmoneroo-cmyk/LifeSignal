"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { Activity, AlertTriangle, ShieldCheck, Printer } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PriorityBadge, StatusBadge } from "@/components/ui/badge";
import { FindingCard } from "@/components/FindingCard";
import { ScoreRing } from "@/components/ScoreRing";
import { Sparkline } from "@/components/Sparkline";
import { Disclaimer } from "@/components/Disclaimer";
import { api } from "@/lib/api";
import { useT } from "@/lib/i18n";
import { LangToggle } from "@/components/LangToggle";
import type { Finding, HealthReport } from "@/lib/types";

interface PageProps {
  params: Promise<{ token: string }>;
}

/**
 * Public read-only report view. No auth required — the unguessable token in
 * the URL is the credential, validated by the backend (expires automatically).
 * Clinicians open this without ever needing to register.
 */
export default function SharedReportPage({ params }: PageProps) {
  const { token } = use(params);
  const { lang } = useT();
  const he = lang === "he";

  const [report, setReport] = useState<HealthReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .viewSharedReport(token, lang)
      .then(setReport)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"));
  }, [token, lang]);

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-16 text-center">
        <AlertTriangle className="mx-auto mb-4 h-10 w-10 text-amber-500" />
        <h1 className="text-2xl font-bold text-slate-800">
          {he ? "הקישור אינו זמין" : "Link unavailable"}
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          {he
            ? "ייתכן שהקישור פג, בוטל, או אינו תקין."
            : "The link may have expired, been revoked, or is invalid."}
        </p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-400">
        {he ? "טוען דוח…" : "Loading report…"}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Public header */}
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 md:px-8">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-brand p-1.5">
            <Activity className="h-4 w-4 text-white" />
          </div>
          <span className="text-base font-bold text-slate-800">LifeSignal</span>
          <span className="ms-2 inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-medium text-emerald-700">
            <ShieldCheck className="h-3 w-3" />
            {he ? "צפייה בלבד · קישור זמני" : "Read-only · time-limited link"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href={`/share/${token}/print`}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
          >
            <Printer className="h-3.5 w-3.5" />
            {he ? "גרסת הדפסה / PDF" : "Print / PDF version"}
          </Link>
          <LangToggle />
        </div>
      </header>

      <div className="mx-auto max-w-5xl space-y-6 px-4 py-6 md:px-8 md:py-10">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">
              {he ? "דוח בריאות" : "Health Report"}
            </h1>
            <p className="text-sm text-slate-500">
              {report.user.name} · {report.user.sex === "male" ? (he ? "זכר" : "Male") : (he ? "נקבה" : "Female")} ·{" "}
              {he ? "גיל" : "age"} {report.user.age}
            </p>
          </div>
        </div>

        {/* Emergency banner */}
        {report.emergency_alerts.length > 0 && (
          <div className="rounded-xl border-2 border-red-300 bg-red-50 p-4">
            <h2 className="font-semibold text-red-700">
              {he ? "מומלצת בדיקה רפואית בהקדם" : "Prompt medical evaluation recommended"}
            </h2>
            <ul className="mt-2 space-y-1 text-sm text-red-800">
              {report.emergency_alerts.map((a, i) => (
                <li key={i}>• {a.plain_language || a.detail}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Score + top priorities */}
        <div className="grid gap-6 md:grid-cols-3">
          <Card className="md:col-span-1">
            <CardHeader>
              <CardTitle>{he ? "ציון בריאות" : "Health Score"}</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center">
              <ScoreRing score={report.health_score} />
            </CardContent>
          </Card>

          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>{he ? "3 הדברים החשובים ביותר" : "Top priorities"}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {report.top_priorities.length === 0 ? (
                <p className="text-sm text-slate-500">{he ? "אין דחיפויות." : "Nothing urgent."}</p>
              ) : (
                report.top_priorities.map((f, i) => <FindingCard key={i} finding={f} />)
              )}
            </CardContent>
          </Card>
        </div>

        {/* Lab trends */}
        {report.trends.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>{he ? "מרקרים ומגמות" : "Lab markers & trends"}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-1">
              {report.trends.map((tr) => (
                <div key={tr.marker} className="flex items-center justify-between gap-4 border-b border-slate-100 py-3 last:border-0">
                  <div className="min-w-0">
                    <p className="font-medium text-slate-800">{tr.label}</p>
                    <p className="text-xs text-slate-400">
                      {tr.points[tr.points.length - 1]?.value} {tr.unit}
                    </p>
                  </div>
                  <Sparkline
                    points={tr.points}
                    stroke={tr.status === "abnormal" ? "#dc2626" : tr.status === "borderline" ? "#d97706" : "#0d9488"}
                  />
                  <StatusBadge status={tr.status} />
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        <Section title={he ? "סיכונים וממצאים" : "Risks & findings"} items={report.findings} />
        <Section title={he ? "אינטראקציות תרופתיות" : "Drug interactions"} items={report.drug_interactions} />
        <Section title={he ? "היסטוריה משפחתית" : "Family history"} items={report.family_insights} />
        <Section title={he ? "בדיקות מונעות מומלצות" : "Recommended screenings"} items={report.missing_screenings} />
        <Section title={he ? "תובנות ביטוח" : "Insurance insights"} items={report.insurance_insights} />

        <Disclaimer text={report.disclaimer} />
      </div>
    </div>
  );
}

function Section({ title, items }: { title: string; items: Finding[] }) {
  if (items.length === 0) return null;
  return (
    <Card>
      <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        {items.map((f, i) => <FindingCard key={i} finding={f} />)}
      </CardContent>
    </Card>
  );
}
