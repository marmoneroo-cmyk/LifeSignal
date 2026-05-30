"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Sparkles, Loader2, User } from "lucide-react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import { Disclaimer } from "@/components/Disclaimer";
import { cn } from "@/lib/utils";

interface Message {
  role: "user" | "assistant";
  text: string;
  source?: string;
}

const SUGGESTIONS_HE = [
  "מה השתנה ב-LDL שלי בשנה האחרונה?",
  "האם הביטוח שלי מכסה קולונוסקופיה?",
  "אילו בדיקות אני מפספס לגילי?",
  "מה הסיכון המשפחתי שלי?",
];
const SUGGESTIONS_EN = [
  "What changed in my LDL over the last year?",
  "Does my insurance cover a colonoscopy?",
  "Which screenings am I missing for my age?",
  "What's my family-history risk?",
];

export default function ChatPage() {
  const { activeProfileId } = useAuth();
  const { lang, t } = useT();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [disclaimer, setDisclaimer] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const he = lang === "he";

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send(question?: string) {
    const q = (question ?? input).trim();
    if (!q || busy || !activeProfileId) return;
    setBusy(true);
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    try {
      const res = await api.chat(activeProfileId, q);
      setMessages((m) => [...m, { role: "assistant", text: res.answer, source: res.generated_by }]);
      if (!disclaimer) setDisclaimer(res.disclaimer);
    } catch (e) {
      setMessages((m) => [...m, {
        role: "assistant",
        text: e instanceof Error ? e.message : (he ? "אירעה שגיאה." : "An error occurred."),
      }]);
    } finally {
      setBusy(false);
    }
  }

  function onKey(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  const suggestions = he ? SUGGESTIONS_HE : SUGGESTIONS_EN;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-4" style={{ minHeight: "calc(100vh - 9rem)" }}>
      <header>
        <h1 className="text-2xl font-bold text-slate-800">
          {he ? "שאל את LifeSignal" : "Ask LifeSignal"}
        </h1>
        <p className="text-sm text-slate-500">
          {he
            ? "שאל כל שאלה על הנתונים שלך — בדיקות, ביטוח, תרופות, היסטוריה משפחתית."
            : "Ask anything about your data — labs, insurance, medications, family history."}
        </p>
      </header>

      {/* Messages */}
      <div className="flex-1 space-y-4 overflow-y-auto rounded-xl border border-slate-200 bg-white p-5">
        {messages.length === 0 && (
          <div className="space-y-4">
            <div className="rounded-lg bg-brand-soft p-4 text-sm text-brand-fg">
              <p className="font-medium">
                {he ? "✨ אני יודע את הנתונים שלך — תשאל אותי כל דבר." : "✨ I know your data — ask me anything."}
              </p>
            </div>
            <p className="text-xs font-medium text-slate-400">
              {he ? "הצעות:" : "Try:"}
            </p>
            <div className="grid gap-2">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => send(s)}
                  disabled={busy}
                  className="rounded-lg border border-slate-200 px-3 py-2 text-start text-sm text-slate-700 transition hover:border-brand hover:bg-brand-soft disabled:opacity-50"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={cn("flex gap-2", m.role === "user" ? "justify-end" : "justify-start")}>
            {m.role === "assistant" && (
              <div className="mt-0.5 rounded-lg bg-brand-soft p-1.5">
                <Sparkles className="h-3.5 w-3.5 text-brand" />
              </div>
            )}
            <div
              className={cn(
                "max-w-[80%] whitespace-pre-wrap rounded-xl px-3.5 py-2 text-sm leading-relaxed",
                m.role === "user"
                  ? "bg-brand text-white"
                  : "bg-slate-100 text-slate-800",
              )}
              dir={/[֐-׿]/.test(m.text) ? "rtl" : "ltr"}
            >
              {m.text}
              {m.source && m.source !== "claude" && (
                <p className="mt-1 text-[10px] opacity-60">
                  {he ? "(מצב מבוסס-כללים)" : "(rule-based mode)"}
                </p>
              )}
            </div>
            {m.role === "user" && (
              <div className="mt-0.5 rounded-lg bg-slate-200 p-1.5">
                <User className="h-3.5 w-3.5 text-slate-600" />
              </div>
            )}
          </div>
        ))}

        {busy && (
          <div className="flex gap-2">
            <div className="mt-0.5 rounded-lg bg-brand-soft p-1.5">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-brand" />
            </div>
            <div className="rounded-xl bg-slate-100 px-3.5 py-2 text-sm text-slate-500">
              {he ? "חושב…" : "Thinking…"}
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Composer */}
      <div className="flex gap-2 rounded-xl border border-slate-200 bg-white p-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKey}
          placeholder={he ? "שאל שאלה… (Enter לשליחה)" : "Ask a question… (Enter to send)"}
          rows={1}
          className="flex-1 resize-none rounded-lg px-3 py-2 text-sm focus:outline-none"
          disabled={busy}
        />
        <button
          onClick={() => send()}
          disabled={busy || !input.trim()}
          className="rounded-lg bg-brand p-2 text-white hover:bg-brand-fg disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
        </button>
      </div>

      {disclaimer && <Disclaimer text={disclaimer} />}
    </div>
  );
}
