from fastapi import APIRouter, HTTPException

from ..services.options_2026 import load_options_2026

router = APIRouter()


@router.get("/options/2026")
def options_2026():
    try:
        return load_options_2026()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

