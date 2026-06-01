"use client";

import { useEffect, useState } from "react";
import {
  Users, FlaskConical, ShieldCheck, Pill, Heart,
  Target, Link2, Activity,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Disclaimer } from "@/components/Disclaimer";
import { useT } from "@/lib/i18n";
import { API_BASE } from "@/lib/api";

interface Stats {
  profiles: number;
  labs: number;
  policies: number;
  medications: number;
  family_members: number;
  goals: number;
  active_shares: number;
  latest_lab: { marker: string; value: number; unit: string; taken_on: string } | null;
}

export default function AdminPage() {
  const { lang } = useT();
  const he = lang === "he";
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch via the shared `req` helper isn't exported as such — call raw API.
    const token = typeof window !== "undefined" ? window.localStorage.getItem("ls_token") : null;
    fetch(`${API_BASE}/api/admin/stats`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      cache: "no-store",
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`API ${r.status}`))))
      .then(setStats)
      .catch((e) => setError(e instanceof Error ? e.message : "failed"));
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">
          {he ? "סטטיסטיקות חשבון" : "Account Stats"}
        </h1>
        <p className="text-sm text-slate-500">
          {he
            ? "סיכום הנתונים על פני כל הפרופילים שאתה מנהל."
            : "Aggregate counts across all profiles you manage."}
        </p>
      </header>

      {error && (
        <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">{error}</p>
      )}

      {!stats && !error && <p className="text-sm text-slate-500">{he ? "טוען…" : "Loading…"}</p>}

      {stats && (
        <>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <Stat label={he ? "פרופילים" : "Profiles"}        value={stats.profiles}        icon={<Users className="h-4 w-4" />} />
            <Stat label={he ? "תוצאות בדיקה" : "Lab results"} value={stats.labs}            icon={<FlaskConical className="h-4 w-4" />} />
            <Stat label={he ? "פוליסות" : "Policies"}         value={stats.policies}        icon={<ShieldCheck className="h-4 w-4" />} />
            <Stat label={he ? "תרופות" : "Medications"}       value={stats.medications}     icon={<Pill className="h-4 w-4" />} />
            <Stat label={he ? "קרובי משפחה" : "Family"}       value={stats.family_members}  icon={<Heart className="h-4 w-4" />} />
            <Stat label={he ? "מטרות" : "Goals"}              value={stats.goals}           icon={<Target className="h-4 w-4" />} />
            <Stat label={he ? "קישורים פעילים" : "Active links"} value={stats.active_shares} icon={<Link2 className="h-4 w-4" />} />
            <Stat label={he ? "סטטוס" : "Status"} value="OK" icon={<Activity className="h-4 w-4" />} />
          </div>

          {stats.latest_lab && (
            <Card>
              <CardContent className="py-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  {he ? "התוצאה החדשה ביותר" : "Latest lab result"}
                </p>
                <p className="mt-1 text-lg font-semibold text-slate-800">
                  {stats.latest_lab.marker.toUpperCase()}: {stats.latest_lab.value} {stats.latest_lab.unit}
                </p>
                <p className="text-xs text-slate-400">{stats.latest_lab.taken_on}</p>
              </CardContent>
            </Card>
          )}
        </>
      )}

      <Disclaimer text={he
        ? "סטטיסטיקות אלו מציגות נתונים על חשבונך בלבד."
        : "These stats only reflect data on your own account."} />
    </div>
  );
}

function Stat({ label, value, icon }: { label: string; value: number | string; icon: React.ReactNode }) {
  return (
    <Card>
      <CardContent className="py-4">
        <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-slate-500">
          {icon}
          <span>{label}</span>
        </div>
        <p className="mt-2 text-2xl font-bold text-slate-800">{value}</p>
      </CardContent>
    </Card>
  );
}
