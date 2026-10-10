# SpendWise — Smart Spending Dashboard 💸

A polished, interactive personal-finance dashboard built with Python. Explore spending trends, compare category budgets, spot unusually large transactions, and export filtered records.

## Why this project?
SpendWise demonstrates practical Python skills through data cleaning, analysis, interactive visualization, and a user-friendly interface. It is designed as a portfolio project and works with fictional demo data or a user's own CSV file.

## Features
- 📊 Key metrics: income, spending, net balance, and savings rate
- 📈 Interactive spending trends over time
- 🥧 Category breakdown chart
- 🎯 Editable category budgets and budget progress bars
- 💡 Descriptive insights and simple large-transaction flags
- 🔎 Searchable transaction table
- 📥 Upload your own CSV and download filtered results
- 🧪 Included sample data to try immediately

## Preview
Run the app locally to explore the interactive dashboard. The app generates fictional demo transactions automatically.

## Run locally
1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Open a terminal in the project folder and run:

```bash
python -m venv .venv
```

Activate the environment:
- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS/Linux: `source .venv/bin/activate`

Install dependencies and start the dashboard:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens in your browser. Upload `sample_transactions.csv` using the sidebar to try the CSV import feature.

## CSV format
Your file should contain these columns:

| Column | Description |
|---|---|
| `Date` | Date such as `2026-09-01` |
| `Description` | Transaction or merchant name |
| `Category` | Category such as Groceries, Housing, or Income |
| `Amount` | Positive numeric amount |
| `Type` | Optional; `Income` or `Expense` |
| `Payment Method` | Optional |

**Privacy:** Your data is processed by the app instance you run. Do not upload sensitive financial information to a public repository. The included sample data is fictional.

## Tech stack
- Python
- Pandas and NumPy
- Plotly
- Streamlit

## What I learned / demonstrated
- Data validation and cleaning
- Feature engineering and grouping by time periods
- Interactive charts and dashboard design
- CSV import/export
- Turning numerical analysis into understandable insights

## Limitations
This is an educational project, not a bank-connected service or financial-advice tool. Currency selection changes the displayed symbol only; it does not convert exchange rates. Budget values are illustrative and should be adjusted to suit the selected period.

## Future improvements
- Add a proper multi-currency conversion service
- Persist user budgets between sessions
- Add recurring-payment detection
- Add a forecasting model with uncertainty intervals
- Deploy a public demo using Streamlit Community Cloud

## Author
**Naila Aslam**  
Mathematics | Python | Computational Modelling | Data Visualization

GitHub: [nailaaslam2003](https://github.com/nailaaslam2003)
