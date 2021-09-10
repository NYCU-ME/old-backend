import jwt
from datetime import timezone, datetime

class UnauthorizedError(Exception):

    def __init__(self, msg):
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "Unauthorized: " + self.msg

class Users:

    def __init__(self, logger, sql, secret):
        self.sql = sql
        self.logger = logger
        self.JWT_secretKey = secret

    def login(self, token):

        if not token:
            raise UnauthorizedError("not valid token")

        now = int(datetime.now(tz=timezone.utc).timestamp())
        token['iss'] = 'dns.nycu.me'
        token['exp'] = (now) + 3600
        token['iat'] = token['nbf'] = now

        stuId   = int(token['username'])
        email   = token['email']
        # name    = token['name']
        # status  = token['status']

        oldData = self.sql.getUser(uid = stuId)

        if oldData and len(oldData):
            oldData = oldData[0]

            if oldData[4] != email:
                self.sql.updateEmail(uid = stuId, email = email)
            # if oldData['status'] != token['status']:
            #     pass                
            # if oldData['name'] != token['name']:
            #     pass

        else:
            self.sql.newUser(uid = stuId, email = email)

        token = jwt.encode(token, self.JWT_secretKey, algorithm="HS256")

        return token

    def authenticate(self, payload): 
        try:
            if not payload:
                raise UnauthorizedError("not logged")

            payload = payload.split(' ')

            if len(payload) != 2:
                raise UnauthorizedError("invalid payload")

            tokenType, token = payload

            if tokenType != 'Bearer': 
                raise UnauthorizedError("invalid payload")

            try:
                payload = jwt.decode(token, self.JWT_secretKey, algorithms=["HS256"])
            except Exception as e:
                raise UnauthorizedError(e.__repr__())
            
            return payload

        except UnauthorizedError as e:
            self.logger.warning(e.__str__())
            return None

