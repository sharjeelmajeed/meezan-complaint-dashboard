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
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview", "Bugs", "Transactions", "UI/UX", "Feedback", "Priority Complaints"
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

st.divider()
st.caption("Classification powered by a pretrained zero-shot AI model (no training data required).")
