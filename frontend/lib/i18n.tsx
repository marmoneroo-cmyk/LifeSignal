"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { translate, type Lang } from "./translations";

interface I18n {
  lang: Lang;
  dir: "rtl" | "ltr";
  setLang: (l: Lang) => void;
  toggle: () => void;
  t: (key: string, vars?: Record<string, string | number>) => string;
}

const Ctx = createContext<I18n | null>(null);
const LANG_KEY = "ls_lang";

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  // Hebrew is the default language.
  const [lang, setLangState] = useState<Lang>("he");

  useEffect(() => {
    const stored = (typeof window !== "undefined" && window.localStorage.getItem(LANG_KEY)) as Lang | null;
    if (stored === "he" || stored === "en") setLangState(stored);
  }, []);

  useEffect(() => {
    const dir = lang === "he" ? "rtl" : "ltr";
    document.documentElement.lang = lang;
    document.documentElement.dir = dir;
  }, [lang]);

  const setLang = (l: Lang) => {
    window.localStorage.setItem(LANG_KEY, l);
    setLangState(l);
  };

  const value: I18n = {
    lang,
    dir: lang === "he" ? "rtl" : "ltr",
    setLang,
    toggle: () => setLang(lang === "he" ? "en" : "he"),
    t: (key, vars) => translate(lang, key, vars),
  };

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useT(): I18n {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useT must be used within LanguageProvider");
  return ctx;
}
