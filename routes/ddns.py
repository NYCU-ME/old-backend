from flask import Response, request
from __main__ import app, g, users, dns

@app.route('/ddns/<path:domain>')
def newRecord(domain):
    domain = domain.strip("/").split('/')
    print(domain)
    return '.'.join(reversed(domain))