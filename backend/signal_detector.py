"""
Rule-Based Signal Detector
============================
Detects specific scam SIGNAL CATEGORIES independent of the ML classifier.
This gives us:
  1. An explainable, auditable layer (judges will ask "why did it flag this?")
  2. A second, independent detection path to fuse with the ML model
     (mirrors the "compound risk" / multi-signal-fusion pattern used across
     the hackathon problem statements — no single signal should carry the
     whole decision).
  3. A safety net if the ML model is ever uncertain — rules catch known
     hard patterns (e.g. explicit mention of "digital arrest") deterministically.
"""

import re
from dataclasses import dataclass, field


@dataclass
class SignalMatch:
    category: str
    weight: float
    matched_phrases: list = field(default_factory=list)


# Each category maps to regex patterns + a severity weight.
# Weights are illustrative and would be calibrated against real complaint
# data (NCRP/CERT-In) in a production deployment.
SIGNAL_PATTERNS = {
    "authority_impersonation": {
        "weight": 0.25,
        "patterns": [
            r"\b(cbi|ed\b|enforcement directorate|customs department|narcotics control|trai|rbi|cyber crime cell|income tax department|supreme court)\b",
            r"\b(officer|inspector|sub-?inspector)\s+\w+\s+(calling|from)",
        ],
    },
    "urgency_fear_induction": {
        "weight": 0.20,
        "patterns": [
            r"\b(warrant.{0,20}arrest|non-?bailable|arrest.{0,20}unless|frozen.{0,20}(minutes|hours))\b",
            r"\bwithin (the )?(next )?\d+ (minutes|hours)\b",
            r"\b(fir|f\.i\.r\.).{0,30}(filed|registered|against you)\b",
        ],
    },
    "isolation_instruction": {
        "weight": 0.20,
        "patterns": [
            r"\bdo not (disconnect|hang up|tell|inform|contact|leave|end)\b",
            r"\bstay on (this|the) (video )?call\b",
            r"\bkeep (the |your )?camera on\b",
            r"\bcannot let you disconnect\b",
            r"\bdo not (go to|contact) (the )?(police|lawyer)\b",
            r"\bconfidential.{0,20}(investigation|proceeding)\b",
        ],
    },
    "payment_demand": {
        "weight": 0.25,
        "patterns": [
            r"\btransfer.{0,30}(rs\.?|rupees|inr)\s?\d+",
            r"\bsafe custody account\b",
            r"\bshare the otp\b",
            r"\bgift cards?\b.{0,20}(purchase|share|codes)",
            r"\bupi\b.{0,20}(id|transfer|send)",
            r"\b(processing charge|settlement amount|verification fee|clearance fee|compounding fee|verification account)\b",
        ],
    },
    "digital_arrest_explicit": {
        "weight": 0.30,
        "patterns": [
            r"\bdigital arrest\b",
            r"\bmandatory (digital )?arrest protocol\b",
        ],
    },
    "video_call_coercion": {
        "weight": 0.15,
        "patterns": [
            r"\bturn on your camera\b",
            r"\bdo not leave the frame\b",
        ],
    },
    # --- Phishing-specific categories (distinct mechanism from digital arrest scams:
    # link-bait + credential harvesting rather than voice-based social engineering) ---
    "suspicious_link_bait": {
        "weight": 0.25,
        "patterns": [
            r"\bclick (here|below|this link|to verify|to confirm)\b",
            r"\b(verify|confirm|update)\s+(your\s+)?(identity|account|details|kyc)\b.{0,40}\b(link|url|below|here)?",
            r"https?://\S+|www\.\S+|\S+\.(com|net|in|xyz|info)/\S*",
            r"\bbit\.ly\b",
        ],
    },
    "account_threat_language": {
        "weight": 0.25,
        "patterns": [
            r"\baccount (will be|has been|is)\s*(temporarily\s+|permanently\s+|immediately\s+)?(suspended|locked|blocked|deactivated|terminated|restricted)\b",
            r"\bunusual (sign-?in|login) activity\b",
            r"\bpermanently (suspended|deactivated|blocked)\b",
            r"\bkyc\s*(non-?compliance|verification|update)\b.{0,40}(suspend|block|deactivat)",
        ],
    },
}


def detect_signals(text: str) -> list:
    """Return list of SignalMatch objects for every category with a hit."""
    text_lower = text.lower()
    matches = []
    for category, cfg in SIGNAL_PATTERNS.items():
        hits = []
        for pattern in cfg["patterns"]:
            found = re.findall(pattern, text_lower)
            if found:
                hits.append(pattern)
        if hits:
            matches.append(SignalMatch(category=category, weight=cfg["weight"], matched_phrases=hits))
    return matches


def compute_rule_score(text: str) -> tuple:
    """
    Returns (score in [0,1], list of SignalMatch, compound_risk_flag)

    compound_risk_flag mirrors the hackathon's "compound risk detection"
    concept: the co-occurrence of MULTIPLE independent signal categories is
    far more predictive than any single one — a call that only mentions
    'RBI' isn't necessarily a scam, but 'RBI' + 'do not disconnect' +
    'transfer funds' together is a near-certain digital arrest pattern.
    """
    matches = detect_signals(text)
    raw_score = sum(m.weight for m in matches)
    score = min(raw_score, 1.0)
    compound_risk = len(matches) >= 3  # 3+ independent categories co-occurring
    return score, matches, compound_risk


if __name__ == "__main__":
    test_scam = ("This is Officer Sharma calling from the Cyber Crime Cell, Mumbai. "
                 "A warrant has been issued for your arrest under Section 420 unless "
                 "this is resolved today. Do not disconnect this video call. "
                 "Transfer Rs 50000 to this RBI verification account immediately.")
    test_legit = ("Hi, this is HDFC Bank customer service regarding your card application. "
                   "Could you confirm your registered email address? Thanks for your time.")

    for label, text in [("SCAM", test_scam), ("LEGIT", test_legit)]:
        score, matches, compound = compute_rule_score(text)
        print(f"\n[{label}] rule_score={score:.2f} compound_risk={compound}")
        for m in matches:
            print(f"  - {m.category} (weight {m.weight})")
