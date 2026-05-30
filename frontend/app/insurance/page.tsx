"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import type { CoverageMeta } from "@/lib/types";

interface Row { provider: string; coverage_type: string; monthly_premium: string; renewal_date: string }
const empty = (): Row => ({ provider: "", coverage_type: "health_basic", monthly_premium: "", renewal_date: "" });

export default function InsurancePage() {
  const { activeProfileId } = useAuth();
  const { t } = useT();
  const [types, setTypes] = useState<CoverageMeta[]>([]);
  const [rows, setRows] = useState<Row[]>([empty()]);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    api.coverageTypes().then(setTypes).catch(() => setMsg(t("common.apiError")));
  }, []);

  const update = (i: number, patch: Partial<Row>) =>
    setRows((r) => r.map((row, idx) => (idx === i ? { ...row, ...patch } : row)));

  async function submit() {
    setMsg(null);
    try {
      if (!activeProfileId) return setMsg(t("common.noProfile"));
      const policies = rows.filter((r) => r.provider.trim()).map((r) => ({
        provider: r.provider, coverage_type: r.coverage_type,
        monthly_premium: Number(r.monthly_premium || 0), renewal_date: r.renewal_date || null,
      }));
      if (!policies.length) return setMsg(t("ins.needOne"));
      const res = (await api.addPolicies(activeProfileId, policies)) as { added: number };
      setMsg(t("ins.saved", { n: res.added }));
      setRows([empty()]);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : t("common.apiError"));
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">{t("ins.title")}</h1>
        <p className="text-sm text-slate-500">{t("ins.subtitle")}</p>
      </header>
      <Card>
        <CardHeader><CardTitle>{t("ins.policies")}</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {rows.map((row, i) => (
            <div key={i} className="flex items-end gap-2">
              <label className="flex-1 text-xs text-slate-500">
                {t("ins.provider")}
                <input className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  value={row.provider} onChange={(e) => update(i, { provider: e.target.value })} />
              </label>
              <label className="flex-1 text-xs text-slate-500">
                {t("ins.coverage")}
                <select className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  value={row.coverage_type} onChange={(e) => update(i, { coverage_type: e.target.value })}>
                  {types.map((tp) => <option key={tp.key} value={tp.key}>{tp.label}</option>)}
                </select>
              </label>
              <label className="w-24 text-xs text-slate-500">
                {t("ins.perMonth")}
                <input type="number" className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  value={row.monthly_premium} onChange={(e) => update(i, { monthly_premium: e.target.value })} />
              </label>
              <label className="w-40 text-xs text-slate-500">
                {t("ins.renewal")}
                <input type="date" className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  value={row.renewal_date} onChange={(e) => update(i, { renewal_date: e.target.value })} />
              </label>
              <button className="mb-0.5 rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-red-500"
                onClick={() => setRows((r) => r.filter((_, idx) => idx !== i))}>
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          ))}
          <button className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-fg hover:underline"
            onClick={() => setRows((r) => [...r, empty()])}>
            <Plus className="h-4 w-4" /> {t("ins.addAnother")}
          </button>
          <div className="flex items-center gap-3 pt-2">
            <button className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg" onClick={submit}>
              {t("ins.save")}
            </button>
            {msg && <span className="text-sm text-slate-600">{msg}</span>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
