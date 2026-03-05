# F1 Teammate Outcome Predictor

A small end-to-end project that predicts which driver finishes ahead in a **teammate vs teammate** matchup.
It’s meant to be practical: pick a 2026 team, choose a GP round, enter both drivers’ qualifying positions, and get a win probability.

## What It Does

- **Frontend (Next.js):** 2026-only UI: `constructor -> 2 drivers`, `round (GP)`, `quali pos A/B`, then predict.
- **Backend (FastAPI):** feature building + model inference + simple “options” endpoints for the UI.
- **Model:** started with **Logistic Regression** as a baseline, but accuracy wasn’t good enough, so I switched to **XGBoost** for better precision.

## Inputs You Need (Checked In)

These files drive the 2026 UX and the season table:

- `data/raw/schedule_2026.csv`
- `data/raw/driver_list_2026.csv` (format below)

`data/raw/driver_list_2026.csv`:

```csv
driver_id,constructor_id
norris,mclaren
piastri,mclaren
max_verstappen,red_bull
hadjar,red_bull
...
```

## How Predictions Work

The model uses 2 features:

- `quali_pos_diff` = `quali_pos_a - quali_pos_b` (you type both qualifying ranks in the UI)
- `h2h_win_rate_last_10` = historical teammate head-to-head rate for A vs B (rolling lookback)

The API returns:

- `probability_win`: probability Driver A finishes ahead
- `prediction`: `1` means A wins, `0` means B wins
- `features_used`: the exact feature values used for inference

## Quickstart

### 1) Backend

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install fastapi uvicorn pandas numpy scikit-learn xgboost joblib fastf1
uvicorn backend.app.main:app --reload --port 8000
```

Backend endpoints:

- `GET /health`
- `GET /options/2026` (constructors, drivers by constructor, rounds)
- `POST /predict_manual` (manual qualifying positions)
- `GET /predictions/season/2026` (all rounds, all teams)

### 2) Frontend

```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev
```

Open `http://localhost:3000`.

## Training (Optional)

If you want to rebuild the model artifacts:

- Logistic Regression baseline: `ml/training/training_logistic.py`
- XGBoost training: `ml/training/training_XGBoost.py`

Both write artifacts under `ml/artifacts/` (model + feature list + metrics).

## Result 
<img width="1311" height="697" alt="image" src="https://github.com/user-attachments/assets/2f361dbe-c7e1-45c6-8096-ad19d1354ab6" />
Users can select a constructor and a Grand Prix, then input the qualifying positions of a driver and their teammate. Based on this information, the platform predicts the probability of the driver outperforming their teammate.

