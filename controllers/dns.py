import re
import _thread
from enum import Enum

domainRegex = re.compile(r"^[A-Za-z0-9_]{2,}$")

class DNSErrors(Enum):
    NXDomain    = "Non-ExistentDomain"
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

def check(domains, domain, allow3 = 0):

    for p in domain:
        if not domainRegex.fullmatch(p):
            return None
        if p[0] == '-' or p[-1] == '-':
            return None

    def isMatch(rule, sample, allow3):
    
        if len(rule) > len(sample):
            return False
        
        for i in range(len(rule)):
            if rule[i] == '*':
                if allow3 or len(sample[i]) >= 4:
                    return len(sample) == i + 1 and True
                return False
            elif rule[i] == '':
                return True
            elif rule[i] != sample[i]:
                return False
        return False

    for can in domains:
        if isMatch(can, domain, allow3):
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

    
    def __listUserDomains(self, uid):

        return self.sql.listUserDomains(uid)

    def __listRecords(self, domain, type_ = None):

        return self.sql.listRecords(domain, type_)

    def __addRecord(self, domainName, domainId, type_, value, ttl):
        self.sql.addRecord(domainId, type_, value, ttl)
        self.ddns.addRecord(domainName, type_, value, ttl)

    def __delRecord(self, domainName, domainId, type_, value):

        self.sql.delRecord(domainId, type_, value)
        self.ddns.delRecord(domainName, type_, value)

    def applyDomain(self, uid, domainName):

        self.sql.applyDomain(uid, domainName)

    def releaseDomain(self, uid, domainName):

        domain_entry = self.sql.searchDomain(domainName)
        domainId, domainOwner = domain_entry[0][:2]

        for i in self.__listRecords(domainId):
            type_, value, ttl = i
            self.__delRecord(domainName, domainId, type_, value)

        self.sql.releaseDomain(domainName)

    def addRecord(self, uid, domainName, type_, value, ttl):
        
        domain_entry = self.sql.searchDomain(domainName)
        
        if not domain_entry:
            raise DNSError(DNSErrors.NXDomain, "NXDomain")

        domainId, domainOwner = domain_entry[0][:2]

        if type_ not in self.rectypes:
            raise DNSError(DNSErrors.NotAllowedRecordType, "You cannot add a new record with type %s" % (type_, ))

        if self.sql.searchRecord(domainId, type_, value):
            raise DNSError(DNSErrors.DuplicateRecord, "You have created same record.")

        self.__addRecord(domainName, domainId, type_, value, ttl)

    def delRecord(self, uid, domainName, type_, value):

        domain_entry = self.sql.searchDomain(domainName)
        
        if not domain_entry:
            raise DNSError(DNSErrors.NXDomain, "NXDomain")

        domainId, domainOwner = domain_entry[0][:2]

        if type_ not in self.rectypes:
            raise DNSError(DNSErrors.NotAllowedRecordType, "You cannot have a record with type %s" % (type_, ))

        if not self.sql.searchRecord(domainId, type_, value):
            raise DNSError(DNSErrors.DuplicateRecord, "You haven't created such a record.")

        self.__delRecord(domainName, domainId, type_, value)