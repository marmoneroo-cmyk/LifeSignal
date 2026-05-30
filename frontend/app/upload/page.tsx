"use client";

import { useState } from "react";
import {
  Upload, AlertTriangle, CheckCircle2, TrendingUp, TrendingDown,
  Sparkles, FileSpreadsheet, Save, Lightbulb,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PriorityBadge } from "@/components/ui/badge";
import { Disclaimer } from "@/components/Disclaimer";
import { api, type TableAnalysis, type ExtractResult } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";

type Mode = "idle" | "preview" | "saved" | "regex_fallback";
const ACCEPT = ".pdf,.xlsx,.xls,.ods,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";

export default function UploadPage() {
  const { activeProfileId } = useAuth();
  const { t } = useT();
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>("idle");
  const [result, setResult] = useState<TableAnalysis | null>(null);
  const [extract, setExtract] = useState<ExtractResult | null>(null);
  const [currentFile, setCurrentFile] = useState<File | null>(null);

  async function onFile(file: File) {
    if (!activeProfileId) return setMsg(t("common.noProfile"));
    setBusy(true);
    setMsg(null);
    setMode("idle");
    setResult(null);
    setExtract(null);
    setCurrentFile(file);

    try {
      // 1) Preview: analyze without saving
      const r = await api.analyzeTable(file, activeProfileId, false);
      if (r.total_rows > 0) {
        setResult(r);
        setMode("preview");
      } else {
        // PDF without table — fall back to regex extraction
        const ex = await api.extractDocument(file, "auto");
        setExtract(ex);
        setMode("regex_fallback");
      }
    } catch (e) {
      setMsg(e instanceof Error ? e.message : t("common.apiError"));
    } finally {
      setBusy(false);
    }
  }

  async function confirmSave() {
    if (!currentFile || !activeProfileId) return;
    setBusy(true);
    setMsg(null);
    try {
      // 2) Save: analyze with persistence — full engine pipeline runs
      const r = await api.analyzeTable(currentFile, activeProfileId, true);
      setResult(r);
      setMode("saved");
      setMsg(`✅ נשמרו ${r.mapped} תוצאות. הפעלנו ${r.recommendations.length} המלצות חכמות.`);
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "שמירה נכשלה.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">ניתוח תוצאות בדיקה</h1>
        <p className="text-sm text-slate-500">
          העלה Excel או PDF של בדיקות דם — המערכת מזהה את הטבלה, קוראת את טווחי הייחוס של המעבדה,
          ומפעילה את כל מנועי הניתוח להפקת המלצות מותאמות לך.
        </p>
      </header>

      <Card>
        <CardContent className="pt-5">
          <label className={cn(
            "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed px-6 py-12 text-center transition-colors",
            busy ? "border-brand bg-brand-soft" : "border-slate-300 bg-slate-50 hover:border-brand",
          )}>
            <Upload className={cn("h-8 w-8", busy ? "animate-bounce text-brand" : "text-slate-400")} />
            <div>
              <p className="font-medium text-slate-700">{busy ? "מנתח…" : "לחץ לבחירת קובץ"}</p>
              <p className="mt-1 text-xs text-slate-400">
                Excel (.xlsx) · PDF דיגיטלי · מזהה אוטומטית את הפורמט
              </p>
            </div>
            <input type="file" accept={ACCEPT} className="hidden" disabled={busy}
              onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} />
          </label>
          {msg && (
            <p className={cn("mt-3 text-sm", msg.startsWith("✅") ? "text-emerald-700" : "text-slate-600")}>
              {msg}
            </p>
          )}
        </CardContent>
      </Card>

      {mode === "preview" && result && (
        <PreviewView result={result} onSave={confirmSave} saving={busy} />
      )}

      {mode === "saved" && result && (
        <SavedView result={result} />
      )}

      {mode === "regex_fallback" && extract && (
        <RegexFallback extract={extract} />
      )}

      <Disclaimer text={t("up.disclaimer")} />
    </div>
  );
}

/* ---- Preview (before save) ----------------------------------------------- */

function PreviewView({ result, onSave, saving }: {
  result: TableAnalysis; onSave: () => void; saving: boolean;
}) {
  return (
    <div className="space-y-4">
      {/* Summary bar */}
      <Card>
        <CardContent className="flex items-center gap-4 py-3">
          <FileSpreadsheet className="h-5 w-5 text-brand" />
          <div className="flex-1">
            <p className="text-sm font-medium text-slate-700">{result.filename}</p>
            <p className="text-xs text-slate-500">
              זוהו <span className="font-semibold text-slate-700">{result.total_rows}</span> בדיקות ·{" "}
              <span className="font-semibold text-slate-700">{result.mapped}</span> מותאמות למנועים ·{" "}
              <span className={cn("font-semibold", result.doc_flags.length > 0 ? "text-orange-600" : "text-emerald-600")}>
                {result.doc_flags.length} חריגות
              </span>
            </p>
          </div>
          <button onClick={onSave} disabled={saving}
            className="inline-flex items-center gap-1.5 rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg disabled:opacity-50">
            <Save className="h-4 w-4" />
            {saving ? "שומר…" : "שמור וקבל המלצות"}
          </button>
        </CardContent>
      </Card>

      {result.warnings.map((w, i) => (
        <div key={i} className="flex gap-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
          <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" /> {w}
        </div>
      ))}

      {result.doc_flags.length > 0 && <FlagsTable flags={result.doc_flags} />}

      <DataTable rows={result.matched_rows} title={`בדיקות שזוהו (${result.matched_rows.length})`} highlight />
      {result.unmatched_rows.length > 0 && (
        <DataTable rows={result.unmatched_rows} title={`בדיקות נוספות (${result.unmatched_rows.length})`} />
      )}
    </div>
  );
}

