from flask import Flask, g, Response, request
import flask_cors

from datetime import timezone, datetime
import logging

from modules import DDNS, MySQL
from modules.nctu_oauth import Oauth

from models.users import Users, UnauthorizedError
from models.dns  import DNS

from config import *

logging.basicConfig(encoding="utf-8", level=Logging_Level,
                    format=Logging_Format, datefmt=Logging_DatetimeFormat)
app = Flask(__name__)
flask_cors.CORS(app)

#modules
sql     = MySQL(logging.getLogger("SQL Module"), MySQL_Host, MySQL_User, MySQL_Pswd, MySQL_DB)
ddns    = DDNS(logging.getLogger("DDNS Module"), DDNS_KeyFile, DDNS_Server, DDNS_Zone)
nycu_oauth = Oauth(redirect_uri = NYCU_Oauth_rURL, 
                   client_id = NYCU_Oauth_ID, 
                   client_secret = NYCU_Oauth_key)

#models
users   = Users(logging.getLogger("User Models"), sql, JWT_secretKey)
dns     = DNS(logging.getLogger("DNS Models"), sql, ddns, Allowed_DomainName, 
                                                          Allowed_RecordType, 
                                                          User_Max_DomainNum)

#controller
@app.before_request
def before_request():
    g.user = users.authenticate(request.headers.get('Authorization'))

from routes import *

if __name__ == "__main__":
    app.run("127.0.0.1", port=8080, debug=True)

