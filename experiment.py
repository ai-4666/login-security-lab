"""Generate measured results and verify regression expectations."""
import csv
import json
from pathlib import Path
from lab import connect, login

CASES = [
    ("normal", "student", "demo-pass", True, True),
    ("wrong_password", "student", "wrong", False, False),
    ("unknown_user", "nobody", "wrong", False, False),
    ("empty_username", "", "demo-pass", False, False),
    ("empty_password", "student", "", False, False),
    ("quote_error", "'", "wrong", False, False),
    ("login_bypass", "student' -- ", "wrong", True, False),
    ("ordinary_apostrophe", "o'connor", "wrong", False, False),
]
def run():
    rows = []
    db = connect()
    try:
        for case, username, password, expected_v, expected_s in CASES:
            for mode, expected in (("vulnerable", expected_v), ("secure", expected_s)):
                result = login(db, mode, username, password)
                assert result["success"] is expected, (case, mode, result)
                rows.append(dict(case=case, mode=mode, username=username,
                                 password=password, **result))
        assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert login(db, "secure", "'", "wrong")["status"] == "rejected"
    finally:
        db.close()
    Path("results").mkdir(exist_ok=True)
    with open("results/results.csv", "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    Path("results/results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"PASS: {len(rows)} comparisons; database intact; secure quote handling verified")
if __name__ == "__main__":
    run()
