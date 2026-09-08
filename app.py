from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "it_support.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee TEXT NOT NULL,
            issue TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_name TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            employee TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Add sample assets only when database is empty
    count = conn.execute(
        "SELECT COUNT(*) FROM assets"
    ).fetchone()[0]

    if count == 0:
        conn.execute("""
            INSERT INTO assets
            (asset_name, asset_type, employee, status)
            VALUES (?, ?, ?, ?)
        """, ("Dell Laptop", "Laptop", "Dhanam", "Assigned"))

        conn.execute("""
            INSERT INTO assets
            (asset_name, asset_type, employee, status)
            VALUES (?, ?, ?, ?)
        """, ("HP Desktop", "Desktop", "Available", "Available"))

    conn.commit()
    conn.close()


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/create-ticket", methods=["POST"])
def create_ticket():

    data = request.get_json()

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO tickets
        (employee, issue, priority, status)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("employee"),
        data.get("issue"),
        data.get("priority"),
        "Pending"
    ))

    ticket_id = cursor.lastrowid

    conn.commit()
    conn.close()

    ticket = {
        "id": ticket_id,
        "employee": data.get("employee"),
        "issue": data.get("issue"),
        "priority": data.get("priority"),
        "status": "Pending"
    }

    return jsonify({
        "message": "Ticket created successfully",
        "ticket": ticket
    })


@app.route("/tickets")
def get_tickets():

    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM tickets
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/add-asset", methods=["POST"])
def add_asset():

    data = request.get_json()

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO assets
        (asset_name, asset_type, employee, status)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("asset_name"),
        data.get("asset_type"),
        data.get("employee"),
        "Assigned"
    ))

    asset_id = cursor.lastrowid

    conn.commit()
    conn.close()

    asset = {
        "id": asset_id,
        "asset_name": data.get("asset_name"),
        "asset_type": data.get("asset_type"),
        "employee": data.get("employee"),
        "status": "Assigned"
    }

    return jsonify({
        "message": "Asset added successfully",
        "asset": asset
    })


@app.route("/assets")
def get_assets():

    conn = get_db()

    rows = conn.execute("""
        SELECT * FROM assets
        ORDER BY id
    """).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


if __name__ == "__main__":
    init_db()
    app.run(debug=True)