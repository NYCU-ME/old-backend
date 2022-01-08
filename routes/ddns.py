from flask import Response, request
from __main__ import app, g, users, dns
from controllers.users import OperationError
from controllers.dns import DNSError

@app.route("/ddns/<path:domain>/records/<string:type_>/<string:value>", methods=['POST'])
def addRecord(domain, type_, value):
    if not g.user:
        return {"message": "Unauth."}, 401

    user         = users.getUser(g.user['uid'])
    domainStruct = domain.strip('/').split('/')
    domainName   = '.'.join(reversed(domainStruct))
    domain       = dns.getDomain(domainName)

    req = request.json
    ttl = 5
    
    if req and 'ttl' in req:
        ttl = int(req[ttl])

    try:
        if not users.authorize(user, "MODIFY", domainStruct):
            return {"errorType": "PermissionDenied", "msg": ""}, 403
        dns.addRecord(user['uid'], domain, type_, value, ttl)
    except OperationError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403
    except DNSError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403

    return {"msg":"ok"}

@app.route("/ddns/<path:domain>/records/<string:type_>/<string:value>", methods=['DELETE'])
def delRecord(domain, type_, value):
    if not g.user:
        return {"message": "Unauth."}, 401

    user         = users.getUser(g.user['uid'])
    domainStruct = domain.strip('/').split('/')
    domainName   = '.'.join(reversed(domainStruct))
    domain       = dns.getDomain(domainName)

    try:
        if not users.authorize(user, "MODIFY", domainStruct):
            return {"errorType": "PermissionDenied", "msg": ""}, 403
        dns.delRecord(user['uid'], domain, type_, value)
    except OperationError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403
    except DNSError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403

    return {"msg":"ok"}
