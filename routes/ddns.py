from flask import Response, request
from __main__ import app, g, users, dns
from models.dns import DNSError, DNSErrors

@app.route("/ddns/<path:domain>", methods=['POST'])
def applyDomain(domain):
    if not g.user:
        return {"message": "Unauth."}, 401

    uid = g.user['uid']
    domain = domain.strip('/').split('/')

    try:
        dns.applyDomain(uid, domain)
    except DNSError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403

    return {"msg": "ok"}

@app.route("/ddns/<path:domain>", methods=['DELETE'])
def releaseDomain(domain):
    if not g.user:
        return {"message": "Unauth."}, 401

    uid = g.user['uid']
    domain = domain.strip('/').split('/')

    try:
        dns.releaseDomain(uid, domain)
    except DNSError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403

    return {"msg": "ok"}