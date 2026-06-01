"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { ChevronDown, LogOut, UserPlus } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { useT } from "@/lib/i18n";
import { api } from "@/lib/api";
import { Sidebar } from "@/components/Sidebar";
import { LoginScreen } from "@/components/LoginScreen";
import { CommandPalette } from "@/components/CommandPalette";

// Path prefixes whose URL itself acts as the credential (server validates the
// opaque token + expiry). These render WITHOUT the sidebar / profile bar.
const PUBLIC_PREFIXES = ["/share/"];

export function AuthGate({ children }: { children: React.ReactNode }) {
  const { ready, account } = useAuth();
  const pathname = usePathname();

  const isPublic = PUBLIC_PREFIXES.some((p) => pathname?.startsWith(p));
  if (isPublic) return <>{children}</>;

  if (!ready)
    return (
      <div className="flex min-h-screen items-center justify-center text-slate-400">
        טוען…
      </div>
    );
  if (!account) return <LoginScreen />;

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <ProfileBar />
        <div className="px-8 py-6">{children}</div>
      </main>
      <CommandPalette />
    </div>
  );
}

function ProfileBar() {
  const { profiles, activeProfile, activeProfileId, setActiveProfile, logout, account, refreshProfiles } =
    useAuth();
  const { t } = useT();
  const [open, setOpen] = useState(false);
  const [adding, setAdding] = useState(false);

  return (
    <div className="flex items-center justify-between border-b border-slate-200 bg-white px-8 py-3 print:hidden">
      <div className="relative">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-1.5 text-sm hover:bg-slate-50"
        >
          <span className="font-medium text-slate-700">{activeProfile?.name}</span>
          <span className="text-xs text-slate-400">({activeProfile?.age})</span>
          <ChevronDown className="h-4 w-4 text-slate-400" />
        </button>
        {open && (
          <div className="absolute z-10 mt-1 w-56 rounded-lg border border-slate-200 bg-white py-1 shadow-lg">
            {profiles.map((p) => (
              <button
                key={p.id}
                onClick={() => { setActiveProfile(p.id); setOpen(false); }}
                className={
                  "flex w-full items-center justify-between px-3 py-2 text-sm hover:bg-slate-50 " +
                  (p.id === activeProfileId ? "text-brand-fg" : "text-slate-700")
                }
              >
                {p.name}
                {p.id === account?.id && (
                  <span className="text-xs text-slate-400">{t("profile.account")}</span>
                )}
              </button>
            ))}
            <button
              onClick={() => { setOpen(false); setAdding(true); }}
              className="flex w-full items-center gap-2 border-t border-slate-100 px-3 py-2 text-sm text-brand-fg hover:bg-slate-50"
            >
              <UserPlus className="h-4 w-4" /> {t("profile.add")}
            </button>
          </div>
        )}
      </div>

      <button
        onClick={logout}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-red-500"
      >
        <LogOut className="h-4 w-4" /> {t("common.logout")}
      </button>

      {adding && <AddProfileModal onClose={() => setAdding(false)} onAdded={refreshProfiles} />}
    </div>
  );
}

function AddProfileModal({ onClose, onAdded }: { onClose: () => void; onAdded: () => void }) {
  const { t } = useT();
  const [name, setName] = useState("");
  const [sex, setSex] = useState("male");
  const [birthDate, setBirthDate] = useState("2015-01-01");
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    try {
      await api.addProfile({ name, sex, birth_date: birthDate });
      await onAdded();
      onClose();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="fixed inset-0 z-20 flex items-center justify-center bg-black/30" onClick={onClose}>
      <div className="w-full max-w-sm rounded-xl bg-white p-5 shadow-xl" onClick={(e) => e.stopPropagation()}>
        <h3 className="mb-3 font-semibold text-slate-800">{t("profile.addTitle")}</h3>
        <div className="space-y-3">
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder={t("profile.namePlaceholder")}
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
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
          </div>
          <div className="flex justify-end gap-2">
            <button onClick={onClose} className="rounded-lg px-3 py-1.5 text-sm text-slate-500">
              {t("common.cancel")}
            </button>
            <button
              onClick={save}
              disabled={busy || !name}
              className="rounded-lg bg-brand px-4 py-1.5 text-sm font-semibold text-white disabled:opacity-50"
            >
              {t("common.add")}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
