"""
Smoke Test Suite
==================
Run this before EVERY demo/judging session. If anything fails here,
it WILL fail on stage. Takes ~5 seconds.

Usage: python3 -m tests.smoke_test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.detection_engine import analyze_transcript, generate_alert
from backend.signal_detector import compute_rule_score, detect_signals
from data.adversarial_eval_set import ADVERSARIAL_CASES

PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

failures = []


def check(name, condition):
    status = PASS if condition else FAIL
    print(f"[{status}] {name}")
    if not condition:
        failures.append(name)


def run():
    print("=" * 60)
    print("SMOKE TEST SUITE — Digital Public Safety Shield")
    print("=" * 60)

    # --- Model files exist ---
    check(
        "Trained model files exist",
        os.path.exists("models/vectorizer.joblib") and os.path.exists("models/classifier.joblib"),
    )
    check("Metrics file exists", os.path.exists("models/metrics.json"))

    # --- Core pipeline doesn't crash on edge cases ---
    edge_cases = ["a", "1234", "!!!", "x" * 3000, "   spaces   ", "MixedCASE Text 123"]
    crashed = False
    for ec in edge_cases:
        try:
            analyze_transcript(ec)
        except Exception as e:
            crashed = True
            print(f"    CRASH on input {ec[:20]!r}: {e}")
    check("Edge case inputs do not crash", not crashed)

    # --- Verdict fields are always present and well-typed ---
    v = analyze_transcript("This is Officer Sharma from CBI, transfer money now, do not disconnect.")
    check("Verdict has valid verdict label", v.verdict in ("HIGH_RISK", "MEDIUM_RISK", "LOW_RISK"))
    check("Fused score in [0,1]", 0.0 <= v.fused_score <= 1.0)
    check("ML score in [0,1]", 0.0 <= v.ml_score <= 1.0)
    check("Rule score in [0,1]", 0.0 <= v.rule_score <= 1.0)

    # --- Clear scam case should be flagged ---
    obvious_scam = (
        "This is Officer Verma from CBI. A warrant has been issued for your arrest. "
        "Do not disconnect this video call. Transfer Rs 100000 to this account immediately "
        "or you will be arrested. This is a digital arrest protocol."
    )
    v_scam = analyze_transcript(obvious_scam)
    check("Obvious scam flagged as HIGH_RISK", v_scam.verdict == "HIGH_RISK")
    check("Obvious scam triggers compound_risk", v_scam.compound_risk is True)

    # --- Clear legit case should NOT be flagged ---
    obvious_legit = "Hi, just checking if we're still on for lunch tomorrow at 1pm?"
    v_legit = analyze_transcript(obvious_legit)
    check("Obvious legit case is LOW_RISK", v_legit.verdict == "LOW_RISK")

    # --- Alert generation works and is JSON-serializable ---
    import json
    try:
        alert = generate_alert(v_scam, "+91-9999999999")
        json.dumps(alert)  # must not throw
        alert_ok = True
    except Exception as e:
        print(f"    Alert generation error: {e}")
        alert_ok = False
    check("Alert package generates and is JSON-serializable", alert_ok)
    check("Alert contains audit_trail", "audit_trail" in alert if alert_ok else False)

    # --- Adversarial set accuracy stays above threshold (regression guard) ---
    correct = 0
    for case in ADVERSARIAL_CASES:
        v = analyze_transcript(case["text"])
        predicted = 1 if v.verdict in ("HIGH_RISK", "MEDIUM_RISK") else 0
        correct += predicted == case["label"]
    acc = correct / len(ADVERSARIAL_CASES)
    check(f"Adversarial accuracy >= 80% (actual: {acc:.1%})", acc >= 0.80)

    # --- Signal detector never throws on weird input ---
    weird_inputs = [None, "", "\n\n\n", "🎉🎊", "a" * 10000]
    signal_crash = False
    for wi in weird_inputs:
        try:
            if wi is not None:
                compute_rule_score(wi)
        except Exception as e:
            signal_crash = True
            print(f"    Signal detector crash on {wi!r}: {e}")
    check("Signal detector handles weird inputs", not signal_crash)

    print("=" * 60)
    if failures:
        print(f"❌ {len(failures)} TEST(S) FAILED: {failures}")
        print("DO NOT DEMO until these are fixed.")
        sys.exit(1)
    else:
        print("✅ ALL TESTS PASSED — safe to demo.")
    print("=" * 60)


if __name__ == "__main__":
    run()
