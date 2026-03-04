
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes_health import router as health_router
from .api.routes_predict import router as predict_router
from .api.routes_metadata import router as metadata_router
from .api.routes_season_predictions import router as season_predictions_router
from .api.routes_options_2026 import router as options_2026_router


app = FastAPI(title="F1 Teammate Outcome Predictor")

origins = [
    "http://localhost:3000",   # Next.js dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(metadata_router)
app.include_router(predict_router)
app.include_router(season_predictions_router)
app.include_router(options_2026_router)
