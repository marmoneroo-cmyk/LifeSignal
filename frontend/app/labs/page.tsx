"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import type { MarkerMeta } from "@/lib/types";

interface Row { marker: string; value: string; taken_on: string }
const today = () => new Date().toISOString().slice(0, 10);

export default function LabsPage() {
  const { activeProfileId } = useAuth();
  const { t } = useT();
  const [markers, setMarkers] = useState<MarkerMeta[]>([]);
  const [rows, setRows] = useState<Row[]>([{ marker: "ldl", value: "", taken_on: today() }]);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    api.markers().then(setMarkers).catch(() => setMsg(t("common.apiError")));
  }, []);

  const update = (i: number, patch: Partial<Row>) =>
    setRows((r) => r.map((row, idx) => (idx === i ? { ...row, ...patch } : row)));

  async function submit() {
    setMsg(null);
    try {
      if (!activeProfileId) return setMsg(t("common.noProfile"));
      const results = rows.filter((r) => r.value !== "").map((r) => ({
        marker: r.marker, value: Number(r.value), taken_on: r.taken_on,
      }));
      if (!results.length) return setMsg(t("labs.enterValue"));
      const res = (await api.addLabs(activeProfileId, results)) as { added: number };
      setMsg(t("labs.saved", { n: res.added }));
      setRows([{ marker: "ldl", value: "", taken_on: today() }]);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : t("labs.failed"));
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">{t("labs.title")}</h1>
        <p className="text-sm text-slate-500">{t("labs.subtitle")}</p>
      </header>
      <Card>
        <CardHeader><CardTitle>{t("labs.new")}</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {rows.map((row, i) => {
            const meta = markers.find((m) => m.key === row.marker);
            return (
              <div key={i} className="flex items-end gap-2">
                <label className="flex-1 text-xs text-slate-500">
                  {t("labs.marker")}
                  <select className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                    value={row.marker} onChange={(e) => update(i, { marker: e.target.value })}>
                    {markers.map((m) => <option key={m.key} value={m.key}>{m.label}</option>)}
                  </select>
                </label>
                <label className="w-28 text-xs text-slate-500">
                  {t("labs.value")} {meta ? `(${meta.unit})` : ""}
                  <input type="number" className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                    value={row.value} onChange={(e) => update(i, { value: e.target.value })} />
                </label>
                <label className="w-40 text-xs text-slate-500">
                  {t("labs.date")}
                  <input type="date" className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                    value={row.taken_on} onChange={(e) => update(i, { taken_on: e.target.value })} />
                </label>
                <button className="mb-0.5 rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-red-500"
                  onClick={() => setRows((r) => r.filter((_, idx) => idx !== i))}>
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            );
          })}
          <button className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-fg hover:underline"
            onClick={() => setRows((r) => [...r, { marker: "ldl", value: "", taken_on: today() }])}>
            <Plus className="h-4 w-4" /> {t("labs.addAnother")}
          </button>
          <div className="flex items-center gap-3 pt-2">
            <button className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg" onClick={submit}>
              {t("labs.save")}
            </button>
            {msg && <span className="text-sm text-slate-600">{msg}</span>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
