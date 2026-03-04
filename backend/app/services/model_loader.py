import json
import joblib
from ..core.config import MODEL_PATH, FEATURE_LIST_PATH

def load_model_and_features():
    model = joblib.load(MODEL_PATH)
    feature_list = json.loads(FEATURE_LIST_PATH.read_text())
    return model, feature_list