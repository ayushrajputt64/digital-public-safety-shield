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

FIXES APPLIED (see PR notes):
  - Added the missing "digital_arrest_explicit" category. It was referenced
    in compute_rule_score() and SIGNAL_EXPLANATIONS but never defined in
    SIGNAL_PATTERNS, so the score bonus and explanation could never fire.
  - matched_phrases now stores the ACTUAL matched text (e.g. "arrest warrant"),
    not the raw regex source. Showing a judge/officer a regex blob instead of
    the words the caller actually said undermines the "auditable" claim.
  - digital_arrest_explicit added to HIGH_PRIORITY so it counts toward the
    compound-risk trigger, since it is the strongest single indicator we have.
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

    # ---------------------------------------------------
    # DIGITAL ARREST SIGNALS
    # ---------------------------------------------------

    "authority_impersonation": {
        "weight": 0.30,
        "patterns": [
            r"\b(cbi|police|cyber crime|cyber cell|crime branch|ed|enforcement directorate|rbi|income tax|customs|supreme court|high court|narcotics|cid|crime investigation)\b",

            r"\b(officer|inspector|commissioner|superintendent|sub-?inspector)\b",

            # Hindi
            r"सीबीआई",
            r"पुलिस",
            r"साइबर क्राइम",
            r"ईडी",

            # Tamil
            r"சிபிஐ",
            r"காவல்துறை",
            r"சைபர்",

            # Telugu
            r"సీబీఐ",
            r"పోలీస్",

            # Bengali
            r"সিবিআই",
            r"পুলিশ"
        ]
    },

    "identity_document": {
        "weight": 0.20,
        "patterns": [
            r"\baadhaar\b",
            r"\baadhar\b",
            r"\bpan\b",
            r"\bpassport\b",
            r"\bsim\b",
            r"\bbank account\b",
            r"\bupi id\b"
        ]
    },

    "financial_crime": {
        "weight": 0.30,
        "patterns": [
            r"\bmoney laundering\b",
            r"\billegal transaction\b",
            r"\bdrug trafficking\b",
            r"\bterror funding\b",
            r"\bparcel scam\b",
            r"\bfake parcel\b",
            r"\bfinancial fraud\b"
        ]
    },

    "legal_threat": {
        "weight": 0.30,
        "patterns": [
            r"\barrest\b",
            r"\barrest warrant\b",
            r"\bwarrant\b",
            r"\bfir\b",
            r"\blegal action\b",
            r"\bsection\s+\d+\b",
            r"\bcourt order\b"
        ]
    },

    "urgency": {
        "weight": 0.20,
        "patterns": [
            r"\bimmediately\b",
            r"\bright now\b",
            r"\bwithin\s+\d+\s+(minutes|hours)\b",
            r"\burgent\b",
            r"\bact now\b"
        ]
    },

    "video_call": {
        "weight": 0.20,
        "patterns": [
            r"\bvideo call\b",
            r"\bstay on (this|the) call\b",
            r"\bkeep your camera on\b",
            r"\bturn on your camera\b",
            r"\bdo not disconnect\b",
            r"\bdo not leave the frame\b"
        ]
    },

    "isolation_instruction": {
        "weight": 0.25,
        "patterns": [
            r"\bdon't tell anyone\b",
            r"\bdo not tell anyone\b",
            r"\bkeep this confidential\b",
            r"\bdo not inform anyone\b",
            r"\bdo not contact police\b",
            r"\bdo not contact lawyer\b"
        ]
    },

    "payment_demand": {
        "weight": 0.35,
        "patterns": [
            r"\btransfer\b",
            r"\bsend money\b",
            r"\bsafe account\b",
            r"\bverification account\b",
            r"\bgovernment account\b",
            r"\bupi\b",
            r"\bshare otp\b",
            r"\bgift card\b",
            r"\bprocessing fee\b"
        ]
    },

    # Explicit mention of the scam mechanism itself. This is the strongest
    # single deterministic signal available — if the caller literally says
    # "digital arrest", treat it as near-conclusive regardless of ML score.
    "digital_arrest_explicit": {
        "weight": 0.35,
        "patterns": [
            r"\bdigital arrest\b",
            r"\bdigitally arrested\b",
            r"\bonline arrest\b",
            r"\bvirtual arrest\b",
            # Hindi
            r"डिजिटल अरेस्ट",
            # Tamil
            r"டிஜிட்டல் கைது",
            # Telugu
            r"డిజిటల్ అరెస్ట్",
            # Bengali
            r"ডিজিটাল অ্যারেস্ট"
        ]
    },

    # ---------------------------------------------------
    # PHISHING
    # ---------------------------------------------------

    "suspicious_link": {
        "weight": 0.25,
        "patterns": [
            r"https?://\S+",
            r"www\.\S+",
            r"\bbit\.ly\b",
            r"\bclick here\b",
            r"\bverify your account\b",
            r"\bupdate kyc\b"
        ]
    },

    "account_threat": {
        "weight": 0.25,
        "patterns": [
            r"\baccount suspended\b",
            r"\baccount blocked\b",
            r"\baccount locked\b",
            r"\bkyc expired\b",
            r"\bunusual login\b"
        ]
    }

}


def detect_signals(text: str) -> list:
    """
    Detects all matching scam signal categories.

    Returns:
        List[SignalMatch]
    """

    text_lower = text.lower()
    matches = []

    for category, cfg in SIGNAL_PATTERNS.items():

        matched_text = []

        for pattern in cfg["patterns"]:

            try:
                m = re.search(pattern, text_lower, re.IGNORECASE)
                if m:
                    # Store what was actually said, not the regex source,
                    # so the audit trail is human-readable.
                    matched_text.append(m.group(0))

            except re.error:
                # Ignore malformed regex instead of crashing
                continue

        if matched_text:

            matches.append(
                SignalMatch(
                    category=category,
                    weight=cfg["weight"],
                    matched_phrases=matched_text
                )
            )

    return matches


