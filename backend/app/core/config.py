from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]  # backend/app
PROJECT_DIR = BASE_DIR.parents[1]  # repo root
DB_PATH = BASE_DIR / "data" / "f1.db"
ARTIFACT_DIR = BASE_DIR / "ml" / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "model.pkl"
FEATURE_LIST_PATH = ARTIFACT_DIR / "feature_list.json"
PROCESSED_DATA_PATH = PROJECT_DIR / "data" / "processed" / "output.csv"
