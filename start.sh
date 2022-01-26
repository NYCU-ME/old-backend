#!/bin/bash
python -m gunicorn -w 4 -b 0.0.0.0:8080 main:app --daemon
echo $! > /var/run/nycume-api.pid
python sync_repo.py
