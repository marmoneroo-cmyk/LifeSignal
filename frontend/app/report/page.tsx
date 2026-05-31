"use client";

import { useEffect, useState } from "react";
import { Download, Printer } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { FindingCard } from "@/components/FindingCard";
import { Sparkline } from "@/components/Sparkline";
import { MarkerChart } from "@/components/MarkerChart";
import { Disclaimer } from "@/components/Disclaimer";
import { NarrativeCard } from "@/components/NarrativeCard";
import { useReport } from "@/lib/useReport";
import { api, type AnnualReport } from "@/lib/api";
import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import type { Finding } from "@/lib/types";

export default function ReportPage() {
  const { report, error, loading } = useReport();
  const { t } = useT();

  if (loading) return <p className="text-slate-500">{t("report.building")}</p>;
  if (error) return <p className="text-amber-700">{error}</p>;
  if (!report) return null;

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">{t("report.title")}</h1>
          <p className="text-sm text-slate-500">
            {report.user.name} · {report.user.sex === "male" ? t("sex.male") : t("sex.female")}, {report.user.age}
          </p>
        </div>
        <ReportActions userId={report.user.id} name={report.user.name} />
      </header>

      <NarrativeCard userId={report.user.id} />

      <Card>
        <CardHeader><CardTitle>{t("report.scoreByDomain")}</CardTitle></CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {report.score_components.map((c) => (
            <div key={c.domain} className="rounded-lg border border-slate-100 p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-slate-700">{c.domain}</span>
                <span className="text-sm font-semibold text-slate-800">
                  {c.score >= 0 ? c.score : "—"}
                </span>
              </div>
              <div className="mt-2 h-2 rounded-full bg-slate-100">
                <div
                  className="h-2 rounded-full bg-brand"
                  style={{ width: `${c.score >= 0 ? c.score : 0}%` }}
                />
              </div>
              <p className="mt-1 text-xs text-slate-400">{c.note}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>{t("report.labMarkers")}</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          {report.trends.length === 0 && (
            <p className="text-sm text-slate-500">{t("report.noLabData")}</p>
          )}
          <div className="grid gap-4 md:grid-cols-2">
            {report.trends.map((tr) => (
              <div key={tr.marker} className="rounded-lg border border-slate-100 p-3">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-slate-800">{tr.label}</p>
                    <p className="text-xs text-slate-400">
                      {t("report.latest")} {tr.points[tr.points.length - 1]?.value} {tr.unit} · {t(`dir.${tr.direction}`)}
                    </p>
                  </div>
                  <StatusBadge status={tr.status} />
                </div>
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
        </CardContent>
      </Card>

      {report.percentiles.length > 0 && (
        <Card>
          <CardHeader><CardTitle>{t("report.howCompare")}</CardTitle></CardHeader>
          <CardContent className="space-y-2.5">
            {report.percentiles.map((p) => {
              const concerning = p.higher_is_risk ? p.percentile >= 75 : p.percentile <= 25;
              return (
                <div key={p.marker} className="flex items-center gap-3">
                  <span className="w-40 shrink-0 text-sm text-slate-700">{p.label}</span>
                  <div className="relative h-2 flex-1 rounded-full bg-slate-100">
                    <div
                      className={cn("h-2 rounded-full", concerning ? "bg-orange-500" : "bg-brand")}
                      style={{ width: `${p.percentile}%` }}
                    />
                  </div>
                  <span className="w-20 text-right text-xs text-slate-500">
                    {p.percentile} {t("report.percentile")}
                  </span>
                </div>
              );
            })}
            <p className="text-xs text-slate-400">{t("report.percentileNote")}</p>
          </CardContent>
        </Card>
      )}

      <AnnualCard userId={report.user.id} />

      <Section title={t("section.urgent")}      items={report.emergency_alerts} />
      <Section title={t("section.risks")}       items={report.findings} />
      <Section title={t("section.projections")} items={report.projections} />
      <Section title={t("section.secondOpinion")} items={report.second_opinions} />
      <Section title={t("section.drugs")}       items={report.drug_interactions} />
      <Section title={t("section.family")}      items={report.family_insights} />
      <Section title={t("section.screenings")}  items={report.missing_screenings} />
      <Section title={t("section.insurance")}   items={report.insurance_insights} />
      <Section title={t("section.negotiator")}  items={report.insurance_negotiation} />
      <Section title={t("section.claims")}      items={report.claim_opportunities} />
      <Section title={t("section.coverage")}    items={report.coverage_matches} />

      <Disclaimer text={report.disclaimer} />
    </div>
  );
}

function ReportActions({ userId, name }: { userId: number; name: string }) {
  const { t } = useT();

  async function exportJson() {
    const data = await api.exportData(userId);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `lifesignal-${name.replace(/\s+/g, "_").toLowerCase()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="flex gap-2 print:hidden">
      <button
        onClick={() => window.print()}
        className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
      >
        <Printer className="h-4 w-4" /> {t("report.print")}
      </button>
      <button
        onClick={exportJson}
        className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
      >
        <Download className="h-4 w-4" /> {t("report.export")}
      </button>
    </div>
  );
}

function AnnualCard({ userId }: { userId: number }) {
  const { t } = useT();
  const [data, setData] = useState<AnnualReport | null>(null);

  useEffect(() => {
    api.annual(userId).then(setData).catch(() => setData(null));
  }, [userId]);

  if (!data || data.years_covered.length === 0) return null;

  return (
    <Card>
      <CardHeader><CardTitle>{t("report.yearOverYear")}</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {data.years_covered.map((row) => (
          <div key={row.marker} className="flex items-center justify-between border-b border-slate-100 py-2 text-sm last:border-0">
            <span className="font-medium text-slate-700">{row.marker.toUpperCase()}</span>
            <span className="text-slate-500">{row.points.map((p) => `${p.year}: ${p.value}`).join("  →  ")}</span>
            <span className={cn("font-medium", row.change > 0 ? "text-orange-600" : "text-emerald-600")}>
              {row.change > 0 ? "+" : ""}{row.change}
            </span>
          </div>
        ))}
      </CardContent>
    </Card>
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
