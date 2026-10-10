import io
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="SpendWise | Smart Money Dashboard",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Styling ---------------------------------------
st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #f7f9fc 0%, #eef3f9 100%); }
    [data-testid="stSidebar"] { background: #101b33; }
    [data-testid="stSidebar"] * { color: #f3f6ff !important; }
    .hero {
        padding: 1.4rem 1.6rem; border-radius: 22px; color: white;
        background: linear-gradient(115deg, #14213d 0%, #244b76 58%, #397c88 100%);
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0; font-size: 2.15rem; }
    .hero p { margin: .45rem 0 0 0; color: #d9e8f6; font-size: 1rem; }
    .metric-card {
        background: white; padding: 1rem 1.15rem; border-radius: 16px;
        border: 1px solid #e3eaf2; box-shadow: 0 4px 16px rgba(24, 44, 76, .05);
        min-height: 112px;
    }
    .metric-label { color: #64748b; font-size: .88rem; margin-bottom: .35rem; }
    .metric-value { color: #172554; font-size: 1.7rem; font-weight: 750; }
    .metric-note { color: #64748b; font-size: .78rem; margin-top: .25rem; }
    .section-title { color: #172554; font-weight: 700; font-size: 1.12rem; margin: .2rem 0 .6rem 0; }
    div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

CATEGORIES = [
    "Housing", "Groceries", "Transport", "Dining", "Health",
    "Shopping", "Education", "Bills", "Entertainment", "Travel", "Income", "Other"
]
DEFAULT_BUDGETS = {
    "Housing": 650, "Groceries": 250, "Transport": 100, "Dining": 120,
    "Health": 80, "Shopping": 100, "Education": 100, "Bills": 120,
    "Entertainment": 80, "Travel": 150, "Other": 100,
}
COLORS = {
    "Housing": "#315c9b", "Groceries": "#3b9b83", "Transport": "#e4a64d",
    "Dining": "#d87964", "Health": "#8b78c6", "Shopping": "#d76e9b",
    "Education": "#4d9fce", "Bills": "#8b98a8", "Entertainment": "#b38a45",
    "Travel": "#3e9ea8", "Income": "#2f9e63", "Other": "#a3aab6"
}

def sample_data():
    """Create reproducible sample transactions for a demo."""
    rng = np.random.default_rng(24)
    end = date.today()
    start = end - timedelta(days=179)
    rows = []
    merchants = {
        "Housing": ["Rent", "Home supplies", "Maintenance"],
        "Groceries": ["Local market", "Supermarket", "Bakery"],
        "Transport": ["Bus pass", "Train ticket", "Fuel"],
        "Dining": ["Cafe", "Restaurant", "Takeaway"],
        "Health": ["Pharmacy", "Clinic", "Wellness"],
        "Shopping": ["Clothing", "Online store", "Bookshop"],
        "Education": ["Course fee", "Books", "Learning platform"],
        "Bills": ["Internet", "Phone", "Electricity"],
        "Entertainment": ["Cinema", "Streaming", "Museum"],
        "Travel": ["Hotel", "Train trip", "Flight"],
        "Income": ["Salary", "Tutoring", "Freelance work"],
        "Other": ["Gift", "Miscellaneous", "Household item"],
    }
    weights = np.array([.04, .17, .10, .14, .04, .08, .07, .09, .06, .04, .05, .12])
    for i in range(210):
        d = start + timedelta(days=int(rng.integers(0, 180)))
        cat = str(rng.choice(CATEGORIES, p=weights / weights.sum()))
        if cat == "Income":
            amount = float(rng.integers(250, 1500))
        elif cat == "Housing":
            amount = float(rng.integers(350, 850))
        else:
            amount = float(np.round(rng.uniform(5, 125), 2))
        rows.append({
            "Date": d.isoformat(),
            "Description": str(rng.choice(merchants[cat])),
            "Category": cat,
            "Amount": amount,
            "Type": "Income" if cat == "Income" else "Expense",
            "Payment Method": str(rng.choice(["Card", "Cash", "Bank transfer"])),
        })
    return pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)

def normalize_data(df):
    df = df.copy()
    required = {"Date", "Description", "Category", "Amount"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError("Missing required CSV columns: " + ", ".join(sorted(missing)))
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Description"] = df["Description"].fillna("Transaction").astype(str)
    df["Category"] = df["Category"].fillna("Other").astype(str)
    df = df.dropna(subset=["Date", "Amount"])
    df["Category"] = df["Category"].where(df["Category"].isin(CATEGORIES), "Other")
    if "Type" not in df.columns:
        df["Type"] = np.where(df["Category"].str.lower().eq("income"), "Income", "Expense")
    df["Type"] = df["Type"].astype(str).str.title()
    df["Type"] = np.where(df["Type"].eq("Income"), "Income", "Expense")
    if "Payment Method" not in df.columns:
        df["Payment Method"] = "Not specified"
    return df.sort_values("Date").reset_index(drop=True)

def euro(value):
    return f"€{value:,.2f}"

# ----------------------------- Sidebar ---------------------------------------
st.sidebar.markdown("## 💸 SpendWise")
st.sidebar.caption("Your money, made clearer.")
uploaded = st.sidebar.file_uploader("Upload your transactions (CSV)", type=["csv"])
if uploaded is not None:
    try:
        raw_df = normalize_data(pd.read_csv(uploaded))
        data_source = "Your uploaded data"
    except Exception as exc:
        st.sidebar.error(str(exc))
        raw_df = sample_data()
        raw_df = normalize_data(raw_df)
        data_source = "Sample data (upload could not be read)"
else:
    raw_df = normalize_data(sample_data())
    data_source = "Interactive demo data"

st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")
min_date = raw_df["Date"].min().date()
max_date = raw_df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
available_categories = sorted(raw_df["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Categories", available_categories, default=available_categories
)
currency = st.sidebar.selectbox("Display currency", ["EUR (€)", "USD ($)", "GBP (£)"], index=0)
currency_symbol = {"EUR (€)": "€", "USD ($)": "$", "GBP (£)": "£"}[currency]

def money(v):
    return f"{currency_symbol}{v:,.2f}"

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date = pd.Timestamp(min_date)
    end_date = pd.Timestamp(max_date)

df = raw_df[
    raw_df["Date"].between(start_date, end_date + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1))
    & raw_df["Category"].isin(selected_categories)
].copy()

income_df = df[df["Type"].eq("Income")]
expense_df = df[df["Type"].eq("Expense")]
total_income = float(income_df["Amount"].sum())
total_expenses = float(expense_df["Amount"].sum())
net_savings = total_income - total_expenses
savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0.0
daily_average = total_expenses / max((end_date - start_date).days + 1, 1)

# ----------------------------- Main view -------------------------------------
st.markdown("""
<div class="hero">
  <h1>SpendWise 💸</h1>
  <p>A smarter view of your spending — track patterns, check budgets, and make informed decisions.</p>
</div>
""", unsafe_allow_html=True)
st.caption(f"Data source: **{data_source}** · Demo data is fictional. Upload a CSV to analyze your own transactions.")

m1, m2, m3, m4 = st.columns(4)
metrics = [
    (m1, "TOTAL INCOME", money(total_income), "Money coming in"),
    (m2, "TOTAL SPENDING", money(total_expenses), "Money going out"),
    (m3, "NET BALANCE", money(net_savings), "Income minus spending"),
    (m4, "SAVINGS RATE", f"{savings_rate:.1f}%", "Net balance ÷ income"),
]
for col, label, value, note in metrics:
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
            unsafe_allow_html=True,
        )

st.write("")
left, right = st.columns([1.25, 1])
with left:
    st.markdown('<div class="section-title">Spending over time</div>', unsafe_allow_html=True)
    if expense_df.empty:
        st.info("No expense transactions match these filters.")
    else:
        daily = expense_df.assign(Period=expense_df["Date"].dt.to_period("W").dt.start_time)
        trend = daily.groupby("Period", as_index=False)["Amount"].sum()
        fig = px.area(trend, x="Period", y="Amount", markers=True)
        fig.update_traces(line_color="#397c88", fillcolor="rgba(57,124,136,0.18)")
        fig.update_layout(
            height=330, margin=dict(l=10, r=10, t=15, b=10),
            xaxis_title="", yaxis_title="Spending",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
with right:
    st.markdown('<div class="section-title">Where your money goes</div>', unsafe_allow_html=True)
    if expense_df.empty:
        st.info("No expense transactions match these filters.")
    else:
        by_cat = expense_df.groupby("Category", as_index=False)["Amount"].sum().sort_values("Amount", ascending=False)
        fig = px.pie(
            by_cat, values="Amount", names="Category", hole=.62,
            color="Category", color_discrete_map=COLORS,
        )
        fig.update_layout(
            height=330, margin=dict(l=5, r=5, t=15, b=5),
            legend=dict(orientation="h", yanchor="bottom", y=-.18, xanchor="center", x=.5),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(fig, use_container_width=True)

st.write("")
tab_budget, tab_insights, tab_transactions = st.tabs(["🎯 Budget planner", "💡 Spending insights", "🧾 Transactions"])

with tab_budget:
    st.markdown("#### Monthly category budgets")
    st.write("Adjust the example budgets in the sidebar panel below. Budget comparisons use the selected date range.")
    with st.expander("Edit category budgets", expanded=False):
        budget_cols = st.columns(3)
        budgets = {}
        expense_cats = [c for c in CATEGORIES if c != "Income"]
        for i, cat in enumerate(expense_cats):
            with budget_cols[i % 3]:
                budgets[cat] = st.number_input(
                    f"{cat} budget (€)", min_value=0.0, max_value=100000.0,
                    value=float(DEFAULT_BUDGETS.get(cat, 100)), step=10.0, key=f"budget_{cat}"
                )
    if "budgets" not in locals():
        budgets = DEFAULT_BUDGETS.copy()
    spent_by_cat = expense_df.groupby("Category")["Amount"].sum().to_dict()
    budget_rows = []
    days = max((end_date - start_date).days + 1, 1)
    months_equiv = max(days / 30.4375, 1 / 30.4375)
    for cat in [c for c in CATEGORIES if c != "Income"]:
        spent = float(spent_by_cat.get(cat, 0))
        budget = float(budgets.get(cat, DEFAULT_BUDGETS.get(cat, 100)))
        # Scale the monthly budget to the selected range.
        range_budget = budget * months_equiv
        ratio = (spent / range_budget) if range_budget else (1.0 if spent else 0.0)
        budget_rows.append({"Category": cat, "Spent": spent, "Budget": range_budget, "Used": ratio * 100})
    budget_df = pd.DataFrame(budget_rows).sort_values("Used", ascending=False)
    for _, row in budget_df.iterrows():
        a, b, c = st.columns([1.1, 2.4, 1])
        a.write(f"**{row['Category']}**")
        b.progress(min(max(float(row["Used"]) / 100, 0), 1))
        c.write(f"{money(row['Spent'])} / {money(row['Budget'])}")
    over = budget_df[budget_df["Spent"] > budget_df["Budget"]]
    if not over.empty:
        st.warning("Over budget: " + ", ".join(over["Category"].tolist()))
    else:
        st.success("No category is over its budget for this selected period.")

with tab_insights:
    st.markdown("#### Quick insights")
    if expense_df.empty:
        st.info("Add or select expense transactions to see insights.")
    else:
        top = expense_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        biggest = top.index[0]
        share = top.iloc[0] / total_expenses * 100 if total_expenses else 0
        st.info(f"**Largest spending category:** {biggest} accounts for {share:.1f}% of spending in this period.")
        st.info(f"**Average daily spending:** {money(daily_average)} across the selected dates.")
        if len(expense_df) >= 3:
            med = expense_df["Amount"].median()
            unusual = expense_df[expense_df["Amount"] > max(med * 3, med + 100)]
            if not unusual.empty:
                st.warning(f"**Potentially large transactions:** {len(unusual)} transaction(s) are much larger than your typical expense. Review them below.")
                st.dataframe(
                    unusual[["Date", "Description", "Category", "Amount"]]
                    .sort_values("Amount", ascending=False)
                    .assign(Date=lambda x: x["Date"].dt.strftime("%Y-%m-%d")),
                    use_container_width=True, hide_index=True
                )
            else:
                st.success("No unusually large expenses were flagged by the simple rule used in this demo.")
        st.caption("Insights are descriptive, not financial advice. Large-transaction flags use a simple heuristic, not an AI model.")

with tab_transactions:
    st.markdown("#### Filtered transactions")
    search = st.text_input("Search description", placeholder="e.g. groceries, train, salary")
    show = df.copy()
    if search.strip():
        show = show[show["Description"].str.contains(search.strip(), case=False, na=False)]
    display = show.sort_values("Date", ascending=False).copy()
    display["Date"] = display["Date"].dt.strftime("%Y-%m-%d")
    display["Amount"] = display["Amount"].map(money)
    st.dataframe(display, use_container_width=True, hide_index=True, height=350)
    csv_bytes = show.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered transactions (CSV)", data=csv_bytes,
                       file_name="spendwise_transactions.csv", mime="text/csv")

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#64748b;font-size:.85rem;'>"
    "Built with Python · Pandas · Plotly · Streamlit &nbsp;|&nbsp; "
    "A portfolio project for learning and personal insights</div>",
    unsafe_allow_html=True,
)
