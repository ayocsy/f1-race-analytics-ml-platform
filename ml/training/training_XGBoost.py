
import argparse
import json
from pathlib import Path
import pandas as pd
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import joblib

REPO_ROOT = Path(__file__).resolve().parents[2]

features = ["quali_pos_diff", "h2h_win_rate_last_10"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2014)
    ap.add_argument("--end", type=int, default=2025) 
    args = ap.parse_args()

    proc_dir = REPO_ROOT / "data" / "processed"
    all_seasons = []
    for season in range(args.start, args.end + 1):
        path = proc_dir / f"matchups_{season}.parquet"
        if path.exists():
            all_seasons.append(season)

    all_seasons = sorted(all_seasons)
    if len(all_seasons) < 2:
        raise SystemExit("Need at least 2 seasons to run rolling backtest")

    def load_seasons(seasons):
        return pd.concat(
            [pd.read_parquet(proc_dir / f"matchups_{s}.parquet") for s in seasons],
            ignore_index=True,
        )

    print("[ROLLING BACKTEST]")
    for i in range(1, len(all_seasons)):
        train_seasons = all_seasons[:i]
        test_season = all_seasons[i]

        train_df = load_seasons(train_seasons)
        test_df = load_seasons([test_season])

        x_train = train_df[features]
        y_train = train_df["label"].astype(int)
        x_test = test_df[features]
        y_test = test_df["label"].astype(int)

        model = XGBClassifier(
            n_estimators=200,
            max_depth=10,
            learning_rate=0.2
        )
        model.fit(x_train, y_train)

        y_pred = model.predict(x_test)
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)

        joblib.dump(model, REPO_ROOT / "ml" / "artifacts" / "model_XGBoost.pkl")
        (REPO_ROOT / "ml" / "artifacts" / "feature_list.json").write_text(json.dumps(features, indent=2))
        (REPO_ROOT / "ml" / "artifacts" / "metrics_XGBoost.json").write_text(json.dumps({
            "accuracy": acc,
            "f1": f1,
            "confusion_matrix": cm.tolist()
        }, indent=2))
    
        print(f"Train seasons: {train_seasons} -> Test season: {test_season}")
        print(f"Accuracy: {acc}")
        print(f"F1 Score: {f1}")
        print(f"Confusion Matrix:\n{cm}")

if __name__ == "__main__":
    main()
