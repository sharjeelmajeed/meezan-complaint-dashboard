"""
Meezan Bank App - AI Complaint Analysis Dashboard
----------------------------------------------------
How to run:
  1. pip install streamlit pandas matplotlib google-play-scraper
  2. Make sure dashboard_data.csv is in the same folder as this file
  3. Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Meezan Bank - AI Complaint Analysis", layout="wide", page_icon="📊")

# ---------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------
EMERALD = "#0F6B4C"
EMERALD_DARK = "#0B4F38"
GOLD = "#C89B3C"
BRICK = "#B5453B"
TEAL = "#1B4D3E"
CREAM = "#F6F4EE"
INK = "#1F2A24"

# ---------------------------------------------------------------
# Custom styling (safe, targets stable Streamlit test-ids / baseweb classes)
# ---------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {INK};
}}

.dashboard-banner {{
    background: linear-gradient(90deg, {EMERALD_DARK} 0%, {EMERALD} 100%);
    padding: 1.4rem 1.8rem;
    border-radius: 10px;
    margin-bottom: 1.2rem;
}}
.dashboard-banner h1 {{
    color: white;
    font-size: 1.7rem;
    font-weight: 700;
    margin: 0;
}}
.dashboard-banner p {{
    color: #E4F3EC;
    font-size: 0.95rem;
    margin: 0.3rem 0 0 0;
}}

[data-testid="stMetric"] {{
    background-color: {CREAM};
    border: 1px solid #E4E0D3;
    border-left: 4px solid {EMERALD};
    border-radius: 8px;
    padding: 0.9rem 1rem;
}}
[data-testid="stMetricValue"] {{
    color: {EMERALD_DARK};
    font-weight: 700;
}}

button[data-baseweb="tab"] {{
    font-weight: 600;
    font-size: 0.95rem;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {EMERALD_DARK};
    border-bottom-color: {GOLD} !important;
}}

.stButton>button, .stButton>button[kind="primary"] {{
    background-color: {EMERALD};
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 600;
}}
.stButton>button:hover {{
    background-color: {EMERALD_DARK};
    color: white;
}}

.priority-card {{
    background-color: white;
    border: 1px solid #E4E0D3;
    border-left: 5px solid {BRICK};
    border-radius: 8px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
}}
.priority-card.urgent-only {{
    border-left-color: {GOLD};
}}
.badge {{
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.4rem;
}}
.badge-churn {{
    background-color: #FBEAE8;
    color: {BRICK};
}}
.badge-urgent {{
    background-color: #FBF1DE;
    color: #8A6D22;
}}
.badge-category {{
    background-color: #E8F3EE;
    color: {EMERALD_DARK};
}}

.key-finding {{
    background-color: #FBF1DE;
    border-left: 4px solid {GOLD};
    border-radius: 6px;
    padding: 0.7rem 1rem;
    font-size: 0.92rem;
}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Shared keyword classifier (used by Live Checker and Play Store Monitor)
# ---------------------------------------------------------------
categories_keywords = {
    "Transaction": ["deducted", "refund", "no cash", "unpaid", "double", "twice", "withdrew", "activat"],
    "Login": ["login", "credentials", "password", "fingerprint", "biometric", "cooling period", "cnic", "otp"],
    "Bug": ["glitch", "menu", "freeze", "load", "screenshot", "stuck", "crash", "not working", "not open"],
    "Security": ["breach", "unknown device", "data breaching", "trust", "unauthorized", "rooted", "modified"],
    "Support": ["complain", "helpline", "customer support", "unresolved", "no solution", "branch visit"],
    "UI/Design": ["layout", "theme", "interface", "design", "dark mode", "ui"],
    "Suggestion": ["please add", "should improve", "kindly", "would be better", "request"],
}
urgency_keywords = ["days", "weeks", "months", "years", "closing my account", "close my account",
                     "considering", "highly disappointed", "extremely"]
churn_keywords = ["closing my account", "close my account", "switch bank", "leaving"]
negative_words = ["bad", "disappointed", "worst", "scammer", "useless", "frustrat"]

def classify_live(text):
    text_l = str(text).lower()
    matched = [cat for cat, kws in categories_keywords.items() if any(kw in text_l for kw in kws)]
    urgency = sum(1 for kw in urgency_keywords if kw in text_l)
    churn = any(kw in text_l for kw in churn_keywords) or ("years" in text_l and any(neg in text_l for neg in negative_words))
    return matched or ["Positive / Other"], urgency, churn

# ---------------------------------------------------------------
# Load data
# ---------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard_data.csv")
    return df

df = load_data()

# ---------------------------------------------------------------
# Chart styling helper
# ---------------------------------------------------------------
def style_bar_chart(fig, ax, color):
    bars = ax.patches
    for bar in bars:
        bar.set_color(color)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color("#CFCABA")
    ax.spines['bottom'].set_color("#CFCABA")
    ax.yaxis.grid(True, color="#E5E2D8", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(axis='both', labelsize=10)
    ax.set_ylabel(ax.get_ylabel(), fontsize=11, color=INK)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', fontsize=10, fontweight='bold', color=INK)
    fig.patch.set_facecolor('white')

# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.markdown("""
<div class="dashboard-banner">
    <h1>📊 Meezan Bank App — AI-Powered Complaint Analysis</h1>
    <p>Prototype dashboard: automatically classifies customer reviews and highlights priority complaints.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# Top metrics
