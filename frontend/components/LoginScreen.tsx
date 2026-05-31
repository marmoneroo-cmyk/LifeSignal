"use client";

import { useState } from "react";
import {
  Activity, Sparkles, ShieldCheck, FlaskConical,
  FileText, Users, MessageCircleQuestion, Check,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import { LangToggle } from "@/components/LangToggle";

const REGIONS = ["intl", "il", "us", "eu"] as const;

export function LoginScreen() {
  const { login, register } = useAuth();
  const { lang, t } = useT();
  const [mode, setMode] = useState<"login" | "register">("register");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [sex, setSex] = useState("male");
  const [birthDate, setBirthDate] = useState("1990-01-01");
  const [region, setRegion] = useState(lang === "he" ? "il" : "intl");

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

  const he = lang === "he";

  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-soft/40 via-slate-50 to-white">
      {/* Top nav */}
      <header className="flex items-center justify-between px-4 py-4 md:px-8">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-brand p-1.5">
            <Activity className="h-4 w-4 text-white" />
          </div>
          <span className="text-base font-bold text-slate-800">{t("app.name")}</span>
        </div>
        <LangToggle />
      </header>

      {/* Hero + login side-by-side */}
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-8 md:grid-cols-2 md:gap-16 md:py-16 md:px-8">
        {/* Left: hero */}
        <div className="space-y-6">
          <div className="inline-flex items-center gap-1.5 rounded-full bg-brand-soft px-3 py-1 text-xs font-medium text-brand-fg">
            <Sparkles className="h-3 w-3" />
            {he ? "תמיכת החלטות רפואית — לא תחליף לרופא" : "Clinical decision support — not a doctor replacement"}
          </div>

          <h1 className="text-3xl font-bold leading-tight tracking-tight text-slate-800 md:text-4xl lg:text-5xl">
            {he ? (
              <>
                האינטליגנציה הבריאותית{" "}
                <span className="text-brand">האישית</span> שלך
              </>
            ) : (
              <>
                Your <span className="text-brand">personal</span> health intelligence
              </>
            )}
          </h1>

          <p className="text-base text-slate-600 md:text-lg">
            {he
              ? "העלה בדיקות דם ופוליסות ביטוח — וקבל ניתוח רוחבי שמזהה מגמות, חוסר בכיסוי, אינטראקציות תרופתיות, וסיכון תורשתי. הכל מאובטח, פרטי, ובעברית."
              : "Upload your blood tests and insurance policies — get cross-cutting analysis that detects trends, coverage gaps, drug interactions, and inherited risk. Secure, private, in your language."}
          </p>

          {/* Feature grid */}
          <div className="grid grid-cols-1 gap-3 pt-2 sm:grid-cols-2">
            <Feature icon={<FlaskConical className="h-4 w-4" />} text={he ? "32 סוגי בדיקות מזוהים" : "32 lab markers"} />
            <Feature icon={<ShieldCheck className="h-4 w-4" />} text={he ? "ניתוח ביטוחי חכם" : "Smart insurance review"} />
            <Feature icon={<FileText className="h-4 w-4" />} text={he ? "העלאת Excel ו-PDF" : "Excel & PDF upload"} />
            <Feature icon={<MessageCircleQuestion className="h-4 w-4" />} text={he ? "צ'אט עם הנתונים שלך" : "Chat with your data"} />
            <Feature icon={<Users className="h-4 w-4" />} text={he ? "ניהול פרופילים משפחתיים" : "Family profiles"} />
            <Feature icon={<Sparkles className="h-4 w-4" />} text={he ? "המלצות מותאמות אישית" : "Personal recommendations"} />
          </div>

          {/* Social proof / trust */}
          <div className="flex items-center gap-2 pt-2 text-xs text-slate-500">
            <ShieldCheck className="h-4 w-4 text-emerald-500" />
            <span>
              {he
                ? "הנתונים שלך נשארים שלך. אין שיתוף עם צד שלישי. אבטחה ברמת בנק."
                : "Your data stays yours. No third-party sharing. Bank-grade security."}
            </span>
          </div>
        </div>

        {/* Right: login card */}
        <div className="md:pt-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-xl shadow-brand/5">
            <div className="mb-5 flex gap-2 text-sm">
              {(["register", "login"] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setMode(m)}
                  className={
                    "flex-1 rounded-lg px-3 py-2 font-medium transition-colors " +
                    (mode === m
                      ? "bg-brand text-white shadow-sm"
                      : "bg-slate-100 text-slate-600 hover:bg-slate-200")
                  }
                >
                  {m === "login" ? t("auth.login") : (he ? "התחל בחינם" : "Get started free")}
                </button>
              ))}
            </div>

            <div className="space-y-3">
              {mode === "register" && (
                <input
                  className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20"
                  placeholder={t("auth.fullName")}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              )}
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20"
                placeholder={t("auth.email")}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <input
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20"
                placeholder={t("auth.password")}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              {mode === "register" && (
                <div className="grid grid-cols-2 gap-2">
                  <select
                    className="rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-brand focus:outline-none"
                    value={sex}
                    onChange={(e) => setSex(e.target.value)}
                  >
                    <option value="male">{t("sex.male")}</option>
                    <option value="female">{t("sex.female")}</option>
                  </select>
                  <input
                    type="date"
                    className="rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-brand focus:outline-none"
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                  />
                  <select
                    className="col-span-2 rounded-lg border border-slate-300 px-3 py-2.5 text-sm focus:border-brand focus:outline-none"
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

              {error && (
                <div className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
              )}

              <button
                onClick={submit}
                disabled={busy}
                className="w-full rounded-lg bg-brand px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-brand-fg disabled:opacity-50"
              >
                {busy
                  ? t("auth.pleaseWait")
                  : mode === "login"
                  ? t("auth.login")
                  : (he ? "צור חשבון חינם" : "Create free account")}
              </button>

              <p className="text-center text-[11px] text-slate-400">
                {he
                  ? "ללא כרטיס אשראי. בלי הצעות שיווק. ביטול בכל רגע."
                  : "No credit card. No marketing emails. Cancel anytime."}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-200 px-4 py-6 text-center text-xs text-slate-400 md:px-8">
        {he
          ? "מערכת תמיכה בהחלטות בלבד — אינה אבחנה רפואית. תמיד התייעץ עם רופא."
          : "Decision support only — not a medical diagnosis. Always consult a physician."}
      </footer>
    </div>
  );
}

function Feature({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-700">
      <div className="rounded-md bg-brand-soft p-1 text-brand-fg">{icon}</div>
      <span>{text}</span>
      <Check className="ms-auto h-3.5 w-3.5 text-emerald-500" />
    </div>
  );
}
