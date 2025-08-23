from flask import Flask, request, jsonify
from flask_cors import CORS

try:
    from main import ExpenseTracker, Expense
except Exception as e:
    print(">>> ERROR importing main.py:", e)
    ExpenseTracker = Expense = None

app = Flask(__name__)
CORS(app)

tracker = ExpenseTracker() if ExpenseTracker else None

@app.route("/", methods=["GET"])
def home():
    status = "ok" if tracker else "main.py import failed"
    return jsonify({"service": "ExpenseTracker API", "status": status}), 200

@app.route("/expenses", methods=["GET"])
def get_expenses():
    if not tracker:
        return jsonify({"error": "Backend not connected (main.py import failed)"}), 500
    rows = tracker.get_all_expenses()
    data = [
        {"id": r[0], "amount": float(r[1]), "category": r[2], "description": r[3], "date": r[4]}
        for r in rows
    ]
    return jsonify(data), 200

@app.route("/expenses", methods=["POST"])
def add_expense():
    if not tracker:
        return jsonify({"error": "Backend not connected (main.py import failed)"}), 500
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Body must be JSON"}), 400
    missing = [k for k in ("amount", "category", "description") if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400
    try:
        amount = float(data["amount"])
    except (TypeError, ValueError):
        return jsonify({"error": "amount must be a number"}), 400
    expense = Expense(amount, data["category"], data["description"], data.get("date"))
    new_id = tracker.add_expense(expense)
    return jsonify({"message": "Expense added", "id": new_id}), 201

@app.route("/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    if not tracker:
        return jsonify({"error": "Backend not connected (main.py import failed)"}), 500
    existing = tracker.get_expense_by_id(expense_id)
    if not existing:
        return jsonify({"error": "Expense not found"}), 404
    data = request.get_json(silent=True) or {}
    amount = float(data.get("amount", existing[1]))
    category = data.get("category", existing[2])
    description = data.get("description", existing[3])
    date = data.get("date", existing[4])
    tracker.update_expense(expense_id, amount, category, description, date)
    return jsonify({"message": "Expense updated"}), 200

@app.route("/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    if not tracker:
        return jsonify({"error": "Backend not connected (main.py import failed)"}), 500
    existing = tracker.get_expense_by_id(expense_id)
    if not existing:
        return jsonify({"error": "Expense not found"}), 404
    tracker.delete_expense(expense_id)
    return jsonify({"message": "Expense deleted"}), 200

if __name__ == "__main__":
    print(">>> LOADING APP.PY (basic API)")
    app.run(debug=True)