def compute_rule_score(text: str) -> tuple:
    """
    Computes an explainable rule-based risk score.

    Returns:
        (
            score: float [0,1],
            matches: List[SignalMatch],
            compound_risk: bool
        )

    NOTE:
    The return signature is unchanged, so this function remains
    backward compatible with detection_engine.py.
    """

    matches = detect_signals(text)

    if not matches:
        return 0.0, [], False

    raw_score = sum(match.weight for match in matches)

    categories = {m.category for m in matches}

    score = min(raw_score, 1.0)

    # -------------------------------------------------
    # Strong Digital Arrest combinations
    # -------------------------------------------------

    if (
        "authority_impersonation" in categories
        and "legal_threat" in categories
    ):
        score += 0.10

    if (
        "authority_impersonation" in categories
        and "video_call" in categories
    ):
        score += 0.10

    if (
        "authority_impersonation" in categories
        and "payment_demand" in categories
    ):
        score += 0.15

    if (
        "financial_crime" in categories
        and "identity_document" in categories
    ):
        score += 0.10

    if (
        "video_call" in categories
        and "isolation_instruction" in categories
    ):
        score += 0.10

    if (
        "legal_threat" in categories
        and "payment_demand" in categories
    ):
        score += 0.15

    # -------------------------------------------------
    # Digital Arrest explicit mention
    # -------------------------------------------------

    if "digital_arrest_explicit" in categories:
        score += 0.25

    # -------------------------------------------------
    # Compound Risk
    # -------------------------------------------------

    HIGH_PRIORITY = {
        "authority_impersonation",
        "legal_threat",
        "payment_demand",
        "video_call",
        "isolation_instruction",
        "financial_crime",
        "digital_arrest_explicit",
    }

    high_hits = len(categories & HIGH_PRIORITY)

    compound_risk = high_hits >= 3

    if compound_risk:
        score += 0.10

    score = min(score, 1.0)

    return score, matches, compound_risk

# ----------------------------------------------------------
# Human-readable explanations for the detected signals
# ----------------------------------------------------------

SIGNAL_EXPLANATIONS = {

    "authority_impersonation":
        "The caller is pretending to be a government official or law enforcement agency.",

    "identity_document":
        "The conversation references Aadhaar, PAN, passport, SIM or other identity documents.",

    "financial_crime":
        "The victim is falsely accused of financial crimes such as money laundering or illegal transactions.",

    "legal_threat":
        "The caller threatens arrest, legal action, FIR or court proceedings.",

    "urgency":
        "The victim is pressured to act immediately without verification.",

    "video_call":
        "The caller attempts to keep the victim continuously on a video call.",

    "isolation_instruction":
        "The victim is instructed not to tell anyone or seek outside help.",

    "payment_demand":
        "The caller demands money transfer, OTPs or payment to a so-called safe account.",

    "digital_arrest_explicit":
        "The caller explicitly mentions Digital Arrest.",

    "suspicious_link":
        "The message attempts to lure the victim into clicking suspicious links.",

    "account_threat":
        "The victim is threatened with account suspension or blocking."
}


def generate_explanations(matches):
    """
    Converts SignalMatch objects into
    human-readable explanations.
    """

    explanations = []

    seen = set()

    for match in matches:

        if match.category in SIGNAL_EXPLANATIONS:

            text = SIGNAL_EXPLANATIONS[match.category]

            if text not in seen:

                explanations.append(text)

                seen.add(text)

    return explanations

def detect_scam_type(matches):
    """
    Classifies the overall scam type
    from detected rule categories.
    """

    categories = {m.category for m in matches}

    # ----------------------------
    # Digital Arrest
    # ----------------------------

    if (
        "digital_arrest_explicit" in categories
        or
        (
            "authority_impersonation" in categories
            and
            (
                "legal_threat" in categories
                or
                "video_call" in categories
                or
                "isolation_instruction" in categories
            )
        )
    ):
        return "Digital Arrest Scam"

    # ----------------------------
    # Phishing
    # ----------------------------

    if (
        "suspicious_link" in categories
        or
        "account_threat" in categories
    ):
        return "Phishing Scam"

    # ----------------------------
    # OTP Fraud
    # ----------------------------

    if (
        "payment_demand" in categories
        and
        "identity_document" in categories
    ):
        return "OTP / Banking Fraud"

    # ----------------------------
    # Unknown
    # ----------------------------

    return "unknown scam"


if __name__ == "__main__":
    test_scam = ("This is Officer Sharma calling from the Cyber Crime Cell, Mumbai. "
                 "A warrant has been issued for your arrest under Section 420 unless "
                 "this is resolved today. Do not disconnect this video call, this is a "
                 "mandatory digital arrest protocol. Transfer Rs 50000 to this RBI "
                 "verification account immediately.")
    test_legit = ("Hi, this is HDFC Bank customer service regarding your card application. "
                   "Could you confirm your registered email address? Thanks for your time.")

    for label, text in [("SCAM", test_scam), ("LEGIT", test_legit)]:
        score, matches, compound = compute_rule_score(text)
        print(f"\n[{label}] rule_score={score:.2f} compound_risk={compound}")
        for m in matches:
            print(f"  - {m.category} (weight {m.weight}) matched: {m.matched_phrases}")