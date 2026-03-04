
import pandas as pd
from functools import lru_cache
from .db import get_conn
from ..core.config import PROCESSED_DATA_PATH

def race_key(season: int, rnd: int) -> int:
    return season * 100 + rnd

@lru_cache(maxsize=1)
def _load_processed_df() -> pd.DataFrame:
    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(f"Processed data not found at {PROCESSED_DATA_PATH}")
    return pd.read_csv(PROCESSED_DATA_PATH)

def get_quali_pos_map(season: int, rnd: int, driver_ids: list[str]) -> dict[str, int]:
    # Prefer SQLite when available, but fall back to processed CSV if DB is empty.
    try:
        con = get_conn()  # get connection to the database
        q = con.execute(
            f"""
            SELECT driver_id, quali_pos
            FROM qualifying
            WHERE season = ? AND round = ? AND driver_id IN ({",".join(["?"] * len(driver_ids))})
            """,
            (season, rnd, *driver_ids),
        ).fetchall()
        con.close()
        if q:
            return {row["driver_id"]: int(row["quali_pos"]) for row in q}
    except Exception:
        # Fall through to CSV path
        pass

    df = _load_processed_df()
    subset = df[(df["season"] == season) & (df["round"] == rnd) & (df["driver_id"].isin(driver_ids))]
    return {row["driver_id"]: int(row["quali_pos"]) for _, row in subset.iterrows()}

def compute_quali_pos_diff(season: int, rnd: int, a: str, b: str) -> int:
    mp = get_quali_pos_map(season, rnd, [a, b])
    if a not in mp or b not in mp:
        raise ValueError("Missing qualifying data for one or both drivers.")
    return mp[a] - mp[b]

def compute_h2h_win_rate_last_n(season: int, rnd: int, a: str, b: str, n: int = 10) -> float:
    """Head-to-head win rate for A vs B in past teammate meetings only."""
    target = race_key(season, rnd)

    try:
        con = get_conn()
        # Past results for both drivers (we filter in python)
        ra = pd.read_sql_query(
            "SELECT season, round, constructor_id, finish_order, status FROM results WHERE driver_id = ?",
            con, params=(a,)
        )
        rb = pd.read_sql_query(
            "SELECT season, round, constructor_id, finish_order, status FROM results WHERE driver_id = ?",
            con, params=(b,)
        )
        con.close()
    except Exception:
        df = _load_processed_df()
        ra = df[df["driver_id"] == a][["season", "round", "constructor_id", "finish_order"]].copy()
        rb = df[df["driver_id"] == b][["season", "round", "constructor_id", "finish_order"]].copy()
        ra["status"] = ""
        rb["status"] = ""

    # Create time key and filter to past only
    ra["rk"] = ra["season"] * 100 + ra["round"]
    rb["rk"] = rb["season"] * 100 + rb["round"]
    ra = ra[ra["rk"] < target]
    rb = rb[rb["rk"] < target]

    # Join where they were teammates (same constructor in same race)
    m = ra.merge(rb, on=["season", "round", "constructor_id"], suffixes=("_a", "_b"))

    if m.empty:
        return 0.5  # neutral prior if never teammates historically

    m["rk"] = m["season"] * 100 + m["round"]
    m = m.sort_values("rk", ascending=False).head(n)

    # Win = smaller finish_order (assumes finish_order exists and comparable)
    wins = (m["finish_order_a"].astype(int) < m["finish_order_b"].astype(int)).sum()
    total = len(m)
    return float(wins / total) if total > 0 else 0.5

def build_features(season: int, rnd: int, driver_a: str, driver_b: str) -> dict:
    quali_pos_diff = compute_quali_pos_diff(season, rnd, driver_a, driver_b)
    h2h = compute_h2h_win_rate_last_n(season, rnd, driver_a, driver_b, n=10)

    return {
        "quali_pos_diff": quali_pos_diff,
        "h2h_win_rate_last_10": h2h,
    }
