import re
from enum import Enum

domainRegex = re.compile(r"^[A-Za-z0-9_]{2,}$")

class DNSErrors(Enum):
    NotAllowedDomain     = "NotAllowedDomain"
    NumberLimitExceed    = "NumberLimitExceed"
    AssignedDomainName   = "AssignedDomainName"
    PermissionDenied     = "PermissionDenied"
    NotAllowedRecordType = "NotAllowedRecordType"
    DuplicateRecord      = "DuplicateRecord" 

class DNSError(Exception):

    def __init__(self, typ, msg = ""):
        self.typ = str(typ)
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "%s: %s" % (self.typ, self.msg)

def check(domains, domain):

    for p in domain:
        if not domainRegex.fullmatch(p):
            return None
        if p[0] == '-' or p[-1] == '-':
            return None

    def isMatch(rule, sample):
    
        if len(rule) > len(sample):
            return False
        
        for i in range(len(rule)):
            if rule[i] == '*':
                if len(sample[i]) >= 4:
                    return len(sample) == i + 1 and True
                return False
            elif rule[i] == '':
                return True
            elif rule[i] != sample[i]:
                return False
        return False

    for can in domains:
        if isMatch(can, domain):
            return can

    return None

class DNS():

    def __init__(self, logger, sql, ddns, AllowedDomainName, AllowedRecordType, User_Max_DomainNum):
        
        self.logger  = logger
        self.sql     = sql
        self.ddns    = ddns
        
        self.rectypes = AllowedRecordType
        self.User_Max_DomainNum = User_Max_DomainNum
        self.domains = []
        for domain in AllowedDomainName:
            self.domains.append(tuple(reversed(domain.split('.'))))

    
    def listUserDomains(self, uid):
        
        return self.sql.listUserDomains(uid)

    def applyDomain(self, uid, domain):
        
        domainName = '.'.join(reversed([i.replace(".", r"\.") for i in domain]))

        if not check(self.domains, domain):
            raise DNSError(DNSErrors.NotAllowedDomain, "%s is not allowed." % (domainName, ))

        if len(self.sql.searchDomain(domainName)) >= 1:
            raise DNSError(DNSErrors.AssignedDomainName, "%s is used." % (domainName, ))
        
        if len(self.listUserDomains(uid)) >= self.User_Max_DomainNum:
            raise DNSError(DNSErrors.NumberLimitExceed)

        self.sql.applyDomain(uid, domainName)

    def releaseDomain(self, uid, domain):

        domainName = '.'.join(reversed([i.replace(".", r"\.") for i in domain]))

        if not check(self.domains, domain):
            raise DNSError(DNSErrors.NotAllowedDomain, "%s is not allowed." % (domainName, ))

        domain_entry = self.sql.searchDomain(domainName)

        if len(domain_entry) == 0:
            raise DNSError(DNSErrors.AssignedDomainName, "%s is not being used." % (domainName, ))

        if domain_entry[0][1] != uid:
            raise DNSError(DNSErrors.PermissionDenied, "You cannot release %s." % (domainName, ))

        self.sql.releaseDomain(domainName)

    def addRecord(self, uid, domain, type_, value, ttl):
        
        domainName = '.'.join(reversed([i.replace(".", r"\.") for i in domain]))
 
        if not check(self.domains, domain):
            raise DNSError(DNSErrors.NotAllowedDomain, "%s is not allowed." % (domainName, ))
        if not (domain := self.sql.searchDomain(domainName)):
            raise DNSError(DNSErrors.PermissionDenied, "You cannot add a new record to %s." % (domainName, ))

        domainId, domainOwner = domain[0][:2]

        if domainOwner != uid:
            raise DNSError(DNSErrors.PermissionDenied, "You cannot add a new record to %s." % (domainName,))
        
        if type_ not in self.rectypes:
            raise DNSError(DNSErrors.NotAllowedRecordType, "You cannot add a new record with type %s" % (type_, ))

        if self.sql.searchRecord(domainId, type_, value):
            raise DNSError(DNSErrors.DuplicateRecord, "You have created same record.")

        self.sql.addRecord(domainId, type_, value, ttl)
        self.ddns.addRecord(domainName, type_, value, ttl)

    def delRecord(self, uid, domain, type_, value):

        domainName = '.'.join(reversed([i.replace(".", r"\.") for i in domain]))
 
        if not check(self.domains, domain):
            raise DNSError(DNSErrors.NotAllowedDomain, "%s is not allowed." % (domainName, ))
        if not (domain := self.sql.searchDomain(domainName)):
            raise DNSError(DNSErrors.PermissionDenied, "You cannot modify %s." % (domainName, ))

        domainId, domainOwner = domain[0][:2]

        if domainOwner != uid:
            raise DNSError(DNSErrors.PermissionDenied, "You cannot modify %s." % (domainName,))
        
        if type_ not in self.rectypes:
            raise DNSError(DNSErrors.NotAllowedRecordType, "You cannot have a record with type %s" % (type_, ))

        if not self.sql.searchRecord(domainId, type_, value):
            raise DNSError(DNSErrors.DuplicateRecord, "No such record.")

        self.sql.delRecord(domainId, type_, value)
        self.ddns.delRecord(domainName, type_, value)
