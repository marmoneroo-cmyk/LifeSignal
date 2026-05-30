"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { Disclaimer } from "@/components/Disclaimer";
import { useReport } from "@/lib/useReport";
import { useT } from "@/lib/i18n";

export default function TimelinePage() {
  const { report, error, loading } = useReport();
  const { t } = useT();

  if (loading) return <p className="text-slate-500">{t("common.loading")}</p>;
  if (error) return <p className="text-amber-700">{error}</p>;
  if (!report) return null;

  const events = report.trends
    .flatMap((tr) =>
      tr.points.map((p) => ({
        date: p.taken_on,
        label: `${tr.label}: ${p.value} ${tr.unit}`,
        status: tr.status,
      }))
    )
    .sort((a, b) => (a.date < b.date ? 1 : -1));

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">{t("timeline.title")}</h1>
        <p className="text-sm text-slate-500">{t("timeline.subtitle")}</p>
      </header>

      <Card>
        <CardHeader><CardTitle>{t("timeline.events")}</CardTitle></CardHeader>
        <CardContent>
          {events.length === 0 && (
            <p className="text-sm text-slate-500">{t("timeline.noEvents")}</p>
          )}
          <ol className="relative border-s border-slate-200 ps-6">
            {events.map((e, i) => (
              <li key={i} className="mb-5 last:mb-0">
                <span className="absolute -start-[7px] mt-1.5 h-3 w-3 rounded-full bg-brand" />
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium text-slate-800">{e.label}</p>
                    <p className="text-xs text-slate-400">{e.date}</p>
                  </div>
                  {e.status && <StatusBadge status={e.status} />}
                </div>
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>

      <Disclaimer text={report.disclaimer} />
    </div>
  );
}
