import re
from enum import Enum

class err(Enum):
    NotAllowedDomain    = "NotAllowedDomain"
    NumberLimitExceed   = "NumberLimitExceed"

class DNSError(Exception):

    def __init__(self, typ, msg = ""):
        self.typ = str(typ)
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "%s: %s" % (self.typ.name, self.msg)

class DNS():
    
    def __isMatch(self, rule, sample):
        if len(rule) > len(sample):
            return False
        
        for i in range(len(rule)):
            if rule[i] == '*':
                continue
            elif rule[i] == '':
                return True
            elif rule[i] != sample[i]:
                return False
        return False

    def __check(self, domain):
        
        regex = r"/^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/ig"

        if not re.fullmatch(regex, domain):
            return None

        for can in self.domains:
            if self.__isMatch(can, self.domains):
                return can
        return None

    def __init__(self, logger, sql, ddns, Allowed_DomainName, User_Max_DomainNum):
        self.logger  = logger
        self.sql     = sql
        self.ddns    = ddns
        self.domains = []
        for domain in Allowed_DomainName:
            self.domains.append(tuple(reversed(domain.strip('.').split('.'))))

    def applyDomain(self, uid, domain):
        if type(uid) != int:
            raise TypeError("wrong type for field `id`")

        if not __check(domain):
            raise DNSError(err.NotAllowedDomain, domain)

        if len(self.sql.searchDomains(uid)) >= User_Max_DomainNum:
            raise DNSError(err.NumberLimitExceed)
        

    def newRecord(self, uid, record):
        pass