# Digital Public Safety Shield
**ET AI Hackathon 2026 — Problem Statement 6: AI for Digital Public Safety**

A working prototype for **Digital Arrest Scam Detection**, **Phishing Detection**, and **Citizen Fraud Shield**,
built to demonstrate compound-risk fusion detection over multi-signal inputs, matching
the challenge brief's requirement for "detecting compound risk conditions no single
sensor would flag alone." Covers two distinct scam mechanisms — voice-based social
engineering (digital arrest) and link-based credential harvesting (phishing) — through
separate signal categories feeding one fusion verdict.

## Quick start

```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

This installs dependencies, regenerates the dataset, trains the model, runs the full
smoke test suite, and launches the app. Every step is idempotent — safe to re-run.

**Before every demo/judging session**, run:
```bash
python3 -m tests.smoke_test
```
14 automated checks. If anything fails, DO NOT demo until fixed — see the test output
for exactly what broke.

## What this is

Two integrated tools sharing one detection engine:

1. **Law Enforcement / Telecom Dashboard** — paste a transcript, get a fused risk
   verdict, explainable signal breakdown, and an auto-generated structured alert
   package (JSON, audit-trail-ready).
2. **Citizen Fraud Shield** — plain-language guided chat (English + Hindi) that tells
   a worried citizen exactly what to do, with a "show technical details" expander for
   judges.

## Architecture

```
Transcript ──┬──► Rule-based signal detector (6 explainable categories)
             └──► ML classifier (TF-IDF + Logistic Regression)
                              │
                    Fusion engine (weighted + compound-risk override)
                              │
                         Risk verdict (HIGH / MEDIUM / LOW + audit trail)
                    ┌─────────┴─────────┐
        Law enforcement dashboard   Citizen fraud shield
           + auto alert JSON           (EN / HI chat)
```

**Why two independent detectors, not one model?** The brief explicitly asks for
compound-risk detection — conditions that "no single sensor would flag alone." Here,
agreement between the ML model and the rule engine gives high confidence; disagreement
is visible in the audit trail rather than silently resolved. This directly targets the
brief's "false positive rate for citizen-facing tools must be very low" requirement.

**Why no live external API for the core decision?** A judged live demo cannot depend
on venue wifi or a third-party API rate limit. The core classifier is a small trained
model that runs entirely offline. This was a deliberate reliability choice, not a
capability gap — see `ROADMAP.md` for where an LLM layer would add value in production.

## Honest performance numbers

We report two numbers, not one, because testing only on data from the same generation
templates is misleading:

| Test set | Accuracy | Notes |
|---|---|---|
| Held-out split of training data | 100% | Same template family as training — expected to be high, not a generalization claim |
| **Independent adversarial set** (60 hand-written cases, never seen in training) | **98.3%** (59/60) | The number we stand behind. 30 scam / 30 legit, spanning digital arrest scams AND phishing scams, plus Hinglish phrasing. 1 false positive (legit OTP warning), 0 false negatives |

Run `python3 -m backend.detection_engine` to reproduce the adversarial evaluation.

## Project structure

```
scam-shield/
├── app.py                        # Streamlit app (3 tabs: LE dashboard, citizen shield, judge metrics)
├── setup_and_run.sh               # One-command setup
├── requirements.txt
├── data/
│   ├── generate_dataset.py        # Synthetic training data generator
│   ├── adversarial_eval_set.py    # Independent hand-written test cases
│   └── scam_dataset.csv           # Generated dataset (900 labeled transcripts)
├── backend/
│   ├── signal_detector.py         # Rule-based explainable pattern detection
│   ├── train_model.py             # ML model training + evaluation
│   └── detection_engine.py        # Fusion logic, verdict, alert generation
├── models/                        # Trained model artifacts (generated)
└── tests/
    └── smoke_test.py              # 14-check pre-demo validation suite
```

## Scope (intentional, not a limitation)

The brief's "Digital Arrest Scam Detection & Alerting" sub-track specifically calls for a classifier
"trained on digital arrest scam patterns." We built that, and added phishing detection (fake
account-suspension links) as it directly extends the Citizen Fraud Shield's broader mandate to
assess "suspicious calls, payment requests, or messages." Other scam families named nowhere in
the brief — lottery/prize fraud, fake job offers, romance scams, loan-app harassment — are
**out of scope by design**, not missed. The brief explicitly notes its examples are "illustrative
only," giving teams latitude to go deep rather than attempt exhaustive coverage. Extending to
additional scam families is a natural Phase 2 (see ROADMAP.md) using the same fusion architecture
— new signal category + training examples — but isn't required for this submission.

## Known limitations (be upfront about these with judges)

- **Hinglish (code-mixed Hindi-English) is a weaker spot.** The classifier and rule engine work primarily on English text. Hinglish scam scripts are detected via the ML model's general scam-vocabulary learning (English loanwords like "case," "arrest," "camera" still trigger it), but the explainable rule engine — which relies on English regex — often can't parse it directly. Detection still works in practice (verified on our adversarial set) but with lower confidence and less explainability than pure English or Hindi input.
- **Synthetic training data.** No real NCRP/CERT-In complaint data was available in the
  2-day window. The architecture and fusion methodology are the contribution; a
  production deployment needs real, anonymized complaint data at scale.
- **English + Hindi only** in this prototype; the brief calls for 12 regional languages
  — architecture supports adding more language packs to the advice dictionary.
- **No live telecom/NCRP integration** — the alert JSON is structured to be
  API-ready but isn't wired to a real endpoint (no such sandbox was available).

Being upfront about these earns more credibility with judges than overclaiming.
