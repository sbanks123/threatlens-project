import sqlite3
import hashlib
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "threatlens.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def event_hash(source: str, title: str, content: str) -> str:
    raw = f"{source}|{title}|{content}".encode("utf-8", errors="ignore")
    return hashlib.sha256(raw).hexdigest()


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_hash TEXT,
            source TEXT,
            title TEXT,
            content TEXT,
            credential_found INTEGER,
            infra_hit INTEGER,
            attack_intent_hit INTEGER,
            risky_source_hit INTEGER,
            score INTEGER,
            severity TEXT,
            confidence TEXT,
            urgency TEXT,
            sector TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute("PRAGMA table_info(events)")
    cols = {r[1] for r in cur.fetchall()}
    for col_def in [
        ("event_hash", "TEXT"),
        ("confidence", "TEXT"),
        ("urgency", "TEXT"),
        ("sector", "TEXT"),
    ]:
        if col_def[0] not in cols:
            cur.execute(f"ALTER TABLE events ADD COLUMN {col_def[0]} {col_def[1]}")

    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_events_event_hash ON events(event_hash)")
    conn.commit()
    conn.close()


def save_event(event):
    conn = get_conn()
    cur = conn.cursor()
    h = event_hash(event["source"], event["title"], event["content"])
    cur.execute(
        """
        INSERT OR IGNORE INTO events (
            event_hash, source, title, content,
            credential_found, infra_hit, attack_intent_hit, risky_source_hit,
            score, severity, confidence, urgency, sector
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            h,
            event["source"],
            event["title"],
            event["content"],
            int(event["credential_found"]),
            int(event["infra_hit"]),
            int(event["attack_intent_hit"]),
            int(event["risky_source_hit"]),
            event["score"],
            event["severity"],
            event.get("confidence", "LOW"),
            event.get("urgency", "LOW"),
            event.get("sector", "General"),
        ),
    )
    inserted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return inserted


def latest_events(limit=30):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def stats():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM events")
    total = cur.fetchone()[0]

    out = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    cur.execute("SELECT severity, COUNT(*) c FROM events GROUP BY severity")
    for sev, cnt in cur.fetchall():
        out[sev] = cnt

    cur.execute(
        """
        SELECT source, COUNT(*) c
        FROM events
        GROUP BY source
        ORDER BY c DESC
        LIMIT 1
        """
    )
    row = cur.fetchone()
    top_source = row[0] if row else "-"

    cur.execute(
        """
        SELECT sector, COUNT(*) c
        FROM events
        GROUP BY sector
        ORDER BY c DESC
        LIMIT 1
        """
    )
    row2 = cur.fetchone()
    top_sector = row2[0] if row2 else "General"

    conn.close()
    return {
        "total": total,
        "low": out["LOW"],
        "medium": out["MEDIUM"],
        "high": out["HIGH"],
        "critical": out["CRITICAL"],
        "top_source": top_source,
        "top_sector": top_sector,
    }


def sector_distribution(limit=8):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT sector, COUNT(*) c
        FROM events
        GROUP BY sector
        ORDER BY c DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = [{"sector": r[0] if r[0] else "General", "count": r[1]} for r in cur.fetchall()]
    conn.close()
    return rows


def daily_trend(days=7):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DATE(created_at) d, COUNT(*) c
        FROM events
        WHERE created_at >= datetime('now', ?)
        GROUP BY DATE(created_at)
        ORDER BY d ASC
        """,
        (f"-{days} day",),
    )
    rows = [{"day": r[0], "count": r[1]} for r in cur.fetchall()]
    conn.close()
    return rows


def reset_events():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM events")
    conn.commit()
    conn.close()
