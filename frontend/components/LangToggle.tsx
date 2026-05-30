"use client";

import { useT } from "@/lib/i18n";
import { cn } from "@/lib/utils";

export function LangToggle({ className }: { className?: string }) {
  const { lang, setLang } = useT();

  return (
    <div className={cn("flex rounded-lg border border-slate-200 overflow-hidden text-xs font-medium", className)}>
      <button
        onClick={() => setLang("he")}
        className={cn(
          "px-2.5 py-1.5 transition-colors",
          lang === "he"
            ? "bg-brand text-white"
            : "bg-white text-slate-500 hover:bg-slate-50",
        )}
        aria-label="עברית"
      >
        עב
      </button>
      <button
        onClick={() => setLang("en")}
        className={cn(
          "px-2.5 py-1.5 border-s border-slate-200 transition-colors",
          lang === "en"
            ? "bg-brand text-white"
            : "bg-white text-slate-500 hover:bg-slate-50",
        )}
        aria-label="English"
      >
        EN
      </button>
    </div>
  );
}
