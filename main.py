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


def main():
    tracker = ExpenseTracker()

    expense1 = Expense(100, "Transport", "Bus ticket")
    expense2 = Expense(50, "Food", "Pizza dinner")
    expense3 = Expense(20, "Food", "Coffee", "2025-08-01")
    expense4 = Expense(200, "Shopping", "New shoes", "2025-08-02")

    tracker.add_expense(expense1)
    tracker.add_expense(expense2)
    tracker.add_expense(expense3)
    tracker.add_expense(expense4)

    print("All expenses:")
    for e in tracker.get_all_expenses():
        print(e)

    print("\nExpenses in category 'Food':")
    for e in tracker.get_expenses_by_category("Food"):
        print(e)

    print("\nExpenses between 2025-08-01 and 2025-08-02:")
    for e in tracker.get_expenses_by_date_range("2025-08-01", "2025-08-02"):
        print(e)


if __name__ == "__main__":
    main()
