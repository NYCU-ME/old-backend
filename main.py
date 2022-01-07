from flask import Flask, g, Response, request
import flask_cors

from datetime import timezone, datetime
import logging

from models import DDNS, MySQL
from models.nctu_oauth import Oauth

from controllers.users import Users, UnauthorizedError
from controllers.dns  import DNS

from config import *

logging.basicConfig(encoding="utf-8", level=Logging_Level,
                    format=Logging_Format, datefmt=Logging_DatetimeFormat)
app = Flask(__name__)
flask_cors.CORS(app)

#models
sql     = MySQL(logging.getLogger("SQL Models"), MySQL_Host, MySQL_User, MySQL_Pswd, MySQL_DB)
ddns    = DDNS(logging.getLogger("DDNS Models"), DDNS_KeyFile, DDNS_Server, DDNS_Zone)
nycu_oauth = Oauth(redirect_uri = NYCU_Oauth_rURL, 
                   client_id = NYCU_Oauth_ID, 
                   client_secret = NYCU_Oauth_key)

#controller
users   = Users(logging.getLogger("User Controller"), sql, JWT_secretKey, Allowed_DomainName)
dns     = DNS(logging.getLogger("DNS Controller"), sql, ddns, Allowed_RecordType)

#route
from routes import *

if __name__ == "__main__":
    app.run("127.0.0.1", port=8080, debug=True)

