"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api, getToken, setToken } from "./api";
import type { UserOut } from "./types";

interface AuthState {
  ready: boolean;
  account: UserOut | null;
  profiles: UserOut[];
  activeProfileId: number | null;
  activeProfile: UserOut | null;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: Record<string, unknown>) => Promise<void>;
  logout: () => void;
  setActiveProfile: (id: number) => void;
  refreshProfiles: () => Promise<void>;
}

const Ctx = createContext<AuthState | null>(null);

const ACTIVE_KEY = "ls_active_profile";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [account, setAccount] = useState<UserOut | null>(null);
  const [profiles, setProfiles] = useState<UserOut[]>([]);
  const [activeProfileId, setActiveId] = useState<number | null>(null);

  async function loadSession() {
    if (!getToken()) {
      setReady(true);
      return;
    }
    try {
      const me = await api.me();
      setAccount(me);
      const profs = await api.profiles();
      setProfiles(profs);
      const stored = Number(window.localStorage.getItem(ACTIVE_KEY));
      const valid = profs.find((p) => p.id === stored);
      setActiveId(valid ? stored : me.id);
    } catch {
      setToken(null);
      setAccount(null);
    } finally {
      setReady(true);
    }
  }

  useEffect(() => {
    loadSession();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function login(email: string, password: string) {
    const res = await api.login(email, password);
    setToken(res.token);
    await loadSession();
  }

  async function register(payload: Record<string, unknown>) {
    const res = await api.register(payload);
    setToken(res.token);
    await loadSession();
  }

  function logout() {
    setToken(null);
    window.localStorage.removeItem(ACTIVE_KEY);
    setAccount(null);
    setProfiles([]);
    setActiveId(null);
  }

  function setActiveProfile(id: number) {
    window.localStorage.setItem(ACTIVE_KEY, String(id));
    setActiveId(id);
  }

  async function refreshProfiles() {
    setProfiles(await api.profiles());
  }

  const activeProfile = profiles.find((p) => p.id === activeProfileId) ?? account;

  return (
    <Ctx.Provider
      value={{
        ready,
        account,
        profiles,
        activeProfileId,
        activeProfile,
        login,
        register,
        logout,
        setActiveProfile,
        refreshProfiles,
      }}
    >
      {children}
    </Ctx.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
