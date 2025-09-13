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
# Sidebar filter with "All"
# ---------------------------
client_types = df["client_type"].unique().tolist()
client_types.insert(0, "All")   # add option at top

selected_type = st.sidebar.selectbox("Select Client Type", client_types)

if selected_type != "All":
    df = df[df["client_type"] == selected_type]

# ---------------------------
# Cohort Preparation
# ---------------------------
df["order_month"] = df["order_date"].dt.to_period("M")
df["cohort"] = df.groupby("clientID")["order_month"].transform("min")
df["period_number"] = (df["order_month"] - df["cohort"]).apply(attrgetter("n"))

# Pivot = counts of unique customers
cohort_data = (
    df.groupby(["cohort", "period_number"])["clientID"]
      .nunique()
      .reset_index()
)
cohort_table = cohort_data.pivot(index="cohort", columns="period_number", values="clientID")

# # Normalize ALL columns (first column = 100%)
# new_cohort_table = cohort_table.divide(cohort_table.iloc[:, 0], axis=0)

# # ---------------------------
# # Plot
# # ---------------------------
# title_suffix = f"{selected_type} clients" if selected_type != "All" else "All clients"
# st.title("📊 Cohorts Analysis (Normalized)")
# st.write(f"Retention analysis for **{title_suffix}**")
# # new_cohort_table = new_cohort_table.fillna(0)


# fig, ax = plt.subplots(figsize=(12, 6))
# sns.heatmap(
#     new_cohort_table,
#     annot=True,
#     fmt=".0%",
#     cmap="Blues",
#     ax=ax,
#     annot_kws={"color": "black"},      # make numbers always black
#     mask=new_cohort_table.isnull()     # hide NaN cells
# )

# # Titles and labels
# ax.set_title("Cohort Retention Heatmap", pad=30)
# ax.set_ylabel("Cohort (Signup Month)")

# # Put months (CohortIndex) on top
# ax.set_xlabel("Periods after first order")
# ax.xaxis.tick_top()
# ax.xaxis.set_label_position('top')

# st.pyplot(fig)
# ---------------------------
# Cohort Table
# ---------------------------
# --- Build a % matrix only for color, and lock the color scale ---
cohort_sizes = cohort_table.iloc[:, 0]          # raw counts for col 0
retention = cohort_table.divide(cohort_sizes, axis=0)  # 0..1 for all cols
retention.iloc[:, 0] = 1.0                      # make col 0 a constant (won't affect cbar)

retention.rename(columns={0: "New User"}, inplace=True)
color_mat = retention.copy()
mask = color_mat.isnull()

# Rename the first column header
# vals_for_pct.rename(columns={0: "User Count"}, inplace=True)

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(
    color_mat,
    annot=True,              # we'll overwrite the texts next
    fmt="",                  # blank for now
    cmap="Blues",
    vmin=0, vmax=1,          # lock colorbar to 0–100%
    ax=ax,
    annot_kws={"color": "black"},
    mask=mask,
    cbar_kws={"label": "Retention %"}
)

# Overwrite annotation texts:
#   - col 0: show integer counts
#   - other cols: show percentages
# We need access to the underlying numeric table for proper values.
vals_for_pct = cohort_table.divide(cohort_sizes, axis=0)

for text in ax.texts:
    # text positions are centered on 0.5, 1.5, ...
    col = int(round(text.get_position()[0] - 0.5))
    row = int(round(text.get_position()[1] - 0.5))

    if col == 0:
        # raw counts
        val = cohort_sizes.iloc[row]
        text.set_text(f"{int(val)}")
    else:
        # percentage from vals_for_pct (guard NaNs)
        val = vals_for_pct.iloc[row, col]
        text.set_text("" if pd.isna(val) else f"{val:.0%}")

# Titles and labels
ax.set_title("Cohort Retention Heatmap", pad=30)
ax.set_ylabel("Cohort")
ax.set_xlabel("Retention rate by months after signup")
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

st.pyplot(fig)