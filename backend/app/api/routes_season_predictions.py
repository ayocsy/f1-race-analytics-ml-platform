from fastapi import APIRouter, HTTPException

from ..services.season_predictions import build_season_predictions

router = APIRouter()


@router.get("/predictions/season/{season}")
def season_predictions(season: int):
    try:
        df = build_season_predictions(season)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "season": season,
        "assumptions": {
            "quali_pos_diff": 0,
            "note": "Pre-race predictions assume equal qualifying pace for both teammates.",
        },
        "count": len(df),
        "predictions": df.to_dict(orient="records"),
    }

