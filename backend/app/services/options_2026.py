from __future__ import annotations

from functools import lru_cache

import pandas as pd

from .season_predictions import _load_driver_list, _load_schedule


@lru_cache(maxsize=1)
def load_options_2026() -> dict:
    season = 2026
    drivers = _load_driver_list(season)
    schedule = _load_schedule(season)

    constructors = sorted(drivers["constructor_id"].unique().tolist())
    drivers_by_constructor: dict[str, list[str]] = {}
    for constructor_id in constructors:
        ids = sorted(
            drivers.loc[drivers["constructor_id"] == constructor_id, "driver_id"]
            .unique()
            .tolist()
        )
        drivers_by_constructor[constructor_id] = ids

    rounds = [
        {
            "round": int(r["round"]),
            "event_name": str(r["event_name"]),
            "event_date": str(r["event_date"]) if pd.notna(r["event_date"]) else "",
        }
        for _, r in schedule.iterrows()
    ]

    return {
        "season": season,
        "constructors": constructors,
        "drivers_by_constructor": drivers_by_constructor,
        "rounds": rounds,
    }

