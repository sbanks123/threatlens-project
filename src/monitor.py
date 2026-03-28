import csv
from pathlib import Path
from datetime import datetime, UTC
from dotenv import load_dotenv

from ingest import fetch_posts
from detector import analyze
from db import init_db, save_event, latest_events
from alerter import send_webhook, send_email

BASE = Path(__file__).resolve().parents[1]
REPORT_FILE = BASE / "reports" / "latest_report.txt"
CSV_FILE = BASE / "reports" / "latest_report.csv"
load_dotenv(BASE / ".env")


def run_once(notify=True):
    init_db()

    posts = fetch_posts()
    print(f"POSTS LOADED: {len(posts)}")

    inserted = 0
    alert_count = 0

    for p in posts:
        event = analyze(
            source=p.get("source", "unknown"),
            title=p.get("title", ""),
            content=p.get("content", ""),
        )

        is_new = save_event(event)

        if is_new:
            inserted += 1

            if notify and event["severity"] in ("HIGH", "CRITICAL"):
                msg = (
                    f"[ThreatLens] {event['severity']} | score={event['score']} | "
                    f"confidence={event['confidence']} | urgency={event['urgency']}\n"
                    f"sector={event['sector']} | source={event['source']}\n"
                    f"title={event['title']}"
                )
                send_webhook(msg)
                send_email(f"ThreatLens {event['severity']} Alert", msg)
                alert_count += 1

    rows = latest_events(limit=20)

    lines = [
        "ThreatLens Prototype Report",
        "=" * 60,
        f"Generated: {datetime.now(UTC).isoformat()}",
        f"New events inserted: {inserted}",
        f"Alerts sent: {alert_count}",
        "",
    ]

    for r in rows:
        lines.append(
            f"[{r['severity']}] score={r['score']} conf={r.get('confidence', '-')} "
            f"urg={r.get('urgency', '-')} sector={r.get('sector', 'General')} | "
            f"{r['source']} | {r['title']}"
        )

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")

    with CSV_FILE.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["id", "severity", "score", "confidence", "urgency", "sector", "source", "title", "created_at"]
        )
        for r in rows:
            w.writerow([
                r["id"],
                r["severity"],
                r["score"],
                r.get("confidence", "-"),
                r.get("urgency", "-"),
                r.get("sector", "General"),
                r["source"],
                r["title"],
                r["created_at"],
            ])

    return {"inserted": inserted, "alerts": alert_count, "rows": rows}


if __name__ == "__main__":
    result = run_once(notify=False)
    print("ThreatLens run complete:", result)