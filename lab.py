"""Local-only educational SQL injection comparison. No third-party dependencies."""
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from pathlib import Path

def connect():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE users (username TEXT, password TEXT)")
    db.execute("INSERT INTO users VALUES (?, ?)", ("student", "demo-pass"))
    return db

def login(db, mode, username, password):
    if mode not in ("vulnerable", "secure"):
        raise ValueError("Unknown mode")
    if not username or not password:
        return {"success": False, "status": "empty_input"}
    try:
        if mode == "vulnerable":
            row = db.execute(
                f"SELECT username FROM users WHERE username = '{username}' AND password = '{password}'"
            ).fetchone()
        else:
            row = db.execute(
                "SELECT username FROM users WHERE username = ? AND password = ?",
                (username, password),
            ).fetchone()
        return {"success": row is not None, "status": "accepted" if row else "rejected"}
    except sqlite3.Error:
        return {"success": False, "status": "query_error"}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return
        data = Path(__file__).with_name("index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path not in ("/login/vulnerable", "/login/secure"):
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        if length > 4096:
            self.send_error(413)
            return
        fields = parse_qs(self.rfile.read(length).decode(), keep_blank_values=True)
        db = connect()
        try:
            result = login(db, self.path.rsplit("/", 1)[1],
                           fields.get("username", [""])[0], fields.get("password", [""])[0])
        finally:
            db.close()
        data = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)

if __name__ == "__main__":
    print("Open http://127.0.0.1:8765 — local educational demo only", flush=True)
    HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
