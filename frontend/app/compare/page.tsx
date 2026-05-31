"use client";

import { useEffect, useMemo, useState } from "react";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Disclaimer } from "@/components/Disclaimer";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";

/**
 * Side-by-side comparison of two time periods. Useful for: "before/after a
 * treatment", "this year vs last year", "first lab vs latest". Picks the
 * single closest value to each period's end-date for each marker.
 */

interface ExportShape {
  lab_results: { marker: string; value: number; unit: string; taken_on: string }[];
}

interface RowDiff {
  marker: string;
  unit: string;
  before: { value: number; date: string } | null;
  after: { value: number; date: string } | null;
  delta: number | null;       // after - before, when both exist
  pctChange: number | null;   // (after - before) / before * 100
}

function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}
function monthsAgoISO(months: number): string {
  const d = new Date();
  d.setMonth(d.getMonth() - months);
  return d.toISOString().slice(0, 10);
}

export default function ComparePage() {
  const { activeProfileId } = useAuth();
  const { lang } = useT();
  const he = lang === "he";

  const [data, setData] = useState<ExportShape | null>(null);
  const [periodA, setPeriodA] = useState({ start: monthsAgoISO(24), end: monthsAgoISO(12) });
  const [periodB, setPeriodB] = useState({ start: monthsAgoISO(12), end: todayISO() });

  useEffect(() => {
    if (!activeProfileId) return;
    api.exportData(activeProfileId).then((d) => setData(d as ExportShape)).catch(() => setData(null));
  }, [activeProfileId]);

  const rows = useMemo<RowDiff[]>(() => {
    if (!data) return [];
    return buildDiffs(data.lab_results, periodA, periodB);
  }, [data, periodA, periodB]);

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">
          {he ? "השוואת תקופות" : "Compare periods"}
        </h1>
        <p className="text-sm text-slate-500">
          {he
            ? "בחר שתי תקופות (לפני/אחרי טיפול, שנה מול שנה) וראה איך כל מרקר השתנה."
            : "Pick two periods (before/after treatment, year over year) and see how each marker changed."}
        </p>
      </header>

      {/* Period pickers */}
      <Card>
        <CardHeader>
          <CardTitle>{he ? "טווחי זמן" : "Time ranges"}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <PeriodPicker
              label={he ? "תקופה א (לפני)" : "Period A (before)"}
              value={periodA}
              onChange={setPeriodA}
            />
            <PeriodPicker
              label={he ? "תקופה ב (אחרי)" : "Period B (after)"}
              value={periodB}
              onChange={setPeriodB}
            />
          </div>
        </CardContent>
      </Card>

      {/* Diff table */}
      <Card>
        <CardHeader>
          <CardTitle>{he ? "מה השתנה" : "What changed"}</CardTitle>
        </CardHeader>
        <CardContent>
          {!data ? (
            <p className="text-sm text-slate-500">{he ? "טוען…" : "Loading…"}</p>
          ) : rows.length === 0 ? (
            <p className="text-sm text-slate-500">
              {he ? "אין נתונים בתקופות שנבחרו." : "No data in the selected periods."}
            </p>
          ) : (
            <div className="overflow-hidden rounded-lg border border-slate-200">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-xs text-slate-500">
                  <tr>
                    <th className="px-3 py-2 text-start">{he ? "מרקר" : "Marker"}</th>
                    <th className="px-3 py-2 text-start">{he ? "תקופה א" : "Period A"}</th>
                    <th className="px-3 py-2 text-start">{he ? "תקופה ב" : "Period B"}</th>
                    <th className="px-3 py-2 text-start">{he ? "שינוי" : "Change"}</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.marker} className="border-t border-slate-100">
                      <td className="px-3 py-2 font-medium uppercase text-slate-700">{r.marker}</td>
                      <td className="px-3 py-2">
                        {r.before ? `${r.before.value} ${r.unit}` : "—"}
                        {r.before && <span className="ms-1 text-xs text-slate-400">({r.before.date})</span>}
                      </td>
                      <td className="px-3 py-2">
                        {r.after ? `${r.after.value} ${r.unit}` : "—"}
                        {r.after && <span className="ms-1 text-xs text-slate-400">({r.after.date})</span>}
                      </td>
                      <td className="px-3 py-2">
                        <DeltaCell delta={r.delta} pct={r.pctChange} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      <Disclaimer text={he
        ? "ההשוואה היא בין הערכים הקרובים ביותר לסוף כל תקופה. אינה תחליף לייעוץ רפואי."
        : "Comparison uses the value closest to the end of each period. Not medical advice."} />
    </div>
  );
}

function PeriodPicker({
  label, value, onChange,
}: {
  label: string;
  value: { start: string; end: string };
  onChange: (v: { start: string; end: string }) => void;
}) {
  return (
    <div>
      <p className="mb-2 text-sm font-medium text-slate-700">{label}</p>
      <div className="grid grid-cols-2 gap-2">
        <input
          type="date"
          value={value.start}
          onChange={(e) => onChange({ ...value, start: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
        <input
          type="date"
          value={value.end}
          onChange={(e) => onChange({ ...value, end: e.target.value })}
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        />
      </div>
    </div>
  );
}

function DeltaCell({ delta, pct }: { delta: number | null; pct: number | null }) {
  if (delta === null) return <span className="text-slate-400">—</span>;
  const Icon = delta > 0 ? TrendingUp : delta < 0 ? TrendingDown : Minus;
  const color = delta > 0 ? "text-orange-600" : delta < 0 ? "text-emerald-600" : "text-slate-500";
  const sign = delta > 0 ? "+" : "";
  return (
    <span className={cn("inline-flex items-center gap-1 font-medium", color)}>
      <Icon className="h-3.5 w-3.5" />
      {sign}{delta.toFixed(1)}
      {pct !== null && <span className="text-xs opacity-70">({sign}{pct.toFixed(0)}%)</span>}
    </span>
  );
}

function buildDiffs(
  labs: ExportShape["lab_results"],
  periodA: { start: string; end: string },
  periodB: { start: string; end: string },
): RowDiff[] {
  const byMarker = new Map<string, ExportShape["lab_results"]>();
  for (const r of labs) {
    if (!byMarker.has(r.marker)) byMarker.set(r.marker, []);
    byMarker.get(r.marker)!.push(r);
  }
  const out: RowDiff[] = [];
  for (const [marker, rows] of byMarker.entries()) {
    const before = closestInPeriod(rows, periodA);
    const after = closestInPeriod(rows, periodB);
    if (!before && !after) continue;
    const delta = before && after ? +(after.value - before.value).toFixed(2) : null;
    const pct = before && after && before.value !== 0
      ? +(delta! / Math.abs(before.value) * 100).toFixed(0)
      : null;
    out.push({
      marker,
      unit: rows[0].unit,
      before: before ? { value: before.value, date: before.taken_on } : null,
      after: after ? { value: after.value, date: after.taken_on } : null,
      delta,
      pctChange: pct,
    });
  }
  out.sort((a, b) => Math.abs(b.delta ?? 0) - Math.abs(a.delta ?? 0));
  return out;
}

function closestInPeriod(
  rows: ExportShape["lab_results"],
  period: { start: string; end: string },
): ExportShape["lab_results"][number] | null {
  const inRange = rows.filter((r) => r.taken_on >= period.start && r.taken_on <= period.end);
  if (inRange.length === 0) return null;
  return inRange.reduce((latest, r) => (r.taken_on > latest.taken_on ? r : latest));
}
