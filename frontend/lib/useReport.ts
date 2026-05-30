"use client";

import { useEffect, useState } from "react";
import { api } from "./api";
import type { HealthReport } from "./types";
import { useAuth } from "./auth-context";
import { useT } from "./i18n";

// Loads the report for the currently active profile, in the active language.
// Re-fetches whenever profile OR language changes so engine findings stay localized.
export function useReport() {
  const { activeProfileId } = useAuth();
  const { lang } = useT();
  const [report, setReport] = useState<HealthReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeProfileId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const r = await api.getReport(activeProfileId, lang);
        if (!cancelled) setReport(r);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "Failed to load report");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [activeProfileId, lang]);

  return { report, error, loading };
}
