from flask import Flask, g, Response, request
import flask_cors

from datetime import timezone, datetime

from nctu_oauth import Oauth
from modules import Logger, DDNS, MySQL
from user import Users, UnauthorizedError

from config import *

app = Flask(__name__)
flask_cors.CORS(app)


sql     = MySQL(Logger("SQL Module", app.logger), MySQL_Host, MySQL_User, MySQL_Pswd, MySQL_DB)
dns     = DDNS()
users   = Users(Logger("Users Module", app.logger), sql, JWT_secretKey)

nycu_oauth = Oauth(redirect_uri = NYCU_Oauth_rURL, 
                   client_id = NYCU_Oauth_ID, 
                   client_secret = NYCU_Oauth_key)

from routes import *

# https://id.nycu.edu.tw/o/authorize/?client_id=29ZuGjlHp2R4ctu7lKc6jwLLJjfxrXnuK7LzD55Z&response_type=code&scope=profile

@app.route('/ddns/<path:domain>')
def newRecord(domain):
    return ".".join(reversed(domain.split("/")))

@app.before_request
def before_request():
    g.user = users.authenticate(request.headers.get('Authorization'))

if __name__ == "__main__":
    app.run("127.0.0.1", port=8080, debug=True)

