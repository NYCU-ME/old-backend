from flask import Response, request
from __main__ import app, g, users

@app.route('/ddns/<path:domain>')
def newRecord(domain):
        return ".".join(reversed(domain.split("/"))) 
