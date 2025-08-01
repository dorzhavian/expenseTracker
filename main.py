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


def main():
    tracker = ExpenseTracker()

    expense1 = Expense(100, "Transport", "Bus ticket")
    tracker.add_expense(expense1)

    print("All expenses:")
    for e in tracker.get_all_expenses():
        print(e)


if __name__ == "__main__":
    main()
