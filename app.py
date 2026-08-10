"""
Meezan Bank App - AI Complaint Analysis Dashboard

"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Meezan Bank - AI Complaint Analysis", layout="wide")

# ---------------------------------------------------------------
# Load data
# ---------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard_data.csv")
    return df

df = load_data()

# ---------------------------------------------------------------
# Header
# ---------------------------------------------------------------
st.title("📊 Meezan Bank App - AI-Powered Complaint Analysis")
st.markdown("Prototype dashboard: automatically classifies customer reviews and highlights priority complaints.")

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
    ax.bar(category_counts.index, category_counts.values, color="#2a78d6")
    ax.set_ylabel("Number of complaints")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig)

    st.caption("Note: This is a prototype AI classification (~75% accuracy). Rare categories have limited training examples.")

# ---------------- TAB 2: Bugs ----------------
with tab2:
    st.subheader("Bug Complaints - Detailed Breakdown")
    bug_df = df[df["bug_subcategory"] != ""]

    if len(bug_df) > 0:
        bug_counts = bug_df["bug_subcategory"].value_counts()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(bug_counts.index, bug_counts.values, color="#c0392b")
        ax.set_ylabel("Number of complaints")
        plt.xticks(rotation=25, ha="right")
        st.pyplot(fig)

        st.markdown("**🔑 Key Finding:** 'Side Menu Stuck' issue is the most repeated, identifiable bug.")

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
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(txn_counts.index, txn_counts.values, color="#e07b39")
        ax.set_ylabel("Number of complaints")
        plt.xticks(rotation=25, ha="right")
        st.pyplot(fig)

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
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.bar(ui_counts.index, ui_counts.values, color="#8e44ad")
        ax.set_ylabel("Number of complaints")
        plt.xticks(rotation=25, ha="right")
        st.pyplot(fig)

        st.markdown("**🔑 Key Finding:** Combined with Bugs tab, 'Side Menu Stuck' was mentioned 8 times total - including one device-specific case (Vivo Y20s, Android 10).")

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
        text_l = text.lower()
        matched = [cat for cat, kws in categories_keywords.items() if any(kw in text_l for kw in kws)]
        urgency = sum(1 for kw in urgency_keywords if kw in text_l)
        churn = any(kw in text_l for kw in churn_keywords) or ("years" in text_l and any(neg in text_l for neg in negative_words))
        return matched or ["Positive / Other"], urgency, churn

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
st.caption("classification powered by a pretrained zero-shot AI model (no training data required).")
