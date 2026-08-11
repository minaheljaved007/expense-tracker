"""
test_tracker_logic.py
----------------------
Unit tests for the accumulator engine (tracker_logic.py).

Run in VS Code:
    1. Open the Testing sidebar (flask icon) -> it should auto-discover
       these via pytest, OR
    2. Open a terminal in this folder and run:
           pytest -v

These tests directly check the "Quality Standard" checklist from the
training slides:
    - Stability: handles 5+ transactions
    - State: total initialized outside the loop, never resets accidentally
    - Defense: invalid input raises a catchable error, doesn't crash
    - Control: totals are correct and reversible on delete
"""

import pytest
from tracker_logic import ExpenseTracker, InvalidExpenseError


# ---------------------------------------------------------------------
# Basic accumulation
# ---------------------------------------------------------------------

def test_starts_at_zero():
    tracker = ExpenseTracker()
    assert tracker.total == 0.0
    assert tracker.count() == 0


def test_single_expense_accumulates():
    tracker = ExpenseTracker()
    tracker.add_expense("100")
    assert tracker.total == 100.0
    assert tracker.count() == 1


def test_multiple_expenses_accumulate_correctly():
    """Mirrors the slide's worked example: 5 + 10 + 20 + 50 + 100 = 185."""
    tracker = ExpenseTracker()
    for amount in ["5", "10", "20", "50", "100"]:
        tracker.add_expense(amount)
    assert tracker.total == 185.0
    assert tracker.count() == 5


def test_state_does_not_reset_between_additions():
    """
    This is the 'Anatomy of State' check from the slides: total must be
    initialized ONCE, not reset to 0 on every call.
    """
    tracker = ExpenseTracker()
    tracker.add_expense("50")
    assert tracker.total == 50.0
    tracker.add_expense("25")
    # If total were being reset each call, this would be 25.0, not 75.0
    assert tracker.total == 75.0


# ---------------------------------------------------------------------
# Validation / "The Gatekeeper"
# ---------------------------------------------------------------------

def test_rejects_non_numeric_string():
    tracker = ExpenseTracker()
    with pytest.raises(InvalidExpenseError):
        tracker.add_expense("ten")
    # A rejected expense must NOT affect the total
    assert tracker.total == 0.0


def test_rejects_empty_string():
    tracker = ExpenseTracker()
    with pytest.raises(InvalidExpenseError):
        tracker.add_expense("")


def test_rejects_zero_and_negative():
    tracker = ExpenseTracker()
    with pytest.raises(InvalidExpenseError):
        tracker.add_expense("0")
    with pytest.raises(InvalidExpenseError):
        tracker.add_expense("-20")


def test_accepts_amount_with_commas_and_whitespace():
    tracker = ExpenseTracker()
    tracker.add_expense("  1,250.50  ")
    assert tracker.total == 1250.50


def test_rounds_to_two_decimal_places():
    tracker = ExpenseTracker()
    tracker.add_expense("10.999")
    assert tracker.total == 11.0


# ---------------------------------------------------------------------
# Deletion / reversal
# ---------------------------------------------------------------------

def test_remove_expense_reverses_total():
    tracker = ExpenseTracker()
    e1 = tracker.add_expense("100")
    tracker.add_expense("50")
    assert tracker.total == 150.0

    removed = tracker.remove_expense(e1.id)
    assert removed is True
    assert tracker.total == 50.0
    assert tracker.count() == 1


def test_remove_nonexistent_id_returns_false():
    tracker = ExpenseTracker()
    tracker.add_expense("10")
    assert tracker.remove_expense(9999) is False
    assert tracker.total == 10.0  # unaffected


# ---------------------------------------------------------------------
# Clear / kill switch
# ---------------------------------------------------------------------

def test_clear_resets_everything():
    tracker = ExpenseTracker()
    tracker.add_expense("100")
    tracker.add_expense("200")
    tracker.clear()
    assert tracker.total == 0.0
    assert tracker.count() == 0
    # next id should also reset so a fresh session starts clean
    new_expense = tracker.add_expense("5")
    assert new_expense.id == 1


# ---------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------

def test_totals_by_category():
    tracker = ExpenseTracker()
    tracker.add_expense("100", category="Food")
    tracker.add_expense("50", category="Food")
    tracker.add_expense("30", category="Transport")

    breakdown = tracker.totals_by_category()
    assert breakdown["Food"] == 150.0
    assert breakdown["Transport"] == 30.0


def test_average():
    tracker = ExpenseTracker()
    tracker.add_expense("10")
    tracker.add_expense("20")
    tracker.add_expense("30")
    assert tracker.average() == 20.0


def test_average_with_no_expenses_is_zero():
    tracker = ExpenseTracker()
    assert tracker.average() == 0.0


# ---------------------------------------------------------------------
# Serialization (used for saving/restoring a session)
# ---------------------------------------------------------------------

def test_to_dict_and_from_dict_roundtrip():
    tracker = ExpenseTracker()
    tracker.add_expense("100", category="Food", note="Lunch")
    tracker.add_expense("40", category="Transport")

    snapshot = tracker.to_dict()
    restored = ExpenseTracker.from_dict(snapshot)

    assert restored.total == tracker.total
    assert restored.count() == tracker.count()
    assert restored.expenses[0].category == "Food"
    assert restored.expenses[0].note == "Lunch"


# ---------------------------------------------------------------------
# Stability under load (the slide's "Handles 5+ transactions?" check)
# ---------------------------------------------------------------------

def test_handles_many_transactions():
    tracker = ExpenseTracker()
    for i in range(1, 51):  # 50 transactions
        tracker.add_expense(str(i))
    expected_total = sum(range(1, 51))
    assert tracker.total == expected_total
    assert tracker.count() == 50
