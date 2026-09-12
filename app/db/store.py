import json, os, sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(os.getenv("AURA_DB_PATH", "aura.db"))

def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS cases (
      case_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, payload TEXT NOT NULL,
      created_at TEXT NOT NULL, updated_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS audit_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL,
      event_type TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS actions (
      id INTEGER PRIMARY KEY AUTOINCREMENT, case_id TEXT NOT NULL,
      action TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL
    );
    ''')
    c.commit(); c.close()

def save_case(case_id, customer_id, payload):
    now = datetime.now(timezone.utc).isoformat()
    c = _conn(); c.execute("INSERT OR REPLACE INTO cases VALUES (?,?,?,?,?)", (case_id, customer_id, json.dumps(payload), now, now)); c.commit(); c.close()

def get_case(case_id):
    c = _conn(); row = c.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone(); c.close()
    return json.loads(row["payload"]) if row else None

def audit(case_id, event_type, detail):
    now = datetime.now(timezone.utc).isoformat()
    c = _conn(); c.execute("INSERT INTO audit_events(case_id,event_type,detail,created_at) VALUES(?,?,?,?)", (case_id,event_type,detail,now)); c.commit(); c.close()

def action(case_id, name, status):
    now = datetime.now(timezone.utc).isoformat()
    c = _conn(); c.execute("INSERT INTO actions(case_id,action,status,created_at) VALUES(?,?,?,?)", (case_id,name,status,now)); c.commit(); c.close()

def events(case_id):
    c = _conn(); rows = c.execute("SELECT event_type,detail,created_at FROM audit_events WHERE case_id=? ORDER BY id", (case_id,)).fetchall(); c.close()
    return [dict(r) for r in rows]
