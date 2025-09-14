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
client_types.insert(0, "All")   # add "All" at the top of the list

selected_type = st.sidebar.selectbox("Select Client Type", client_types)

if selected_type != "All":
    df = df[df["client_type"] == selected_type]

# ---------------------------
# Cohort preparation
# ---------------------------
df["order_month"] = df["order_date"].dt.to_period("M")              # month of each order
df["cohort"] = df.groupby("clientID")["order_month"].transform("min")  # first month per client
df["period_number"] = (df["order_month"] - df["cohort"]).apply(attrgetter("n"))  # months since first order

# Build cohort table: number of unique clients per (cohort, period)
cohort_data = (
    df.groupby(["cohort", "period_number"])["clientID"]
      .nunique()
      .reset_index()
)
cohort_table = cohort_data.pivot(index="cohort", columns="period_number", values="clientID")

cohort_sizes = cohort_table.iloc[:, 0]          # cohort sizes (raw counts)
retention = cohort_table.divide(cohort_sizes, axis=0)  # convert to retention rates
retention.iloc[:, 0] = 0                      # set first column to 1.0 so it won’t affect color scale

retention.rename(columns={0: "New User"}, inplace=True) #set the first columen lable to ( New User ) insted of 0
color_mat = retention.copy()
mask = color_mat.isnull()

# ---------------------------
# Heatmap
# ---------------------------
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(
    color_mat,
    annot=True,              # add annotations (will be customized below)
    fmt="",                  # keep blank; we’ll overwrite text
    cmap="Blues",
    vmin=0, vmax=1,          # lock color scale at 0–100%
    ax=ax,
    annot_kws={"color": "black"},
    mask=mask,
    cbar_kws={"label": "Retention %"}
)

# Overwrite annotations:
# - First column shows cohort size (raw number)
# - Other columns show percentages
vals_for_pct = cohort_table.divide(cohort_sizes, axis=0)

for text in ax.texts:
    col = int(round(text.get_position()[0] - 0.5))
    row = int(round(text.get_position()[1] - 0.5))

    if col == 0:
        val = cohort_sizes.iloc[row]             # raw count
        text.set_text(f"{int(val)}")
    else:
        val = vals_for_pct.iloc[row, col]        # percentage
        text.set_text("" if pd.isna(val) else f"{val:.0%}")

# ---------------------------
# Titles and labels
# ---------------------------
ax.set_title("Cohort Retention Heatmap", pad=30)
ax.set_ylabel("Cohort")
ax.set_xlabel("Retention rate by months after signup")
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')

st.pyplot(fig)