#!/usr/bin/env bash
set -e
cd /home/ubuntu/threatlens-prototype
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
. .venv/bin/activate
pip install -q -r requirements.txt
python src/app.py
