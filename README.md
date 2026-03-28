# ThreatLens

**ThreatLens** is a cyber threat intelligence MVP built for **Hack KRMU 5.0 (PS2)**:  
**Web Forum Threat Intelligence Scraper and Analyzer**.

It monitors selected public sources, detects potential leak/attack signals, scores risk, and surfaces prioritized alerts in a SOC-style dashboard.

---

## 🚩 Problem
Security teams often miss early warning signals because:
- Threat chatter is noisy and high-volume
- Manual monitoring is slow and inconsistent
- Raw keyword hits create too many false positives

ThreatLens solves this by converting noisy public signals into **actionable triage**.

---

## ✅ What this MVP does
- Automated source monitoring (scheduler-based)
- Credential leak signal detection (regex + entropy checks)
- Attack-intent and sector relevance tagging
- Risk scoring with:
  - **Severity** (LOW/MEDIUM/HIGH/CRITICAL)
  - **Confidence**
  - **Urgency**
- Deduplicated storage (event hash)
- Live SOC dashboard (filters + trends + sector distribution)
- CSV/TXT report export
- Optional webhook/email alerts for HIGH/CRITICAL events

---

## 🧠 Scoring logic (current)
- Credential signal: **+40**
- Infra keyword signal: **+30**
- Attack intent signal: **+20**
- Risky source context: **+10**

Severity mapping:
- 0–25 → LOW
- 26–50 → MEDIUM
- 51–75 → HIGH
- 76–100 → CRITICAL

---

## 🏗️ Architecture (MVP)
Sources → Ingestion → Detection Engine → Scoring → SQLite → Dashboard/Alerts/Reports

### Current source mode
- Curated demo dataset (`data/sample_posts.json`)
- Live RSS feeds (configurable)

---

## 🧰 Tech Stack
- **Backend:** Python, Flask
- **Scheduler:** APScheduler
- **Detection:** regex, entropy heuristics, keyword-intent logic
- **Database:** SQLite (easy upgrade path to PostgreSQL)
- **Server:** Gunicorn + Nginx + systemd
- **Frontend:** HTML/CSS/JS (custom SOC UI)

---

## 📁 Project structure
```text
threatlens-prototype/
├── data/
│   ├── sample_posts.json
│   └── threatlens.db
├── reports/
│   ├── latest_report.txt
│   └── latest_report.csv
├── src/
│   ├── app.py
│   ├── monitor.py
│   ├── ingest.py
│   ├── detector.py
│   ├── db.py
│   ├── alerter.py
│   ├── config.py
│   └── static/robot.mp4
├── templates/
│   └── dashboard.html
├── .env.example
├── requirements.txt
├── run.sh
├── start.sh
├── stop.sh
└── status.sh
```

---

## ⚙️ Local run
```bash
cd /home/ubuntu/threatlens-prototype
cp .env.example .env
./run.sh
```

Open:
- `http://localhost:8080` (if tunneled)
- `http://<server-ip>:8080` (direct)

---

## 🚀 Production run (already configured on VPS)
- Service: `threatlens.service`
- Proxy: Nginx on port 80

Public:
- `http://<server-ip>/`
- `http://<server-ip>/health`

Control:
```bash
/home/ubuntu/threatlens-prototype/start.sh
/home/ubuntu/threatlens-prototype/status.sh
/home/ubuntu/threatlens-prototype/stop.sh
```

---

## 🔌 API / Routes
### UI + control
- `GET /` → Dashboard
- `GET /run` → Trigger scan (redirects to UI unless JSON requested)
- `GET /demo/reset` → Clear events for demo
- `GET /demo/test-webhook` → Send webhook test

### Data APIs
- `GET /api/events` → Recent events
- `GET /api/stats` → Stats + sector distribution + trend
- `GET /health` → Health status

### Reports
- `GET /report/csv`
- `GET /report/txt`

---

## 🔐 Environment variables
See `.env.example`:
- `THREATLENS_INTERVAL_MIN`
- `THREATLENS_ENABLE_LIVE`
- `THREATLENS_LIVE_MAX_ITEMS`
- `THREATLENS_ADMIN_TOKEN`
- `THREATLENS_WEBHOOK_URL`
- SMTP settings for email alerts

---

## ⚠️ Scope note
This MVP is for **defensive threat monitoring** and **public-source intelligence**.  
It does not directly block attackers or notify end-users in the current version.

---

## 🛣️ Next roadmap
- More live connectors
- Better context NLP (spaCy/transformer path)
- SIEM/SOAR integration
- Role-based access + case management
- Enterprise-ready PostgreSQL + queue workers

---

## 👥 Team
**Team PHASER**  
Project: **ThreatLens**
