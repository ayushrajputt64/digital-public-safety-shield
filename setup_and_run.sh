#!/bin/bash
# One-command setup: generates data, trains model, runs tests, launches app.
# Safe to re-run any time — every step is idempotent.
set -e

echo "=== 1/4: Installing dependencies ==="
pip install -r requirements.txt --break-system-packages -q || pip install -r requirements.txt -q

echo "=== 2/4: Generating training dataset ==="
python3 data/generate_dataset.py

echo "=== 3/4: Training model ==="
python3 backend/train_model.py

echo "=== 4/4: Running smoke tests ==="
python3 -m tests.smoke_test

echo ""
echo "All checks passed. Launching app..."
echo "If this is the demo machine, run: streamlit run app.py"
streamlit run app.py
