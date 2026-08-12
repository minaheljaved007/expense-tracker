"""
main.py
-------
Streamlit web interface for the Expense Tracker.

The calculation/state logic lives in tracker_logic.py.
This file is only responsible for the web UI.

Run locally:
    streamlit run main.py
"""

import streamlit as st

from tracker_logic import ExpenseTracker, InvalidExpenseError


# ---------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="centered",
)


# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

CATEGORIES = [
    "General",
    "Food",
    "Transport",
    "Bills",
    "Shopping",
    "Health",
    "Entertainment",
    "Other",
]


# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------

# Streamlit reruns this file whenever the user interacts with the UI.
# Therefore, the ExpenseTracker object must live in session_state.
if "tracker" not in st.session_state:
    st.session_state.tracker = ExpenseTracker()

tracker = st.session_state.tracker


# ---------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #777;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #ddd;
            text-align: center;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------

st.markdown(
    '<div class="main-title">💰 Expense Tracker</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">Track, manage, and understand your expenses.</div>',
    unsafe_allow_html=True,
)

st.divider()


# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Total Spent",
        f"${tracker.total:,.2f}",
    )

with col2:
    count = tracker.count()
    st.metric(
        "Transactions",
        count,
    )

with col3:
    st.metric(
        "Average",
        f"${tracker.average():,.2f}",
    )


st.divider()


# ---------------------------------------------------------------------
# Add expense
# ---------------------------------------------------------------------

st.subheader("➕ Add an Expense")

with st.form("add_expense_form", clear_on_submit=True):

    col1, col2 = st.columns([2, 1])

    with col1:
        amount = st.text_input(
            "Amount",
            placeholder="e.g. 250 or 1,250.50",
        )

    with col2:
        category = st.selectbox(
            "Category",
            CATEGORIES,
        )

    note = st.text_input(
        "Note (optional)",
        placeholder="e.g. Groceries at the market",
    )

    submitted = st.form_submit_button(
        "Add Expense",
        use_container_width=True,
    )

    if submitted:

        try:
            tracker.add_expense(
                raw_amount=amount,
                category=category,
                note=note,
            )

            st.success("Expense added successfully!")

            # Rerun so all metrics/history update immediately.
            st.rerun()

        except InvalidExpenseError as error:
            st.error(str(error))


st.divider()


# ---------------------------------------------------------------------
# Expense history
# ---------------------------------------------------------------------

st.subheader("📋 Expense History")

if not tracker.expenses:

    st.info("No expenses yet — add your first expense above.")

else:

    # Display newest expenses first.
    for expense in reversed(tracker.expenses):

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            if expense.note:
                st.write(
                    f"**{expense.category}** — {expense.note}"
                )
            else:
                st.write(
                    f"**{expense.category}**"
                )

            st.caption(expense.timestamp)

        with col2:
            st.write(
                f"**${expense.amount:,.2f}**"
            )

        with col3:

            if st.button(
                "🗑️",
                key=f"delete_{expense.id}",
            ):

                tracker.remove_expense(expense.id)
                st.rerun()


st.divider()


# ---------------------------------------------------------------------
# Category breakdown
# ---------------------------------------------------------------------

st.subheader("📊 Spending by Category")

breakdown = tracker.totals_by_category()

if not breakdown:

    st.info("Nothing to break down yet.")

else:

    for category, amount in sorted(
        breakdown.items(),
        key=lambda item: -item[1],
    ):

        percentage = (
            amount / tracker.total * 100
            if tracker.total
            else 0
        )

        col1, col2 = st.columns([3, 1])

        with col1:
            st.write(f"**{category}**")

        with col2:
            st.write(
                f"${amount:,.2f} ({percentage:.0f}%)"
            )

        st.progress(
            min(percentage / 100, 1.0)
        )


st.divider()


# ---------------------------------------------------------------------
# Clear all
# ---------------------------------------------------------------------

if tracker.expenses:

    st.subheader("⚠️ Manage Data")

    if st.button(
        "Clear All Expenses",
        type="secondary",
        use_container_width=True,
    ):

        tracker.clear()

        st.success("All expenses have been cleared.")

        st.rerun()


# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------

st.markdown(
    """
    <div style="text-align:center; color:#888; margin-top:2rem;">
        Expense Tracker • Built with Python + Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)