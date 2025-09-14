# 📊 Cohort Retention Analysis - Baly Food Task (Part 2)

This is the **second task** implemented for the Baly Food Business Intelligence internship assignment. It analyzes customer retention by cohort and presents the data in a clean and interactive **heatmap dashboard** using Streamlit.

---

## 🎯 Objective

Build an interactive cohort analysis dashboard where Baly BI team members can:

- ✅ Filter customers by type (e.g., "A", "B", etc.)
- ✅ View monthly customer cohorts
- ✅ Track user retention by month after sign-up
- ✅ Visually interpret retention rates in a color-coded heatmap

---

## 🧱 Tech Stack

| Component     | Technology       |
|---------------|------------------|
| Web Framework | Streamlit        |
| Data Analysis | pandas           |
| Charting      | seaborn + matplotlib |
| Deployment    | Streamlit Cloud  |

---

## 📂 Project Structure

```
baly-cohorts/
├── app.py                # Streamlit app logic
├── Cohorts-Sheet1.csv    # Input dataset with client activity
├── requirements.txt      # Dependencies for deployment
├── .gitignore            # Ignore venv, cache, etc.
└── README.md             # This documentation
```

---

## 🔎 Dataset Example

Sample structure of `Cohorts-Sheet1.csv`:

| clientID | order_date | client_type |
|----------|------------|--------------|
| 101      | 2024-01-12 | A            |
| 102      | 2024-02-04 | B            |

---

## 📊 Key Features

### 🔄 Filtering
- Use sidebar to select a specific client type or "All"

### 📅 Cohort Calculation
- `cohort`: first month each client placed an order
- `period_number`: months after cohort start

### 🔥 Heatmap Visualization
- Y-axis: cohort month
- X-axis: months after signup
- Color intensity: retention %
- First column shows absolute number of users in each cohort

### 🎨 Chart Options
- Seaborn heatmap
- Blue gradient from 0% to 100%
- Annotated with raw numbers and percentages

---

## 🚀 How to Run Locally

1. Clone the repo:
```bash
git clone https://github.com/kjasim98/baly-cohorts.git
cd baly-cohorts
```

2. (Optional) Create a virtual environment:
```bash
python3 -m venv streamlit_env
source streamlit_env/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app:
```bash
streamlit run app.py
```

---

## 🌐 Live Demo
[View on Streamlit Cloud](https://kjasim98-baly-task2-app-clcone.streamlit.app/)

---


## 💬 Contact
- Email: [kjasim98@gmail.com](mailto:kjasim98@gmail.com)
- GitHub: [kjasim98](https://github.com/kjasim98)

---

## ✅ Status
Submitted as the second task for Baly’s internship technical evaluation.

---