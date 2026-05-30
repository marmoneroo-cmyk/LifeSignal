"use client";

import { useState } from "react";
import { Activity } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import { LangToggle } from "@/components/LangToggle";

const REGIONS = ["intl", "il", "us", "eu"] as const;

export function LoginScreen() {
  const { login, register } = useAuth();
  const { t } = useT();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [email, setEmail] = useState("demo@demo.com");
  const [password, setPassword] = useState("demo1234");
  const [name, setName] = useState("");
  const [sex, setSex] = useState("male");
  const [birthDate, setBirthDate] = useState("1990-01-01");
  const [region, setRegion] = useState("intl");

  async function submit() {
    setError(null);
    setBusy(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register({ name, email, password, sex, birth_date: birthDate, region });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-sm space-y-4">
        {/* Lang toggle above the card */}
        <div className="flex justify-center">
          <LangToggle />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-5 flex items-center gap-2">
            <Activity className="h-6 w-6 text-brand" />
            <span className="text-lg font-bold text-slate-800">{t("app.name")}</span>
          </div>

          <div className="mb-4 flex gap-2 text-sm">
            {(["login", "register"] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={
                  "rounded-md px-3 py-1.5 font-medium " +
                  (mode === m ? "bg-brand text-white" : "bg-slate-100 text-slate-600")
                }
              >
                {m === "login" ? t("auth.login") : t("auth.register")}
              </button>
            ))}
          </div>

          <div className="space-y-3">
            {mode === "register" && (
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
                placeholder={t("auth.fullName")}
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            )}
            <input
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder={t("auth.email")}
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              placeholder={t("auth.password")}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {mode === "register" && (
              <div className="grid grid-cols-2 gap-2">
                <select
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  value={sex}
                  onChange={(e) => setSex(e.target.value)}
                >
                  <option value="male">{t("sex.male")}</option>
                  <option value="female">{t("sex.female")}</option>
                </select>
                <input
                  type="date"
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  value={birthDate}
                  onChange={(e) => setBirthDate(e.target.value)}
                />
                <select
                  className="col-span-2 rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                >
                  {REGIONS.map((r) => (
                    <option key={r} value={r}>
                      {t("auth.guidelines")} {t(`region.${r}`)}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {error && <p className="text-sm text-red-600">{error}</p>}

            <button
              onClick={submit}
              disabled={busy}
              className="w-full rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white hover:bg-brand-fg disabled:opacity-50"
            >
              {busy
                ? t("auth.pleaseWait")
                : mode === "login"
                ? t("auth.login")
                : t("auth.create")}
            </button>

            {mode === "login" && (
              <p className="text-center text-xs text-slate-400">{t("auth.demoHint")}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
