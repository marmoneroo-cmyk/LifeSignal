import type {
  Copilot,
  CoverageMeta,
  HealthReport,
  MarkerMeta,
  Narrative,
  UserOut,
} from "./types";

// Empty default = same-origin relative paths. In production on Vercel the
// /api/* requests hit the Python serverless function (vercel.json rewrites).
// In dev, next.config.mjs proxies /api/* to the local uvicorn backend.
const BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

const TOKEN_KEY = "ls_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API ${res.status}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export interface TokenOut {
  token: string;
  user: UserOut;
}

export interface AnnualReport {
  years_covered: { marker: string; points: { year: number; value: number }[]; change: number }[];
  disclaimer: string;
}

export const api = {
  register: (payload: Record<string, unknown>) =>
    req<TokenOut>("/api/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  login: (email: string, password: string) =>
    req<TokenOut>("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  me: () => req<UserOut>("/api/auth/me"),
  profiles: () => req<UserOut[]>("/api/auth/profiles"),
  addProfile: (payload: Record<string, unknown>) =>
    req<UserOut>("/api/auth/profiles", { method: "POST", body: JSON.stringify(payload) }),
  annual: (userId: number) => req<AnnualReport>(`/api/users/${userId}/annual`),
  exportUrl: (userId: number) => `${BASE}/api/users/${userId}/export`,
  exportData: (userId: number) => req<unknown>(`/api/users/${userId}/export`),
  listUsers: () => req<UserOut[]>("/api/users"),
  getReport: (userId: number, lang: "he" | "en" = "he") =>
    req<HealthReport>(`/api/users/${userId}/report?lang=${lang}`),
  markers: () => req<MarkerMeta[]>("/api/reference/markers"),
  narrative: (userId: number, lang: "he" | "en") =>
    req<Narrative>(`/api/users/${userId}/narrative?lang=${lang}`),
  copilot: (userId: number, lang: "he" | "en") =>
    req<Copilot>(`/api/users/${userId}/copilot?lang=${lang}`),
  hasData: (userId: number) =>
    req<{ labs: boolean; policies: boolean; medications: boolean; family: boolean; is_empty: boolean }>(
      `/api/users/${userId}/has-data`,
    ),
  loadSample: (userId: number) =>
    req<{ added: Record<string, number> }>(`/api/users/${userId}/load-sample`, { method: "POST" }),
  chat: (userId: number, question: string) =>
    req<{ answer: string; generated_by: string; model: string | null; disclaimer: string }>(
      `/api/users/${userId}/chat`,
      { method: "POST", body: JSON.stringify({ question }) },
    ),
  knownDrugs: (userId: number) =>
    req<{ key: string; label: string }[]>(`/api/users/${userId}/medications/known`),
  familyReference: (userId: number) =>
    req<{ relations: string[]; conditions: string[] }>(`/api/users/${userId}/family/reference`),
  addMedications: (userId: number, medications: unknown[]) =>
    req(`/api/users/${userId}/medications`, {
      method: "POST",
      body: JSON.stringify({ medications }),
    }),
  addFamily: (userId: number, members: unknown[]) =>
    req(`/api/users/${userId}/family`, {
      method: "POST",
      body: JSON.stringify({ members }),
    }),
  coverageTypes: () => req<CoverageMeta[]>("/api/reference/coverage-types"),
  addLabs: (userId: number, results: unknown[]) =>
    req(`/api/users/${userId}/labs`, {
      method: "POST",
      body: JSON.stringify({ results }),
    }),
  addPolicies: (userId: number, policies: unknown[]) =>
    req(`/api/users/${userId}/policies`, {
      method: "POST",
      body: JSON.stringify({ policies }),
    }),
  analyzeTable: async (file: File, userId: number, save = false): Promise<TableAnalysis> => {
    const form = new FormData();
    form.append("file", file);
    form.append("user_id", String(userId));
    form.append("save", save ? "true" : "false");
    const res = await fetch(`${BASE}/api/documents/analyze-table`, {
      method: "POST",
      body: form,
      headers: authHeaders(),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
    return res.json() as Promise<TableAnalysis>;
  },
  extractDocument: async (file: File, kind: string): Promise<ExtractResult> => {
    const form = new FormData();
    form.append("file", file);
    form.append("kind", kind);
    // Note: no Content-Type header — the browser sets the multipart boundary.
    const res = await fetch(`${BASE}/api/documents/extract`, {
      method: "POST",
      body: form,
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
    return res.json() as Promise<ExtractResult>;
  },
};

export interface ExtractedLab {
  marker: string;
  label: string;
  value: number;
  unit: string;
  taken_on: string;
  source_line: string;
}

export interface ExtractedPolicy {
  provider: string;
  coverage_type: string;
  label: string;
  monthly_premium: number;
  renewal_date: string | null;
  source_line: string;
}

export interface DocFlag {
  name: string;
  value: number;
  unit: string;
  status: "high" | "low";
  ref: string;
  matched: boolean;
}

export interface MatchedRow {
  original_name: string;
  marker: string | null;
  value: number;
  unit: string;
  ref: string;
  status: string;
  taken_on: string;
}

export interface TableAnalysis {
  filename: string;
  total_rows: number;
  mapped: number;
  saved: boolean;
  doc_flags: DocFlag[];
  matched_rows: MatchedRow[];
  unmatched_rows: MatchedRow[];
  health_score?: number;
  recommendations: import("./types").Finding[];
  warnings: string[];
}

export interface ExtractResult {
  kind: string;
  filename?: string;
  text_chars: number;
  labs: ExtractedLab[];
  policies: ExtractedPolicy[];
  warnings: string[];
}

export { BASE as API_BASE };
