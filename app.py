import os
import sqlite3
from flask import Flask, g, jsonify, redirect, render_template, request, url_for

DB_PATH = os.environ.get("DB_PATH", "library.db")

app = Flask(__name__)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute(
            "CREATE TABLE IF NOT EXISTS issues ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "book TEXT NOT NULL, student TEXT NOT NULL,"
            "issued_on TEXT DEFAULT CURRENT_DATE, returned INTEGER DEFAULT 0)"
        )
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    like = f"%{q}%"
    rows = get_db().execute(
        "SELECT * FROM issues WHERE book LIKE ? OR student LIKE ? ORDER BY id DESC",
        (like, like),
    ).fetchall()
    return render_template("index.html", rows=rows, q=q)


@app.route("/add", methods=["POST"])
def add():
    book = request.form.get("book", "").strip()
    student = request.form.get("student", "").strip()
    if book and student:
        db = get_db()
        db.execute("INSERT INTO issues (book, student) VALUES (?, ?)", (book, student))
        db.commit()
    return redirect(url_for("index"))


@app.route("/return/<int:issue_id>", methods=["POST"])
def mark_returned(issue_id):
    db = get_db()
    db.execute("UPDATE issues SET returned = 1 WHERE id = ?", (issue_id,))
    db.commit()
    return redirect(url_for("index"))


@app.route("/api/issues")
def api_issues():
    rows = get_db().execute("SELECT * FROM issues ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
