"""
Meezan Bank App - AI Complaint Analysis Dashboard

"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

st.set_page_config(page_title="Meezan Bank - AI Complaint Analysis", layout="wide")

# ---------------------------------------------------------------
# Design tokens - dark theme, vivid accents for glow/contrast
# ---------------------------------------------------------------
BG = "#0A0B0D"
CARD_BG = "#15171A"
BORDER = "#262930"
GREEN = "#22C55E"
GREEN_DIM = "#16A34A"
PURPLE = "#A855F7"
RED = "#F87171"
TEXT_PRIMARY = "#F5F5F5"
TEXT_MUTED = "#9CA3AF"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {BG};
    color: {TEXT_PRIMARY};
}}
[data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
    background-color: {BG} !important;
}}

/* Custom scrollbar */
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: {BG}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 10px; }}
::-webkit-scrollbar-thumb:hover {{ background: {GREEN}; }}
* {{ scrollbar-width: thin; scrollbar-color: {BORDER} {BG}; }}

/* Hero */
.hero-wrap {{
    padding: 1rem 0 1.5rem 0;
}}

.hero-wrap > * {{
    position: relative;
    z-index: 1;
}}
.live-badge {{
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    color: {TEXT_MUTED};
    font-weight: 600;
    margin-bottom: 0.9rem;
}}
.live-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: {GREEN};
    animation: pulse 1.8s infinite;
}}
@keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 rgba(34,197,94,0.5); }}
    70% {{ box-shadow: 0 0 0 8px rgba(34,197,94,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(34,197,94,0); }}
}}

.eyebrow {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: {GREEN};
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}}
.hero-title {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 2.6rem;
    line-height: 1.15;
    color: {TEXT_PRIMARY};
    margin: 0;
}}
.hero-title .glow {{
    color: {GREEN};
    text-shadow: 0 0 28px rgba(34,197,94,0.45);
}}
.hero-subtitle {{
    font-size: 1rem;
    color: {TEXT_MUTED};
    margin-top: 0.9rem;
    max-width: 640px;
}}

/* Section headers */
h2, h3, .stMarkdown h5 {{
    font-family: 'Space Grotesk', sans-serif;
    color: {TEXT_PRIMARY};
}}

/* Tabs */
button[data-baseweb="tab"] {{
    font-weight: 600;
    color: {TEXT_MUTED};
}}
button[data-baseweb="tab"][aria-selected="true"] {{
    color: {GREEN} !important;
    border-bottom-color: {GREEN} !important;
}}

/* Buttons */
.stButton>button {{
    background-color: {GREEN};
    color: #0A0B0D;
    border: none;
    border-radius: 6px;
    font-weight: 700;
}}
.stButton>button:hover {{
    background-color: {GREEN_DIM};
    color: white;
}}

/* Key finding callout */
.key-finding {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-left: 3px solid {PURPLE};
    border-radius: 8px;
    padding: 0.8rem 1.1rem;
    font-size: 0.92rem;
    color: {TEXT_MUTED};
}}
.key-finding b {{
    color: {TEXT_PRIMARY};
}}

/* Priority containers */
[data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: {CARD_BG};
    border-color: {BORDER} !important;
}}

hr {{
    border-color: {BORDER};
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
# Chart helper (dark-theme Plotly bar chart)
# ---------------------------------------------------------------
def interactive_bar_chart(counts_series, color):
    chart_df = counts_series.reset_index()
    chart_df.columns = ["category", "count"]
    fig = px.bar(chart_df, x="category", y="count", text="count", color_discrete_sequence=[color])
    fig.update_traces(textposition="outside", hovertemplate="%{x}: %{y} complaints<extra></extra>",
                       textfont=dict(color=TEXT_PRIMARY))
    fig.update_layout(
        xaxis_title="", yaxis_title="Number of complaints", showlegend=False,
        margin=dict(t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_MUTED),
        xaxis=dict(gridcolor=BORDER), yaxis=dict(gridcolor=BORDER),
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------
# KPI row - rendered as a single HTML component with count-up animation and hover-lift
# ---------------------------------------------------------------
def render_kpi_row(items):
    cards_html = ""
    for item in items:
        accent_class = "purple" if item.get("accent") == "purple" else "green"
        if item["numeric"]:
            suffix = item.get("suffix", "")
            value_html = (
                f'<span class="count" data-target="{item["value"]}" data-decimals="{item["decimals"]}">0</span>{suffix}'
            )
        else:
            value_html = f'{item["value"]}'
        cards_html += f'''
        <div class="kpi-card {accent_class}">
            <p class="kpi-label">{item["label"]}</p>
            <p class="kpi-value">{value_html}</p>
        </div>
        '''

    template = """
    <style>
    * { box-sizing: border-box; }
    body { margin: 0; font-family: 'Inter', sans-serif; background: transparent; }
    .kpi-row { display: flex; gap: 12px; }
    .kpi-card {
        flex: 1; background-color: @@CARD_BG@@; border: 1px solid @@BORDER@@;
        border-top: 2px solid @@GREEN@@; border-radius: 10px; padding: 14px 16px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card.purple { border-top-color: @@PURPLE@@; }
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.45);
    }
    .kpi-label {
        font-size: 11px; color: @@TEXT_MUTED@@; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.06em; margin: 0;
        font-family: Inter, sans-serif;
    }
    .kpi-value {
        font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 700;
        color: @@TEXT_PRIMARY@@; margin: 6px 0 0 0;
    }
    </style>
    <div class="kpi-row">
    @@CARDS@@
    </div>
    <script>
    document.querySelectorAll('.count').forEach(function(el){
        var target = parseFloat(el.getAttribute('data-target'));
        var decimals = parseInt(el.getAttribute('data-decimals'));
        var duration = 900;
        var startTime = null;
        function step(timestamp){
            if(!startTime) { startTime = timestamp; }
            var progress = Math.min((timestamp - startTime) / duration, 1);
            var current = target * progress;
            el.textContent = current.toFixed(decimals);
            if(progress < 1){ requestAnimationFrame(step); } else { el.textContent = target.toFixed(decimals); }
        }
        requestAnimationFrame(step);
    });
    </script>
    """
    template = template.replace("@@CARD_BG@@", CARD_BG)
    template = template.replace("@@BORDER@@", BORDER)
    template = template.replace("@@GREEN@@", GREEN)
    template = template.replace("@@PURPLE@@", PURPLE)
    template = template.replace("@@TEXT_MUTED@@", TEXT_MUTED)
    template = template.replace("@@TEXT_PRIMARY@@", TEXT_PRIMARY)
    template = template.replace("@@CARDS@@", cards_html)
    return template

# ---------------------------------------------------------------
# Header / Hero
# ---------------------------------------------------------------
st.markdown(f"""
<div class="hero-wrap">
    <div class="live-badge"><span class="live-dot"></span>Live Prototype</div>
    <div class="eyebrow">AI-Powered Complaint Analysis</div>
    <h1 class="hero-title">Meezan Bank App.<br><span class="glow">Complaints, prioritized.</span></h1>
    <p class="hero-subtitle">A prototype dashboard that automatically classifies customer reviews and surfaces the complaints that matter most — before they turn into churn.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# KPI values (computed dynamically from the data - no hardcoded numbers)
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

