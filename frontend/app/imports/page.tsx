"use client";

import { useState } from "react";
import { Upload, AlertTriangle, Dna, Activity, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Disclaimer } from "@/components/Disclaimer";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import { API_BASE, api, getToken } from "@/lib/api";
import { cn } from "@/lib/utils";

interface AppleResult {
  filename: string;
  count: number;
  records: { marker: string; value: number; unit: string; taken_on: string }[];
}

interface GeneticResult {
  filename: string;
  total_rows_scanned: number;
  notable: { rsid: string; gene: string; topic: string; genotype: string }[];
  disclaimer_he: string;
  disclaimer_en: string;
}

export default function ImportsPage() {
  const { activeProfileId } = useAuth();
  const { lang } = useT();
  const he = lang === "he";

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">
          {he ? "ייבוא נתונים מתקדם" : "Advanced Imports"}
        </h1>
        <p className="text-sm text-slate-500">
          {he
            ? "ייבא מקבצי Apple Health או נתוני raw מ-23andMe. כל הנתונים נשארים אצלך."
            : "Import from Apple Health exports or 23andMe raw data. All data stays with you."}
        </p>
      </header>

      <AppleHealthCard activeProfileId={activeProfileId} lang={lang} />
      <GeneticCard lang={lang} />

      <Disclaimer text={he
        ? "ייבוא נתונים אינו מהווה ייעוץ רפואי. להחלטות טיפוליות התייעץ עם רופא או יועץ גנטי מוסמך."
        : "Imported data is not medical advice. Consult a clinician or certified genetic counselor for clinical decisions."} />
    </div>
  );
}

