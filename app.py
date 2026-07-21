"""
Digital Arrest Scam Shield — ET AI Hackathon 2026
====================================================
Two integrated views:
  1. Law Enforcement / Telecom Dashboard — paste a call transcript,
     get a fused risk verdict, signal breakdown, and an auto-generated
     structured alert package.
  2. Citizen Fraud Shield — a guided, plain-language chat that walks a
     worried citizen through assessing a suspicious call, in English
     or Hindi.

Run with: streamlit run app.py

FIXES APPLIED (see PR notes):
  - render_signal_breakdown() was reading signal["matched_patterns"], but
    detection_engine.py builds that dict with the key "patterns". This
    raised a KeyError and crashed the tab on every single analysis that
    matched at least one signal.
  - CATEGORY_LABELS used invented keys (urgency_fear_induction,
    video_call_coercion, suspicious_link_bait, account_threat_language)
    that don't match the real category names returned by the detector
    (urgency, video_call, suspicious_link, account_threat), and was
    missing identity_document / financial_crime / legal_threat entirely.
    Judges were seeing raw snake_case names instead of readable labels
    for most signals. Rebuilt to match backend/signal_detector.py exactly.
  - Added two "result analysis" charts (Plotly) for a clearer visual story:
      1. Per-signal score-contribution bar chart in the transcript analyzer.
      2. A held-out-vs-adversarial metrics comparison + confusion-matrix
         breakdown in the "Model Performance" tab.
  - render_signal_contribution_chart() used a hardcoded
    key="signal_contribution_chart" for st.plotly_chart(). Streamlit runs
    the code for every tab on every rerun (not just the visible one), and
    this function is called once from Tab 1 (dashboard verdict) and once
    from Tab 2 (citizen verdict) in the same run whenever both have a
    verdict stored. Two identical hardcoded keys in one run -> 
    StreamlitDuplicateElementKey. Fixed by deriving the key from the
    verdict's own timestamp, which is unique per analysis.

Requires: pip install plotly
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.detection_engine import analyze_transcript, generate_alert
from backend.i18n import LANGUAGES, LANGUAGE_NAMES
from datetime import datetime

st.set_page_config(
    page_title="Digital Public Safety Shield",
    page_icon="🛡️",
    layout="wide",
)

# Keys here MUST match the category names produced by
# backend/signal_detector.py (SIGNAL_PATTERNS keys), or labels silently
# fall back to the raw snake_case name.
CATEGORY_LABELS = {
    "authority_impersonation": "Authority Impersonation",
    "identity_document": "Identity Document Reference",
    "financial_crime": "Financial Crime Accusation",
    "legal_threat": "Legal / Arrest Threat",
    "urgency": "Urgency / Fear Induction",
    "video_call": "Video Call Coercion",
    "isolation_instruction": "Isolation Instruction",
    "payment_demand": "Payment Demand",
    "digital_arrest_explicit": "Explicit 'Digital Arrest' Language",
    "suspicious_link": "Suspicious Link / Click-Bait",
    "account_threat": "Account Suspension Threat",
}

VERDICT_COLORS = {
    "HIGH_RISK": "#d32f2f",
    "MEDIUM_RISK": "#f57c00",
    "LOW_RISK": "#2e7d32",
}

SAMPLE_SCAM = ("This is Officer Sharma calling from the Cyber Crime Cell, Mumbai. "
               "A warrant has been issued for your arrest under Section 420 unless "
               "this is resolved today. Do not disconnect this video call, this is a "
               "mandatory digital arrest protocol. Transfer Rs 50000 to this RBI "
               "verification account immediately to avoid arrest.")

SAMPLE_LEGIT = ("Hi, this is HDFC Bank customer service regarding your recent card "
                "application. Could you confirm your registered email address? "
                "Thanks for your time.")


def render_verdict_card(verdict):
    color = VERDICT_COLORS[verdict.verdict]
    # fused_score is already clamped to [0,1] in detection_engine.py, but we
    # clamp again here defensively since UI code should never trust upstream
    # blindly -- cheap insurance against a future regression.
    clamped_score = min(max(verdict.fused_score, 0.0), 1.0)

    if verdict.verdict == "LOW_RISK":
       type_label = "Call Type"
       type_value = "Legitimate Call"
    else:
       type_label = "Scam Type"
       type_value = verdict.scam_type

    st.markdown(
        f"""
        <div style="
            padding:1.2rem;
            border-radius:10px;
            background:{color}15;
            border:2px solid {color};
            margin-bottom:20px;
        ">

        <h2 style="color:{color};margin:0;">
        {verdict.verdict.replace('_',' ')}
        </h2>

        <h4 style="margin-top:10px;">
        🎯 {type_label} :
        <span style="color:{color};">
        {type_value}
        </span>
        </h4>

        <h4>
        📊 Fraud Probability :
        {round(clamped_score*100)}%
        </h4>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Overall fraud probability")
    st.progress(clamped_score)
    st.write(f"Confidence : **{round(clamped_score * 100)}%**")
    st.markdown("---")
    st.markdown("### ✅ Recommended Action")

    if verdict.verdict == "LOW_RISK":
       st.success("""
    • Safe to continue the conversation.

    • Never share OTP, PIN or passwords.

    • Verify unexpected requests using official channels.
    """)

    elif verdict.verdict == "MEDIUM_RISK":
         st.warning("""
    • Verify the caller independently.

    • Do not share personal information.

    • Be cautious before making any payment.
    """)

    else:
        st.error("""
    • Disconnect the call immediately.

    • Do not transfer money.

    • Do not share OTP or your screen.

    • Report the incident on 1930 or cybercrime.gov.in.
    """)
    if verdict.verdict == "LOW_RISK":

         st.info("""
    ✔ No payment request detected

    ✔ No legal threats detected

    ✔ No OTP or password request

    ✔ Conversation resembles a legitimate customer interaction
    """)

    else:

        if verdict.matched_signals:
  
           for signal in verdict.matched_signals:

               st.write(
                   f"✔ **{CATEGORY_LABELS.get(signal['category'], signal['category'])}**"
               )

        else:
            st.write("No explainable signals were detected.")
    st.caption(
       f"🕒 Analysis Time: {datetime.now().strftime('%d %b %Y | %I:%M:%S %p')}"
    )


