from flask import Response, request
from __main__ import app, g, users, nycu_oauth, dns


@app.route("/oauth/<string:code>", methods = ['GET'])
def getToken(code):
    token = nycu_oauth.get_token(code)
    if token:
        return {"token": users.login(nycu_oauth.get_profile(token))}
    else:
        return {"message": "Invalid code."}, 401


@app.route("/auth", methods = ['GET'])
def whoami():
    if g.user:
        res = g.user
        res['domains'] = []
        for domain in dns.listUserDomains(res['uid']):
            res['domains'].append({
                "id": domain[0],
                "domain": domain[1],
                "regDate": domain[2],
                "expDate": domain[3]})
        return res
    return {"message": "Unauth."}, 401
