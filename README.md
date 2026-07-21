# 🛡️ Digital Public Safety Shield

**Scam detection for "digital arrest" fraud and phishing calls, fused from an ML classifier and an explainable rule engine — with a citizen-facing safety chat in 6 languages.**

Built for the ET AI Hackathon 2026 — Problem Statement 6: *AI for Digital Public Safety*.

---

## The problem

"Digital arrest" scams are one of the fastest-growing fraud patterns in India: a caller impersonates police, CBI, customs, or a court, claims the victim is under investigation, keeps them on a forced video call, and pressures them to transfer money to avoid "arrest." These scams work because they compound multiple pressure tactics at once — authority, urgency, isolation, and payment demands — and no single cue is enough on its own to call it out with confidence. That's the core design constraint this project is built around.

## What this is

A working prototype with two integrated tools sharing one detection engine:

1. **Law Enforcement / Telecom Dashboard** — paste a call transcript, get a fused risk verdict, a plain-English breakdown of exactly which signals fired and why, and an auto-generated structured alert package (JSON, audit-trail-ready).
2. **Citizen Fraud Shield** — a guided, plain-language chat that walks a worried citizen through assessing a suspicious call or message, with advice in English, Hindi, Tamil, Telugu, Bengali, and Marathi.

Both tools sit on top of the same fusion engine, so the risk logic is defined once and consumed twice — no duplicated or drifting detection rules between the "expert" and "citizen" views.

## Architecture

```
Transcript ──┬──► Rule-based signal detector (11 explainable categories)
             └──► ML classifier (TF-IDF + Logistic Regression)
                              │
                    Fusion engine (weighted + compound-risk override)
                              │
                    Risk verdict: HIGH / MEDIUM / LOW + audit trail
                    ┌─────────┴─────────┐
        Law enforcement dashboard   Citizen fraud shield
           + auto alert JSON          (6-language chat)
```

**Why fuse two independent detectors instead of shipping one model?**
The brief specifically asks for detecting "compound risk conditions that no single sensor would flag alone." Here, agreement between the ML model and the rule engine produces a high-confidence verdict; disagreement is visible in the audit trail rather than silently smoothed over. A `compound_risk` override also independently boosts the score when 3+ distinct rule categories fire together (e.g. authority impersonation + urgency + payment demand), which is exactly the multi-signal pattern real digital-arrest calls follow.

**Why run entirely offline, with no live external API in the decision path?**
A judged live demo can't depend on venue wifi or a third-party rate limit. The classifier is small, trains in seconds, and runs fully offline at inference time — a reliability choice, not a capability gap. See [`ROADMAP.md`](ROADMAP.md) for where an LLM layer would add value in a production system (explanation generation, never the core risk decision).

## Detection signals

The rule engine (`backend/signal_detector.py`) checks for 11 independent, explainable categories, each with its own severity weight and matched-phrase output (so a reviewer sees the actual words that triggered it, not a regex dump):

`authority_impersonation` · `identity_document` · `financial_crime` · `legal_threat` · `urgency` · `video_call` · `isolation_instruction` · `payment_demand` · `digital_arrest_explicit` · `suspicious_link` · `account_threat`

The first nine cover digital-arrest social engineering; `suspicious_link` and `account_threat` cover phishing (fake bank/e-commerce "your account will be suspended" messages), giving the same fusion verdict two distinct scam mechanisms to reason over.

## Honest performance numbers

We report two numbers, not one — testing only on the same generation templates used for training is misleading and we don't want to overclaim:

| Test set | Accuracy | Notes |
|---|---|---|
| Held-out split of training data | 100% | Same template family as training — expected to be high; not a generalization claim |
| **Independent adversarial set** (60 hand-written cases, never seen in training) | **98.3%** (59/60) | The number we stand behind. 30 scam / 30 legitimate, spanning digital-arrest scams and phishing, plus Hinglish phrasing. 1 false positive (a legitimate OTP warning), 0 false negatives |

Reproduce it yourself:
```bash
python3 -m backend.detection_engine
```

## Project structure

