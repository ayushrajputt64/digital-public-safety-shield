"""
Synthetic Dataset Generator - Digital Arrest Scam Detection
=============================================================
Generates labeled transcripts (scam vs legitimate) modeling the patterns
described in MHA/CERT-In advisories on 'digital arrest' scams:
- Authority impersonation (CBI/ED/Customs/Police/RBI)
- Urgency + fear induction
- Isolation instructions ("don't tell anyone", "stay on video call")
- Payment/verification demands (UPI, crypto, "safe custody" transfers)
- Fake legal jargon (FIR numbers, warrant references, Section citations)

This is synthetic data for prototype/demo purposes. In production this
would be augmented with (anonymized, consented) real complaint data from
NCRP / telecom SIP metadata, per the problem statement's suggested sources.
"""

import pandas as pd
import random
import json

random.seed(42)

# ---------------------------------------------------------------------------
# SCAM COMPONENT LIBRARY
# Built from *pattern descriptions*, not copied text — phrases are original
# recombinations reflecting publicly reported scam mechanics.
# ---------------------------------------------------------------------------

AUTHORITY_CLAIMS = [
    "This is Officer {name} calling from the Cyber Crime Cell, Mumbai.",
    "I am Inspector {name} from CBI Headquarters, Delhi.",
    "You are being contacted by the Enforcement Directorate regarding your bank account.",
    "This call is from Customs Department, Mumbai Airport division.",
    "I'm calling on behalf of TRAI regarding your mobile number linked to illegal activity.",
    "This is a call from RBI's Fraud Monitoring Cell.",
    "You have been named in an FIR filed at {city} Police Station.",
    "I am a Sub-Inspector with the Narcotics Control Bureau.",
]

URGENCY_FEAR = [
    "A warrant has been issued for your arrest under Section {sec} unless this is resolved today.",
    "Your Aadhaar number has been used in a money laundering case involving Rs {amount} lakh.",
    "If you disconnect this call, a team will be sent to your residence within the hour.",
    "This is a non-bailable offence. You must cooperate immediately or face digital arrest.",
    "Your bank account will be frozen in the next 30 minutes if you do not comply.",
    "A parcel booked in your name containing illegal substances was intercepted at customs.",
    "Your PAN and Aadhaar are linked to a fraud case worth crores. This is extremely serious.",
]

ISOLATION_INSTRUCTIONS = [
    "Do not disconnect this video call under any circumstances, this is now an official proceeding.",
    "You are not permitted to inform any family member about this investigation, it is confidential.",
    "Stay on this call and do not contact any lawyer until verification is complete.",
    "Turn on your camera now and do not leave the frame, this is a mandatory digital arrest protocol.",
    "Do not go to the police station yourself, we will guide you through the process here.",
]

PAYMENT_DEMANDS = [
    "To verify your identity and clear your name, transfer Rs {amount} to this RBI verification account.",
    "You must deposit funds into a government safe custody account for 24 hours, it will be refunded.",
    "Share the OTP sent to your phone so we can verify your account is not compromised.",
    "Send Rs {amount} via UPI to this ID immediately to avoid asset seizure.",
    "Purchase gift cards worth Rs {amount} and share the codes for verification purposes.",
    "Transfer funds to this account for RBI clearance, failure to comply will result in arrest.",
]

# --- Phishing template components (distinct scam mechanism: link-bait + account
# suspension threats, rather than voice-based authority impersonation) ---
PHISHING_BRANDS = ["SBI", "HDFC Bank", "ICICI Bank", "Amazon", "Paytm", "Axis Bank", "PhonePe", "Flipkart"]
PHISHING_OPENERS = [
    "Dear customer, your {brand} account will be suspended in 24 hours due to KYC non-compliance.",
    "Your {brand} account has been locked due to suspicious activity.",
    "ALERT: Unusual sign-in activity detected on your {brand} account.",
    "Your {brand} account will be permanently deactivated unless you verify immediately.",
    "Final notice: your {brand} KYC has expired, account access will be restricted today.",
]
PHISHING_LINKS = [
    "Click here to verify: http://{brand_slug}-kyc-verify.com/update",
    "Verify your identity now at {brand_slug}-secure-login.net to avoid suspension.",
    "Confirm your details within 24 hours: bit.ly/{brand_slug}-verify",
    "Update your KYC immediately at {brand_slug}-online-update.in/kyc",
]

def generate_phishing_transcript():
    brand = random.choice(PHISHING_BRANDS)
    slug = brand.lower().replace(" ", "")
    opener = random.choice(PHISHING_OPENERS).format(brand=brand)
    link = random.choice(PHISHING_LINKS).format(brand_slug=slug)
    return f"{opener} {link}"

LEGAL_JARGON_FILLER = [
    "FIR number {fir} has been registered against you.",
    "This falls under Section {sec} of the IT Act and PMLA.",
    "Your case reference number is {ref}, please note it down.",
    "This is being recorded as evidence for the Supreme Court proceeding.",
]

NAMES = ["Sharma", "Verma", "Iyer", "Reddy", "Khan", "Singh", "Patel", "Gupta", "Nair", "Mehta"]
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Chennai", "Pune", "Hyderabad", "Kolkata"]

