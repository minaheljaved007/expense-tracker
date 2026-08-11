"""
tracker_logic.py
-----------------
The "engine" of the Expense Tracker.

This module deliberately has ZERO knowledge of NiceGUI, the web,
or how numbers get displayed. It only knows how to:
  1. validate raw input,
  2. accumulate a running total,
  3. store a simple transaction history.

Keeping this separate from the UI (main.py) is exactly the
"Phase 3: Decoupling Logic (Model) from Display (View)" idea from
the training slides -- it also means we can unit-test the math
without ever opening a browser.
"""

from dataclasses import dataclass, field
from datetime import datetime


class InvalidExpenseError(ValueError):
    """Raised when raw input cannot be turned into a valid expense."""
    pass


@dataclass
class Expense:
    """A single transaction in the ledger."""
    id: int
    amount: float
    category: str
    note: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class ExpenseTracker:
    """
    The accumulator engine.

    State:
        total        -> running sum of all expenses (the "accumulator")
        expenses     -> ordered history of Expense records
        _next_id     -> internal counter for assigning unique ids

    This mirrors the slide's "Anatomy of State":
        - total is initialized ONCE, outside any loop (Initialization)
        - each call to add_expense() updates it in place (Iteration)
        - nothing resets `total` to 0 accidentally on every add
    """

    def __init__(self):
        self.total: float = 0.0
        self.expenses: list[Expense] = []
        self._next_id: int = 1

    # ---- Phase 1: The Gatekeeper (validation) --------------------------
    @staticmethod
    def parse_amount(raw_value: str) -> float:
        """
        Validate and convert raw user input into a positive float.

        Equivalent to the slide's:
            try:
                expense = int(input())
            except ValueError:
                print("Invalid Data")

        Raises InvalidExpenseError with a human-readable message on
        any bad input, so the UI layer can just catch one exception
        type and show it to the user.
        """
        if raw_value is None:
            raise InvalidExpenseError("No amount entered.")

        cleaned = str(raw_value).strip().replace(",", "")
        if cleaned == "":
            raise InvalidExpenseError("Amount can't be empty.")

        try:
            amount = float(cleaned)
        except ValueError:
            raise InvalidExpenseError(f"'{raw_value}' is not a valid number.")

        if amount <= 0:
            raise InvalidExpenseError("Amount must be greater than zero.")

        # Guard against absurd/typo'd inputs (e.g. accidentally typing
        # an extra zero). Adjust the ceiling if you have a real use case
        # that needs larger single transactions.
        if amount > 1_000_000_000:
            raise InvalidExpenseError("Amount is unrealistically large.")

        return round(amount, 2)

    # ---- Phase 2: The Accumulator Pattern ------------------------------
    def add_expense(self, raw_amount: str, category: str = "General", note: str = "") -> Expense:
        """
        Validate, then accumulate: total += new_expense.

        Returns the created Expense record so the UI can display it
        immediately without re-querying state.
        """
        amount = self.parse_amount(raw_amount)  # raises InvalidExpenseError if bad

        expense = Expense(
            id=self._next_id,
            amount=amount,
            category=(category or "General").strip() or "General",
            note=(note or "").strip(),
        )
        self.expenses.append(expense)
        self.total += amount  # <-- the accumulator pattern, State(new) = State(old) + Input
        self._next_id += 1
        return expense

    def remove_expense(self, expense_id: int) -> bool:
        """
        Remove a single expense by id and correctly reverse the
        accumulator (total -= removed_amount). Returns True if
        something was actually removed.
        """
        for i, exp in enumerate(self.expenses):
            if exp.id == expense_id:
                self.total -= exp.amount
                self.total = round(self.total, 2)
                del self.expenses[i]
                return True
        return False

    def clear(self) -> None:
        """Full reset: total back to 0, history wiped (the 'kill switch')."""
        self.total = 0.0
        self.expenses.clear()
        self._next_id = 1

    # ---- Phase 3: Output / reporting helpers ---------------------------
    def totals_by_category(self) -> dict[str, float]:
        """Breakdown of spend per category, useful for a summary view."""
        breakdown: dict[str, float] = {}
        for exp in self.expenses:
            breakdown[exp.category] = round(breakdown.get(exp.category, 0.0) + exp.amount, 2)
        return breakdown

    def count(self) -> int:
        return len(self.expenses)

    def average(self) -> float:
        if not self.expenses:
            return 0.0
        return round(self.total / len(self.expenses), 2)

    def to_dict(self) -> dict:
        """Serializable snapshot, e.g. for saving to disk or a session."""
        return {
            "total": self.total,
            "next_id": self._next_id,
            "expenses": [
                {
                    "id": e.id,
                    "amount": e.amount,
                    "category": e.category,
                    "note": e.note,
                    "timestamp": e.timestamp,
                }
                for e in self.expenses
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ExpenseTracker":
        """Rebuild a tracker from a snapshot produced by to_dict()."""
        tracker = cls()
        tracker.total = data.get("total", 0.0)
        tracker._next_id = data.get("next_id", 1)
        tracker.expenses = [
            Expense(
                id=e["id"],
                amount=e["amount"],
                category=e["category"],
                note=e.get("note", ""),
                timestamp=e.get("timestamp", ""),
            )
            for e in data.get("expenses", [])
        ]
        return tracker
