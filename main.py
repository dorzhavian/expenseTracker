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
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
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
        cur = self.conn.execute(query, (expense.amount, expense.category, expense.description, expense.date))
        self.conn.commit()
        return cur.lastrowid

    def get_all_expenses(self):
        cursor = self.conn.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")
        return cursor.fetchall()

    def get_expenses_by_category(self, category: str):
        cursor = self.conn.execute("SELECT * FROM expenses WHERE category = ? ORDER BY date DESC, id DESC", (category,))
        return cursor.fetchall()

    def get_expenses_by_date_range(self, start_date: str, end_date: str):
        cursor = self.conn.execute(
            "SELECT * FROM expenses WHERE date BETWEEN ? AND ? ORDER BY date DESC, id DESC",
            (start_date, end_date),
        )
        return cursor.fetchall()

    def get_total_expenses(self):
        cursor = self.conn.execute("SELECT SUM(amount) FROM expenses")
        return cursor.fetchone()[0] or 0

    def get_total_by_category(self):
        cursor = self.conn.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY SUM(amount) DESC")
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