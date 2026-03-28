import os
from pathlib import Path
from flask import Flask, jsonify, render_template, request, send_file, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from db import init_db, latest_events, stats, reset_events, sector_distribution, daily_trend
from monitor import run_once
from alerter import send_webhook

BASE = Path(__file__).resolve().parents[1]
REPORT_TXT = BASE / "reports" / "latest_report.txt"
REPORT_CSV = BASE / "reports" / "latest_report.csv"
load_dotenv(BASE / ".env")

app = Flask(__name__, template_folder=str(BASE / "templates"))
init_db()

scheduler = BackgroundScheduler(timezone="UTC")
interval = int(os.getenv("THREATLENS_INTERVAL_MIN", "30"))
scheduler.add_job(lambda: run_once(notify=True), "interval", minutes=interval, id="threatlens-scan", replace_existing=True)
scheduler.start()


def _is_demo_admin(req):
    token = os.getenv("THREATLENS_ADMIN_TOKEN", "").strip()
    if not token:
        return True
    got = req.args.get("token", "") or req.headers.get("x-threatlens-token", "")
    return got == token


@app.route("/")
def home():
    data_stats = stats()
    return render_template(
        "dashboard.html",
        stats=data_stats,
        events=latest_events(60),
        interval=interval,
        sectors=sector_distribution(),
        trend=daily_trend(7),
    )

@app.route("/run")
def run_now():
    import traceback

    try:
        result = run_once(notify=False)
        wants_json = (
            request.args.get("format") == "json"
            or "application/json" in (request.headers.get("Accept") or "")
        )
        if wants_json:
            return jsonify({"ok": True, **result})
        return redirect(url_for("home"))
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/demo/reset")
def demo_reset():
    if not _is_demo_admin(request):
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    reset_events()
    if request.args.get("format") == "json":
        return jsonify({"ok": True, "message": "events reset"})
    return redirect(url_for("home"))


@app.route("/demo/test-webhook")
def demo_test_webhook():
    if not _is_demo_admin(request):
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    ok, msg = send_webhook("[ThreatLens] Webhook test message")
    return jsonify({"ok": ok, "message": msg})


@app.route("/report/txt")
def report_txt():
    if not REPORT_TXT.exists():
        run_once(notify=False)
    return send_file(REPORT_TXT, as_attachment=True)


@app.route("/report/csv")
def report_csv():
    if not REPORT_CSV.exists():
        run_once(notify=False)
    return send_file(REPORT_CSV, as_attachment=True)


@app.route("/api/events")
def api_events():
    return jsonify(latest_events(80))


@app.route("/api/stats")
def api_stats():
    return jsonify(
        {
            "stats": stats(),
            "sectors": sector_distribution(),
            "trend": daily_trend(7),
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "threatlens"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
