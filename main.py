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


def run_cli(tracker: ExpenseTracker):
    while True:
        print("\nExpense Tracker Menu:")
        print("1. Add expense")
        print("2. Show all expenses")
        print("3. Filter by category")
        print("4. Filter by date range")
        print("5. Show summary")
        print("6. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            amount = float(input("Amount: "))
            category = input("Category: ")
            description = input("Description: ")
            date = input("Date (YYYY-MM-DD, press Enter for today): ")
            expense = Expense(amount, category, description, date if date else None)
            tracker.add_expense(expense)
            print("Expense added.")

        elif choice == "2":
            expenses = tracker.get_all_expenses()
            for e in expenses:
                print(e)

        elif choice == "3":
            category = input("Enter category: ")
            expenses = tracker.get_expenses_by_category(category)
            for e in expenses:
                print(e)

        elif choice == "4":
            start_date = input("Start date (YYYY-MM-DD): ")
            end_date = input("End date (YYYY-MM-DD): ")
            expenses = tracker.get_expenses_by_date_range(start_date, end_date)
            for e in expenses:
                print(e)

        elif choice == "5":
            print(f"Total expenses: {tracker.get_total_expenses()}")
            print("Total by category:")
            for row in tracker.get_total_by_category():
                print(f"{row[0]}: {row[1]}")

        elif choice == "6":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Try again.")


def main():
    tracker = ExpenseTracker()
    run_cli(tracker)


if __name__ == "__main__":
    main()
