from flask import Flask, g, Response, request
import flask_cors

from datetime import timezone, datetime

from modules import Logger, DDNS, MySQL
from modules.nctu_oauth import Oauth

from models.users import Users, UnauthorizedError

from config import *

app = Flask(__name__)
flask_cors.CORS(app)

#modules

sql     = MySQL(Logger("SQL Module", app.logger), MySQL_Host, MySQL_User, MySQL_Pswd, MySQL_DB)
dns     = DDNS(Logger("DDNS Module", app.logger), DDNS_KeyFile, DDNS_Server, DDNS_Zone)
nycu_oauth = Oauth(redirect_uri = NYCU_Oauth_rURL, 
                   client_id = NYCU_Oauth_ID, 
                   client_secret = NYCU_Oauth_key)

#models

users   = Users(Logger("Users Controller", app.logger), sql, JWT_secretKey)

#controller

from routes import *

@app.before_request
def before_request():
    g.user = users.authenticate(request.headers.get('Authorization'))

if __name__ == "__main__":
    app.run("127.0.0.1", port=8080, debug=True)

