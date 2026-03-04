PY=python3

help:
	@echo "Targets:"
	@echo "  ingest       - fetch schedule/results/quali"
	@echo "  build        - create matchups parquet"
	@echo "  check        - sanity checks"
	@echo "  train        - heuristic + logistic regression"
	@echo ""
	@echo "Vars:"
	@echo "  START=2021 END=2024 SEASON=2024"

ingest:
	
	@for y in $(shell seq $(START) $(END)); do \
		$(PY) scripts/ingest_qualifying.py --season $$y; \
	done

build:
	@for y in $(shell seq $(START) $(END)); do \
		$(PY) scripts/build_rank_features.py --season $$y; \
	done

check:
	@for y in $(shell seq $(START) $(END)); do \
		$(PY) scripts/validate_checks.py --season $$y; \
	done

train:
	$(PY) ml/training/baseline_heuristic.py --season $(SEASON)
	$(PY) ml/training/train_baseline.py --season $(SEASON)
