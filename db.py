import sqlite3
import json
import math

DB_FILE = "resq.db"
MATCH_RADIUS_M = 300
MATCH_WINDOW_HOURS = 24

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            location_text TEXT,
            location_confidence TEXT,
            people_count INTEGER,
            situation TEXT,
            medical_details TEXT,
            needs TEXT,
            urgency INTEGER,
            languages TEXT,
            status TEXT,
            lat REAL,
            lng REAL,
            duplicate_of INTEGER,
            report_count INTEGER DEFAULT 1,
            verified INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # adds new columns to an older database file
    for col in ("duplicate_of INTEGER", "report_count INTEGER DEFAULT 1", "verified INTEGER DEFAULT 0"):
        try:
            conn.execute("ALTER TABLE requests ADD COLUMN " + col)
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()

def distance_m(lat1, lng1, lat2, lng2):
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

def find_match(lat, lng):
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, lat, lng FROM requests
           WHERE duplicate_of IS NULL AND status = 'open' AND lat IS NOT NULL
           AND created_at >= datetime('now', ?)""",
        ("-%d hours" % MATCH_WINDOW_HOURS,),
    ).fetchall()
    conn.close()
    best_id = None
    best_dist = MATCH_RADIUS_M
    for row in rows:
        d = distance_m(lat, lng, row["lat"], row["lng"])
        if d <= best_dist:
            best_id, best_dist = row["id"], d
    return best_id

def save_request(message, result, duplicate_of=None):
    coords = result.get("coordinates") or {}
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO requests
           (message, location_text, location_confidence, people_count, situation,
            medical_details, needs, urgency, languages, status, lat, lng, duplicate_of)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            message,
            result.get("location_text"),
            result.get("location_confidence"),
            result.get("people_count"),
            result.get("situation"),
            result.get("medical_details"),
            json.dumps(result.get("needs", [])),
            result.get("urgency"),
            json.dumps(result.get("languages", [])),
            result.get("status"),
            coords.get("lat"),
            coords.get("lng"),
            duplicate_of,
        ),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def merge_into(primary_id, result):
    conn = get_connection()
    row = conn.execute("SELECT * FROM requests WHERE id = ?", (primary_id,)).fetchone()
    needs = sorted(set(json.loads(row["needs"])) | set(result.get("needs", [])))
    urgency = max(row["urgency"] or 0, result.get("urgency") or 0)
    people = max(row["people_count"] or 0, result.get("people_count") or 0) or None
    medical = row["medical_details"] or result.get("medical_details")
    conn.execute(
        """UPDATE requests SET needs = ?, urgency = ?, people_count = ?,
           medical_details = ?, report_count = COALESCE(report_count, 1) + 1
           WHERE id = ?""",
        (json.dumps(needs), urgency, people, medical, primary_id),
    )
    conn.commit()
    conn.close()

def approve_request(request_id):
    conn = get_connection()
    conn.execute("UPDATE requests SET verified = 1 WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()

def get_all_requests():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM requests WHERE duplicate_of IS NULL ORDER BY urgency DESC, id DESC"
    ).fetchall()
    conn.close()
    items = []
    for row in rows:
        item = dict(row)
        item["needs"] = json.loads(item["needs"])
        item["languages"] = json.loads(item["languages"])
        items.append(item)
    return items