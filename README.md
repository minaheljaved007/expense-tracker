# 💰 Expense Tracker

A simple web-based expense tracker built with **Python** and **NiceGUI**, built as a training exercise in accumulator patterns, input validation, and separating core logic from UI.

Enter an expense, watch the running total update, break spending down by category, and delete entries — all backed by a small, fully unit-tested accumulator engine.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![NiceGUI](https://img.shields.io/badge/UI-NiceGUI-4A90D9)
![Tests](https://img.shields.io/badge/tests-17%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## ✨ Features

- **Live running total** — add an expense and the total updates instantly
- **Category breakdown** — see spend per category with percentage bars
- **Delete individual expenses** — removes the entry and correctly reverses the total
- **Clear all** — reset the whole session
- **Input validation** — rejects empty, non-numeric, zero, or negative amounts with a clear error message instead of crashing
- **Notes per expense** — optional free-text note alongside each entry
- **Fully unit-tested core logic** — 17 tests covering accumulation, validation, deletion, and edge cases

## 🧠 Why this project exists

Most "expense tracker" tutorials jump straight to a database. This one is deliberately built around a single idea first: **the accumulator pattern.**

```python
total += new_expense
```

Before adding persistence, authentication, or a database, this project focuses on getting that one line — and everything that has to be true around it (validation, state that doesn't accidentally reset, correct reversal on delete) — right. The [`tracker_logic.py`](./tracker_logic.py) module has zero dependency on the UI, so the math can be verified independently of anything web-related.

## 🏗️ Architecture

```
expense_tracker/
├── tracker_logic.py       # Core accumulator engine — pure Python, no UI
├── main.py                 # NiceGUI web interface
├── test_tracker_logic.py  # Unit tests for the engine
├── wsgi_app.py              # WSGI adapter for deploying to WSGI-only hosts
└── requirements.txt
```

The project follows a simple separation of concerns:

| Layer | File | Responsibility |
|---|---|---|
| **Logic** | `tracker_logic.py` | Validates input, accumulates totals, tracks history. No knowledge of NiceGUI or the browser. |
| **UI** | `main.py` | Renders the interface and wires user actions to the logic layer. |
| **Tests** | `test_tracker_logic.py` | Verifies the logic layer in isolation — no browser needed. |
| **Deployment** | `wsgi_app.py` | Bridges NiceGUI's async (ASGI) foundation to WSGI-only hosting environments. |

Keeping logic and UI apart means the engine can be tested in milliseconds, and the UI can be redesigned later without touching how the math works.

## 🚀 Getting started

### Prerequisites

- Python 3.10 or later

### Installation

```bash
# Clone the repo
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run locally

```bash
python main.py
```

Open **http://localhost:8080** in your browser.

### Run the tests

```bash
pytest -v
```

Expect `17 passed`.

## 📸 How it works

1. Enter an amount (and optionally a category and note)
2. Hit **Add Expense** — the total, transaction count, average, and category breakdown all update
3. Click the ✕ on any entry to delete it — the total is correctly reversed
4. **Clear All** resets the session back to zero

Each browser session gets its own independent tracker — nothing is shared between tabs or users, and nothing persists across a page refresh yet (see [Roadmap](#-roadmap)).

## 🧪 Testing philosophy

The accumulator engine is tested independently of the UI, covering:

- Basic accumulation across single and multiple expenses
- State correctness (totals don't silently reset between additions)
- Input validation (empty strings, non-numeric input, zero/negative amounts, whitespace and commas)
- Deletion and correct reversal of totals
- Category breakdowns and averages
- Serialization round-trips (`to_dict()` / `from_dict()`)
- Stability under a larger batch of transactions

Run `pytest -v` to see the full list.

## 🗺️ Roadmap

This project intentionally ships without persistence — every refresh starts a clean session. `tracker_logic.py` already includes `to_dict()` / `from_dict()` methods to make adding persistence straightforward later, without touching the accumulator logic itself. Natural next steps:

- [ ] Persist expenses (file-based or a lightweight database)
- [ ] Export history to CSV
- [ ] Date-range filtering
- [ ] Multi-currency support
- [ ] User accounts

## 🛠️ Built with

- [Python](https://www.python.org/)
- [NiceGUI](https://nicegui.io/) — Python-based web UI framework
- [pytest](https://pytest.org/) — testing framework
- [a2wsgi](https://github.com/abersheeran/a2wsgi) — ASGI-to-WSGI bridge for deployment

## 📄 License

MIT — feel free to use this as a learning reference or a starting point for your own project.

---

*Built as part of a Python backend training exercise focused on accumulator patterns and defensive coding.*