kpi_items = [
    {"label": "Total Reviews", "value": total_reviews, "numeric": True, "decimals": 0, "accent": "green"},
    {"label": "Complaint Rate", "value": complaint_rate, "numeric": True, "decimals": 1, "suffix": "%", "accent": "green"},
    {"label": "Churn Risk", "value": churn_count, "numeric": True, "decimals": 0, "accent": "purple"},
    {"label": "Avg Rating", "value": avg_rating, "numeric": True, "decimals": 2, "accent": "green"},
    {"label": "Top Issue", "value": top_category, "numeric": False, "accent": "purple"},
    {"label": "'Side Menu Stuck' Mentions", "value": int(side_menu_count), "numeric": True, "decimals": 0, "accent": "green"},
]

components.html(render_kpi_row(kpi_items), height=140)

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
        labels=donut_df["type"], values=donut_df["count"], hole=0.6,
        marker=dict(colors=[GREEN, PURPLE], line=dict(color=BG, width=2)),
        textinfo="label+percent",
        textfont=dict(color=TEXT_PRIMARY),
    )])
    fig_donut.update_layout(
        margin=dict(t=10, b=10, l=10, r=10), height=280, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_donut, use_container_width=True)
with note_col:
    st.markdown("##### At a glance")
    st.markdown(
        f"<span style='color:{TEXT_MUTED}'>Out of <b style='color:{TEXT_PRIMARY}'>{total_reviews}</b> reviews analyzed, "
        f"<b style='color:{TEXT_PRIMARY}'>{complaint_count} ({complaint_rate}%)</b> represent genuine complaints. "
        f"<b style='color:{TEXT_PRIMARY}'>{churn_count}</b> of these show signs of churn risk or high urgency — these are the ones that would otherwise "
        f"sit in a FIFO queue with no priority. The most common identifiable issue across the dataset is "
        f"<b style='color:{TEXT_PRIMARY}'>'Side Menu Stuck'</b>, mentioned <b style='color:{TEXT_PRIMARY}'>{int(side_menu_count)} times</b> across Bug and UI/Design reviews.</span>",
        unsafe_allow_html=True
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
    interactive_bar_chart(category_counts, GREEN)
    st.caption("Note: This is a prototype AI classification (~75% accuracy). Rare categories have limited training examples.")

# ---------------- TAB 2: Bugs ----------------
with tab2:
    st.subheader("Bug Complaints - Detailed Breakdown")
    bug_df = df[df["bug_subcategory"] != ""]

    if len(bug_df) > 0:
        bug_counts = bug_df["bug_subcategory"].value_counts()
        interactive_bar_chart(bug_counts, PURPLE)
        st.markdown('<div class="key-finding"><b>Key Finding:</b> \'Side Menu Stuck\' issue is the most repeated, identifiable bug.</div>', unsafe_allow_html=True)

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
        interactive_bar_chart(txn_counts, GREEN_DIM)
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
        interactive_bar_chart(ui_counts, PURPLE)
        st.markdown('<div class="key-finding"><b>Key Finding:</b> Combined with Bugs tab, \'Side Menu Stuck\' was mentioned 8 times total - including one device-specific case (Vivo Y20s, Android 10).</div>', unsafe_allow_html=True)

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
    st.subheader("High Priority Complaints (Urgency or Churn Risk)")
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
    st.subheader("Type a Complaint - Get Instant Classification")
    st.caption("Note: This demo uses a fast keyword-based classifier (lightweight, works instantly on the web). The full AI model used for the bulk analysis above is heavier and runs offline.")

    user_input = st.text_area("Type a customer complaint here:", height=100,
                               placeholder="e.g. my payment failed and amount got deducted but no refund")

    if st.button("Classify Complaint", type="primary"):
        if user_input.strip():
            cats, urgency, churn = classify_live(user_input)
            st.success(f"**Detected Category:** {', '.join(cats)}")
            col_a, col_b = st.columns(2)
            col_a.metric("Urgency Score", urgency)
            col_b.metric("Churn Risk", "Yes" if churn else "No")
        else:
            st.warning("Please type a complaint first.")

# ---------------- TAB 8: Live Play Store Monitor ----------------
with tab8:
    st.subheader("Check Play Store for New Reviews")
    st.caption("Click the button to fetch the latest reviews directly from Google Play and classify any new ones instantly.")

    known_keys = set((r, t) for r, t in zip(df["reviewer"], df["text"]))

    if st.button("Check for New Reviews Now", type="primary"):
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
                            st.markdown(f"**{r.get('userName', 'Unknown')}** (Rating: {r.get('score', '?')})")
                            st.write(r.get("content", ""))
                            st.markdown(f"**Detected Category:** {', '.join(cats)} | **Urgency:** {urgency} | **Churn Risk:** {'Yes' if churn else 'No'}")
                else:
                    st.info("No new reviews found right now. Google Play may take some time to index a newly posted review - try again in a few minutes.")
            except Exception as e:
                st.error(f"Could not fetch reviews right now: {e}")

st.divider()
st.caption("Bulk classification powered by a pretrained zero-shot AI model (no training data required).")
