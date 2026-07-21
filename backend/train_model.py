"""
Train the ML scam classifier (TF-IDF + Logistic Regression).

Why this model choice for a 2-day hackathon prototype:
  - Trains in seconds, no GPU dependency, no internet call at inference time
    -> zero risk of live-demo failure from API/network issues.
  - Logistic Regression gives interpretable coefficients (we can show judges
    the top scam-indicative n-grams -- good for "technical excellence" and
    "auditability" evaluation criteria).
  - Calibrated probability output doubles as our confidence score.
"""

import pandas as pd
import joblib
import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE, "data", "scam_dataset.csv")
MODEL_DIR = os.path.join(BASE, "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def train():
    df = pd.read_csv(DATA_PATH)
    X_train, X_test, y_train, y_test = train_test_split(
        df["transcript"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=2,
        max_features=3000,
        sublinear_tf=True,
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    clf = LogisticRegression(max_iter=1000, C=1.0, class_weight="balanced")
    clf.fit(X_train_vec, y_train)

    y_pred = clf.predict(X_test_vec)
    y_proba = clf.predict_proba(X_test_vec)[:, 1]

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "f1_score": round(f1_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
        "test_set_size": len(y_test),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }

    # Top predictive features (for the "explainability" story in the deck)
    feature_names = vectorizer.get_feature_names_out()
    coefs = clf.coef_[0]
    top_scam_idx = coefs.argsort()[-15:][::-1]
    top_legit_idx = coefs.argsort()[:15]
    metrics["top_scam_indicators"] = [feature_names[i] for i in top_scam_idx]
    metrics["top_legit_indicators"] = [feature_names[i] for i in top_legit_idx]

    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "vectorizer.joblib"))
    joblib.dump(clf, os.path.join(MODEL_DIR, "classifier.joblib"))
    with open(os.path.join(MODEL_DIR, "metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    print("=== Model Evaluation ===")
    for k, v in metrics.items():
        if k not in ("confusion_matrix", "top_scam_indicators", "top_legit_indicators"):
            print(f"{k}: {v}")
    print(f"Confusion matrix [[TN,FP],[FN,TP]]: {metrics['confusion_matrix']}")
    print(f"\nTop scam indicator terms: {metrics['top_scam_indicators'][:8]}")
    print(f"Top legit indicator terms: {metrics['top_legit_indicators'][:8]}")
    print(f"\nModel saved to {MODEL_DIR}/")
    return metrics


if __name__ == "__main__":
    train()
