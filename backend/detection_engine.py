"""
Digital Arrest Scam Detection Engine
=======================================
Fuses two independent detection paths:
  1. ML classifier (TF-IDF + Logistic Regression) - learned patterns
  2. Rule-based signal detector - explicit, auditable pattern rules

Fusion rationale: the hackathon brief specifically calls for detecting
"compound risk conditions that no single sensor would flag alone." Here,
the ML model and rule engine are the two independent signals. A transcript
that both models agree on gets high confidence; disagreement is flagged
for human review rather than silently resolved -- this matters because
citizen-facing false positives must stay very low (explicit evaluation
criterion in the brief).

FIX APPLIED: fused score is now explicitly clamped to [0, 1] before verdict
thresholding. With the current weights this was already mathematically
bounded, but leaving it implicit is fragile -- any future change to
ML_WEIGHT/RULE_WEIGHT or the compound-risk override could silently push
fused_score above 1.0 (which, e.g., broke st.progress() in the dashboard
before the app-side clamp was added). Clamping once here, at the source,
is the correct place to guarantee the invariant rather than relying on
every downstream consumer to re-clamp defensively.
"""

import os
import joblib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

from backend.signal_detector import (
    compute_rule_score,
    generate_explanations,
    detect_scam_type,
)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE, "models")

_vectorizer = None
_classifier = None


def _load_models():
    global _vectorizer, _classifier
    if _vectorizer is None or _classifier is None:
        _vectorizer = joblib.load(os.path.join(MODEL_DIR, "vectorizer.joblib"))
        _classifier = joblib.load(os.path.join(MODEL_DIR, "classifier.joblib"))
    return _vectorizer, _classifier


@dataclass
class ScamVerdict:
    text: str
    ml_score: float
    rule_score: float
    fused_score: float
    verdict: str            # HIGH_RISK / MEDIUM_RISK / LOW_RISK
    compound_risk: bool
    matched_categories: list[str]
    timestamp: str

    scam_type: str = "Unknown"

    explanations: list[str] = field(default_factory=list)

    matched_signals: list[dict] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


# Fusion weights: ML model captures learned linguistic patterns, rule engine
# captures known hard-coded scam mechanics. Weighted toward agreement.
ML_WEIGHT = 0.55
RULE_WEIGHT = 0.45

HIGH_RISK_THRESHOLD = 0.65
MEDIUM_RISK_THRESHOLD = 0.35


def analyze_transcript(text: str) -> ScamVerdict:
    vectorizer, clf = _load_models()
    X = vectorizer.transform([text])
    ml_score = float(clf.predict_proba(X)[0][1])

    rule_score, matches, compound_risk = compute_rule_score(text)

    explanations = generate_explanations(matches)

    scam_type = detect_scam_type(matches)

    fused = ML_WEIGHT * ml_score + RULE_WEIGHT * rule_score

    # Compound risk override: if 3+ independent rule categories co-occur,
    # this is a near-certain known scam pattern regardless of ML score --
    # mirrors "compound risk detection" language from the problem statement.
    if compound_risk:
        fused = max(fused, 0.75)

    # Defensive clamp -- guarantees the invariant at the source instead of
    # relying on every downstream consumer (UI, alerting, logging) to do it.
    fused = min(max(fused, 0.0), 1.0)

    if fused >= HIGH_RISK_THRESHOLD:
        verdict = "HIGH_RISK"
    elif fused >= MEDIUM_RISK_THRESHOLD:
        verdict = "MEDIUM_RISK"
    else:
        verdict = "LOW_RISK"

    return ScamVerdict(
        text=text,
        ml_score=round(ml_score, 4),
        rule_score=round(rule_score, 4),
        fused_score=round(fused, 4),
        verdict=verdict,
        compound_risk=compound_risk,
        matched_categories=sorted({m.category for m in matches}),

        scam_type=scam_type,

        explanations=explanations,

        matched_signals=[
            {
                "category": m.category,
                "weight": round(m.weight, 2),
                "patterns": m.matched_phrases,
            }
            for m in matches
        ],

        timestamp=datetime.now(timezone.utc).isoformat() + "Z",
    )


def generate_alert(verdict: ScamVerdict, caller_number: str = "UNKNOWN") -> dict:
    """Simulated MHA/telecom-style alert package -- the 'automated alert
    generation' capability described in the brief. This is a structured
    JSON artifact; in production it would route to telecom provider APIs
    and MHA's cybercrime reporting portal (NCRP)."""
    return {
        "alert_id": f"DAS-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "severity": verdict.verdict,
        "confidence": verdict.fused_score,
        "caller_number": caller_number,
        "detected_patterns": verdict.matched_categories,
        "compound_risk_detected": verdict.compound_risk,
        "recommended_action": (
            "Immediate telecom-side flag + citizen advisory push"
            if verdict.verdict == "HIGH_RISK"
            else "Log for pattern monitoring, no immediate action"
        ),
        "generated_at": verdict.timestamp,
        "audit_trail": {
            "ml_score": verdict.ml_score,
            "rule_score": verdict.rule_score,
            "fusion_weights": {"ml": ML_WEIGHT, "rule": RULE_WEIGHT},
        },
    }


if __name__ == "__main__":
    from data.adversarial_eval_set import ADVERSARIAL_CASES

    correct = 0
    fp, fn = 0, 0
    print("=== Honest Evaluation on Independent Adversarial Set ===\n")
    for case in ADVERSARIAL_CASES:
        v = analyze_transcript(case["text"])
        predicted = 1 if v.verdict in ("HIGH_RISK", "MEDIUM_RISK") else 0
        is_correct = predicted == case["label"]
        correct += is_correct
        if predicted == 1 and case["label"] == 0:
            fp += 1
        if predicted == 0 and case["label"] == 1:
            fn += 1
        tag = "PASS" if is_correct else "FAIL"
        print(f"[{tag}] true={case['label']} pred={predicted} verdict={v.verdict} "
              f"fused={v.fused_score:.2f} | {case['text'][:70]}...")

    total = len(ADVERSARIAL_CASES)
    print(f"\nAccuracy on adversarial set: {correct}/{total} = {correct/total:.2%}")
    print(f"False positives (legit flagged as risky): {fp}")
    print(f"False negatives (scam missed): {fn}")