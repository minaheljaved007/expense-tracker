"""
tracker_logic.py
----------------
Core Expense Tracker logic.

This file contains NO Streamlit code and NO UI code.
It can be tested independently.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any


# ---------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------

class InvalidExpenseError(ValueError):
    """Raised when an expense amount is invalid."""
    pass


# ---------------------------------------------------------------------
# Expense model
# ---------------------------------------------------------------------

@dataclass
class Expense:
    id: int
    amount: float
    category: str
    note: str
    timestamp: str


# ---------------------------------------------------------------------
# Expense Tracker
# ---------------------------------------------------------------------

class ExpenseTracker:

    def __init__(self) -> None:

        self.expenses: list[Expense] = []

        self.total: float = 0.0

        self._next_id: int = 1


    # -----------------------------------------------------------------
    # Add expense
    # -----------------------------------------------------------------

    def add_expense(
        self,
        raw_amount: Any,
        category: str = "General",
        note: str = "",
    ) -> Expense:
        """
        Validate and add an expense.

        Accepts values such as:

            250
            "250"
            "1,250.50"
            " 250 "

        Rejects:

            ""
            "abc"
            0
            negative values
        """

        # Convert to string first so None and other raw values
        # are handled safely.
        value = str(raw_amount).strip()

        if not value:
            raise InvalidExpenseError(
                "Amount cannot be empty."
            )

        # Remove commas so values such as 1,250.50 work.
        value = value.replace(",", "")

        try:
            amount = float(value)

        except (ValueError, TypeError):
            raise InvalidExpenseError(
                "Amount must be a valid number."
            )

        if amount <= 0:
            raise InvalidExpenseError(
                "Amount must be greater than zero."
            )

        # Always keep money to two decimal places.
        amount = round(amount, 2)

        category = (
            str(category).strip()
            if category is not None
            else "General"
        )

        if not category:
            category = "General"

        note = (
            str(note).strip()
            if note is not None
            else ""
        )

        expense = Expense(
            id=self._next_id,
            amount=amount,
            category=category,
            note=note,
            timestamp=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )

        self.expenses.append(expense)

        self.total = round(
            self.total + amount,
            2,
        )

        self._next_id += 1

        return expense


    # -----------------------------------------------------------------
    # Remove expense
    # -----------------------------------------------------------------

    def remove_expense(
        self,
        expense_id: int,
    ) -> bool:
        """
        Remove an expense by ID.

        Returns:
            True  -> expense was removed
            False -> ID was not found
        """

        for index, expense in enumerate(self.expenses):

            if expense.id == expense_id:

                self.expenses.pop(index)

                self.total = round(
                    self.total - expense.amount,
                    2,
                )

                # Protect against floating-point residue.
                if abs(self.total) < 0.005:
                    self.total = 0.0

                return True

        return False


    # -----------------------------------------------------------------
    # Clear
    # -----------------------------------------------------------------

    def clear(self) -> None:
        """Remove all expenses and reset the tracker."""

        self.expenses.clear()

        self.total = 0.0

        self._next_id = 1


    # -----------------------------------------------------------------
    # Count
    # -----------------------------------------------------------------

    def count(self) -> int:
        """Return the number of expenses."""

        return len(self.expenses)


    # -----------------------------------------------------------------
    # Average
    # -----------------------------------------------------------------

    def average(self) -> float:
        """Return the average expense."""

        if not self.expenses:
            return 0.0

        return round(
            self.total / len(self.expenses),
            2,
        )


    # -----------------------------------------------------------------
    # Category totals
    # -----------------------------------------------------------------

    def totals_by_category(self) -> dict[str, float]:
        """
        Return total spending grouped by category.
        """

        result: dict[str, float] = {}

        for expense in self.expenses:

            result[expense.category] = round(
                result.get(expense.category, 0.0)
                + expense.amount,
                2,
            )

        return result


    # -----------------------------------------------------------------
    # Serialization
    # -----------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Convert tracker state into a dictionary.
        """

        return {
            "expenses": [
                asdict(expense)
                for expense in self.expenses
            ],
            "total": self.total,
            "next_id": self._next_id,
        }


    # -----------------------------------------------------------------
    # Deserialization
    # -----------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> "ExpenseTracker":
        """
        Reconstruct a tracker from a dictionary.
        """

        tracker = cls()

        for item in data.get("expenses", []):

            expense = Expense(
                id=int(item["id"]),
                amount=round(
                    float(item["amount"]),
                    2,
                ),
                category=str(
                    item.get(
                        "category",
                        "General",
                    )
                ),
                note=str(
                    item.get(
                        "note",
                        "",
                    )
                ),
                timestamp=str(
                    item.get(
                        "timestamp",
                        "",
                    )
                ),
            )

            tracker.expenses.append(expense)

        tracker.total = round(
            sum(
                expense.amount
                for expense in tracker.expenses
            ),
            2,
        )

        if tracker.expenses:

            tracker._next_id = (
                max(
                    expense.id
                    for expense in tracker.expenses
                )
                + 1
            )

        else:

            tracker._next_id = 1

        return tracker