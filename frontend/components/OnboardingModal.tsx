"use client";

import { useEffect, useState } from "react";
import { Sparkles, Upload, Plus, X, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";

/**
 * Shown the first time an empty profile lands on the dashboard.
 * Offers two paths: load realistic sample data, or start adding own data.
 * Skips itself once the profile has any data. State is per-profile.
 */
export function OnboardingModal() {
  const { activeProfileId } = useAuth();
  const { lang } = useT();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!activeProfileId) return;
    let cancelled = false;
    const dismissedKey = `ls_onboard_dismissed_${activeProfileId}`;
    if (typeof window !== "undefined" && window.sessionStorage.getItem(dismissedKey)) return;

    (async () => {
      try {
        const { is_empty } = await api.hasData(activeProfileId);
        if (!cancelled && is_empty) setOpen(true);
      } catch {
        // silent: not blocking the dashboard
      }
    })();
    return () => { cancelled = true; };
  }, [activeProfileId]);

  function dismiss() {
    if (activeProfileId && typeof window !== "undefined") {
      window.sessionStorage.setItem(`ls_onboard_dismissed_${activeProfileId}`, "1");
    }
    setOpen(false);
  }

  async function loadSample() {
    if (!activeProfileId) return;
    setBusy(true);
    try {
      await api.loadSample(activeProfileId);
      dismiss();
      router.refresh();
      // Hard reload to re-fetch the report with the new data
      window.location.reload();
    } finally {
      setBusy(false);
    }
  }

  if (!open) return null;

  const he = lang === "he";

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="rounded-lg bg-brand-soft p-2">
              <Sparkles className="h-5 w-5 text-brand" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800">
                {he ? "ברוך הבא ל-LifeSignal" : "Welcome to LifeSignal"}
              </h2>
              <p className="text-sm text-slate-500">
                {he ? "איך תרצה להתחיל?" : "How would you like to get started?"}
              </p>
            </div>
          </div>
          <button onClick={dismiss} className="rounded-lg p-1 text-slate-400 hover:bg-slate-100">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-5 space-y-3">
          <button
            onClick={loadSample}
            disabled={busy}
            className="w-full rounded-xl border-2 border-brand bg-brand-soft p-4 text-start transition hover:bg-teal-100 disabled:opacity-50"
          >
            <div className="flex items-center gap-2">
              {busy ? <Loader2 className="h-4 w-4 animate-spin text-brand" /> : <Sparkles className="h-4 w-4 text-brand" />}
              <span className="font-semibold text-brand-fg">
                {he ? "התחל עם נתוני דוגמה" : "Start with sample data"}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-600">
              {he
                ? "נטען פרופיל מציאותי (בדיקות לאורך 3 שנים, ביטוחים, תרופות, היסטוריה משפחתית) שתוכל לחקור מיד."
                : "Loads a realistic profile (3 years of labs, insurance, medications, family history) so you can explore right away."}
            </p>
          </button>

          <button
            onClick={() => { dismiss(); router.push("/upload"); }}
            className="w-full rounded-xl border border-slate-200 p-4 text-start transition hover:bg-slate-50"
          >
            <div className="flex items-center gap-2">
              <Upload className="h-4 w-4 text-slate-600" />
              <span className="font-semibold text-slate-700">
                {he ? "העלה Excel / PDF של הבדיקות שלך" : "Upload your own Excel / PDF"}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              {he
                ? "תוצאות בדיקה מהמעבדה — המערכת מזהה את הטבלה אוטומטית."
                : "Lab results from your provider — the table is detected automatically."}
            </p>
          </button>

          <button
            onClick={() => { dismiss(); router.push("/labs"); }}
            className="w-full rounded-xl border border-slate-200 p-4 text-start transition hover:bg-slate-50"
          >
            <div className="flex items-center gap-2">
              <Plus className="h-4 w-4 text-slate-600" />
              <span className="font-semibold text-slate-700">
                {he ? "הזן ידנית" : "Enter data manually"}
              </span>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              {he
                ? "הוסף ערכים ופוליסות שדה-שדה."
                : "Add values and policies one by one."}
            </p>
          </button>
        </div>

        <p className="mt-5 text-center text-[11px] text-slate-400">
          {he ? "תמיכה בהחלטות בלבד — אינה אבחנה רפואית." : "Decision support only — not a medical diagnosis."}
        </p>
      </div>
    </div>
  );
}
