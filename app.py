import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from operator import attrgetter

st.set_page_config(page_title="Cohorts Analysis", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("Cohorts-Sheet1.csv")
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

df = load_data()

# ---------------------------
# Sidebar filter
# ---------------------------
client_types = df["client_type"].unique().tolist()
client_types.insert(0, "All")  # add "All" at the top
selected_type = st.sidebar.selectbox("Select Client Type", client_types)

if selected_type != "All":
    df = df[df["client_type"] == selected_type]

# ---------------------------
# Explanation message
# ---------------------------
st.info(
    "📌 While exploring the data, I noticed that no acquisitions occurred after **2024-03-18**. "
    "So the best way to analyze retention is to cut the period to the **first three months only** "
    "and build **weekly cohorts** instead of monthly."
)


# ---------------------------
# Toggle for updated weekly version (<= 2024-05-01)
# ---------------------------
use_weekly = st.toggle("Show UPDATED version (≤ 2024-03-17, weekly cohorts)")

if use_weekly:
    # Filter rows to keep only dates on/before 2024-05-01
    df_view = df[df["order_date"] <= pd.Timestamp("2024-03-17")].copy()

    # Weekly cohorts
    df_view["order_period"] = df_view["order_date"].dt.to_period("W-SUN")
    df_view["cohort"] = df_view.groupby("clientID")["order_period"].transform("min")
    df_view["period_number"] = (df_view["order_period"] - df_view["cohort"]).apply(attrgetter("n"))

    title_text = "Cohort Retention Heatmap (WEEKLY, ≤ 2024-03-17)"
    xlabel_text = "Retention rate by weeks after signup"
else:
    # Original monthly logic (unchanged)
    df_view = df.copy()
    df_view["order_period"] = df_view["order_date"].dt.to_period("M")  # month of each order
    df_view["cohort"] = df_view.groupby("clientID")["order_period"].transform("min")  # first month per client
    df_view["period_number"] = (df_view["order_period"] - df_view["cohort"]).apply(attrgetter("n"))  # months since first order

    title_text = "Cohort Retention Heatmap (MONTHLY)"
    xlabel_text = "Retention rate by months after signup"

# ---------------------------
# Build cohort table: unique clients by (cohort, period_number)
# ---------------------------
cohort_data = (
    df_view.groupby(["cohort", "period_number"])["clientID"]
           .nunique()
           .reset_index()
)

cohort_table = cohort_data.pivot(index="cohort", columns="period_number", values="clientID")

# Cohort sizes (first column) and retention matrix
cohort_sizes = cohort_table.iloc[:, 0] if cohort_table.shape[1] > 0 else pd.Series(dtype=float)
retention = cohort_table.divide(cohort_sizes, axis=0)

# Set first column to 0 so the color scale isn’t dominated by the cohort-size column
if retention.shape[1] > 0:
    retention.iloc[:, 0] = 0
    # Rename the first column label from 0 -> "New User" if 0 exists
    if 0 in retention.columns:
        retention = retention.rename(columns={0: "New User"})

# Copy for coloring/masking
color_mat = retention.copy()
mask = color_mat.isnull()

# ---------------------------
# Heatmap
# ---------------------------
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(
    color_mat,
    annot=True,
    fmt="",
    cmap="Blues",
    vmin=0, vmax=1,            # lock color scale at 0–100%
    ax=ax,
    annot_kws={"color": "black"},
    mask=mask,
    cbar_kws={"label": "Retention %"}
)

# Overwrite annotation text:
# - First visible column shows raw cohort size
# - Other columns show percentages
vals_for_pct = cohort_table.divide(cohort_sizes, axis=0)

for text in ax.texts:
    # Convert heatmap text positions to integer row/col indices
    col = int(round(text.get_position()[0] - 0.5))
    row = int(round(text.get_position()[1] - 0.5))

    # Bounds guard (can happen if some rows/cols are masked)
    if row < 0 or row >= cohort_table.shape[0]:
        continue
    if col < 0 or col >= cohort_table.shape[1]:
        # If we renamed the first column to "New User", its underlying data is still column 0 in cohort_table/vals_for_pct
        continue

    if col == 0:
        val = cohort_sizes.iloc[row] if not pd.isna(cohort_sizes.iloc[row]) else None
        text.set_text("" if val is None else f"{int(val)}")
    else:
        val = vals_for_pct.iloc[row, col]
        text.set_text("" if pd.isna(val) else f"{val:.0%}")

# ---------------------------
# Titles and labels
# ---------------------------
ax.set_title(title_text, pad=30)
ax.set_ylabel("Cohort")
ax.set_xlabel(xlabel_text)
ax.xaxis.tick_top()
ax.xaxis.set_label_position("top")

st.pyplot(fig)