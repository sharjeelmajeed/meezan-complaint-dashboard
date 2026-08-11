"""
Meezan Bank App - AI Complaint Analysis Dashboard

"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
}}

.dashboard-banner {{
    background: linear-gradient(90deg, {EMERALD_DARK} 0%, {EMERALD} 100%);
    padding: 1.3rem 1.8rem;
    border-radius: 10px;
    margin-bottom: 1.3rem;
}}
.dashboard-banner h1 {{
    color: white;
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0;
}}
.dashboard-banner p {{
    color: #E4F3EC;
    font-size: 0.92rem;
    margin: 0.3rem 0 0 0;
}}

.kpi-card {{
    background-color: {CREAM};
    border: 1px solid #E4E0D3;
    border-left: 4px solid {EMERALD};
    border-radius: 8px;
    padding: 0.8rem 1rem;
    height: 100%;
}}
.kpi-label {{
    font-size: 0.78rem;
    color: #5A5546;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    margin: 0;
}}
.kpi-value {{
    font-size: 1.6rem;
    font-weight: 700;
    color: {EMERALD_DARK};
    margin: 0.15rem 0 0 0;
}}
.kpi-icon {{
    font-size: 1.3rem;
}}

button[data-baseweb="tab"] {{
    font-weight: 600;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {EMERALD_DARK};
    border-bottom-color: {GOLD} !important;
}}

.stButton>button {{
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
                     "considering", "highly disappointed", "extremely", "frustrating"]
churn_keywords = ["closing my account", "close my account", "switch bank", "leaving", " frustrating experience"]
negative_words = ["bad", "disappointed", "worst", "scammer", "useless", "frustrating"]

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
# Chart helper (interactive Plotly bar chart)
# ---------------------------------------------------------------
def interactive_bar_chart(counts_series, color):
    chart_df = counts_series.reset_index()
    chart_df.columns = ["category", "count"]
    fig = px.bar(chart_df, x="category", y="count", text="count", color_discrete_sequence=[color])
    fig.update_traces(textposition="outside", hovertemplate="%{x}: %{y} complaints<extra></extra>")
    fig.update_layout(xaxis_title="", yaxis_title="Number of complaints", showlegend=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

def kpi_card(col, icon, label, value):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-label"><span class="kpi-icon">{icon}</span> {label}</p>
            <p class="kpi-value">{value}</p>
        </div>
        """, unsafe_allow_html=True)

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
# KPI row (computed dynamically from the data - no hardcoded numbers)
# ---------------------------------------------------------------
total_reviews = len(df)
complaint_count = len(df[df["predicted_category"] != "Positive"])
complaint_rate = round((complaint_count / total_reviews) * 100, 1) if total_reviews else 0
churn_count = int(df["churn_risk"].sum())
avg_rating = round(df["rating"].mean(), 2)

top_category_series = df[df["predicted_category"] != "Positive"]["predicted_category"].value_counts()
top_category = top_category_series.index[0] if len(top_category_series) > 0 else "N/A"

side_menu_count = (
    (df["bug_subcategory"].astype(str).str.contains("Menu", na=False) & df["bug_subcategory"].astype(str).str.contains("Stuck", na=False)).sum()
    + (df["ui_subcategory"].astype(str).str.contains("Menu", na=False) & df["ui_subcategory"].astype(str).str.contains("Stuck", na=False)).sum()
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
kpi_card(k1, "📝", "Total Reviews", total_reviews)
kpi_card(k2, "⚠️", "Complaint Rate", f"{complaint_rate}%")
kpi_card(k3, "📉", "Churn Risk", churn_count)
kpi_card(k4, "⭐", "Avg Rating", avg_rating)
kpi_card(k5, "🏷️", "Top Issue", top_category)
kpi_card(k6, "🔁", "'Side Menu Stuck' Mentions", int(side_menu_count))

st.write("")

# ---------------------------------------------------------------
# Summary donut chart
# ---------------------------------------------------------------
donut_col, note_col = st.columns([1, 2])
with donut_col:
    donut_df = pd.DataFrame({
        "type": ["Positive", "Complaints"],
        "count": [total_reviews - complaint_count, complaint_count]
    })
    fig_donut = go.Figure(data=[go.Pie(
        labels=donut_df["type"], values=donut_df["count"], hole=0.55,
        marker=dict(colors=[EMERALD, BRICK]),
        textinfo="label+percent",
    )])
    fig_donut.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)