/* ---- Saved (after save: recommendations) --------------------------------- */

function SavedView({ result }: { result: TableAnalysis }) {
  return (
    <div className="space-y-4">
      <Card className="border-emerald-200 bg-emerald-50">
        <CardContent className="flex items-center gap-3 py-4">
          <CheckCircle2 className="h-6 w-6 text-emerald-600" />
          <div className="flex-1">
            <p className="font-semibold text-emerald-900">הניתוח הושלם</p>
            <p className="text-sm text-emerald-800">
              נשמרו {result.mapped} תוצאות. ציון הבריאות שלך: <span className="font-bold">{result.health_score}/100</span>
            </p>
          </div>
        </CardContent>
      </Card>

      {result.doc_flags.length > 0 && <FlagsTable flags={result.doc_flags} />}

      {result.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>
              <span className="inline-flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-amber-500" />
                המלצות חכמות
                <Sparkles className="h-3 w-3 text-amber-400" />
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {result.recommendations.map((f, i) => (
              <div key={i} className="rounded-lg border border-slate-200 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <h4 className="font-semibold text-slate-800">{f.title}</h4>
                    {f.plain_language && (
                      <p className="mt-1.5 text-sm text-slate-700">{f.plain_language}</p>
                    )}
                    <p className="mt-1 text-xs text-slate-400">{f.detail}</p>
                  </div>
                  <PriorityBadge priority={f.priority} />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <p className="text-sm text-slate-500">
        תוכל לראות את הניתוח המלא בכרטיסיית{" "}
        <a href="/report" className="font-medium text-brand-fg hover:underline">דוח הבריאות</a>.
      </p>
    </div>
  );
}

/* ---- Shared building blocks --------------------------------------------- */

function FlagsTable({ flags }: { flags: TableAnalysis["doc_flags"] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="inline-flex items-center gap-1.5">
            <AlertTriangle className="h-4 w-4 text-orange-500" />
            חריגות לפי טווחי המעבדה ({flags.length})
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-hidden rounded-lg border border-slate-200">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs text-slate-500">
              <tr>
                <th className="px-3 py-2 text-start">בדיקה</th>
                <th className="px-3 py-2 text-start">תוצאה</th>
                <th className="px-3 py-2 text-start">טווח תקין</th>
                <th className="px-3 py-2 text-start">סטטוס</th>
              </tr>
            </thead>
            <tbody>
              {flags.map((f, i) => (
                <tr key={i} className="border-t border-slate-100">
                  <td className="px-3 py-2 font-medium text-slate-800">
                    {f.name}
                    {!f.matched && <span className="ms-2 text-xs text-slate-400">(לא מוכר)</span>}
                  </td>
                  <td className="px-3 py-2 font-semibold">
                    {f.value} <span className="text-slate-400 font-normal">{f.unit}</span>
                  </td>
                  <td className="px-3 py-2 text-slate-500">{f.ref || "—"}</td>
                  <td className="px-3 py-2">
                    {f.status === "high"
                      ? <span className="inline-flex items-center gap-1 text-red-600"><TrendingUp className="h-3.5 w-3.5" /> גבוה</span>
                      : <span className="inline-flex items-center gap-1 text-blue-600"><TrendingDown className="h-3.5 w-3.5" /> נמוך</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function DataTable({ rows, title, highlight }: {
  rows: TableAnalysis["matched_rows"]; title: string; highlight?: boolean;
}) {
  if (rows.length === 0) return null;
  return (
    <Card>
      <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
      <CardContent>
        <div className="overflow-hidden rounded-lg border border-slate-200">
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-xs text-slate-500">
              <tr>
                <th className="px-3 py-2 text-start">בדיקה</th>
                <th className="px-3 py-2 text-start">ערך</th>
                <th className="px-3 py-2 text-start">תקין</th>
              </tr>
            </thead>
            <tbody>
              {rows.slice(0, 20).map((r, i) => (
                <tr key={i} className="border-t border-slate-100">
                  <td className="px-3 py-2 font-medium text-slate-700">
                    {r.original_name}
                    {highlight && r.marker && (
                      <span className="ms-2 rounded bg-teal-50 px-1.5 py-0.5 text-[10px] text-teal-700">
                        {r.marker}
                      </span>
                    )}
                  </td>
                  <td className="px-3 py-2">{r.value} {r.unit}</td>
                  <td className="px-3 py-2 text-slate-500">{r.ref || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length > 20 && (
            <p className="border-t border-slate-100 bg-slate-50 px-3 py-2 text-xs text-slate-500">
              + {rows.length - 20} בדיקות נוספות
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function RegexFallback({ extract }: { extract: ExtractResult }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="inline-flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            לא זוהתה טבלה — חילוץ מטקסט
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-slate-600">
          זיהינו {extract.labs.length} מרקרים מטקסט המסמך. כדאי לייצא את הקובץ כ-Excel לקבלת ניתוח מלא יותר.
        </p>
        {extract.warnings.map((w, i) => (
          <p key={i} className="mt-2 text-sm text-amber-700">{w}</p>
        ))}
      </CardContent>
    </Card>
  );
}
