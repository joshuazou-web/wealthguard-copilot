import { useEffect, useState } from "react";

export interface DogfoodSession {
  id: string;
  occurredAt: string;
  query: string;
  outcome: string;
  evidenceCount: number;
  evidenceOpened: number;
  feedback?: "useful" | "needs_work";
  note?: string;
}

export interface DogfoodState {
  startedAt: string;
  visitDays: string[];
  sessions: DogfoodSession[];
  miniProgramSignals: Array<{
    occurredAt: string;
    reason: "faster_entry" | "notifications" | "wechat_sharing";
  }>;
}

export function usePersistentState<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const saved = window.localStorage.getItem(key);
      return saved ? (JSON.parse(saved) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    window.localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

export function createDogfoodState(): DogfoodState {
  const now = new Date();
  return {
    startedAt: now.toISOString(),
    visitDays: [now.toISOString().slice(0, 10)],
    sessions: [],
    miniProgramSignals: []
  };
}

export function downloadDogfoodData(data: DogfoodState) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `wealthguard-dogfood-${new Date().toISOString().slice(0, 10)}.json`;
  anchor.click();
  URL.revokeObjectURL(url);
}