with note_col:
    st.markdown("##### At a glance")
    st.markdown(
        f"Out of **{total_reviews}** reviews analyzed, **{complaint_count} ({complaint_rate}%)** represent genuine complaints. "
        f"**{churn_count}** of these show signs of churn risk or high urgency — these are the ones that would otherwise "
        f"sit in a FIFO queue with no priority. The most common identifiable issue across the dataset is "
        f"**'Side Menu Stuck'**, mentioned **{int(side_menu_count)} times** across Bug and UI/Design reviews."
    )

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
    interactive_bar_chart(category_counts, EMERALD)
    st.caption("Note: This is a prototype AI classification (~75% accuracy). Rare categories have limited training examples.")

# ---------------- TAB 2: Bugs ----------------
with tab2:
    st.subheader("Bug Complaints - Detailed Breakdown")
    bug_df = df[df["bug_subcategory"] != ""]

    if len(bug_df) > 0:
        bug_counts = bug_df["bug_subcategory"].value_counts()
        interactive_bar_chart(bug_counts, BRICK)
        st.markdown('<div class="key-finding">🔑 <b>Key Finding:</b> \'Side Menu Stuck\' issue is the most repeated, identifiable bug.</div>', unsafe_allow_html=True)

        with st.expander("View raw complaint text"):
            st.dataframe(bug_df[["reviewer", "text", "bug_subcategory"]], use_container_width=True)
    else:
        st.info("No bug complaints found in this dataset.")

# ---------------- TAB 3: Transactions ----------------
with tab3:
    st.subheader("Transaction Complaints - Payment Type Breakdown")
    txn_df = df[df["transaction_subcategory"] != ""]

    if len(txn_df) > 0:
        txn_counts = txn_df["transaction_subcategory"].value_counts()
        interactive_bar_chart(txn_counts, GOLD)
        st.caption("Note: Many customers don't specify the exact payment method (Bill/QR/IBFT/Raast) - these are marked 'Unspecified'.")

        with st.expander("View raw complaint text"):
            st.dataframe(txn_df[["reviewer", "text", "transaction_subcategory"]], use_container_width=True)
    else:
        st.info("No transaction complaints found in this dataset.")

# ---------------- TAB 4: UI/UX ----------------
with tab4:
    st.subheader("UI/UX Complaints - Issue Breakdown")
    ui_df = df[df["ui_subcategory"] != ""]

    if len(ui_df) > 0:
        ui_counts = ui_df["ui_subcategory"].value_counts()
        interactive_bar_chart(ui_counts, TEAL)
        st.markdown('<div class="key-finding">🔑 <b>Key Finding:</b> Combined with Bugs tab, \'Side Menu Stuck\' was mentioned 8 times total - including one device-specific case (Vivo Y20s, Android 10).</div>', unsafe_allow_html=True)

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
        st.caption("Note: Each request appeared only once in this sample - ranking by frequency needs a larger dataset.")
    else:
        st.info("No genuine feature requests found in this dataset.")

# ---------------- TAB 6: Priority Complaints ----------------
with tab6:
    st.subheader("⚠️ High Priority Complaints (Urgency or Churn Risk)")
    priority_df = df[(df["churn_risk"] == True) | (df["urgency_score"] >= 2)]
    priority_df = priority_df[priority_df["predicted_category"] != "Positive"]

    if len(priority_df) > 0:
        for _, row in priority_df.iterrows():
            with st.container(border=True):
                st.markdown(f"**Category:** {row['predicted_category']} | **Urgency:** {row['urgency_score']} | **Churn Risk:** {row['churn_risk']}")
                st.write(row["text"])
    else:
        st.info("No high-priority complaints found in this dataset.")

# ---------------- TAB 7: Live Checker ----------------
with tab7:
    st.subheader("🔎 Type a Complaint - Get Instant Classification")
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
                new_reviews = [r for r in result if (r.get("userName"), r.get("content")) not in known_keys]

                if new_reviews:
                    st.success(f"Found {len(new_reviews)} new review(s) since last dataset snapshot!")
                    for r in new_reviews:
                        cats, urgency, churn = classify_live(r.get("content", ""))
                        with st.container(border=True):
                            st.markdown(f"🆕 **{r.get('userName', 'Unknown')}** (Rating: {r.get('score', '?')}⭐)")
                            st.write(r.get("content", ""))
                            st.markdown(f"**Detected Category:** {', '.join(cats)} | **Urgency:** {urgency} | **Churn Risk:** {'Yes ⚠️' if churn else 'No'}")
                else:
                    st.info("No new reviews found right now. Google Play may take some time to index a newly posted review - try again in a few minutes.")
            except Exception as e:
                st.error(f"Could not fetch reviews right now: {e}")

st.divider()
st.caption("Bulk classification powered by a pretrained zero-shot AI model (no training data required).")
