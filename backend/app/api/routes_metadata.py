from fastapi import APIRouter
from functools import lru_cache
from ..services.model_loader import load_model_and_features
from ..services.db import get_conn

router = APIRouter()
_, feature_list = load_model_and_features()

@lru_cache(maxsize=1)
def _load_options():
    con = get_conn()
    seasons = [int(r[0]) for r in con.execute(
        "SELECT DISTINCT season FROM qualifying ORDER BY season"
    ).fetchall()]

    rounds_by_season: dict[str, list[int]] = {}
    drivers_by_season: dict[str, list[str]] = {}

    for season in seasons:
        rounds = [int(r[0]) for r in con.execute(
            "SELECT DISTINCT round FROM qualifying WHERE season = ? ORDER BY round",
            (season,),
        ).fetchall()]
        drivers = [r[0] for r in con.execute(
            "SELECT DISTINCT driver_id FROM qualifying WHERE season = ? ORDER BY driver_id",
            (season,),
        ).fetchall()]
        rounds_by_season[str(season)] = rounds
        drivers_by_season[str(season)] = drivers

    con.close()
    return {
        "seasons": seasons,
        "rounds_by_season": rounds_by_season,
        "drivers_by_season": drivers_by_season,
    }

@router.get("/metadata")
def metadata():
    return {
        "model_type": "logistic_regression",
        "features": feature_list,
        "task": "teammate_outcome",
        "options": _load_options(),
    }
