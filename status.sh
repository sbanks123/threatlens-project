#!/usr/bin/env bash
set -e
sudo systemctl --no-pager --full status threatlens.service | sed -n '1,20p'
echo
echo -n "Health: "
curl -s http://127.0.0.1:8080/health || true
echo
