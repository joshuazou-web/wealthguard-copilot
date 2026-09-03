import type { Instrument, ResearchResponse, UserProfile } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) }
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  instruments: () => request<Instrument[]>("/api/instruments"),
  documents: () => request<any[]>("/api/documents"),
  research: (sessionId: string, query: string, profile: UserProfile, instrumentIds: string[]) =>
    request<ResearchResponse>("/api/research", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, query, profile, instrument_ids: instrumentIds })
    }),
  compare: (instrumentIds: string[]) =>
    request<any>("/api/compare", { method: "POST", body: JSON.stringify({ instrument_ids: instrumentIds }) }),
  portfolio: (holdings: Array<{ instrument_id: string; weight: number }>, scenarioShock: number) =>
    request<any>("/api/portfolio", {
      method: "POST",
      body: JSON.stringify({ holdings, scenario_shock: scenarioShock })
    }),
  audit: (sessionId: string) => request<any[]>(`/api/audit?session_id=${encodeURIComponent(sessionId)}`),
  evaluation: () => request<any>("/api/evaluation")
};
