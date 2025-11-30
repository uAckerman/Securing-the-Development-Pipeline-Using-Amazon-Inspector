from flask import Flask, request, g, render_template_string
import sqlite3
import re
import html
import hashlib

app = Flask(__name__)
DATABASE = "clean.db"
app.secret_key = "secure-and-random-secret-key"


def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(_):
    db = getattr(g, "_db", None)
    if db:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password_hash TEXT
        );
        """)
        db.commit()

# @app.route("/login")
# def login():
#     username = request.args.get("user", "")
#     password = request.args.get("pass", "")

#     password_hash = hashlib.sha256(password.encode()).hexdigest()

#     cur = get_db().cursor()
#     cur.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, password_hash))
#     row = cur.fetchone()

#     return f"Login: {row is not None}"


# -----------------------------
# 1. SQL Injection
# -----------------------------
@app.route("/login")
def login():
    u = request.args.get("user", "")
    p = request.args.get("pass", "")

    query = f"SELECT * FROM users WHERE username='{u}' AND password='{p}'"
    cur = get_db().cursor()
    cur.execute(query)
    row = cur.fetchone()
    return f"Login result: {row}"

# -----------------------------
# 2. Reflected XSS
# -----------------------------
@app.route("/search")
def search():
    q = request.args.get("q", "")
    return render_template_string(f"<h2>You searched: {q}</h2>")


# -----------------------------
# 3. Insecure File Upload
# -----------------------------
@app.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("file")
    if not f:
        return "No file uploaded"

    f.save(f"uploads/{f.filename}")
    return f"Uploaded: {f.filename}"


# -----------------------------
# 4. Fake Command Injection
# -----------------------------
@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    return f"Simulated execution: ping {host}"


# -----------------------------
# 5. Insecure Deserialization
# -----------------------------
@app.route("/decode")
def decode():
    payload = request.args.get("data", "")
    decoded = base64.b64decode(payload).decode()
    obj = json.loads(decoded)
    return f"Decoded: {obj}"

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
