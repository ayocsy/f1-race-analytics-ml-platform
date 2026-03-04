
# Index(['season', 'round', 'constructor_id', 'driver_a_id', 'driver_b_id', 
# '     quali_pos_a', 'quali_pos_b', 'quali_pos_diff', 'finish_order_a',
#       'finish_order_b', 'status_a', 'status_b', 'label'], 
#        dtype='object')

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

REPO_ROOT = Path(__file__).resolve().parents[2]

# Predict baseline: A wins if quali_pos_a < quali_pos_b.

def main():
    ap = argparse.ArgumentParser()
    # ap.add_argument("--season", type=int, required=True)

    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)

    args = ap.parse_args()

    proc_dir = REPO_ROOT / "data" / "processed"
    # df = pd.read_parquet(proc_dir / f"matchups_{args.season}.parquet")

    for c in range (args.start, args.end + 1):
        df = pd.read_parquet(proc_dir / f"matchups_{c}.parquet")
        
        a = df["label"].astype(int)
        pred = (df["quali_pos_a"] < df["quali_pos_b"]).astype(int)

        test = df[["driver_a_id", "h2h_win_rate"]]
        acc = accuracy_score(a, pred)
        f1 = f1_score(a, pred)
        cm = confusion_matrix(a, pred)

        print(f"Season {c}:")
        print(f"[HEURISTIC] acc={acc:.4f} f1={f1:.4f}")
        print(cm)
        print(test)


if __name__ == "__main__":
    main()
