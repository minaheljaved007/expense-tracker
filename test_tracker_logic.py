import pytest

from tracker_logic import (
    ExpenseTracker,
    InvalidExpenseError,
)


def test_new_tracker_starts_empty():
    tracker = ExpenseTracker()

    assert tracker.total == 0.0
    assert tracker.count() == 0
    assert tracker.expenses == []


def test_add_single_expense():
    tracker = ExpenseTracker()

    tracker.add_expense(
        "100",
        "Food",
        "Lunch",
    )

    assert tracker.total == 100.0
    assert tracker.count() == 1


def test_multiple_expenses_accumulate_correctly():
    tracker = ExpenseTracker()

    tracker.add_expense("100")
    tracker.add_expense("200")
    tracker.add_expense("50")

    assert tracker.total == 350.0
    assert tracker.count() == 3


def test_state_does_not_reset_between_additions():
    tracker = ExpenseTracker()

    tracker.add_expense("100")
    tracker.add_expense("200")

    assert tracker.total == 300.0
    assert tracker.count() == 2


def test_rejects_non_numeric_string():
    tracker = ExpenseTracker()

    with pytest.raises(InvalidExpenseError):
        tracker.add_expense("abc")


def test_rejects_empty_string():
    tracker = ExpenseTracker()

    with pytest.raises(InvalidExpenseError):
        tracker.add_expense("")


def test_rejects_zero():
    tracker = ExpenseTracker()

    with pytest.raises(InvalidExpenseError):
        tracker.add_expense("0")


def test_rejects_negative():
    tracker = ExpenseTracker()

    with pytest.raises(InvalidExpenseError):
        tracker.add_expense("-50")


def test_accepts_amount_with_commas_and_whitespace():
    tracker = ExpenseTracker()

    tracker.add_expense(" 1,250.50 ")

    assert tracker.total == 1250.50


def test_rounds_to_two_decimal_places():
    tracker = ExpenseTracker()

    tracker.add_expense("10.999")

    assert tracker.total == 11.00


def test_remove_expense_reverses_total():
    tracker = ExpenseTracker()

    expense = tracker.add_expense("100")

    result = tracker.remove_expense(expense.id)

    assert result is True
    assert tracker.total == 0.0
    assert tracker.count() == 0


def test_remove_nonexistent_id_returns_false():
    tracker = ExpenseTracker()

    result = tracker.remove_expense(999)

    assert result is False


def test_clear_resets_everything():
    tracker = ExpenseTracker()

    tracker.add_expense("100")
    tracker.add_expense("200")

    tracker.clear()

    assert tracker.total == 0.0
    assert tracker.count() == 0
    assert tracker.expenses == []


def test_totals_by_category():
    tracker = ExpenseTracker()

    tracker.add_expense("100", "Food")
    tracker.add_expense("50", "Food")
    tracker.add_expense("200", "Transport")

    result = tracker.totals_by_category()

    assert result["Food"] == 150.0
    assert result["Transport"] == 200.0


def test_average():
    tracker = ExpenseTracker()

    tracker.add_expense("100")
    tracker.add_expense("200")

    assert tracker.average() == 150.0


def test_average_with_no_expenses_is_zero():
    tracker = ExpenseTracker()

    assert tracker.average() == 0.0


def test_to_dict_and_from_dict_roundtrip():
    tracker = ExpenseTracker()

    tracker.add_expense(
        "100",
        "Food",
        "Lunch",
    )

    tracker.add_expense(
        "250",
        "Bills",
        "Electricity",
    )

    data = tracker.to_dict()

    restored = ExpenseTracker.from_dict(data)

    assert restored.total == tracker.total
    assert restored.count() == tracker.count()

    assert restored.expenses[0].amount == 100.0
    assert restored.expenses[0].category == "Food"
    assert restored.expenses[1].amount == 250.0


def test_handles_many_transactions():
    tracker = ExpenseTracker()

    for _ in range(100):
        tracker.add_expense("10")

    assert tracker.count() == 100
    assert tracker.total == 1000.0