"use client";

import { useState } from "react";
import { MessageCircleQuestion, Loader2, Clock } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Disclaimer } from "@/components/Disclaimer";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import type { Copilot } from "@/lib/types";

export default function CopilotPage() {
  const { activeProfileId } = useAuth();
  const { lang, t } = useT();
  const [data, setData] = useState<Copilot | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      if (!activeProfileId) { setError(t("common.noProfile")); return; }
      setData(await api.copilot(activeProfileId, lang));
    } catch (e) {
      setError(e instanceof Error ? e.message : t("common.apiError"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">{t("copilot.title")}</h1>
        <p className="text-sm text-slate-500">{t("copilot.subtitle")}</p>
      </header>

      {!data && !loading && (
        <button onClick={load} className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg">
          {t("copilot.prepare")}
        </button>
      )}
      {loading && (
        <p className="flex items-center gap-2 text-sm text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> {t("copilot.preparing")}
        </p>
      )}
      {error && <p className="text-sm text-amber-700">{error}</p>}

      {data && !loading && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>
                <span className="inline-flex items-center gap-1.5">
                  <MessageCircleQuestion className="h-4 w-4 text-brand" />
                  {t("copilot.questions")}
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-inside list-disc space-y-2 text-sm text-slate-700">
                {data.questions.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
            </CardContent>
          </Card>

          {data.changes_since_last.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>
                  <span className="inline-flex items-center gap-1.5">
                    <Clock className="h-4 w-4 text-brand" /> {t("copilot.changes")}
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1.5 text-sm text-slate-700">
                  {data.changes_since_last.map((c, i) => <li key={i}>{c}</li>)}
                </ul>
              </CardContent>
            </Card>
          )}

          <Disclaimer text={data.disclaimer} />
        </>
      )}
    </div>
  );
}
