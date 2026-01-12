from flask import Flask, request, jsonify
import sqlite3
import bcrypt
import subprocess
import os
import re

app = Flask(__name__)

# SECRET via environment variable
SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret")

DATABASE = "users.db"


# ---------------------------
# Database connection helper
# ---------------------------
def get_db():
    return sqlite3.connect(DATABASE)


# ---------------------------
# LOGIN (Secure)
# ---------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "")
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Secure SQL (prepared statement)
    cursor.execute(
        "SELECT password FROM users WHERE username = ?",
        (username,)
    )

    row = cursor.fetchone()
    conn.close()

    if row and bcrypt.checkpw(password.encode(), row[0]):
        return jsonify({"status": "success", "user": username})

    return jsonify({"status": "error", "message": "Invalid credentials"}), 401


# ---------------------------
# PING (Secure)
# ---------------------------
@app.route("/ping", methods=["POST"])
def ping():
    host = request.json.get("host", "")

    # Input validation (allow only IP or domain)
    if not re.match(r"^[a-zA-Z0-9.-]+$", host):
        return jsonify({"error": "Invalid host"}), 400

    try:
        output = subprocess.check_output(
            ["ping", "-c", "1", host],
            stderr=subprocess.STDOUT,
            timeout=3
        )
        return jsonify({"output": output.decode()})
    except Exception:
        return jsonify({"error": "Ping failed"}), 500


# ---------------------------
# COMPUTE (No eval)
# ---------------------------
@app.route("/compute", methods=["POST"])
def compute():
    data = request.json.get("expression", "")

    # Allow only numbers + math operators
    if not re.match(r"^[0-9+\-*/(). ]+$", data):
        return jsonify({"error": "Invalid expression"}), 400

    try:
        result = eval(data, {"__builtins__": {}})
        return jsonify({"result": result})
    except Exception:
        return jsonify({"error": "Computation error"}), 400


# ---------------------------
# HASH PASSWORD (bcrypt)
# ---------------------------
@app.route("/hash", methods=["POST"])
def hash_password():
    pwd = request.json.get("password", "")

    if not pwd:
        return jsonify({"error": "Password required"}), 400

    hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
    return jsonify({"hash": hashed.decode()})


# ---------------------------
# READ FILE (restricted)
# ---------------------------
@app.route("/readfile", methods=["POST"])
def readfile():
    filename = request.json.get("filename", "")

    ALLOWED_FILES = ["test.txt"]

    if filename not in ALLOWED_FILES:
        return jsonify({"error": "Access denied"}), 403

    try:
        with open(filename, "r") as f:
            content = f.read()
        return jsonify({"content": content})
    except Exception:
        return jsonify({"error": "File not found"}), 404


# ---------------------------
# HELLO
# ---------------------------
@app.route("/hello", methods=["GET"])
def hello():
    return jsonify({"message": "Secure DevSecOps API"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
