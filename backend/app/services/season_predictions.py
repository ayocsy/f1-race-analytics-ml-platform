from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable

import pandas as pd

from .features_services import compute_h2h_win_rate_last_n
from .model_loader import load_model_and_features
from .predict_services import predict_from_features
from ..core.config import PROJECT_DIR


def _slugify(value: str) -> str:
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def _load_schedule(season: int) -> pd.DataFrame:
    path = PROJECT_DIR / "data" / "raw" / f"schedule_{season}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Schedule not found at {path}")
    df = pd.read_csv(path)
    keep = ["round", "event_name", "event_date"]
    missing = [c for c in keep if c not in df.columns]
    if missing:
        raise ValueError(f"Schedule missing columns: {missing}")
    return df[keep].copy()


def _load_driver_list(season: int) -> pd.DataFrame:
    path = PROJECT_DIR / "data" / "raw" / f"driver_list_{season}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Driver list not found at {path}")
    df = pd.read_csv(path)

    # Allow a few common column names.
    if "driver_id" not in df.columns:
        for alt in ["driver", "driver_name", "name"]:
            if alt in df.columns:
                df["driver_id"] = df[alt]
                break
    if "constructor_id" not in df.columns:
        for alt in ["constructor", "team", "team_name"]:
            if alt in df.columns:
                df["constructor_id"] = df[alt]
                break

    if "driver_id" not in df.columns or "constructor_id" not in df.columns:
        raise ValueError(
            "Driver list must include columns: driver_id, constructor_id "
            "(or driver_name/constructor as alternatives)."
        )

    df["driver_id"] = df["driver_id"].map(_slugify)
    df["constructor_id"] = df["constructor_id"].map(_slugify)
    df.insert(0, "season", season)
    return df[["season", "driver_id", "constructor_id"]].copy()


def _team_pairs(drivers: pd.DataFrame) -> Iterable[tuple[str, str, str]]:
    grouped = drivers.groupby("constructor_id")
    for constructor_id, g in grouped:
        ids = sorted(g["driver_id"].unique().tolist())
        if len(ids) != 2:
            continue
        yield constructor_id, ids[0], ids[1]


@lru_cache(maxsize=4)
def build_season_predictions(season: int) -> pd.DataFrame:
    schedule = _load_schedule(season)
    drivers = _load_driver_list(season)

    model, feature_list = load_model_and_features()

    rows: list[dict] = []
    for _, r in schedule.iterrows():
        rnd = int(r["round"])
        event_name = str(r["event_name"])
        event_date = str(r["event_date"]) if pd.notna(r["event_date"]) else ""

        for constructor_id, driver_a, driver_b in _team_pairs(drivers):
            # Pre-race assumption: equal qualifying pace.
            quali_pos_diff = 0
            h2h = compute_h2h_win_rate_last_n(season, rnd, driver_a, driver_b, n=10)
            features = {
                "quali_pos_diff": quali_pos_diff,
                "h2h_win_rate_last_10": h2h,
            }
            proba, pred = predict_from_features(model, feature_list, features)
            predicted_winner = driver_a if pred == 1 else driver_b

            rows.append(
                {
                    "season": season,
                    "round": rnd,
                    "event_name": event_name,
                    "event_date": event_date,
                    "constructor_id": constructor_id,
                    "driver_a": driver_a,
                    "driver_b": driver_b,
                    "probability_driver_a_win": proba,
                    "prediction": pred,
                    "predicted_winner": predicted_winner,
                    "quali_pos_diff": quali_pos_diff,
                    "h2h_win_rate_last_10": h2h,
                }
            )

    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values(["round", "constructor_id", "driver_a"]).reset_index(drop=True)
    return out

