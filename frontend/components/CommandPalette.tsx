"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search, LayoutDashboard, FileText, Sparkles, MessageCircleQuestion,
  Clock, Upload, FlaskConical, ShieldCheck, Pill, Users, Target, Link2,
  GitCompare, Moon, Sun, Calendar,
} from "lucide-react";
import { useT } from "@/lib/i18n";
import { useTheme } from "@/lib/theme";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";

/**
 * Cmd+K / Ctrl+K command palette. Provides quick navigation across all major
 * pages, plus inline actions (toggle dark mode, download calendar, log out).
 *
 * Mounted once at the app shell so the keyboard shortcut works on every page.
 */
export function CommandPalette() {
  const { lang, t } = useT();
  const { toggle: toggleTheme } = useTheme();
  const { activeProfileId, logout } = useAuth();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const he = lang === "he";

  // Keyboard shortcut: Cmd/Ctrl+K opens; Esc closes (handled by browser focus).
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const isMac = navigator.platform.toLowerCase().includes("mac");
      const cmd = isMac ? e.metaKey : e.ctrlKey;
      if (cmd && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((o) => !o);
      } else if (e.key === "Escape") {
        setOpen(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  // Reset query whenever the palette reopens.
  useEffect(() => { if (open) setQuery(""); }, [open]);

  type Item = { id: string; label: string; icon: React.ReactNode; run: () => void; keywords?: string };

  const items = useMemo<Item[]>(() => {
    const go = (href: string) => () => { router.push(href); setOpen(false); };
    return [
      { id: "dash",   label: t("nav.dashboard"),   icon: <LayoutDashboard className="h-4 w-4" />, run: go("/"),            keywords: "home בית" },
      { id: "report", label: t("nav.report"),      icon: <FileText className="h-4 w-4" />,        run: go("/report"),      keywords: "דוח report" },
      { id: "chat",   label: t("nav.chat"),        icon: <Sparkles className="h-4 w-4" />,        run: go("/chat"),        keywords: "ai claude שאל ask" },
      { id: "copilot",label: t("nav.copilot"),     icon: <MessageCircleQuestion className="h-4 w-4" />, run: go("/copilot") },
      { id: "timeline",label: t("nav.timeline"),   icon: <Clock className="h-4 w-4" />,           run: go("/timeline") },
      { id: "compare",label: t("nav.compare"),     icon: <GitCompare className="h-4 w-4" />,      run: go("/compare") },
      { id: "upload", label: t("nav.upload"),      icon: <Upload className="h-4 w-4" />,          run: go("/upload"),      keywords: "pdf excel" },
      { id: "labs",   label: t("nav.labs"),        icon: <FlaskConical className="h-4 w-4" />,    run: go("/labs"),        keywords: "blood בדיקות דם" },
      { id: "insurance",label:t("nav.insurance"),  icon: <ShieldCheck className="h-4 w-4" />,     run: go("/insurance"),   keywords: "ביטוח policy" },
      { id: "meds",   label: t("nav.medications"), icon: <Pill className="h-4 w-4" />,            run: go("/medications"), keywords: "תרופות drug" },
      { id: "family", label: t("nav.family"),      icon: <Users className="h-4 w-4" />,           run: go("/family") },
      { id: "goals",  label: t("nav.goals"),       icon: <Target className="h-4 w-4" />,          run: go("/goals") },
      { id: "share",  label: t("nav.share"),       icon: <Link2 className="h-4 w-4" />,           run: go("/share"),       keywords: "doctor רופא" },
      // Inline actions
      {
        id: "ics",
        label: he ? "ייצוא בדיקות מומלצות ליומן (.ics)" : "Export screenings to calendar (.ics)",
        icon: <Calendar className="h-4 w-4" />,
        run: () => {
          if (activeProfileId) window.location.href = `/api/users/${activeProfileId}/screenings.ics?lang=${lang}`;
          setOpen(false);
        },
        keywords: "calendar ics יומן",
      },
      {
        id: "theme",
        label: he ? "החלף מצב כהה" : "Toggle dark mode",
        icon: <Moon className="h-4 w-4" />,
        run: () => { toggleTheme(); setOpen(false); },
        keywords: "dark light theme",
      },
      {
        id: "logout",
        label: t("common.logout"),
        icon: <Sun className="h-4 w-4" />,
        run: () => { logout(); setOpen(false); },
      },
    ];
  }, [t, router, he, lang, activeProfileId, toggleTheme, logout]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((it) =>
      it.label.toLowerCase().includes(q) || (it.keywords ?? "").toLowerCase().includes(q),
    );
  }, [items, query]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center bg-black/40 px-4 pt-24"
      onClick={() => setOpen(false)}
      role="dialog"
      aria-modal="true"
      aria-label={he ? "חיפוש מהיר" : "Command palette"}
    >
      <div
        className="w-full max-w-lg overflow-hidden rounded-xl bg-white shadow-2xl dark:bg-slate-800"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 border-b border-slate-200 px-4 py-3 dark:border-slate-700">
          <Search className="h-4 w-4 text-slate-400" />
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={he ? "חפש עמוד או פעולה…" : "Search for a page or action…"}
            className="flex-1 bg-transparent text-sm focus:outline-none"
          />
          <kbd className="rounded border border-slate-200 px-1.5 py-0.5 text-[10px] text-slate-400">esc</kbd>
        </div>
        <ul className="max-h-96 overflow-y-auto py-1">
          {filtered.length === 0 && (
            <li className="px-4 py-3 text-sm text-slate-500">
              {he ? "אין תוצאות" : "No results"}
            </li>
          )}
          {filtered.map((it) => (
            <li key={it.id}>
              <button
                onClick={it.run}
                className="flex w-full items-center gap-3 px-4 py-2 text-start text-sm hover:bg-slate-50 dark:hover:bg-slate-700"
              >
                <span className="text-brand">{it.icon}</span>
                <span className="text-slate-700 dark:text-slate-200">{it.label}</span>
              </button>
            </li>
          ))}
        </ul>
        <div className="border-t border-slate-200 px-4 py-2 text-[11px] text-slate-400 dark:border-slate-700">
          <kbd className="rounded border border-slate-300 px-1">⌘K</kbd>{" / "}
          <kbd className="rounded border border-slate-300 px-1">Ctrl+K</kbd>
          {" — "}{he ? "כדי לפתוח מכל מסך" : "from any screen"}
        </div>
      </div>
    </div>
  );
}
