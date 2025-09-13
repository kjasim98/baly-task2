import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from operator import attrgetter 

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Cohorts-Sheet1.csv")  # replace with your file
    df['order_date'] = pd.to_datetime(df['order_date'])
    return df

df = load_data()
df.info()
df["order_date"] = pd.to_datetime(df["order_date"])


# Find min and max
min_date = df["order_date"].min()
max_date = df["order_date"].max()

print("Earliest date:", min_date)
print("Latest date:", max_date)

df['order_month'] = df['order_date'].dt.to_period('M')
df['cohort'] = df.groupby('clientID')['order_month'].transform('min')

# Cohort index = how many periods since first order
df['period_number'] = (df['order_month'] - df['cohort']).apply(attrgetter('n'))

print(df.head())