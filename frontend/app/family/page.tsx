"use client";

import { useEffect, useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";

interface Row { relation: string; conditions: string[] }

export default function FamilyPage() {
  const { activeProfileId } = useAuth();
  const { t } = useT();
  const [ref, setRef] = useState<{ relations: string[]; conditions: string[] }>({
    relations: [], conditions: [],
  });
  const [rows, setRows] = useState<Row[]>([{ relation: "father", conditions: [] }]);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!activeProfileId) return;
    api.familyReference(activeProfileId).then(setRef).catch(() => setMsg(t("common.apiError")));
  }, [activeProfileId]);

  const update = (i: number, patch: Partial<Row>) =>
    setRows((r) => r.map((row, idx) => (idx === i ? { ...row, ...patch } : row)));

  const toggleCondition = (i: number, cond: string) =>
    setRows((r) => r.map((row, idx) =>
      idx === i ? {
        ...row,
        conditions: row.conditions.includes(cond)
          ? row.conditions.filter((c) => c !== cond)
          : [...row.conditions, cond],
      } : row
    ));

  async function submit() {
    setMsg(null);
    try {
      if (!activeProfileId) return setMsg(t("common.noProfile"));
      const members = rows.filter((r) => r.conditions.length);
      if (!members.length) return setMsg(t("fam.needOne"));
      const res = (await api.addFamily(activeProfileId, members)) as { added: number };
      setMsg(t("fam.saved", { n: res.added }));
      setRows([{ relation: "father", conditions: [] }]);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : t("common.apiError"));
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">{t("fam.title")}</h1>
        <p className="text-sm text-slate-500">{t("fam.subtitle")}</p>
      </header>
      <Card>
        <CardHeader><CardTitle>{t("fam.relatives")}</CardTitle></CardHeader>
        <CardContent className="space-y-5">
          {rows.map((row, i) => (
            <div key={i} className="rounded-lg border border-slate-200 p-3">
              <div className="flex items-center justify-between gap-2">
                <label className="text-xs text-slate-500">
                  {t("fam.relation")}
                  <select className="ms-2 rounded-lg border border-slate-300 px-3 py-1.5 text-sm"
                    value={row.relation} onChange={(e) => update(i, { relation: e.target.value })}>
                    {ref.relations.map((rel) => (
                      <option key={rel} value={rel}>{t(`rel.${rel}`) || rel}</option>
                    ))}
                  </select>
                </label>
                <button className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-red-500"
                  onClick={() => setRows((r) => r.filter((_, idx) => idx !== i))}>
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                {ref.conditions.map((cond) => (
                  <button key={cond} onClick={() => toggleCondition(i, cond)}
                    className={cn("rounded-full border px-3 py-1 text-xs",
                      row.conditions.includes(cond)
                        ? "border-brand bg-brand-soft text-brand-fg"
                        : "border-slate-200 text-slate-500 hover:bg-slate-50")}>
                    {t(`cond.${cond}`) || cond}
                  </button>
                ))}
              </div>
            </div>
          ))}
          <button className="inline-flex items-center gap-1.5 text-sm font-medium text-brand-fg hover:underline"
            onClick={() => setRows((r) => [...r, { relation: "mother", conditions: [] }])}>
            <Plus className="h-4 w-4" /> {t("fam.addAnother")}
          </button>
          <div className="flex items-center gap-3 pt-2">
            <button className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg" onClick={submit}>
              {t("fam.save")}
            </button>
            {msg && <span className="text-sm text-slate-600">{msg}</span>}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
