from flask import Response, request
from main import app, g, users, nycu_oauth, dns

@app.before_request
def before_request():

    g.user = users.authenticate(request.headers.get('Authorization'))

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

        res = users.getUser(g.user['uid'])
        domains = []

        for domain in res['domains']:
            domains.append(dns.getDomain(domain))

        res['domains'] = domains
        
        return res

    return {"message": "Unauth."}, 401