function AppleHealthCard({ activeProfileId, lang }: { activeProfileId: number | null; lang: "he" | "en" }) {
  const he = lang === "he";
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<AppleResult | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [selected, setSelected] = useState<Set<number>>(new Set());

  async function onFile(file: File) {
    setBusy(true); setMsg(null); setResult(null); setSelected(new Set());
    try {
      const form = new FormData();
      form.append("file", file);
      const token = getToken();
      const res = await fetch(`${API_BASE}/api/imports/apple-health`, {
        method: "POST",
        body: form,
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        cache: "no-store",
      });
      if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
      const data = (await res.json()) as AppleResult;
      setResult(data);
      // Pre-select everything; user can deselect.
      setSelected(new Set(data.records.map((_, i) => i)));
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "error");
    } finally {
      setBusy(false);
    }
  }

  async function save() {
    if (!result || !activeProfileId) return;
    const picked = result.records.filter((_, i) => selected.has(i));
    if (!picked.length) return setMsg(he ? "לא נבחרו ערכים" : "Nothing selected");
    setBusy(true);
    try {
      await api.addLabs(activeProfileId, picked);
      setMsg(he ? `✅ נשמרו ${picked.length} ערכים` : `✅ Saved ${picked.length} values`);
      setResult(null);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "error");
    } finally { setBusy(false); }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="inline-flex items-center gap-2">
            <Activity className="h-4 w-4 text-brand" /> Apple Health
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-xs text-slate-500">
          {he
            ? "באייפון: בריאות → תמונת פרופיל → ייצא את כל הנתונים → קובץ ZIP. גרור אותו לכאן."
            : "On iPhone: Health → profile → Export All Health Data → ZIP file. Drop it here."}
        </p>

        <label className={cn(
          "flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-6 text-sm transition-colors",
          busy ? "border-brand bg-brand-soft" : "border-slate-300 bg-slate-50 hover:border-brand",
        )}>
          <Upload className="h-4 w-4 text-slate-400" />
          {busy ? (he ? "מנתח…" : "Parsing…") : (he ? "בחר export.zip" : "Choose export.zip")}
          <input type="file" accept=".zip,.xml" className="hidden" disabled={busy}
            onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} />
        </label>

        {msg && <p className="text-sm text-slate-600">{msg}</p>}

        {result && (
          <div>
            <p className="mb-2 text-sm font-medium text-slate-700">
              {he ? `זוהו ${result.count} ערכים. בחר מה לשמור:` : `Found ${result.count} values. Select which to save:`}
            </p>
            <div className="max-h-72 overflow-y-auto rounded-lg border border-slate-200">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-xs text-slate-500">
                  <tr>
                    <th className="px-2 py-1.5 text-start">
                      <input
                        type="checkbox"
                        checked={selected.size === result.records.length}
                        onChange={(e) => setSelected(e.target.checked
                          ? new Set(result.records.map((_, i) => i)) : new Set())}
                      />
                    </th>
                    <th className="px-2 py-1.5 text-start">{he ? "מרקר" : "Marker"}</th>
                    <th className="px-2 py-1.5 text-start">{he ? "ערך" : "Value"}</th>
                    <th className="px-2 py-1.5 text-start">{he ? "תאריך" : "Date"}</th>
                  </tr>
                </thead>
                <tbody>
                  {result.records.map((r, i) => (
                    <tr key={i} className="border-t border-slate-100">
                      <td className="px-2 py-1">
                        <input
                          type="checkbox"
                          checked={selected.has(i)}
                          onChange={(e) => {
                            const ns = new Set(selected);
                            if (e.target.checked) ns.add(i); else ns.delete(i);
                            setSelected(ns);
                          }}
                        />
                      </td>
                      <td className="px-2 py-1">{r.marker}</td>
                      <td className="px-2 py-1">{r.value} {r.unit}</td>
                      <td className="px-2 py-1 text-slate-500">{r.taken_on}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <button onClick={save} disabled={busy}
              className="mt-2 inline-flex items-center gap-1.5 rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg disabled:opacity-50">
              <CheckCircle2 className="h-4 w-4" /> {he ? "שמור נבחרים" : "Save selected"}
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function GeneticCard({ lang }: { lang: "he" | "en" }) {
  const he = lang === "he";
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<GeneticResult | null>(null);
  const [msg, setMsg] = useState<string | null>(null);

  async function onFile(file: File) {
    setBusy(true); setMsg(null); setResult(null);
    try {
      const form = new FormData();
      form.append("file", file);
      form.append("lang", lang);
      const token = getToken();
      const res = await fetch(`${API_BASE}/api/imports/23andme`, {
        method: "POST",
        body: form,
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
      setResult((await res.json()) as GeneticResult);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "error");
    } finally { setBusy(false); }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="inline-flex items-center gap-2">
            <Dna className="h-4 w-4 text-brand" /> 23andMe Raw Data
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex gap-2 rounded-lg bg-amber-50 p-3 text-xs text-amber-800">
          <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
          <span>
            {he
              ? "המידע הגנטי לעיון בלבד. אינו מהווה אבחנה. הנתונים מנותחים בענן שלך — אין שמירה ב-DB."
              : "Genetic info is informational only — not a diagnosis. Parsed in your cloud; not stored in our DB."}
          </span>
        </div>

        <p className="text-xs text-slate-500">
          {he
            ? "ב-23andMe: Account → Browse Raw Data → Download. גרור את הקובץ לכאן."
            : "In 23andMe: Account → Browse Raw Data → Download. Drop the file here."}
        </p>

        <label className={cn(
          "flex cursor-pointer items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-6 text-sm transition-colors",
          busy ? "border-brand bg-brand-soft" : "border-slate-300 bg-slate-50 hover:border-brand",
        )}>
          <Upload className="h-4 w-4 text-slate-400" />
          {busy ? (he ? "מנתח…" : "Parsing…") : (he ? "בחר קובץ raw_data.zip" : "Choose raw_data.zip")}
          <input type="file" accept=".zip,.txt" className="hidden" disabled={busy}
            onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} />
        </label>

        {msg && <p className="text-sm text-amber-700">{msg}</p>}

        {result && (
          <div>
            <p className="mb-2 text-sm text-slate-500">
              {he ? `סרקנו ${result.total_rows_scanned.toLocaleString()} שורות. ${result.notable.length} SNPs מעניינים:`
                  : `Scanned ${result.total_rows_scanned.toLocaleString()} rows. ${result.notable.length} notable SNPs:`}
            </p>
            <div className="overflow-hidden rounded-lg border border-slate-200">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 text-xs text-slate-500">
                  <tr>
                    <th className="px-2 py-1.5 text-start">rsID</th>
                    <th className="px-2 py-1.5 text-start">Gene</th>
                    <th className="px-2 py-1.5 text-start">{he ? "נושא" : "Topic"}</th>
                    <th className="px-2 py-1.5 text-start">{he ? "גנוטיפ" : "Genotype"}</th>
                  </tr>
                </thead>
                <tbody>
                  {result.notable.map((s) => (
                    <tr key={s.rsid} className="border-t border-slate-100">
                      <td className="px-2 py-1 font-mono text-xs">{s.rsid}</td>
                      <td className="px-2 py-1">{s.gene}</td>
                      <td className="px-2 py-1 text-slate-700">{s.topic}</td>
                      <td className="px-2 py-1 font-mono">{s.genotype}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="mt-2 text-xs text-slate-500">
              {he ? result.disclaimer_he : result.disclaimer_en}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
