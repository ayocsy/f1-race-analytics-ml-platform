
import argparse
import json
from pathlib import Path
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix
import joblib

# Index(['season', 'round', 'constructor_id', 'driver_a_id', 'driver_b_id', 
# '     quali_pos_a', 'quali_pos_b', 'quali_pos_diff', 'finish_order_a',
#       'finish_order_b', 'status_a', 'status_b', 'label'], 
#        dtype='object')

# Result -> y
# Feature -> 'quali_pos_diff', 'h2h_win_rate_last_10' -> x
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

    # Split train/test by season
    all_seasons = sorted(all_seasons)
    split_idx = max(1, int(len(all_seasons) * (1.0 - 0.2)))
    train_seasons = all_seasons[:split_idx]
    test_seasons = all_seasons[split_idx:]

    train_df = pd.concat(
        [pd.read_parquet(proc_dir / f"matchups_{s}.parquet") for s in train_seasons],
        ignore_index=True,
    )
    test_df = pd.concat(
        [pd.read_parquet(proc_dir / f"matchups_{s}.parquet") for s in test_seasons],
        ignore_index=True,
    )

    x_train = train_df[features]
    y_train = train_df["label"].astype(int)
    x_test = test_df[features]
    y_test = test_df["label"].astype(int)

    # training
    model = LogisticRegression(max_iter=9999)
    model.fit(x_train, y_train)
    
    # testing
    y_pred = model.predict(x_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    # Saving Model
    artifacts = Path("../ml/artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, REPO_ROOT / "ml" / "artifacts" / "model_quali.pkl")
    (REPO_ROOT / "ml" / "artifacts" / "feature_list.json").write_text(json.dumps(features, indent=2))
    (REPO_ROOT / "ml" / "artifacts" / "metrics_quali.json").write_text(json.dumps({
        "accuracy": acc,
        "f1": f1,
        "confusion_matrix": cm.tolist()
        }, indent=2))
    
    print(f"Accuracy: {acc}")
    print(f"F1 Score: {f1}")
    print(f"Confusion Matrix:\n{cm}")
    print(f"Predict: {y_pred}")
    print(f"Test: {y_test}")

if __name__ == "__main__":
    main()
