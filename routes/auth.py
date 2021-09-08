from flask import Response, request
from __main__ import app, g, sql, dns, users, nycu_oauth


@app.route('/oauth/<string:code>', methods = ['GET'])
def getToken(code):
    token = nycu_oauth.get_token(code)
    if token:
        return users.login(nycu_oauth.get_profile(token))
    else:
        return {"message": "Invalid code."}, 401


@app.route("/auth")
def whoami():
    if g.user:
        return g.user
    return {"message": "Unauth."}, 401
