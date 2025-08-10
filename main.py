import sqlite3
from datetime import datetime

class Expense:
    def __init__(self, amount: float, category: str, description: str, date: str = None):
        self.amount = amount
        self.category = category
        self.description = description
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")


class ExpenseTracker:
    def __init__(self, db_name="expenses.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def add_expense(self, expense: Expense):
        query = "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)"
        self.conn.execute(query, (expense.amount, expense.category, expense.description, expense.date))
        self.conn.commit()

    def get_all_expenses(self):
        cursor = self.conn.execute("SELECT * FROM expenses")
        return cursor.fetchall()

    def get_expenses_by_category(self, category: str):
        cursor = self.conn.execute("SELECT * FROM expenses WHERE category = ?", (category,))
        return cursor.fetchall()

    def get_expenses_by_date_range(self, start_date: str, end_date: str):
        cursor = self.conn.execute("SELECT * FROM expenses WHERE date BETWEEN ? AND ?", (start_date, end_date))
        return cursor.fetchall()

    def get_total_expenses(self):
        cursor = self.conn.execute("SELECT SUM(amount) FROM expenses")
        return cursor.fetchone()[0] or 0

    def get_total_by_category(self):
        cursor = self.conn.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        return cursor.fetchall()

    def update_expense(self, expense_id: int, amount: float, category: str, description: str, date: str):
        query = """
        UPDATE expenses
        SET amount = ?, category = ?, description = ?, date = ?
        WHERE id = ?
        """
        self.conn.execute(query, (amount, category, description, date, expense_id))
        self.conn.commit()

    def delete_expense(self, expense_id: int):
        query = "DELETE FROM expenses WHERE id = ?"
        self.conn.execute(query, (expense_id,))
        self.conn.commit()

    def get_expense_by_id(self, expense_id: int):
        cursor = self.conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        return cursor.fetchone()


def print_expenses(rows):
    if not rows:
        print("No expenses found.")
        return
    print("ID | Amount | Category | Description | Date")
    for e in rows:
        print(f"{e[0]} | {e[1]} | {e[2]} | {e[3]} | {e[4]}")


def input_or_cancel(prompt, caster=str):
    val = input(prompt).strip()
    if val == "-1":
        return None
    try:
        return caster(val) if val != "" else ""
    except Exception:
        return "INVALID"


def get_valid_id_or_back(tracker: ExpenseTracker):
    print_expenses(tracker.get_all_expenses())
    while True:
        val = input_or_cancel("Enter expense ID (-1 to back): ", int)
        if val is None:
            return None
        if val == "INVALID":
            print("Invalid input. Enter a number or -1.")
            continue
        if tracker.get_expense_by_id(val):
            return val
        print("ID not found. Try again or -1 to back.")


def run_cli(tracker: ExpenseTracker):
    while True:
        print("\nExpense Tracker Menu:")
        print("1. Add expense")
        print("2. Show all expenses")
        print("3. Filter by category")
        print("4. Filter by date range")
        print("5. Show summary")
        print("6. Update expense")
        print("7. Delete expense")
        print("8. Exit")

        choice = input_or_cancel("Choose an option (-1 to back): ")
        if choice is None:
            continue

        if choice == "1":
            amount = input_or_cancel("Amount (-1 to cancel): ")
            if amount is None:
                continue
            try:
                amount = float(amount)
            except ValueError:
                print("Amount must be a number.")
                continue
            category = input_or_cancel("Category (-1 to cancel): ")
            if category is None:
                continue
            description = input_or_cancel("Description (-1 to cancel): ")
            if description is None:
                continue
            date = input_or_cancel("Date YYYY-MM-DD (Enter for today, -1 to cancel): ")
            if date is None:
                continue
            expense = Expense(amount, category, description, date if date else None)
            tracker.add_expense(expense)
            print("Expense added.")

        elif choice == "2":
            print_expenses(tracker.get_all_expenses())

        elif choice == "3":
            category = input_or_cancel("Enter category (-1 to cancel): ")
            if category is None:
                continue
            print_expenses(tracker.get_expenses_by_category(category))

        elif choice == "4":
            start_date = input_or_cancel("Start date YYYY-MM-DD (-1 to cancel): ")
            if start_date is None:
                continue
            end_date = input_or_cancel("End date YYYY-MM-DD (-1 to cancel): ")
            if end_date is None:
                continue
            print_expenses(tracker.get_expenses_by_date_range(start_date, end_date))

        elif choice == "5":
            print(f"Total expenses: {tracker.get_total_expenses()}")
            print("Total by category:")
            for row in tracker.get_total_by_category():
                print(f"{row[0]}: {row[1]}")

        elif choice == "6":
            expense_id = get_valid_id_or_back(tracker)
            if expense_id is None:
                continue
            amount = input_or_cancel("New amount (-1 to cancel): ")
            if amount is None:
                continue
            try:
                amount = float(amount)
            except ValueError:
                print("Amount must be a number.")
                continue
            category = input_or_cancel("New category (-1 to cancel): ")
            if category is None:
                continue
            description = input_or_cancel("New description (-1 to cancel): ")
            if description is None:
                continue
            date = input_or_cancel("New date YYYY-MM-DD (-1 to cancel): ")
            if date is None:
                continue
            tracker.update_expense(expense_id, amount, category, description, date)
            print("Expense updated.")

        elif choice == "7":
            expense_id = get_valid_id_or_back(tracker)
            if expense_id is None:
                continue
            tracker.delete_expense(expense_id)
            print("Expense deleted.")

        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")


def main():
    tracker = ExpenseTracker()
    run_cli(tracker)


if __name__ == "__main__":
    main()