"use client";

import { useEffect, useMemo, useState } from "react";
import type { PredictResponse, Options2026Response, SeasonPredictionsResponse } from "@/lib/type";
import {
  fetchOptions2026,
  fetchSeasonPredictions,
  predictTeammateManual,
} from "@/lib/api";

export default function PredictorForm() {
  const season = 2026;
  const [round, setRound] = useState(1);
  const [constructorId, setConstructorId] = useState("mclaren");
  const [driverA, setDriverA] = useState("");
  const [driverB, setDriverB] = useState("");
  const [qualiA, setQualiA] = useState(1);
  const [qualiB, setQualiB] = useState(2);

  const [options, setOptions] = useState<Options2026Response | null>(null);
  const [optionsError, setOptionsError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [seasonPredictions, setSeasonPredictions] =
    useState<SeasonPredictionsResponse | null>(null);
  const [seasonPredictionsError, setSeasonPredictionsError] = useState<string | null>(null);
  const [seasonPredictionsLoading, setSeasonPredictionsLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    fetchOptions2026()
      .then((data) => {
        if (!mounted) return;
        setOptions(data);
      })
      .catch((err: any) => {
        if (!mounted) return;
        setOptionsError(err?.message ?? "Failed to load metadata");
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    setSeasonPredictionsLoading(true);
    fetchSeasonPredictions(2026)
      .then((data) => {
        if (!mounted) return;
        setSeasonPredictions(data);
      })
      .catch((err: any) => {
        if (!mounted) return;
        setSeasonPredictionsError(err?.message ?? "Failed to load season predictions");
      })
      .finally(() => {
        if (!mounted) return;
        setSeasonPredictionsLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!options) return;

    const rounds = options.rounds ?? [];
    if (rounds.length && !rounds.find((r) => r.round === round)) {
      setRound(rounds[0].round);
    }

    if (options.constructors.length && !options.constructors.includes(constructorId)) {
      setConstructorId(options.constructors[0]);
    }

    const drivers = options.drivers_by_constructor[constructorId] ?? [];
    if (drivers.length) {
      if (!drivers.includes(driverA)) setDriverA(drivers[0]);
      if (!drivers.includes(driverB) || driverB === driverA) {
        setDriverB(drivers[1] ?? drivers[0]);
      }
    }
  }, [options, constructorId, round, driverA, driverB]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);

    if (!driverA.trim() || !driverB.trim()) {
      setError("Please enter both driver IDs.");
      return;
    }
    if (driverA.trim() === driverB.trim()) {
      setError("Driver A and Driver B must be different.");
      return;
    }

    const payload = {
      season,
      round,
      driver_a: driverA.trim(),
      driver_b: driverB.trim(),
      quali_pos_a: Number(qualiA),
      quali_pos_b: Number(qualiB),
    };

    try {
      setLoading(true);
      const out = await predictTeammateManual(payload);
      setResult(out);
    } catch (err: any) {
      let msg = err?.message ?? "Prediction failed";
      try {
        const parsed = JSON.parse(msg);
        if (parsed?.detail) msg = parsed.detail;
      } catch {}
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  const rounds = options?.rounds ?? [];
  const constructors = options?.constructors ?? [];
  const drivers = options?.drivers_by_constructor[constructorId] ?? [];
  const driverBOptions = useMemo(() => drivers.filter((d) => d !== driverA), [drivers, driverA]);

  return (
    <>
      <div className="card">
        <form onSubmit={onSubmit} className="form-grid">
          <div className="grid-2">
            <label className="field">
              <span>Constructor (2026)</span>
              <select
                value={constructorId}
                onChange={(e) => setConstructorId(e.target.value)}
                disabled={!constructors.length}
              >
                {constructors.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Round (GP)</span>
              <select
                value={round}
                onChange={(e) => setRound(parseInt(e.target.value, 10))}
                disabled={!rounds.length}
              >
                {rounds.map((r) => (
                  <option key={r.round} value={r.round}>
                    {r.round} — {r.event_name}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="grid-2">
            <label className="field">
              <span>Driver A</span>
              <select
                value={driverA}
                onChange={(e) => setDriverA(e.target.value)}
                disabled={!drivers.length}
              >
                {drivers.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </label>

            <label className="field">
              <span>Driver B</span>
              <select
                value={driverB}
                onChange={(e) => setDriverB(e.target.value)}
                disabled={!driverBOptions.length}
              >
                {driverBOptions.map((d) => (
                  <option key={d} value={d}>
                    {d}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="grid-2">
            <label className="field">
              <span>Qualifying Position A</span>
              <input
                type="number"
                min={1}
                value={qualiA}
                onChange={(e) => setQualiA(parseInt(e.target.value, 10) || 1)}
              />
            </label>

            <label className="field">
              <span>Qualifying Position B</span>
              <input
                type="number"
                min={1}
                value={qualiB}
                onChange={(e) => setQualiB(parseInt(e.target.value, 10) || 1)}
              />
            </label>
          </div>

          <div className="hint">
            2026 only. Drivers are filtered by constructor. Enter qualifying rank to compare.
          </div>

          <button type="submit" className="primary" disabled={loading || !options}>
            {loading ? "Predicting..." : "Predict"}
          </button>
        </form>

        <div className="stack">
          {optionsError && (
            <div className="notice warn">
              <b>Metadata load failed:</b> {optionsError}
            </div>
          )}
          {error && (
            <div className="notice error">
              <b>Error:</b> {error}
            </div>
          )}
          {result && <ResultCard driverA={driverA} driverB={driverB} result={result} />}
        </div>
      </div>

      <div className="card season-card">
        <div className="season-header">
          <div>
            <h3>2026 Season Predictions</h3>
            <p>All rounds, using the 2026 driver list.</p>
          </div>
          {seasonPredictionsLoading && <span className="chip">Loading…</span>}
        </div>

        {seasonPredictionsError && (
          <div className="notice error">
            <b>Season predictions failed:</b> {seasonPredictionsError}
          </div>
        )}

        {seasonPredictions && (
          <>
            <div className="hint">
              Assumption: {seasonPredictions.assumptions.note}
            </div>

            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Round</th>
                    <th>Event</th>
                    <th>Team</th>
                    <th>Driver A</th>
                    <th>Driver B</th>
                    <th>Predicted Winner</th>
                    <th>P(A wins)</th>
                  </tr>
                </thead>
                <tbody>
                  {seasonPredictions.predictions.map((row, idx) => {
                    const pct = Math.round(row.probability_driver_a_win * 100);
                    return (
                      <tr key={`${row.round}-${row.constructor_id}-${idx}`}>
                        <td>{row.round}</td>
                        <td>{row.event_name}</td>
                        <td>{row.constructor_id}</td>
                        <td>{row.driver_a}</td>
                        <td>{row.driver_b}</td>
                        <td className="winner">{row.predicted_winner}</td>
                        <td>{pct}%</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </>
  );
}

function ResultCard({
  driverA,
  driverB,
  result,
}: {
  driverA: string;
  driverB: string;
  result: PredictResponse;
}) {
  const pct = Math.round(result.probability_win * 100);
  const winner = result.prediction === 1 ? driverA : driverB;

  return (
    <div className="result-card">
      <h3>Prediction</h3>
      <p>
        <b>{winner}</b> predicted to finish ahead.
      </p>
      <p>
        Probability {driverA} beats {driverB}: <b>{pct}%</b>
      </p>

      <details>
        <summary>Features used</summary>
        <pre>
{JSON.stringify(result.features_used, null, 2)}
        </pre>
      </details>
    </div>
  );
}
