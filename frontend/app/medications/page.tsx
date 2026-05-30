"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";

interface Row { name: string; dose: string }

export default function MedicationsPage() {
  const { activeProfileId } = useAuth();
  const { t } = useT();
  const [drugs, setDrugs] = useState<{ key: string; label: string }[]>([]);
  const [rows, setRows] = useState<Row[]>([{ name: "", dose: "" }]);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!activeProfileId) return;
    api.knownDrugs(activeProfileId).then(setDrugs).catch(() => setMsg(t("common.apiError")));
  }, [activeProfileId]);

  const update = (i: number, patch: Partial<Row>) =>
    setRows((r) => r.map((row, idx) => (idx === i ? { ...row, ...patch } : row)));

  async function submit() {
    setMsg(null);
    try {
      if (!activeProfileId) return setMsg(t("common.noProfile"));
      const meds = rows.filter((r) => r.name).map((r) => ({ name: r.name, dose: r.dose }));
      if (!meds.length) return setMsg(t("med.needOne"));
      const res = (await api.addMedications(activeProfileId, meds)) as { added: number; unrecognized: string[] };
      const extra = res.unrecognized?.length ? ` (${res.unrecognized.length} לא זוהו)` : "";
      setMsg(t("med.saved", { n: res.added }) + extra);
      setRows([{ name: "", dose: "" }]);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : t("common.apiError"));
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">{t("med.title")}</h1>
        <p className="text-sm text-slate-500">{t("med.subtitle")}</p>
      </header>
      <Card>
        <CardHeader><CardTitle>{t("med.your")}</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {rows.map((row, i) => (
            <div key={i} className="flex items-end gap-2">
              <label className="flex-1 text-xs text-slate-500">
                {t("med.medication")}
                <input list="known-drugs"
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  value={row.name} placeholder="aspirin, warfarin…"
                  onChange={(e) => update(i, { name: e.target.value })} />
              </label>
              <label className="w-32 text-xs text-slate-500">
                {t("med.dose")}
                <input className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  value={row.dose} onChange={(e) => update(i, { dose: e.target.value })} />
              </label>
              <button className="mb-0.5 rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-red-500"
                onClick={() => setRows((r) => r.filter((_, idx) => idx !== i))}>
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
          <datalist id="known-drugs">
            {drugs.map((d) => <option key={d.key} value={d.key} label={d.label} />)}
          </datalist>
          <button className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-fg hover:underline"
            onClick={() => setRows((r) => [...r, { name: "", dose: "" }])}>
            <Plus className="h-4 w-4" /> {t("med.addAnother")}
          </button>
          <div className="flex items-center gap-3 pt-2">
            <button className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg" onClick={submit}>
              {t("med.save")}
            </button>
            {msg && <span className="text-sm text-slate-600">{msg}</span>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
