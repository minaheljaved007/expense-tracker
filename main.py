"""
main.py
-------
NiceGUI front end for the Expense Tracker.

This file is ONLY responsible for display and user interaction.
All the actual math/state logic lives in tracker_logic.py and is
imported here. That separation is what lets tracker_logic.py be
unit-tested without a browser, and lets this UI be redesigned later
without touching the accumulator logic at all.

Run locally:
    python main.py
Then open the URL it prints (usually http://localhost:8080).
"""

from nicegui import ui

from tracker_logic import ExpenseTracker, InvalidExpenseError

# ---------------------------------------------------------------------
# One tracker instance per browser tab/session.
# NiceGUI gives each connecting client its own Python state when you
# create objects inside a @ui.page function (see build_ui below), so
# two different users won't see each other's expenses.
# ---------------------------------------------------------------------

CATEGORIES = ["General", "Food", "Transport", "Bills", "Shopping", "Health", "Entertainment", "Other"]


@ui.page("/")
def build_ui() -> None:
    tracker = ExpenseTracker()

    # -------------------- Header --------------------
    with ui.header().classes("items-center justify-between bg-primary text-white px-6"):
        ui.label("💰 Expense Tracker").classes("text-xl font-bold")
        ui.label("DecodeLabs Project 2").classes("text-sm opacity-80")

    with ui.column().classes("w-full max-w-2xl mx-auto p-4 gap-4"):

        # -------------------- Summary card --------------------
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-center justify-between"):
                with ui.column().classes("gap-0"):
                    ui.label("Total Spent").classes("text-sm text-gray-500")
                    total_label = ui.label("$0.00").classes("text-4xl font-bold text-primary")
                with ui.column().classes("gap-0 items-end"):
                    count_label = ui.label("0 transactions").classes("text-sm text-gray-500")
                    avg_label = ui.label("Avg: $0.00").classes("text-sm text-gray-500")

        # -------------------- Add expense form --------------------
        with ui.card().classes("w-full"):
            ui.label("Add an expense").classes("text-lg font-semibold")

            with ui.row().classes("w-full gap-2 items-start"):
                amount_input = ui.input(
                    label="Amount",
                    placeholder="e.g. 250"
                ).classes("flex-1").props("dense outlined")

                category_select = ui.select(
                    CATEGORIES, value="General", label="Category"
                ).classes("w-40").props("dense outlined")

            note_input = ui.input(
                label="Note (optional)",
                placeholder="e.g. Groceries at the market"
            ).classes("w-full").props("dense outlined")

            error_label = ui.label("").classes("text-red-500 text-sm")

            def handle_add() -> None:
                try:
                    tracker.add_expense(
                        raw_amount=amount_input.value,
                        category=category_select.value,
                        note=note_input.value,
                    )
                except InvalidExpenseError as e:
                    # Exactly the "Defensive Coding" pattern from the slides:
                    # catch the bad input, show a message, don't crash.
                    error_label.text = str(e)
                    return

                error_label.text = ""
                amount_input.value = ""
                note_input.value = ""
                amount_input.run_method("focus")
                refresh_all()

            amount_input.on("keydown.enter", handle_add)
            ui.button("Add Expense", icon="add", on_click=handle_add).classes("w-full")

        # -------------------- History list --------------------
        with ui.card().classes("w-full"):
            with ui.row().classes("w-full items-center justify-between"):
                ui.label("History").classes("text-lg font-semibold")
                clear_button = ui.button(
                    "Clear All", icon="delete_sweep", color="negative"
                ).props("outline dense")

            history_container = ui.column().classes("w-full gap-1")

        # -------------------- Category breakdown --------------------
        with ui.card().classes("w-full"):
            ui.label("By Category").classes("text-lg font-semibold")
            breakdown_container = ui.column().classes("w-full gap-1")

        # -------------------- Refresh logic --------------------
        def refresh_all() -> None:
            total_label.text = f"${tracker.total:,.2f}"
            count_label.text = f"{tracker.count()} transaction{'s' if tracker.count() != 1 else ''}"
            avg_label.text = f"Avg: ${tracker.average():,.2f}"

            history_container.clear()
            with history_container:
                if not tracker.expenses:
                    ui.label("No expenses yet — add your first one above.").classes(
                        "text-gray-400 text-sm italic"
                    )
                else:
                    # Most recent first
                    for exp in reversed(tracker.expenses):
                        with ui.row().classes(
                            "w-full items-center justify-between p-2 rounded hover:bg-gray-100"
                        ):
                            with ui.column().classes("gap-0"):
                                label_text = exp.category
                                if exp.note:
                                    label_text += f" — {exp.note}"
                                ui.label(label_text).classes("font-medium")
                                ui.label(exp.timestamp).classes("text-xs text-gray-400")
                            with ui.row().classes("items-center gap-2"):
                                ui.label(f"${exp.amount:,.2f}").classes("font-semibold")
                                ui.button(
                                    icon="close",
                                    on_click=lambda _, eid=exp.id: handle_remove(eid),
                                ).props("flat dense round size=sm color=negative")

            breakdown_container.clear()
            with breakdown_container:
                breakdown = tracker.totals_by_category()
                if not breakdown:
                    ui.label("Nothing to break down yet.").classes("text-gray-400 text-sm italic")
                else:
                    for category, amount in sorted(breakdown.items(), key=lambda kv: -kv[1]):
                        pct = (amount / tracker.total * 100) if tracker.total else 0
                        with ui.column().classes("w-full gap-0"):
                            with ui.row().classes("w-full items-center justify-between"):
                                ui.label(category).classes("text-sm")
                                ui.label(f"${amount:,.2f} ({pct:.0f}%)").classes("text-sm text-gray-500")
                            ui.linear_progress(value=pct / 100, show_value=False).classes("h-2")

        def handle_remove(expense_id: int) -> None:
            tracker.remove_expense(expense_id)
            refresh_all()

        def handle_clear() -> None:
            tracker.clear()
            error_label.text = ""
            refresh_all()

        clear_button.on_click(handle_clear)

        # Initial render
        refresh_all()


# ---------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="Expense Tracker",
        port=8080,
        reload=True,   # auto-reload on save, handy for local dev in VS Code
        show=False,    # set True if you want it to auto-open a browser tab
    )
