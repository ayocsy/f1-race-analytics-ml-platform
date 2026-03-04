import type {
  PredictRequest,
  PredictResponse,
  MetadataResponse,
  SeasonPredictionsResponse,
  Options2026Response,
  ManualPredictRequest,
} from "./type";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE;

export async function predictTeammate(req: PredictRequest): Promise<PredictResponse> {
  if (!API_BASE) throw new Error("NEXT_PUBLIC_API_BASE is not set");

  const res = await fetch(`${API_BASE}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `Request failed: ${res.status}`);
  }

  return res.json();
}

export async function fetchMetadata(): Promise<MetadataResponse> {
  if (!API_BASE) throw new Error("NEXT_PUBLIC_API_BASE is not set");

  const res = await fetch(`${API_BASE}/metadata`, { cache: "no-store" });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchSeasonPredictions(
  season: number
): Promise<SeasonPredictionsResponse> {
  if (!API_BASE) throw new Error("NEXT_PUBLIC_API_BASE is not set");

  const res = await fetch(`${API_BASE}/predictions/season/${season}`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function fetchOptions2026(): Promise<Options2026Response> {
  if (!API_BASE) throw new Error("NEXT_PUBLIC_API_BASE is not set");

  const res = await fetch(`${API_BASE}/options/2026`, { cache: "no-store" });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function predictTeammateManual(
  req: ManualPredictRequest
): Promise<PredictResponse> {
  if (!API_BASE) throw new Error("NEXT_PUBLIC_API_BASE is not set");

  const res = await fetch(`${API_BASE}/predict_manual`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });

  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `Request failed: ${res.status}`);
  }

  return res.json();
}
