#!/usr/bin/env bash
set -e
sudo systemctl start threatlens.service
sudo systemctl --no-pager --full status threatlens.service | sed -n '1,12p'
