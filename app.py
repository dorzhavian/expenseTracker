from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from datetime import datetime

try:
    from main import ExpenseTracker, Expense
except Exception as e:
    print(">>> ERROR importing main.py:", e)
    ExpenseTracker = Expense = None

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"
CORS(app)

tracker = ExpenseTracker() if ExpenseTracker else None

def compute_totals(rows):
    total = sum(float(r[1]) for r in rows)
    by_cat = {}
    for r in rows:
        by_cat[r[2]] = by_cat.get(r[2], 0.0) + float(r[1])
    by_cat_list = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)
    return total, by_cat_list

@app.route("/", methods=["GET"])
def home():
    status = "ok" if tracker else "main.py import failed"
    return jsonify({"service": "ExpenseTracker API", "status": status}), 200

@app.route("/dashboard", methods=["GET"])
def dashboard():
    if not tracker:
        return render_template("index.html", expenses=[], total=0.0, totals_by_cat=[], filters={"category":"", "start":"", "end":""})

    category = (request.args.get("category") or "").strip()
    start_date = (request.args.get("start") or "").strip()
    end_date = (request.args.get("end") or "").strip()

    if category:
        expenses = tracker.get_expenses_by_category(category)
    elif start_date and end_date:
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
            expenses = tracker.get_expenses_by_date_range(start_date, end_date)
        except ValueError:
            flash("Invalid date range. Use YYYY-MM-DD.", "danger")
            return redirect(url_for("dashboard"))
    else:
        expenses = tracker.get_all_expenses()

    total, totals_by_cat = compute_totals(expenses)

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        totals_by_cat=totals_by_cat,
        filters={"category": category, "start": start_date, "end": end_date},
    )

@app.post("/add")
def add_from_form():
    if not tracker:
        flash("Backend not connected.", "danger")
        return redirect(url_for("dashboard"))

    amount = (request.form.get("amount") or "").strip()
    category = (request.form.get("category") or "").strip()
    description = (request.form.get("description") or "").strip()
    date = (request.form.get("date") or "").strip()

    try:
        amount_val = float(amount)
    except ValueError:
        flash("Amount must be a number.", "danger")
        return redirect(url_for("dashboard"))

    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for("dashboard"))
        date_val = date
    else:
        date_val = None

    exp = Expense(amount_val, category, description, date_val)
    new_id = tracker.add_expense(exp)
    flash(f"Expense #{new_id} added.", "success")
    return redirect(url_for("dashboard"))

@app.get("/edit/<int:expense_id>")
def edit_page(expense_id):
    if not tracker:
        flash("Backend not connected.", "danger")
        return redirect(url_for("dashboard"))
    existing = tracker.get_expense_by_id(expense_id)
    if not existing:
        flash("Expense not found.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("edit.html", e=existing)

@app.post("/edit/<int:expense_id>")
def edit_save(expense_id):
    if not tracker:
        flash("Backend not connected.", "danger")
        return redirect(url_for("dashboard"))

    existing = tracker.get_expense_by_id(expense_id)
    if not existing:
        flash("Expense not found.", "danger")
        return redirect(url_for("dashboard"))

    amount = (request.form.get("amount") or str(existing[1])).strip()
    category = (request.form.get("category") or existing[2]).strip()
    description = (request.form.get("description") or existing[3]).strip()
    date = (request.form.get("date") or existing[4]).strip()

    try:
        amount_val = float(amount)
    except ValueError:
        flash("Amount must be a number.", "danger")
        return redirect(url_for("edit_page", expense_id=expense_id))

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        flash("Invalid date format. Use YYYY-MM-DD.", "danger")
        return redirect(url_for("edit_page", expense_id=expense_id))

    tracker.update_expense(expense_id, amount_val, category, description, date)
    flash(f"Expense #{expense_id} updated.", "success")
    return redirect(url_for("dashboard"))

@app.post("/delete/<int:expense_id>")
def delete_from_form(expense_id):
    if not tracker:
        flash("Backend not connected.", "danger")
        return redirect(url_for("dashboard"))
    existing = tracker.get_expense_by_id(expense_id)
    if not existing:
        flash("Expense not found.", "danger")
        return redirect(url_for("dashboard"))
    tracker.delete_expense(expense_id)
    flash(f"Expense #{expense_id} deleted.", "success")
    return redirect(url_for("dashboard"))

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
    print(">>> LOADING APP.PY (dashboard + filters + totals + add/edit/delete)")
    app.run(debug=True)