```
scam-shield/
├── app.py                        # Streamlit app — 3 tabs: LE dashboard, citizen shield, model performance
├── setup_and_run.sh               # One-command setup (idempotent, safe to re-run)
├── requirements.txt
├── data/
│   ├── generate_dataset.py        # Synthetic training data generator
│   ├── adversarial_eval_set.py    # 60 independent hand-written test cases
│   └── scam_dataset.csv           # Generated dataset (~1,050 labeled transcripts)
├── backend/
│   ├── signal_detector.py         # Rule-based explainable pattern detection (11 categories)
│   ├── i18n.py                    # Citizen-facing translations (6 languages)
│   ├── train_model.py             # TF-IDF + Logistic Regression training + evaluation
│   └── detection_engine.py        # Fusion logic, verdict, alert generation
├── models/                        # Trained model artifacts (generated by train_model.py)
│   ├── vectorizer.joblib
│   ├── classifier.joblib
│   └── metrics.json
└── tests/
    └── smoke_test.py               # 15-check pre-demo validation suite
```

## Getting started

```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

This installs dependencies, regenerates the training dataset, trains the model, runs the full smoke-test suite, and launches the app. Every step is idempotent — safe to re-run at any point, including right before a demo.

**Before every demo or judging session**, run the smoke tests on their own:
```bash
python3 -m tests.smoke_test
```
15 automated checks covering model-artifact presence, edge-case inputs (empty strings, very long text, mixed case), and score/verdict invariants. If anything fails, fix it before demoing — the failure output tells you exactly what broke.

### Manual setup (if you'd rather not use the script)

```bash
pip install -r requirements.txt
python3 data/generate_dataset.py     # build the synthetic training set
python3 backend/train_model.py       # train the classifier + write models/metrics.json
python3 -m tests.smoke_test          # verify everything works
streamlit run app.py
```

## Tech stack

- **UI:** Streamlit
- **ML:** scikit-learn (TF-IDF vectorizer + Logistic Regression), joblib for serialization
- **Visualization:** Plotly (signal-contribution charts, held-out vs. adversarial comparison, confusion-matrix breakdown)
- **Data:** pandas / numpy

Chosen deliberately for a hackathon timeline: everything trains in seconds, needs no GPU, and has zero live-network dependency at inference time — so nothing can fail on stage because of wifi.

## Scope — what's in, what's intentionally out

The brief's "Digital Arrest Scam Detection & Alerting" sub-track asks for a classifier "trained on digital arrest scam patterns." We built that, and added phishing detection (fake account-suspension links) since it directly extends the Citizen Fraud Shield's mandate to assess "suspicious calls, payment requests, or messages." Other scam families — lottery/prize fraud, fake job offers, romance scams, loan-app harassment — are **out of scope by design**, not missed; the brief explicitly calls its examples "illustrative only." Extending to those is natural Phase 2 work using the same fusion architecture (new signal category + training examples) — see [`ROADMAP.md`](ROADMAP.md).

## Known limitations (worth being upfront about)

- **Hinglish (code-mixed Hindi-English) is a weaker spot.** The ML model picks up scam vocabulary fine (English loanwords like "case," "arrest," "camera" still trigger it), but the rule engine's English-language regex often can't parse mixed-script text directly. Detection still works in practice — verified on the adversarial set — but with lower confidence and less explainability than pure English or Hindi input.
- **Synthetic training data.** No real NCRP/CERT-In complaint data was available in the build window. The fusion architecture and methodology are the contribution here; a production deployment needs real, anonymized complaint data at scale.
- **6 languages in this prototype** (English, Hindi, Tamil, Telugu, Bengali, Marathi); the brief calls for 12 regional languages — the `backend/i18n.py` structure is designed so adding a new language is a single dict entry, not scattered UI edits.
- **No live telecom/NCRP integration.** The alert JSON is structured to be API-ready but isn't wired to a real endpoint — no such sandbox was available for this build.

## Roadmap

See [`ROADMAP.md`](ROADMAP.md) for the phased plan: additional scam families, an LLM layer for citizen-facing explanation only (never the core risk decision), telecom/NCRP API integration, and full 12-language coverage.

---

*Prototype built for ET AI Hackathon 2026 — Problem Statement 6: AI for Digital Public Safety. Uses synthetic training data and is not connected to live telecom or NCRP systems.*