# ---------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Reviews Analyzed", len(df))
col2.metric("Complaints (non-Positive)", len(df[df["predicted_category"] != "Positive"]))
col3.metric("High Priority (Churn Risk)", int(df["churn_risk"].sum()))
col4.metric("Avg Rating", round(df["rating"].mean(), 2))

st.divider()

# ---------------------------------------------------------------
# Tabs for each section
# ---------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Overview", "Bugs", "Transactions", "UI/UX", "Feedback", "Priority Complaints", "Live Checker", "Play Store Monitor"
])

# ---------------- TAB 1: Overview ----------------
with tab1:
    st.subheader("Complaint Category Breakdown")
    category_counts = df[df["predicted_category"] != "Positive"]["predicted_category"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(category_counts.index, category_counts.values)
    ax.set_ylabel("Number of complaints")
    plt.xticks(rotation=30, ha="right")
    style_bar_chart(fig, ax, EMERALD)
    st.pyplot(fig)

    st.caption("Note: This is a prototype AI classification (~75% accuracy). Rare categories have limited training examples.")

# ---------------- TAB 2: Bugs ----------------
with tab2:
    st.subheader("Bug Complaints — Detailed Breakdown")
    bug_df = df[df["bug_subcategory"] != ""]

    if len(bug_df) > 0:
        bug_counts = bug_df["bug_subcategory"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(bug_counts.index, bug_counts.values)
        ax.set_ylabel("Number of complaints")
        plt.xticks(rotation=25, ha="right")
        style_bar_chart(fig, ax, BRICK)
        st.pyplot(fig)

        st.markdown('<div class="key-finding">🔑 <b>Key Finding:</b> \'Side Menu Stuck\' issue is the most repeated, identifiable bug.</div>', unsafe_allow_html=True)

        with st.expander("View raw complaint text"):
            st.dataframe(bug_df[["reviewer", "text", "bug_subcategory"]], use_container_width=True)
    else:
        st.info("No bug complaints found in this dataset.")

# ---------------- TAB 3: Transactions ----------------
with tab3:
    st.subheader("Transaction Complaints — Payment Type Breakdown")
    txn_df = df[df["transaction_subcategory"] != ""]

    if len(txn_df) > 0:
        txn_counts = txn_df["transaction_subcategory"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(txn_counts.index, txn_counts.values)
        ax.set_ylabel("Number of complaints")
        plt.xticks(rotation=25, ha="right")
        style_bar_chart(fig, ax, GOLD)
        st.pyplot(fig)

        st.caption("Note: Many customers don't specify the exact payment method (Bill/QR/IBFT/Raast) — these are marked 'Unspecified'.")

        with st.expander("View raw complaint text"):
            st.dataframe(txn_df[["reviewer", "text", "transaction_subcategory"]], use_container_width=True)
    else:
        st.info("No transaction complaints found in this dataset.")

# ---------------- TAB 4: UI/UX ----------------
with tab4:
    st.subheader("UI/UX Complaints — Issue Breakdown")
    ui_df = df[df["ui_subcategory"] != ""]

    if len(ui_df) > 0:
        ui_counts = ui_df["ui_subcategory"].value_counts()
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.bar(ui_counts.index, ui_counts.values)
        ax.set_ylabel("Number of complaints")
        plt.xticks(rotation=25, ha="right")
        style_bar_chart(fig, ax, TEAL)
        st.pyplot(fig)

        st.markdown('<div class="key-finding">🔑 <b>Key Finding:</b> Combined with the Bugs tab, \'Side Menu Stuck\' was mentioned 8 times total — including one device-specific case (Vivo Y20s, Android 10).</div>', unsafe_allow_html=True)

        with st.expander("View raw complaint text"):
            st.dataframe(ui_df[["reviewer", "text", "ui_subcategory"]], use_container_width=True)
    else:
        st.info("No UI/UX complaints found in this dataset.")

# ---------------- TAB 5: Feedback/Suggestions ----------------
with tab5:
    st.subheader("Genuine Feature Requests")
    suggestion_df = df[(df["suggestion_type"] != "") & (~df["suggestion_type"].str.contains("MISCLASSIFIED", na=False))]

    if len(suggestion_df) > 0:
        st.dataframe(suggestion_df[["reviewer", "text", "suggestion_type"]], use_container_width=True)
        st.caption("Note: Each request appeared only once in this sample — ranking by frequency needs a larger dataset.")
    else:
        st.info("No genuine feature requests found in this dataset.")

# ---------------- TAB 6: Priority Complaints ----------------
with tab6:
    st.subheader("⚠️ High Priority Complaints")
    priority_df = df[(df["churn_risk"] == True) | (df["urgency_score"] >= 2)]
    priority_df = priority_df[priority_df["predicted_category"] != "Positive"]

    if len(priority_df) > 0:
        for _, row in priority_df.iterrows():
            card_class = "priority-card" if row["churn_risk"] else "priority-card urgent-only"
            badges = f'<span class="badge badge-category">{row["predicted_category"]}</span>'
            if row["churn_risk"]:
                badges += '<span class="badge badge-churn">📉 Churn Risk</span>'
            if row["urgency_score"] >= 2:
                badges += '<span class="badge badge-urgent">🔥 Urgent</span>'
            st.markdown(f"""
            <div class="{card_class}">
                {badges}
                <p style="margin-top:0.5rem; margin-bottom:0;">{row['text']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No high-priority complaints found in this dataset.")

# ---------------- TAB 7: Live Checker ----------------
with tab7:
    st.subheader("🔎 Type a Complaint — Get Instant Classification")
    st.caption("Note: This demo uses a fast keyword-based classifier (lightweight, works instantly on the web). The full AI model used for the bulk analysis above is heavier and runs offline.")

    user_input = st.text_area("Type a customer complaint here:", height=100,
                               placeholder="e.g. my payment failed and amount got deducted but no refund")

    if st.button("Classify Complaint", type="primary"):
        if user_input.strip():
            cats, urgency, churn = classify_live(user_input)
            st.success(f"**Detected Category:** {', '.join(cats)}")
            col_a, col_b = st.columns(2)
            col_a.metric("Urgency Score", urgency)
            col_b.metric("Churn Risk", "Yes ⚠️" if churn else "No")
        else:
            st.warning("Please type a complaint first.")

# ---------------- TAB 8: Live Play Store Monitor ----------------
with tab8:
    st.subheader("📡 Check Play Store for New Reviews")
    st.caption("Click the button to fetch the latest reviews directly from Google Play and classify any new ones instantly.")

    # Hybrid matching: prefer review_id (reliable), fallback to reviewer+text match
    known_ids = set(df["review_id"].dropna()) if "review_id" in df.columns else set()
    known_keys = set((r, t) for r, t in zip(df["reviewer"], df["text"]))

    if st.button("🔄 Check for New Reviews Now", type="primary"):
        with st.spinner("Fetching latest reviews from Google Play..."):
            try:
                from google_play_scraper import reviews, Sort
                result, _ = reviews(
                    "invo8.meezan.mb",
                    lang='en',
                    country='pk',
                    sort=Sort.NEWEST,
                    count=20,
                )

                new_reviews = []
                for r in result:
                    rid = r.get("reviewId")
                    key = (r.get("userName"), r.get("content"))
                    if rid and rid in known_ids:
                        continue
                    if key in known_keys:
                        continue
                    new_reviews.append(r)

                if new_reviews:
                    st.success(f"Found {len(new_reviews)} new review(s) since last dataset snapshot!")
                    for r in new_reviews:
                        cats, urgency, churn = classify_live(r.get("content", ""))
                        with st.container(border=True):
                            st.markdown(f"🆕 **{r.get('userName', 'Unknown')}** (Rating: {r.get('score', '?')}⭐)")
                            st.write(r.get("content", ""))
                            st.markdown(f"**Detected Category:** {', '.join(cats)} | **Urgency:** {urgency} | **Churn Risk:** {'Yes ⚠️' if churn else 'No'}")
                else:
                    st.info("No new reviews found right now. Google Play may take some time to index a newly posted review — try again in a few minutes.")
            except Exception as e:
                st.error(f"Could not fetch reviews right now: {e}")

st.divider()
st.caption("Prototype built as part of AI/Data Analytics internship project. Bulk classification powered by a pretrained zero-shot AI model (no training data required).")
