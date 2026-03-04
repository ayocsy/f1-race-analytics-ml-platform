import numpy as np

def predict_from_features(model, feature_list: list[str], features: dict):
    missing = [f for f in feature_list if f not in features]
    if missing:
        raise ValueError(f"Missing required features: {missing}")
    
    x = np.array([[features[f] for f in feature_list]], dtype=float)
    proba = float(model.predict_proba(x)[0, 1])
    pred = int(proba >= 0.5)
    return proba, pred