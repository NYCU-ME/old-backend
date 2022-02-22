from flask import Response, request
from main import app, g, users, dns
from controllers.users import OperationError
from controllers.dns import DNSError

@app.route("/domains/<path:domain>", methods=['POST'])
def applyDomain(domain):
    if not g.user:
        return {"message": "Unauth."}, 401

    user         = users.getUser(g.user['uid'])
    domainStruct = domain.strip('/').split('/')
    domainName   = '.'.join(reversed(domainStruct))
    domain       = dns.getDomain(domainName)

    try:
        if not users.authorize(user, "APPLY", domainStruct):
            return {"errorType": "PermissionDenied", "msg": ""}, 403
        dns.applyDomain(user['uid'], domain)
    except OperationError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403

    return {"msg": "ok"}

@app.route("/domains/<path:domain>", methods=['DELETE'])
def releaseDomain(domain):
    if not g.user:
        return {"message": "Unauth."}, 401

    user         = users.getUser(g.user['uid'])
    domainStruct = domain.strip('/').split('/')
    domainName   = '.'.join(reversed(domainStruct))
    domain       = dns.getDomain(domainName)

    try:
        if not users.authorize(user, "REPLEASE", domainStruct):
            return {"errorType": "PermissionDenied", "msg": ""}, 403
        dns.releaseDomain(domain)
    except OperationError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403

    return {"msg": "ok"}


@app.route("/renew/<path:domain>", methods=['POST'])
def renewDomain(domain):
    if not g.user:
        return {"message": "Unauth."}, 401

    user         = users.getUser(g.user['uid'])
    domainStruct = domain.strip('/').split('/')
    domainName   = '.'.join(reversed(domainStruct))
    domain       = dns.getDomain(domainName)

    try:
        if not users.authorize(user, "RENEW", domainStruct):
            return {"errorType": "PermissionDenied", "msg": ""}, 403
        dns.renewDomain(domain)
    except OperationError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403

    return {"msg": "ok"}



