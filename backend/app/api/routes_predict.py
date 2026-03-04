from fastapi import APIRouter, HTTPException
from ..schemas.predict import PredictRequest, PredictResponse, ManualPredictRequest
from ..services.model_loader import load_model_and_features
from ..services.features_services import build_features
from ..services.features_services import compute_h2h_win_rate_last_n
from ..services.predict_services import predict_from_features

router = APIRouter()
model, feature_list = load_model_and_features()

@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    if req.driver_a == req.driver_b:
        raise HTTPException(status_code=400, detail="driver_a and driver_b must be different.")

    try:
        feats = build_features(req.season, req.round, req.driver_a, req.driver_b)
        proba, pred = predict_from_features(model, feature_list, feats)
        return PredictResponse(probability_win=proba, prediction=pred, features_used=feats)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/predict_manual", response_model=PredictResponse)
def predict_manual(req: ManualPredictRequest):
    if req.driver_a == req.driver_b:
        raise HTTPException(status_code=400, detail="driver_a and driver_b must be different.")

    try:
        quali_pos_diff = int(req.quali_pos_a) - int(req.quali_pos_b)
        h2h = compute_h2h_win_rate_last_n(req.season, req.round, req.driver_a, req.driver_b, n=10)
        feats = {
            "quali_pos_diff": quali_pos_diff,
            "h2h_win_rate_last_10": h2h,
        }
        proba, pred = predict_from_features(model, feature_list, feats)
        return PredictResponse(probability_win=proba, prediction=pred, features_used=feats)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
