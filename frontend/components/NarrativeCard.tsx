"use client";

import { useState } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { useT } from "@/lib/i18n";
import type { Narrative } from "@/lib/types";

export function NarrativeCard({ userId }: { userId: number }) {
  const { lang, t } = useT();
  const [data, setData] = useState<Narrative | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Track which lang the current data was fetched in.
  const [dataLang, setDataLang] = useState<"he" | "en" | null>(null);

  async function generate(l: "he" | "en") {
    setLoading(true);
    setError(null);
    try {
      const result = await api.narrative(userId, l);
      setData(result);
      setDataLang(l);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error");
    } finally {
      setLoading(false);
    }
  }

  const sourceLabel =
    data?.generated_by === "claude"
      ? t("narr.sourceAi", { model: data.model ?? "" })
      : t("narr.sourceRule");

  const isStale = data && dataLang !== lang;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          <span className="inline-flex items-center gap-1.5">
            <Sparkles className="h-4 w-4 text-brand" />
            {t("narr.title")}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {!data && !loading && (
          <button
            onClick={() => generate(lang)}
            className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg"
          >
            {t("narr.generate")}
          </button>
        )}
        {loading && (
          <p className="flex items-center gap-2 text-sm text-slate-500">
            <Loader2 className="h-4 w-4 animate-spin" /> {t("narr.writing")}
          </p>
        )}
        {error && <p className="text-sm text-amber-700">{error}</p>}
        {data && !loading && (
          <>
            {isStale && (
              <div className="mb-3 flex items-center justify-between">
                <span className="text-xs text-slate-400">
                  {lang === "he" ? "הסיכום הוצג בשפה אחרת" : "Summary shown in another language"}
                </span>
                <button
                  onClick={() => generate(lang)}
                  className="text-xs font-medium text-brand-fg hover:underline"
                >
                  {lang === "he" ? "רענן בעברית" : "Refresh in English"}
                </button>
              </div>
            )}
            <p
              dir={dataLang === "he" ? "rtl" : "ltr"}
              className="whitespace-pre-line text-sm leading-relaxed text-slate-700"
            >
              {data.text}
            </p>
            <p className="mt-3 text-[11px] text-slate-400">{sourceLabel}</p>
          </>
        )}
      </CardContent>
    </Card>
  );
}
