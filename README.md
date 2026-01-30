# Personal Finance Tracker

A simple expense tracking application built with Streamlit. Track your daily expenses, view spending patterns by category, and export data to Excel.

## Features

- Add expenses with date, category, name, amount, and comments
- Quick category selection buttons for faster entry
- Dashboard with total/average expenses and category breakdown chart
- Filter expenses by category and date range
- Delete expenses
- Automatic sync to SQLite database and Excel file

## Requirements

- Python 3.9+
- pip

## Installation

1. Clone or download this repository

2. Create and activate a virtual environment:
   ```bash
   # Create virtual environment
   python3 -m venv .venv

   # Activate virtual environment
   # On macOS/Linux:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

```bash
python3 -m streamlit run app.py
```

The app will open in your browser at **http://localhost:8501**

To stop the app, press `Ctrl + C` in the terminal.

To deactivate the virtual environment when done:
```bash
deactivate
```

## Data Storage

- **expenses.db** - SQLite database (primary storage)
- **daily_expenses.xlsx** - Excel file with columns: DATE, EXPENSE_CATEGORY, EXPENSE_NAME, AMOUNT, COMMENT
