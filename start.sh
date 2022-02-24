#!/bin/bash
python3.9 -m gunicorn -w 4 -b 0.0.0.0:8080 main:app --daemon
echo $! > /var/run/nycume-api.pid
python3.9 sync_repo.py
