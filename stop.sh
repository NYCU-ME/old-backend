#!/bin/bash
kill -9 `cat /var/run/nycume-api.pid`
if [[ -e "/tmp/nycume-api.sock" ]]; then
    rm -f "/tmp/nycume-api.sock"
fi
