# Demo Video Script — Digital Public Safety Shield
Target length: 90–120 seconds. Judges watch dozens of these — the first 10 seconds decide if they lean in or check their phone.

---

## [0:00–0:12] HOOK — problem, fast, with a real number on screen
**Visual:** Title slide or a clean text card, not the app yet.
**Voiceover:**
> "In just nine months, digital arrest scams cost Indians ₹1,776 crore. The scam works because no single signal gives it away — a caller claiming to be police isn't automatically a threat. It's the pattern that matters. We built the system that catches the pattern."

*(Say this over slide 2 or a simple stat card — don't waste time on a logo animation.)*

---

## [0:12–0:20] WHAT YOU BUILT — one sentence, no jargon dump
**Visual:** Cut to architecture diagram (slide 4) for 3–4 seconds, then straight to the live app.
**Voiceover:**
> "Digital Public Safety Shield fuses a rule-based signal detector with a trained ML classifier — two independent checks, one auditable verdict."

---

## [0:20–0:50] LIVE DEMO #1 — Law Enforcement Dashboard (the money shot)
**Visual:** Screen-record the actual app. Type or paste a transcript live — don't use the pre-loaded sample button, typing it live proves it's not canned.
**Action on screen:**
1. Paste/type a scam transcript
2. Click "Analyze"
3. Let the HIGH RISK card and score breakdown appear on screen for 2–3 full seconds — don't rush past it
4. Scroll to the alert JSON, hold on it briefly

**Voiceover (talk over the typing/clicking, don't narrate every click):**
> "Watch — this transcript was never used to train the model. The system flags it HIGH RISK in under a second, shows exactly which signals fired, and auto-generates an audit-ready alert package a telecom provider or investigator could act on immediately."

---

## [0:50–1:10] LIVE DEMO #2 — Citizen Fraud Shield, bilingual proof
**Visual:** Switch tabs. Show one HIGH RISK result in English, then switch the language toggle and show a LOW RISK result in Hindi (or Tamil/Telugu/Bengali/Marathi if you're confident in the translation).
**Voiceover:**
> "For citizens, the same engine speaks plainly — in six Indian languages — telling them exactly what to do, and just as importantly, when *not* to panic."

*(The contrast of HIGH vs LOW risk in two different languages in ~15 seconds is the single best proof-of-generalization moment you have. Don't cut it short.)*

---

## [1:10–1:30] THE HONESTY BEAT — this is your differentiator, don't skip it
**Visual:** Cut to the "Model Performance (Judges)" tab or slide 8 of the deck.
**Voiceover:**
> "Most hackathon demos show you their best number. We're showing you both: our training data gives a misleading 100% — same-template overlap, not real generalization. On an independent, hand-written adversarial test set, we get 93.75%, with zero false negatives. That's the number we stand behind."

*(This is the moment that separates you from every other team. Say it confidently, not apologetically.)*

---

## [1:30–1:45] CLOSE — impact + ask
**Visual:** Slide 11 (closing slide) or the title card again.
**Voiceover:**
> "Every hour a signal goes unconnected is an hour a scam continues. This is a working prototype today — not a mockup, not a pitch. Digital Public Safety Shield, built for ET AI Hackathon 2026."

---

## Recording checklist before you hit record

1. **Restart the app fresh** right before recording — `Ctrl+C` then `python -m streamlit run app.py` — so there's no leftover state from testing that could confuse the flow.
2. **Pre-write your typed transcript** in Notepad so you can paste it smoothly instead of typing live with typos on camera.
3. **Close other tabs/notifications** — Edge showing 15 tabs or a Windows notification popping up mid-recording looks unpolished.
4. **Zoom your browser to ~110–125%** (Ctrl + Plus) before recording — small UI text is unreadable on a projector or compressed video.
5. **Do one full silent run-through first** to check timing, then record for real.
6. **Screen recording tool:** Windows has one built in — press `Win + Alt + R` while the app is in focus to start/stop recording (uses Xbox Game Bar). No extra install needed.
7. **Keep raw footage** even after editing — if the deck needs a fresh screenshot later, you can pull frames from it.

## Tone notes
- Talk like you're explaining it to a smart colleague, not reciting the deck. Confidence > polish.
- Don't apologize for the synthetic data or the 100%/93.75% gap — frame it as rigor, said once, clearly, then move on.
- If multiple teammates are on camera/voice, decide who says what *before* recording — switching narrators mid-sentence sounds chaotic.
