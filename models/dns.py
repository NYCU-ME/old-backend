import re
from enum import Enum

class DNSErrors(Enum):
    NotAllowedDomain    = "NotAllowedDomain"
    NumberLimitExceed   = "NumberLimitExceed"
    AssignedDomainName  = "AssignedDomainName"

class DNSError(Exception):

    def __init__(self, typ, msg = ""):
        self.typ = str(typ)
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "%s: %s" % (self.typ, self.msg)

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

        for can in self.domains:
            if self.__isMatch(can, domain):
                return can
        return None

    def __init__(self, logger, sql, ddns, Allowed_DomainName, User_Max_DomainNum):
        self.logger  = logger
        self.sql     = sql
        self.ddns    = ddns
        
        self.User_Max_DomainNum = User_Max_DomainNum
        self.domains = []
        for domain in Allowed_DomainName:
            self.domains.append(tuple(reversed(domain.split('.'))))

        self.domainRegex = re.compile(r"^[A-Za-z0-9_]{2,}$")

    def applyDomain(self, uid, domain):
        
        domainName = '.'.join(reversed([i.replace(".", r"\.") for i in domain]))

        for p in domain:
            if not self.domainRegex.fullmatch(p):
                raise DNSError(DNSErrors.NotAllowedDomain, "%s is not allowed." % (domainName, ))

        if not self.__check(domain):
            raise DNSError(DNSErrors.NotAllowedDomain, "%s is not allowed." % (domainName, ))

        if len(self.sql.listUserDomains(uid)) >= self.User_Max_DomainNum:
            raise DNSError(DNSErrors.NumberLimitExceed)

        if len(self.sql.searchDomain(domainName)) >= 1:
            raise DNSError(DNSErrors.AssignedDomainName, "%s is used." % (domainName, ))

        self.sql.applyDomain(uid, domainName)

    def newRecord(self, uid, record):
        pass