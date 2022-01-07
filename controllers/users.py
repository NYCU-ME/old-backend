import jwt
import re
from enum import Enum
from datetime import timezone, datetime

domainRegex = re.compile(r"^[A-Za-z0-9_]{2,}$")

class UnauthorizedError(Exception):

    def __init__(self, msg):
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "Unauthorized: " + self.msg

class OperationErrors(Enum):
    NotAllowedDomain     = "NotAllowedDomain"
    NumberLimitExceed    = "NumberLimitExceed"
    AssignedDomainName   = "AssignedDomainName"
    PermissionDenied     = "PermissionDenied"
    ReservedDomain       = "ReservedDomain"

class OperationError(Exception):

    def __init__(self, typ, msg = ""):
        self.typ = str(typ)
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "%s: %s" % (self.typ, self.msg)


class Users:

    def __init__(self, logger, sql, secret, Allowed_DomainName = []):

        self.sql = sql
        self.logger = logger

        self.JWT_secretKey = secret
        self.domains = []

        for domain in Allowed_DomainName:
            self.domains.append(tuple(reversed(domain.split('.'))))

    def getUser(self, uid):

        user_data = self.sql.getUser(uid)
        
        if not user_data:    
            return None

        user = {}
        user['uid'], user['name'], user['username'], user['status'], user['email'], user['limit'] = user_data[0]

        return user

    def login(self, token):

        if not token:
            raise UnauthorizedError("not valid token")

        now = int(datetime.now(tz=timezone.utc).timestamp())
        token['iss'] = 'dns.nycu.me'
        token['exp'] = (now) + 3600
        token['iat'] = token['nbf'] = now
        token['uid'] = token['username']

        user = self.getUser(token['uid'])

        if user:

            if user['email'] != token['email']:
                self.sql.updateEmail(uid = token['uid'], email = token['email'])
            # if user['status'] != token['status']:
            #     pass                
            # if user['name'] != token['name']:
            #     pass

            token.update(user)
        else:
            self.sql.newUser(uid = token['uid'], email = token['email'])

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

    def authorize(self, user, action, domain):

        def check(domains, domain):
            
            for p in domain:
                # check if the domain is valid
                if not domainRegex.fullmatch(p):
                    return None
                if p[0] == '-' or p[-1] == '-':
                    return None

            def isMatch(rule, sample):
                # check if the domain is matching to a specific rule
                if len(rule) > len(sample):
                    return False
                
                for i in range(len(rule)):
                    if rule[i] == '*':
                        return len(sample) == i + 1
                    elif rule[i] == '':
                        return True
                    elif rule[i] != sample[i]:
                        return False
                return False

            # find a rule matching to this domain
            for can in domains:
                if isMatch(can, domain):
                    return can

            return None

        domainName = '.'.join(reversed(domain))
        domainInfo = self.sql.searchDomain('.'.join(reversed(domain[:3]))) # get level 3 domain
        level      = len(domain)

        if level <= 2 or not check(self.domains, domain): 
            # not a valid domain
            raise OperationError(OperationErrors.NotAllowedDomain, "%s is not allowed." % (domainName, ))

        if not user:
            return False

        # if user['uid'] == '109550028':
        #     # super user
        #     if action == "APPLY" and len(domainInfo) == 1:
        #         raise OperationError(OperationErrors.AssignedDomainName, "%s is being used." % (domainName, ))
        #     return True

        if level == 3 and len(domainInfo) == 0:
            # domain is free
            if len(self.sql.listUserDomains(user['uid'])) >= user['limit']:
                raise OperationError(OperationErrors.NumberLimitExceed, "You cannot apply for more domains")
            if len(domain[2]) <= 3:
                raise OperationError(OperationErrors.ReservedDomain, "Subdomains with its length no more than 3 are reserved.")

            return True
        elif len(domainInfo) == 1 and domainInfo[0][1] == user['uid']:
            if action == "APPLY":
                raise OperationError(OperationErrors.AssignedDomainName, "%s is being used." % (domainName, ))
            return True
        
        raise OperationError(OperationErrors.PermissionDenied, "You cannot modify domain %s." % (domainName, ))

