import type { HealthStatus, HistoryEntry, PredictionResult } from "./types";

export async function predictImage(file: File): Promise<PredictionResult> {
  const form = new FormData();
  form.append("image", file);

  const res = await fetch("/api/predict", { method: "POST", body: form });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || data.detail || "Prediction failed");
  return data;
}

export async function fetchHistory(): Promise<HistoryEntry[]> {
  const res = await fetch("/api/history");
  if (!res.ok) throw new Error("Failed to load history");
  return res.json();
}

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch("/api/health");
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}
