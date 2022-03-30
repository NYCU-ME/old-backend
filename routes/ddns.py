from flask import Response, request
from main import app, g, users, dns
from controllers.users import OperationError
from controllers.dns import DNSError

import re, ipaddress

domainRegex = re.compile(r'^([A-Za-z0-9]\.|[A-Za-z0-9][A-Za-z0-9-]{0,61}[A-Za-z0-9]\.){1,3}[A-Za-z]{2,6}$')

def isIP(addr, protocol = ipaddress.IPv4Address):
    try:
        ip = ipaddress.ip_address(addr)
        if isinstance(ip, protocol):
            return str(ip)
        return False
    except:
        return False

def isDomain(domain):
    return domainRegex.fullmatch(domain)

def checkType(type_, value):

    if type_ == 'A':
        if not isIP(value, ipaddress.IPv4Address):
            return {"errorType": "DNSError", "msg": "Type A with non-IPv4 value."}, 403

        value = isIP(value, ipaddress.IPv4Address)

    if type_ == 'AAAA':
        if not isIP(value, ipaddress.IPv6Address):
            return {"errorType": "DNSError", "msg": "Type AAAA with non-IPv6 value."}, 403

        value = isIP(value, ipaddress.IPv6Address)

    if type_ == 'CNAME' and not isDomain(value):
        return {"errorType": "DNSError", "msg": "Type CNAME with non-domain-name value."}, 403

    if type_ == 'MX' and not isDomain(value):
        return {"errorType": "DNSError", "msg": "Type MX with non-domain-name value."}, 403

    if type_ == 'TXT' and (len(value) > 255 or value.count('\n')):
        return {"errorType": "DNSError", "msg": "Type TXT with value longer than 255 chars or more than 1 line."}, 403

    return None


@app.route("/ddns/<path:domain>/records/<string:type_>/<string:value>", methods=['POST'])
def addRecord(domain, type_, value):

    if not g.user:
        return {"message": "Unauth."}, 401

    user         = users.getUser(g.user['uid'])
    domainStruct = domain.lower().strip('/').split('/')
    domainName   = '.'.join(reversed(domainStruct))
    domain       = dns.getDomain(domainName)

    req = request.json
    ttl = 5
    
    if req and 'ttl' in req and req['ttl'].isnumeric() and 0 < int(req['ttl']) <= 86400:
        ttl = int(req['ttl'])

    try:
        
        test = checkType(type_, value)
        if test:
            return test

        if not users.authorize(user, "MODIFY", domainStruct):
            return {"errorType": "PermissionDenied", "msg": ""}, 403

        dns.addRecord(domain, type_, value, ttl)
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
    domainStruct = domain.lower().strip('/').split('/')
    domainName   = '.'.join(reversed(domainStruct))
    domain       = dns.getDomain(domainName)

    try:
        test = checkType(type_, value)
        if test:
            return test

        if not users.authorize(user, "MODIFY", domainStruct):
            return {"errorType": "PermissionDenied", "msg": ""}, 403
        dns.delRecord(domain, type_, value)
    except OperationError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403
    except DNSError as e:
        return {"errorType": e.typ, "msg": e.msg}, 403

    return {"msg":"ok"}