def rand_fill(template):
    return template.format(
        name=random.choice(NAMES),
        city=random.choice(CITIES),
        sec=random.choice(["420", "467", "120B", "66D", "384"]),
        amount=random.choice([2, 5, 10, 15, 25, 50, 75]),
        fir=f"{random.randint(100,999)}/2026",
        ref=f"REF{random.randint(100000,999999)}",
    )

def generate_scam_transcript():
    """Compose a scam transcript from 3-5 pattern components in randomized order,
    mimicking the multi-stage structure reported in digital arrest scam cases."""
    parts = []
    parts.append(rand_fill(random.choice(AUTHORITY_CLAIMS)))
    parts.append(rand_fill(random.choice(URGENCY_FEAR)))
    if random.random() > 0.3:
        parts.append(rand_fill(random.choice(LEGAL_JARGON_FILLER)))
    if random.random() > 0.2:
        parts.append(rand_fill(random.choice(ISOLATION_INSTRUCTIONS)))
    parts.append(rand_fill(random.choice(PAYMENT_DEMANDS)))
    random.shuffle(parts)  # stage order varies across real reported cases
    # keep authority claim as opener most of the time (realistic call structure)
    if random.random() > 0.15:
        opener = rand_fill(random.choice(AUTHORITY_CLAIMS))
        parts = [opener] + [p for p in parts if p != opener]
    return " ".join(parts)


# ---------------------------------------------------------------------------
# LEGITIMATE TRANSCRIPT LIBRARY (negative class)
# Mix of genuine bank/govt/telecom calls and everyday conversations
# ---------------------------------------------------------------------------

LEGIT_TEMPLATES = [
    "Hi, this is {name} calling from HDFC Bank customer service regarding your recent card application. Could you confirm your registered email address?",
    "Good afternoon, this is a reminder call from Apollo Hospitals about your appointment scheduled for tomorrow at 10 AM.",
    "This is Airtel customer care. We noticed your data pack expires today, would you like to renew it?",
    "Hey, are we still meeting for lunch tomorrow? Let me know what time works.",
    "This is regarding your electricity bill for this month, it is now available on the portal, no action needed unless you have queries.",
    "This is {name} from the school regarding the parent-teacher meeting scheduled next week.",
    "Congratulations, your loan application has been approved, our relationship manager will call you to explain the next steps at your convenience.",
    "Hi, just checking in about the delivery of your order, it should arrive by Thursday.",
    "This is a courtesy call from your insurance provider to remind you about your policy renewal, no urgent action is required.",
    "Can you send me the report by end of day? No rush if you're busy, tomorrow morning also works.",
    "This is the income tax department's official portal notification: your refund has been processed, please check the portal at your convenience.",
    "Hi, this is {name}, I wanted to follow up on the property documents whenever you get a chance.",
    "This is a survey call about your recent visit to our store, would you have two minutes to share feedback?",
    "Reminder: your gym membership renews next week. No action needed if you'd like to continue.",
    "This is your bank calling to confirm a transaction of Rs 1200 you made yesterday at a grocery store, please call the branch back if you did not recognize it.",
]

LEGIT_OPENERS = ["Hi,", "Hello,", "Good morning,", "Good afternoon,", "Hey,", ""]
LEGIT_CLOSERS = [
    "Let me know if you have any questions.",
    "No urgent action is needed.",
    "Thanks for your time.",
    "Feel free to call back if anything is unclear.",
    "Have a good day.",
    "",
]

def generate_legit_transcript():
    t = rand_fill(random.choice(LEGIT_TEMPLATES))
    opener = random.choice(LEGIT_OPENERS)
    closer = random.choice(LEGIT_CLOSERS)
    parts = [p for p in [opener, t, closer] if p]
    # occasionally combine two legit sentences for length variety
    if random.random() > 0.5:
        parts.insert(-1 if closer else len(parts), rand_fill(random.choice(LEGIT_TEMPLATES)))
    return " ".join(parts)


def build_dataset(n_scam=400, n_legit=400, n_phishing=150):
    rows = []
    seen = set()
    attempts = 0
    while len([r for r in rows if r["label"] == 1]) < n_scam and attempts < n_scam * 20:
        t = generate_scam_transcript()
        attempts += 1
        if t not in seen:
            seen.add(t)
            rows.append({"transcript": t, "label": 1})
    attempts = 0
    phishing_count = 0
    while phishing_count < n_phishing and attempts < n_phishing * 20:
        t = generate_phishing_transcript()
        attempts += 1
        if t not in seen:
            seen.add(t)
            rows.append({"transcript": t, "label": 1})
            phishing_count += 1
    attempts = 0
    while len([r for r in rows if r["label"] == 0]) < n_legit and attempts < n_legit * 20:
        t = generate_legit_transcript()
        attempts += 1
        if t not in seen:
            seen.add(t)
            rows.append({"transcript": t, "label": 0})
    df = pd.DataFrame(rows).reset_index(drop=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle
    return df


if __name__ == "__main__":
    import os
    df = build_dataset(n_scam=450, n_legit=450, n_phishing=150)
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scam_dataset.csv")
    df.to_csv(out_path, index=False)
    print(f"Generated {len(df)} labeled transcripts")
    print(df['label'].value_counts())
    print("\nSample scam transcript:\n", df[df.label==1].iloc[0]['transcript'])
    print("\nSample legit transcript:\n", df[df.label==0].iloc[0]['transcript'])
