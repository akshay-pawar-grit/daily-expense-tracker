import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Database setup
DB_PATH = "expenses.db"
EXCEL_PATH = "daily_expenses.xlsx"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            DATE DATE NOT NULL,
            EXPENSE_CATEGORY TEXT NOT NULL,
            EXPENSE_NAME TEXT NOT NULL,
            AMOUNT REAL NOT NULL,
            COMMENT TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_expense(expense_date, category, name, amount, comment):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (DATE, EXPENSE_CATEGORY, EXPENSE_NAME, AMOUNT, COMMENT) VALUES (?, ?, ?, ?, ?)",
        (expense_date, category, name, amount, comment)
    )
    conn.commit()
    conn.close()
    sync_to_excel()


def get_all_expenses():
    conn = get_connection()
    df = pd.read_sql_query("SELECT id, DATE, EXPENSE_CATEGORY, EXPENSE_NAME, AMOUNT, COMMENT FROM expenses ORDER BY id DESC", conn)
    conn.close()
    return df


def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    sync_to_excel()


def sync_to_excel():
    """Sync all expenses from database to Excel file."""
    df = get_all_expenses()
    # Export only the 5 main columns (exclude id)
    export_df = df[["DATE", "EXPENSE_CATEGORY", "EXPENSE_NAME", "AMOUNT", "COMMENT"]]
    export_df.to_excel(EXCEL_PATH, index=False, sheet_name="Expenses")


def get_categories():
    return [
        "Food & Dining",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Health & Medical",
        "Education",
        "Travel",
        "Groceries",
        "Personal Care",
        "Other"
    ]


# Initialize database and sync to Excel
init_db()
sync_to_excel()

# App UI
st.set_page_config(page_title="Finance Tracker", page_icon="💰", layout="wide")
st.title("💰 Personal Finance Tracker")

# Initialize session state for selected category
if "selected_category" not in st.session_state:
    st.session_state.selected_category = get_categories()[0]

# Sidebar for adding new expense
st.sidebar.header("Add New Expense")

# Quick category buttons
st.sidebar.subheader("Quick Category Select")
categories = get_categories()

# Create button grid (3 columns)
cols = st.sidebar.columns(3)
for i, cat in enumerate(categories):
    col_idx = i % 3
    with cols[col_idx]:
        if st.button(cat.split(" ")[0], key=f"cat_{i}", width="stretch"):
            st.session_state.selected_category = cat

st.sidebar.markdown(f"**Selected:** {st.session_state.selected_category}")
st.sidebar.divider()

with st.sidebar.form("expense_form", clear_on_submit=True):
    expense_date = st.date_input("Date", value=date.today())
    expense_category = st.selectbox(
        "Category",
        get_categories(),
        index=get_categories().index(st.session_state.selected_category)
    )
    expense_name = st.text_input("Expense Name")
    amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
    comment = st.text_area("Comment (optional)")

    submitted = st.form_submit_button("Add Expense", type="primary")

    if submitted:
        if expense_name and amount > 0:
            add_expense(expense_date, expense_category, expense_name, amount, comment)
            st.success("Expense added successfully!")
        else:
            st.error("Please enter expense name and amount greater than 0")

# Main content area
tab1, tab2 = st.tabs(["📊 Dashboard", "📋 All Expenses"])

with tab1:
    expenses_df = get_all_expenses()

    if not expenses_df.empty:
        col1, col2, col3 = st.columns(3)

        with col1:
            total_expenses = expenses_df["AMOUNT"].sum()
            st.metric("Total Expenses", f"₹{total_expenses:,.2f}")

        with col2:
            avg_expense = expenses_df["AMOUNT"].mean()
            st.metric("Average Expense", f"₹{avg_expense:,.2f}")

        with col3:
            num_transactions = len(expenses_df)
            st.metric("Total Transactions", num_transactions)

        st.subheader("Expenses by Category")
        category_totals = expenses_df.groupby("EXPENSE_CATEGORY")["AMOUNT"].sum().sort_values(ascending=False)
        st.bar_chart(category_totals)

        st.subheader("Recent Expenses")
        st.dataframe(
            expenses_df.head(10)[["DATE", "EXPENSE_CATEGORY", "EXPENSE_NAME", "AMOUNT", "COMMENT"]],
            width="stretch",
            hide_index=True
        )
    else:
        st.info("No expenses recorded yet. Add your first expense using the sidebar!")

with tab2:
    expenses_df = get_all_expenses()

    if not expenses_df.empty:
        st.subheader("All Expenses")

        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.multiselect(
                "Filter by Category",
                options=get_categories(),
                default=[]
            )
        with col2:
            date_range = st.date_input(
                "Filter by Date Range",
                value=[],
                key="date_filter"
            )

        filtered_df = expenses_df.copy()

        if filter_category:
            filtered_df = filtered_df[filtered_df["EXPENSE_CATEGORY"].isin(filter_category)]

        if len(date_range) == 2:
            filtered_df = filtered_df[
                (pd.to_datetime(filtered_df["DATE"]) >= pd.to_datetime(date_range[0])) &
                (pd.to_datetime(filtered_df["DATE"]) <= pd.to_datetime(date_range[1]))
            ]

        st.dataframe(
            filtered_df[["DATE", "EXPENSE_CATEGORY", "EXPENSE_NAME", "AMOUNT", "COMMENT"]],
            width="stretch",
            hide_index=True
        )

        # Delete expense section
        st.subheader("Delete Expense")
        if not filtered_df.empty:
            expense_to_delete = st.selectbox(
                "Select expense to delete",
                options=filtered_df["id"].tolist(),
                format_func=lambda x: f"{filtered_df[filtered_df['id']==x]['DATE'].values[0]} - {filtered_df[filtered_df['id']==x]['EXPENSE_NAME'].values[0]} - ₹{filtered_df[filtered_df['id']==x]['AMOUNT'].values[0]:.2f}"
            )

            if st.button("Delete Selected Expense", type="secondary"):
                delete_expense(expense_to_delete)
                st.success("Expense deleted!")
                st.rerun()
    else:
        st.info("No expenses recorded yet.")
