"""
Independent Adversarial Evaluation Set
=========================================
Hand-written, NOT generated from the same templates as the training data.
Purpose: give an honest generalization estimate instead of the misleadingly
perfect 100% we get testing on template-derived data.

Includes deliberately HARD cases:
  - Scam calls phrased differently from training templates (paraphrase test)
  - Legit calls that use urgency/money language (false-positive stress test —
    directly relevant to the problem statement's requirement that citizen-facing
    tools must have a very low false positive rate)
"""

ADVERSARIAL_CASES = [
    # --- Scam cases, phrased naturally / differently from training templates ---
    {"text": "Sir this is a very serious matter, your Aadhaar linked courier has drugs, "
             "you need to stay connected on this video call and not tell your family, "
             "we need Rs 40000 sent right now or local police will come to your house.",
     "label": 1},
    {"text": "Ma'am please don't panic but there is a legal case against you, keep the camera on, "
             "we cannot let you disconnect, send the money to the account I am sharing to clear this today itself.",
     "label": 1},
    {"text": "This is from the cyber wing, your number is under surveillance for a financial crime, "
             "you are required to remain on this call and not contact anyone including your lawyer "
             "until the amount is settled.",
     "label": 1},
    {"text": "Namaste, I am calling from the anti money laundering unit. Your bank locker has been "
             "used illegally. Please do not hang up, this is an active proceeding, share your OTP to verify.",
     "label": 1},
    {"text": "You are in big trouble beta, a case is filed, keep your camera on and do exactly as I say, "
             "transfer half the amount now to avoid your arrest today.",
     "label": 1},
    {"text": "This is the special task force, your parcel with illegal items was caught, we are recording "
             "this call as evidence, you must stay online and pay the customs penalty right now to close the case.",
     "label": 1},

    # --- Additional scam cases: broader sub-types and phrasing styles ---
    {"text": "Good evening, FedEx international division here. A package under your name was seized at "
             "Chennai customs containing banned substances and five passports. To avoid a police visit, "
             "connect with our compliance officer on video right away and do not switch off your phone.",
     "label": 1},
    {"text": "This is regarding your income tax refund of Rs 84000, but our system shows a discrepancy "
             "linked to a fraud case. An officer will now verify you over video, please do not end the "
             "call and keep your bank details ready to transfer a processing charge.",
     "label": 1},
    {"text": "TRAI here, your mobile number will be blocked in two hours for illegal activity unless you "
             "press 9 to connect with an officer. Do not disconnect. You will then need to pay a "
             "verification amount to keep your number active.",
     "label": 1},
    {"text": "This is the Narcotics Control Bureau Mumbai unit, your name came up in a drug trafficking "
             "case linked to a courier. We are giving you one chance, stay on this video call, do not "
             "tell your wife anything, and arrange one lakh rupees within the hour.",
     "label": 1},
    {"text": "Sir I am from the Supreme Court legal cell, a non-bailable warrant has been generated "
             "against you today itself. If you disconnect this call it will be treated as absconding. "
             "Please remain online and follow the payment instructions I give you.",
     "label": 1},
    {"text": "Aapke against ek case register hua hai money laundering ka, agar aap ye call cut kiya to "
             "seedha arrest team bhej denge, camera on rakhiye aur turant paisa transfer kijiye humे.",
     "label": 1},
    {"text": "This is your last warning from the cybercrime portal, a complaint has been filed against your "
             "Aadhaar for financial fraud. Stay on this call, don't inform anyone, and pay the settlement "
             "amount to close this before it escalates to arrest.",
     "label": 1},
    {"text": "We are calling from the RBI compliance division. Multiple suspicious transactions were found "
             "linked to your PAN. This is a confidential investigation, you must not disconnect or tell "
             "any bank staff, and you need to move your funds to a secure verification account immediately.",
     "label": 1},
    {"text": "Hello, this is Inspector Malhotra. There's an FIR against you for cheque bounce and fraud. "
             "I'm giving you a chance to settle before we send a team to arrest you. Stay on video, "
             "don't call any lawyer, and pay the compounding fee right now through UPI.",
     "label": 1},
    {"text": "Madam your electricity meter is linked to an illegal power theft case under investigation "
             "by the vigilance department. Do not disconnect this video call, an officer needs to verify "
             "your identity and you must clear the penalty amount within 20 minutes to avoid arrest.",
     "label": 1},
    {"text": "This is a recorded legal notice, your bank account is under scrutiny for terror funding "
             "links. Stay connected on this call, do not alert your family, transfer the flagged amount "
             "to our verification wallet so we can clear your name today.",
     "label": 1},
    {"text": "Sir customs ne aapka parcel hold kiya hai jisme illegal cash mila hai, is call ko disconnect "
             "mat kijiye, hum aapko video pe rakhenge jab tak aap verification fee pay nahi karte.",
     "label": 1},
    {"text": "This is the passport verification cell, your document has flagged in a fraud database linked "
             "to a criminal case abroad. You must remain on this video call, share your OTP for identity "
             "confirmation, and pay a clearance fee to avoid your passport being revoked and arrest.",
     "label": 1},
    {"text": "I'm calling from the state cyber police headquarters. Your SIM card was used to send threat "
             "messages, this is a serious criminal case, keep the camera on, do not hang up, and settle "
             "the bail amount now through the link I'm sending or a team will pick you up tonight.",
     "label": 1},
    {"text": "Respected sir, this is an automated alert from the enforcement wing followed by an officer. "
             "Your GST number shows fraudulent input credit worth lakhs. Remain on this video call, "
             "do not consult your CA, and clear the settlement amount to avoid immediate arrest.",
     "label": 1},
    {"text": "This is your final chance before we escalate. Your account is linked to a cybercrime case, "
             "keep this video call active, don't tell your children, and send the requested gift card "
             "codes to prevent your bank locker from being seized today.",
     "label": 1},
    {"text": "Mein CBI se bol raha hoon, aapke naam pe ek serious case hai fraud ka, agar aap call disconnect "
             "kiya to hum turant warrant execute karenge, camera on rakho aur jo bola hai wo paisa bhejo.",
     "label": 1},
    {"text": "This is airport immigration control, your travel documents are flagged for a financial crime "
             "investigation. You are required to stay on this video verification call, must not inform "
             "anyone, and need to pay a clearance deposit before your case is escalated to arrest.",
     "label": 1},
    {"text": "Ma'am we are from the women's cyber safety cell, your identity was used in an obscene content "
             "case, this is extremely sensitive so do not tell your family, remain on video, and pay the "
             "case closure fee immediately to avoid public arrest and media exposure.",
     "label": 1},

    # --- Phishing scam cases (link-bait / account-suspension mechanism, distinct from digital arrest) ---
    {"text": "Dear valued customer, we detected irregular activity on your Kotak Mahindra account. "
             "Your account access will be restricted within 12 hours unless you re-verify your details "
             "through the secure link: kotak-reverify-portal.com/login",
     "label": 1},
    {"text": "Your PhonePe wallet has been flagged for review due to a policy violation. Failure to "
             "confirm your identity at phonepe-kyc-support.in within 24 hours will result in permanent "
             "account closure and forfeiture of your balance.",
     "label": 1},
    {"text": "URGENT: Your electricity bill payment failed and your connection will be disconnected "
             "tonight. Pay immediately through this link to avoid disconnection: eb-payment-quick.net/pay",
     "label": 1},
    {"text": "Congratulations! You've won a cashback reward of Rs 5000 from your bank. Claim it within "
             "2 hours before it expires by entering your card details and OTP at rewards-claim-now.com",
     "label": 1},
    {"text": "Your income tax refund of Rs 15,480 is pending release. To receive it, please verify your "
             "bank account and PAN details at the secure government portal: incometax-refund-status.in",
     "label": 1},

    # --- Hard legit cases: urgency/money language but NOT a scam ---
    {"text": "Hi, this is your bank, we noticed unusual activity on your card and have temporarily "
             "blocked it for your safety, please call the number on the back of your card to verify recent transactions.",
     "label": 0},
    {"text": "This is urgent, your flight tomorrow morning has been rescheduled by two hours, "
             "please check your email for the updated ticket.",
     "label": 0},
    {"text": "Reminder: your credit card payment of Rs 15000 is due tomorrow, please pay to avoid late fees.",
     "label": 0},
    {"text": "This is the hospital, we need you to confirm the advance payment for your father's surgery "
             "scheduled tomorrow morning, please visit the billing counter.",
     "label": 0},
    {"text": "Your OTP for logging into your net banking is 482913, do not share this with anyone. "
             "This message is auto generated.",
     "label": 0},
    {"text": "Sir this is the electricity board, your connection may be disconnected tomorrow due to pending "
             "dues of Rs 3400, please pay at your earliest to avoid disruption.",
     "label": 0},
    {"text": "This is a collections call regarding your overdue loan EMI, we request you to clear the "
             "pending amount within 7 days to avoid it being reported to the credit bureau.",
     "label": 0},
    {"text": "Congratulations, you've been selected for a scholarship interview, please confirm your "
             "availability for a video call this Friday at 3 PM.",
     "label": 0},
    {"text": "This is your building's security, there was a minor fire alarm test today, no action needed, "
             "just informing all residents.",
     "label": 0},
    {"text": "Hi team, quick reminder the client call has been moved up, please join 15 minutes early today.",
     "label": 0},

    # --- Additional legit edge cases: legal-sounding, police-adjacent, or high false-positive-risk ---
    {"text": "This is the local police station, we recovered a mobile phone matching your complaint from "
             "last month, please visit the station with your ID and complaint copy to collect it whenever convenient.",
     "label": 0},
    {"text": "This is a courtesy call from the housing society office. Please note that as per the society "
             "bylaws, maintenance dues pending beyond 60 days may attract a legal notice, kindly clear "
             "your dues at your convenience to avoid this.",
     "label": 0},
    {"text": "Hello, this is regarding your PM Kisan scheme installment, the amount has been credited to "
             "your linked bank account, please check your passbook whenever you visit the branch next.",
     "label": 0},
    {"text": "This is your telecom provider, your KYC re-verification is due this month as per new "
             "regulations, please visit any store with your Aadhaar at your convenience, no urgent action needed.",
     "label": 0},
    {"text": "This is a fraud alert from your bank. We noticed a transaction of Rs 45000 that looks unusual, "
             "if this was not done by you please call our official helpline number immediately to block your card.",
     "label": 0},
    {"text": "Hi, this is the landlord, just a reminder that rent is due on the 5th as usual, no rush, "
             "transfer whenever it's convenient this week.",
     "label": 0},
    {"text": "This is your child's school, the annual day event has been rescheduled to next Saturday, "
             "kindly note the new date, no action required from your side.",
     "label": 0},
    {"text": "This is an automated weather alert: heavy rainfall is expected in your area over the next "
             "48 hours, please take necessary precautions, this is a public advisory.",
     "label": 0},
    {"text": "This is your vaccination center, your booked slot for tomorrow at 10 AM is confirmed, "
             "please carry your ID card and previous vaccination certificate.",
     "label": 0},
    {"text": "This is the registrar's office, your property registration documents are ready for collection, "
             "please visit anytime during working hours with your receipt.",
     "label": 0},
    {"text": "Hi this is your relationship manager, following up on the query you raised yesterday about "
             "your fixed deposit renewal, please call back at your convenience to discuss options.",
     "label": 0},
    {"text": "This is a reminder from the charity foundation you donated to last year, our annual fundraiser "
             "is next month, no obligation, just wanted to keep you informed in case you'd like to contribute again.",
     "label": 0},
    {"text": "This is your credit card company, we're calling to inform you your card will expire this month, "
             "the new card has already been dispatched to your registered address, no action needed.",
     "label": 0},
    {"text": "Hi, this is the courier company, your package delivery attempt failed as no one was home, "
             "please share a convenient time for redelivery tomorrow.",
     "label": 0},
    {"text": "This is your gym membership renewal reminder, your plan expires in 5 days, you can renew "
             "online or at the front desk whenever suits you, no urgency.",
     "label": 0},

    # --- Legit cases resembling phishing structurally (link + account language) but genuinely benign ---
    {"text": "Your monthly account statement is now available. You can view it anytime by logging into "
             "your net banking portal at your convenience, no action required.",
     "label": 0},
    {"text": "This is a routine reminder that your account password was changed successfully today. "
             "If this wasn't you, please contact support using the number on your card.",
     "label": 0},
    {"text": "Your food delivery order has been confirmed. Track your order status anytime on the app, "
             "estimated delivery in 35 minutes.",
     "label": 0},
    {"text": "This is a newsletter update: check out this month's interest rate changes on our website "
             "whenever you get a chance, no action needed on your part.",
     "label": 0},
    {"text": "Your subscription renewal receipt has been emailed to you. You can review your billing "
             "history anytime by logging into your account dashboard.",
     "label": 0},
]


if __name__ == "__main__":
    scam_n = sum(1 for c in ADVERSARIAL_CASES if c["label"] == 1)
    legit_n = sum(1 for c in ADVERSARIAL_CASES if c["label"] == 0)
    print(f"Adversarial eval set: {len(ADVERSARIAL_CASES)} cases ({scam_n} scam, {legit_n} legit)")
