# Production Roadmap

What this prototype demonstrates vs. what a production deployment would add.

## Phase 1 (this prototype): Architecture proof
- Rule + ML fusion detection engine
- Explainable audit trail
- Bilingual citizen interface
- Structured alert generation

## Phase 2: Additional scam families & LLM augmentation
- Extend the fusion architecture to other scam mechanisms not required by this brief but
  common in India: lottery/prize fraud, fake job offers, loan-app harassment, romance scams —
  each via a new signal category + training examples, same pattern used for phishing
- Replace synthetic dataset with anonymized NCRP complaint corpus (with proper consent/privacy safeguards)
- Add an LLM layer purely for **natural-language explanation** of verdicts to citizens
  (never for the core risk decision — keeps the system auditable and offline-safe)
- Expand signal detector to voice-call metadata: number spoofing signatures, call
  duration patterns, AI-generated voice detection (per the brief's suggested tech)

## Phase 3: Network effects
- Telecom provider API integration for real-time call-level flagging before connection
- NCRP portal integration for one-click guided reporting
- Cross-reference victim reports into a fraud network graph (links to the brief's
  "Fraud Network Graph Intelligence" sub-track) to identify repeat-offender infrastructure

## Phase 4: Scale & language coverage
- All 12 regional languages via a translation + localization layer
- IVR channel for citizens without smartphones
- Federated deployment across state cyber cells with shared threat intelligence,
  respecting jurisdictional data-sharing rules

## What would change the accuracy story
Real complaint data would let us:
- Replace synthetic templates with genuine linguistic diversity
- Properly calibrate the rule engine's severity weights against real outcomes
- Build a proper train/validation/test split with temporal holdout (train on older
  complaints, test on newer ones) to measure true generalization over time