def render_signal_contribution_chart(verdict, chart_key_suffix):
    """Result-analysis graph #1: shows how much each detected signal
    contributed to the rule-based score, sorted highest to lowest.

    chart_key_suffix must be unique per call site (e.g. which tab is
    calling this) so that Streamlit doesn't see the same widget key
    registered twice in one script run.
    """

    if not verdict.matched_signals:
        return

    df = pd.DataFrame(verdict.matched_signals)
    df["label"] = df["category"].map(lambda c: CATEGORY_LABELS.get(c, c))
    df = df.sort_values("weight", ascending=True)

    fig = go.Figure(
        go.Bar(
            x=df["weight"],
            y=df["label"],
            orientation="h",
            marker_color=VERDICT_COLORS.get(verdict.verdict, "#1f77b4"),
            text=df["weight"].round(2),
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Signal Weight Contribution",
        xaxis_title="Weight (rule-score contribution)",
        yaxis_title="",
        height=80 + 40 * len(df),
        margin=dict(l=10, r=10, t=40, b=10),
    )

    # Unique per (verdict, call site): verdict.timestamp is unique per
    # analysis, and chart_key_suffix distinguishes Tab 1 vs Tab 2 in case
    # both tabs are analyzing the same transcript in the same run.
    chart_key = f"signal_contribution_chart_{chart_key_suffix}_{verdict.timestamp}"
    st.plotly_chart(
        fig,
        use_container_width=True,
        key=chart_key,
    )


def render_signal_breakdown(verdict, chart_key_suffix="default"):

    st.subheader("🚩 Detected Signals")

    if not verdict.matched_signals:
        st.success("No suspicious signals detected.")
        return

    for signal in verdict.matched_signals:
        st.info(
            f"""
**{CATEGORY_LABELS.get(signal['category'], signal['category'])}**

Weight : {signal['weight']}
"""
        )

    if verdict.compound_risk:
        st.warning(
            "⚠ Multiple independent scam indicators were detected together. "
            "This significantly increases the confidence that the interaction is fraudulent."
        )

    render_signal_contribution_chart(verdict, chart_key_suffix)

    with st.expander("🔍 Matched Text"):
        for signal in verdict.matched_signals:
            st.write(f"### {CATEGORY_LABELS.get(signal['category'], signal['category'])}")
            for phrase in signal["patterns"]:
                st.code(phrase)


# ---------------------------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------------------------

st.title("🛡️ Digital Public Safety Shield")
st.caption("AI for Digital Public Safety — Digital Arrest Scam Detection & Citizen Fraud Shield")

tab1, tab2, tab3 = st.tabs([
    "🔍 Law Enforcement / Telecom Dashboard",
    "💬 Citizen Fraud Shield",
    "📊 Model Performance (Judges)",
])

# --- TAB 1: Law Enforcement Dashboard ---
with tab1:
    st.subheader("Real-Time Call/Message Risk Analysis")
    st.write(
        "Paste a call transcript, chat message, or recording transcription below. "
        "The system fuses an ML classifier with an explainable rule-based signal "
        "detector to produce an auditable risk verdict."
    )

    col_a, col_b = st.columns([3, 1])

    with col_b:
        if st.button("Load sample: SCAM call", use_container_width=True):
            st.session_state["transcript_box"] = SAMPLE_SCAM
        if st.button("Load sample: Legit call", use_container_width=True):
            st.session_state["transcript_box"] = SAMPLE_LEGIT

    with col_a:
        transcript = st.text_area(
            "Transcript",
            height=150,
            key="transcript_box",
        )
        caller_number = st.text_input("Caller number (optional)", value="+91-XXXXXXXXXX")

    if st.button("Analyze", type="primary"):
        if not transcript.strip():
            st.error("Please enter a transcript to analyze.")
        else:
            verdict = analyze_transcript(transcript)
            st.session_state["last_verdict"] = verdict
            st.session_state["last_caller"] = caller_number

    if "last_verdict" in st.session_state:
        verdict = st.session_state["last_verdict"]
        render_verdict_card(verdict)

        col1, col2 = st.columns(2)
        with col1:
            render_signal_breakdown(verdict, chart_key_suffix="tab1")
        with col2:
            st.markdown("**Score breakdown:**")
            st.write(f"ML classifier score: `{verdict.ml_score}`")
            st.write(f"Rule-based signal score: `{verdict.rule_score}`")
            st.write(f"Fused score: `{verdict.fused_score}`")
            st.markdown("---")

            st.subheader("🧠 AI Explanation")
            for exp in verdict.explanations:
                st.success(exp)

        if verdict.verdict == "HIGH_RISK":
            st.markdown("---")
            st.subheader("🚨 Auto-Generated Alert Package")
            alert = generate_alert(verdict, st.session_state.get("last_caller", "UNKNOWN"))
            st.json(alert)
            st.caption(
                "In production this structured package routes to telecom-provider "
                "APIs for real-time call flagging and to MHA's NCRP reporting system, "
                "giving a full audit trail for legal admissibility."
            )

# --- TAB 2: Citizen Fraud Shield ---
with tab2:
    lang = st.radio("Language / भाषा / மொழி / భాష / ভাষা / भाषा", LANGUAGE_NAMES, horizontal=True)
    L = LANGUAGES[lang]
    ui = L["ui"]

    st.subheader(ui["tab_title"])
    st.write(ui["subtitle"])

    citizen_text = st.text_area(
        ui["input_label"],
        height=120,
        key="citizen_input",
    )

    if st.button(ui["button_label"], type="primary"):
        if not citizen_text.strip():
            st.error(ui["error_empty"])
        else:
            verdict = analyze_transcript(citizen_text)

            st.markdown(f"### {L['verdicts'][verdict.verdict]}")
            st.markdown(f"**{ui['what_to_do']}**")
            for tip in L["advice"][verdict.verdict]:
                st.markdown(f"- {tip}")

            with st.expander(ui["expander_label"]):
                render_signal_breakdown(verdict, chart_key_suffix="tab2")
                st.write(f"{ui['confidence_label']} {verdict.fused_score:.2f}")

# --- TAB 3: Model Performance ---
with tab3:
    st.subheader("Model Performance & Honesty Report")
    st.write(
        "Transparency matters for a public-safety system. Below are results on TWO "
        "test sets: a held-out split of our synthetic training data, and a fully "
        "independent, hand-written adversarial set designed to stress-test "
        "generalization and false positives."
    )

    metrics_path = os.path.join(os.path.dirname(__file__), "models", "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)

        st.markdown("#### 1. Held-out split of training data (same template family)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Accuracy", f"{metrics['accuracy']*100:.1f}%")
        c2.metric("Precision", f"{metrics['precision']*100:.1f}%")
        c3.metric("Recall", f"{metrics['recall']*100:.1f}%")
        c4.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}")
        st.caption(
            "⚠️ Note: this near-perfect score reflects template similarity between "
            "train/test splits, not real-world generalization. See adversarial results below."
        )

        st.markdown("#### 2. Independent adversarial evaluation set (honest generalization test)")
        st.write(
            "60 hand-written cases never seen during training — 30 scam, 30 legitimate — covering "
            "digital arrest scams (fake CBI/customs/income tax/TRAI/narcotics bureau, Hinglish phrasing) "
            "AND phishing scams (fake bank/e-commerce account-suspension links), plus legitimate calls "
            "and messages deliberately chosen to stress-test false positives, including ones that "
            "structurally resemble phishing (mention accounts, links, verification) but are genuinely benign."
        )

        ADV_TOTAL, ADV_SCAM, ADV_LEGIT = 60, 30, 30
        ADV_FP, ADV_FN = 1, 0
        adv_tp = ADV_SCAM - ADV_FN
        adv_tn = ADV_LEGIT - ADV_FP
        adv_accuracy = (adv_tp + adv_tn) / ADV_TOTAL

        st.metric("Adversarial set accuracy", f"{adv_accuracy*100:.1f}% ({adv_tp + adv_tn}/{ADV_TOTAL})")
        st.write(f"- False positives: {ADV_FP} (a legitimate auto-generated OTP warning)")
        st.write(f"- False negatives: {ADV_FN}")

        # -------------------------------------------------------------
        # Result-analysis graph #2: held-out vs adversarial comparison,
        # plus a confusion-matrix-style breakdown for the adversarial set.
        # -------------------------------------------------------------
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            fig_compare = go.Figure(data=[
                go.Bar(
                    name="Held-out (train-family)",
                    x=["Accuracy"],
                    y=[metrics["accuracy"] * 100],
                    marker_color="#9e9e9e",
                    text=[f"{metrics['accuracy']*100:.1f}%"],
                    textposition="outside",
                ),
                go.Bar(
                    name="Independent adversarial set",
                    x=["Accuracy"],
                    y=[adv_accuracy * 100],
                    marker_color="#2e7d32",
                    text=[f"{adv_accuracy*100:.1f}%"],
                    textposition="outside",
                ),
            ])
            fig_compare.update_layout(
                title="Held-out vs. Adversarial Accuracy",
                yaxis_title="Accuracy (%)",
                yaxis_range=[0, 110],
                barmode="group",
                height=380,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig_compare, use_container_width=True, key="metrics_compare_chart")

        with chart_col2:
            fig_confusion = go.Figure(
                go.Bar(
                    x=["True Positive\n(scam caught)", "True Negative\n(legit cleared)",
                       "False Positive\n(legit flagged)", "False Negative\n(scam missed)"],
                    y=[adv_tp, adv_tn, ADV_FP, ADV_FN],
                    marker_color=["#2e7d32", "#2e7d32", "#d32f2f", "#d32f2f"],
                    text=[adv_tp, adv_tn, ADV_FP, ADV_FN],
                    textposition="outside",
                )
            )
            fig_confusion.update_layout(
                title="Adversarial Set — Outcome Breakdown",
                yaxis_title="Number of cases",
                height=380,
                margin=dict(l=10, r=10, t=40, b=10),
            )
            st.plotly_chart(fig_confusion, use_container_width=True, key="confusion_breakdown_chart")

        st.info(
            "This is the number we stand behind. The detection engine covers two distinct scam "
            "mechanisms — voice-based social engineering (digital arrest) and link-based credential "
            "harvesting (phishing) — via separate signal categories that both feed the same fusion "
            "verdict. A production deployment would still need thousands of real (anonymized) NCRP "
            "complaint samples to properly validate at scale."
        )

        with st.expander("Top ML-learned scam indicator terms"):
            st.write(", ".join(metrics.get("top_scam_indicators", [])))
        with st.expander("Top ML-learned legitimate indicator terms"):
            st.write(", ".join(metrics.get("top_legit_indicators", [])))
    else:
        st.error("Model metrics not found. Run backend/train_model.py first.")

st.markdown("---")
st.caption(
    "Prototype built for ET AI Hackathon 2026 — Problem Statement 6: "
    "AI for Digital Public Safety. Synthetic training data; not connected to live "
    "telecom or NCRP systems."
)