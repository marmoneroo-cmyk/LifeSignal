"use client";

import { useEffect, useState } from "react";
import { Link2, Copy, Trash2, Plus, CheckCircle2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Disclaimer } from "@/components/Disclaimer";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import type { ShareLink } from "@/lib/api";

export default function SharePage() {
  const { activeProfileId } = useAuth();
  const { lang } = useT();
  const he = lang === "he";

  const [links, setLinks] = useState<ShareLink[]>([]);
  const [label, setLabel] = useState("");
  const [days, setDays] = useState(7);
  const [busy, setBusy] = useState(false);
  const [copiedToken, setCopiedToken] = useState<string | null>(null);

  useEffect(() => {
    if (activeProfileId) refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeProfileId]);

  async function refresh() {
    if (!activeProfileId) return;
    setLinks(await api.listShares(activeProfileId));
  }

  async function create() {
    if (!activeProfileId) return;
    setBusy(true);
    try {
      await api.createShare(activeProfileId, label, days);
      setLabel("");
      await refresh();
    } finally {
      setBusy(false);
    }
  }

  async function revoke(token: string) {
    if (!activeProfileId) return;
    await api.revokeShare(activeProfileId, token);
    await refresh();
  }

  function urlFor(token: string): string {
    if (typeof window === "undefined") return "";
    return `${window.location.origin}/share/${token}`;
  }

  async function copy(token: string) {
    await navigator.clipboard.writeText(urlFor(token));
    setCopiedToken(token);
    setTimeout(() => setCopiedToken(null), 2000);
  }

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-800">
          {he ? "שיתוף עם רופא" : "Share with a Doctor"}
        </h1>
        <p className="text-sm text-slate-500">
          {he
            ? "צור קישור זמני שכל אחד יכול לפתוח כדי לראות את הדוח שלך — ללא הרשמה. מתפוגג אוטומטית."
            : "Create a time-limited URL anyone can open to view your report — no signup required. Expires automatically."}
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>
            <span className="inline-flex items-center gap-1.5">
              <Plus className="h-4 w-4 text-brand" /> {he ? "קישור חדש" : "New link"}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
            <input
              placeholder={he ? "תווית (למשל ד'ר כהן)" : "Label (e.g. Dr. Cohen)"}
              className="md:col-span-2 rounded-lg border border-slate-300 px-3 py-2 text-sm"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
            />
            <label className="text-xs text-slate-500">
              {he ? "תקף ל" : "Valid for"}
              <select
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
              >
                <option value={1}>{he ? "יום" : "1 day"}</option>
                <option value={7}>{he ? "שבוע" : "7 days"}</option>
                <option value={30}>{he ? "30 יום" : "30 days"}</option>
              </select>
            </label>
            <button
              onClick={create}
              disabled={busy}
              className="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg disabled:opacity-50"
            >
              {he ? "צור קישור" : "Create link"}
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Active links */}
      {links.length === 0 ? (
        <Card>
          <CardContent className="py-8 text-center text-sm text-slate-500">
            {he ? "אין קישורים פעילים." : "No active links."}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {links.map((l) => (
            <Card key={l.token}>
              <CardContent className="py-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <h3 className="font-semibold text-slate-800">
                      <Link2 className="me-1 inline-block h-4 w-4 text-brand" />
                      {l.label || (he ? "קישור ללא תווית" : "Untitled")}
                    </h3>
                    <p className="mt-1 break-all font-mono text-xs text-slate-500">
                      {urlFor(l.token)}
                    </p>
                    <p className="mt-1 text-[11px] text-slate-400">
                      {he ? "פג ב-" : "Expires "} {new Date(l.expires_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => copy(l.token)}
                      className="rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-50"
                      title={he ? "העתק" : "Copy"}
                    >
                      {copiedToken === l.token
                        ? <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                        : <Copy className="h-4 w-4" />}
                    </button>
                    <button
                      onClick={() => revoke(l.token)}
                      className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-red-500"
                      title={he ? "בטל" : "Revoke"}
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Disclaimer text={he
        ? "כל אדם עם הקישור יכול לראות את הדוח. ניתן לבטל בכל רגע."
        : "Anyone with the link can view the report. Revoke anytime."} />
    </div>
  );
}
