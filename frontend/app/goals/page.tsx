"use client";

import { useEffect, useState } from "react";
import { Target, Plus, Trash2, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Disclaimer } from "@/components/Disclaimer";
import { api, type Goal } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";
import type { MarkerMeta } from "@/lib/types";

export default function GoalsPage() {
  const { activeProfileId } = useAuth();
  const { lang } = useT();
  const he = lang === "he";

  const [goals, setGoals] = useState<Goal[]>([]);
  const [markers, setMarkers] = useState<MarkerMeta[]>([]);
  const [msg, setMsg] = useState<string | null>(null);

  // Form state
  const [marker, setMarker] = useState("ldl");
  const [target, setTarget] = useState("100");
  const [direction, setDirection] = useState<"below" | "above">("below");
  const [deadline, setDeadline] = useState("");
  const [note, setNote] = useState("");

  useEffect(() => {
    if (!activeProfileId) return;
    refresh();
    api.markers().then(setMarkers).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeProfileId]);

  async function refresh() {
    if (!activeProfileId) return;
    try {
      setGoals(await api.listGoals(activeProfileId));
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "error");
    }
  }

  async function addGoal() {
    if (!activeProfileId) return;
    setMsg(null);
    try {
      await api.createGoal(activeProfileId, {
        marker,
        target_value: Number(target),
        direction,
        deadline: deadline || null,
        note,
      });
      setTarget(""); setNote(""); setDeadline("");
      await refresh();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "error");
    }
  }

  async function removeGoal(id: number) {
    if (!activeProfileId) return;
    await api.deleteGoal(activeProfileId, id);
    await refresh();
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">
          {he ? "מטרות בריאות" : "Health Goals"}
        </h1>
        <p className="text-sm text-slate-500">
          {he
            ? "הגדר יעדים מדידים — ה-system יעקוב אחר ההתקדמות שלך לפי בדיקות אמיתיות."
            : "Set measurable targets — the system tracks your progress against real lab values."}
        </p>
      </header>

      {/* Create form */}
      <Card>
        <CardHeader>
          <CardTitle>
            <span className="inline-flex items-center gap-1.5">
              <Plus className="h-4 w-4 text-brand" /> {he ? "מטרה חדשה" : "New goal"}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-5">
            <label className="text-xs text-slate-500 md:col-span-2">
              {he ? "מרקר" : "Marker"}
              <select
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                value={marker}
                onChange={(e) => setMarker(e.target.value)}
              >
                {markers.map((m) => (
                  <option key={m.key} value={m.key}>{m.label}</option>
                ))}
              </select>
            </label>
            <label className="text-xs text-slate-500">
              {he ? "מתחת/מעל" : "Direction"}
              <select
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                value={direction}
                onChange={(e) => setDirection(e.target.value as "below" | "above")}
              >
                <option value="below">{he ? "מתחת ל-" : "Below"}</option>
                <option value="above">{he ? "מעל ל-" : "Above"}</option>
              </select>
            </label>
            <label className="text-xs text-slate-500">
              {he ? "ערך יעד" : "Target value"}
              <input
                type="number"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
              />
            </label>
            <label className="text-xs text-slate-500">
              {he ? "תאריך יעד" : "Deadline"}
              <input
                type="date"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
              />
            </label>
            <input
              placeholder={he ? "הערה (אופציונלי)" : "Note (optional)"}
              className="md:col-span-4 rounded-lg border border-slate-300 px-3 py-2 text-sm"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
            <button
              onClick={addGoal}
              disabled={!target}
              className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg disabled:opacity-50"
            >
              {he ? "הוסף מטרה" : "Add goal"}
            </button>
          </div>
          {msg && <p className="mt-2 text-sm text-amber-700">{msg}</p>}
        </CardContent>
      </Card>

      {/* Active goals */}
      {goals.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-sm text-slate-500">
            {he
              ? "אין עדיין מטרות. הוסף מטרה ראשונה למעלה."
              : "No goals yet. Add your first one above."}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {goals.map((g) => (
            <Card key={g.id}>
              <CardContent className="py-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-800">
                      {g.label}{" "}
                      <span className="text-slate-400">
                        {g.direction === "below" ? (he ? "מתחת ל-" : "below ") : (he ? "מעל ל-" : "above ")}
                        {g.target_value} {g.unit}
                      </span>
                    </h3>
                    {g.note && <p className="text-xs text-slate-500">{g.note}</p>}

                    <div className="mt-3 flex items-center gap-3">
                      <div className="relative h-2 flex-1 rounded-full bg-slate-100">
                        <div
                          className={cn(
                            "h-2 rounded-full transition-all",
                            g.achieved ? "bg-emerald-500" : "bg-brand",
                          )}
                          style={{ width: `${g.progress_pct}%` }}
                        />
                      </div>
                      <span className="w-20 text-end text-xs font-medium text-slate-700">
                        {g.achieved ? (
                          <span className="inline-flex items-center gap-1 text-emerald-600">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            {he ? "הושג!" : "Met!"}
                          </span>
                        ) : (
                          `${g.progress_pct}%`
                        )}
                      </span>
                    </div>

                    <p className="mt-1 text-[11px] text-slate-400">
                      {he ? "נוכחי: " : "Latest: "}
                      {g.latest_value !== null
                        ? `${g.latest_value} ${g.unit} (${g.latest_taken_on})`
                        : he ? "אין בדיקות עדיין" : "no labs yet"}
                      {g.deadline && (
                        <> · {he ? "יעד: " : "due "}{g.deadline}</>
                      )}
                    </p>
                  </div>
                  <button
                    onClick={() => removeGoal(g.id)}
                    className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-red-500"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Disclaimer text={he
        ? "ההתקדמות מחושבת מול הבדיקה האחרונה במערכת. אינה תחליף להתייעצות עם רופא."
        : "Progress is computed against your latest stored lab. Not a substitute for medical advice."} />
    </div>
  );
}
