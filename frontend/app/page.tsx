"use client";

import Link from "next/link";
import { AlertTriangle, ShieldCheck, Stethoscope, Bell, Siren } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScoreRing } from "@/components/ScoreRing";
import { FindingCard } from "@/components/FindingCard";
import { PriorityBadge } from "@/components/ui/badge";
import { Disclaimer } from "@/components/Disclaimer";
import { useReport } from "@/lib/useReport";
import { useT } from "@/lib/i18n";
import { OnboardingModal } from "@/components/OnboardingModal";
import type { Finding } from "@/lib/types";

export default function DashboardPage() {
  const { report, error, loading } = useReport();
  const { t } = useT();

  if (loading) return <p className="text-slate-500">{t("dash.loading")}</p>;
  if (error)
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{error}</div>
    );
  if (!report) return null;

  const sex = report.user.sex === "male" ? t("sex.male") : t("sex.female");

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <OnboardingModal />
      <header>
        <h1 className="text-2xl font-bold text-slate-800">
          {t("dash.hello", { name: report.user.name.split(" ")[0] })}
        </h1>
        <p className="text-sm text-slate-500">
          {t("dash.subtitle", { sex, age: report.user.age })}
        </p>
      </header>

      {report.emergency_alerts.length > 0 && (
        <div className="rounded-xl border-2 border-red-300 bg-red-50 p-4">
          <div className="flex items-center gap-2 text-red-700">
            <Siren className="h-5 w-5" />
            <h2 className="font-semibold">{t("dash.emergencyTitle")}</h2>
          </div>
          <ul className="mt-2 space-y-1 text-sm text-red-800">
            {report.emergency_alerts.map((a, i) => (
              <li key={i}>• {a.plain_language || a.detail}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-1">
          <CardHeader><CardTitle>{t("dash.healthScore")}</CardTitle></CardHeader>
          <CardContent className="flex flex-col items-center">
            <ScoreRing score={report.health_score} />
            <p className="mt-3 text-center text-xs text-slate-400">
              {t("dash.scoreFooter", {
                n: report.score_components.filter((c) => c.score >= 0).length,
              })}
            </p>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>
              <span className="inline-flex items-center gap-1.5">
                <AlertTriangle className="h-4 w-4 text-orange-500" />
                {t("dash.topThree")}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {report.top_priorities.length === 0 && (
              <p className="text-sm text-slate-500">{t("dash.nothingUrgent")}</p>
            )}
            {report.top_priorities.map((f, i) => (
              <FindingCard key={i} finding={f} />
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <DashCard
          icon={<Stethoscope className="h-4 w-4 text-teal-600" />}
          title={t("dash.missingScreenings")}
          items={report.missing_screenings}
          href="/report"
          moreLabel={t("dash.more", { n: 0 })}
        />
        <DashCard
          icon={<ShieldCheck className="h-4 w-4 text-teal-600" />}
          title={t("dash.insuranceInsights")}
          items={report.insurance_insights}
          href="/report"
          moreLabel={t("dash.more", { n: 0 })}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            <span className="inline-flex items-center gap-1.5">
              <Bell className="h-4 w-4 text-teal-600" /> {t("dash.reminders")}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {report.notifications.length === 0 && (
            <p className="text-sm text-slate-500">{t("dash.noReminders")}</p>
          )}
          {report.notifications.map((n, i) => (
            <div key={i} className="flex items-center justify-between border-b border-slate-100 py-2 last:border-0">
              <span className="text-sm text-slate-700">{n.title}</span>
              <PriorityBadge priority={n.priority} />
            </div>
          ))}
        </CardContent>
      </Card>

      <Disclaimer text={report.disclaimer} />
    </div>
  );
}

function DashCard({
  icon, title, items, href, moreLabel,
}: {
  icon: React.ReactNode;
  title: string;
  items: Finding[];
  href: string;
  moreLabel: string;
}) {
  const { t } = useT();
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="inline-flex items-center gap-1.5">{icon} {title}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {items.slice(0, 4).map((it, i) => (
          <div key={i} className="flex items-center justify-between gap-2">
            <span className="text-sm text-slate-700">{it.title}</span>
            <PriorityBadge priority={it.priority} />
          </div>
        ))}
        {items.length > 4 && (
          <Link href={href} className="text-xs font-medium text-brand-fg hover:underline">
            {t("dash.more", { n: items.length - 4 })}
          </Link>
        )}
        {items.length === 0 && <p className="text-sm text-slate-500">{t("common.nothingFlagged")}</p>}
      </CardContent>
    </Card>
  );
}
