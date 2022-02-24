import hashlib
import socket
import os
import time
import unittest
import hmac

from flask import Flask, g, Response, request, abort
import flask_cors

from datetime import timezone, datetime
import logging

from models import DDNS, MySQL
from models.nctu_oauth import Oauth

from controllers.users import Users, UnauthorizedError
from controllers.dns  import DNS

from config import *

logging.basicConfig(encoding="utf-8", level=Logging_Level, filename="/var/log/flask.log",
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

def check_github_signature(payload, github_signature):
    key = bytes(GH_Secret, "utf-8")
    digester = hmac.new(key=key, msg=payload, digestmod=hashlib.sha256)
    signature = digester.hexdigest()
    return "sha256=" + signature == github_signature

@app.route("/sync_repo", methods=["POST"])
def sync_repo_endpoint():
    github_signature = request.headers.get("X-Hub-Signature-256")
    if not github_signature:
        abort(401)
    secret = hashlib.sha256()
    secret.update(GH_Secret.encode("utf-8"))
    if check_github_signature(request.data, github_signature):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(SocketFilePath)
        successful = False
        fail_count = 0
        while not successful and fail_count < 10:
            try:
                sock.sendall(b"update")
                time.sleep(0.2)
            except:
                pass
            else:
                successful = True
                sock.close()
        if not successful:
            abort(503)
        else:
            return ""
    else:
        abort(403)

#tests
@app.cli.command()
def test():
    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)

