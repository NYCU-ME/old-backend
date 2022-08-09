import _thread
from enum import Enum
import time

class DNSErrors(Enum):

    NXDomain             = "Non-ExistentDomain"
    NotAllowedRecordType = "NotAllowedRecordType"
    DuplicatedRecord      = "DuplicatedRecord"
    NotAllowedOperation  = "NotAllowedOperation" 

class DNSError(Exception):

    def __init__(self, typ, msg = ""):
        self.typ = str(typ)
        self.msg = str(msg)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return "%s: %s" % (self.typ, self.msg)

class DNS():

    def __init__(self, logger, sql, ddns, AllowedRecordType):
        
        self.logger  = logger
        self.sql     = sql
        self.ddns    = ddns
        
        self.rectypes = AllowedRecordType
        _thread.start_new_thread(self.__check_outdate, tuple())

    def __listRecords(self, domainId, type_ = None):

        return self.sql.listRecords(domainId, type_)

    def __addRecord(self, domain, type_, value, ttl):

        self.sql.addRecord(domain['id'], type_, value, ttl)
        self.ddns.addRecord(domain['domainName'], type_, value, ttl)

    def __delRecord(self, domain, type_, value):

        self.sql.delRecord(domain['id'], type_, value)
        self.ddns.delRecord(domain['domainName'], type_, value)

    def __getDomain(self, domain_entry):

        domain = {}
        domain['id'], domain['userId'], domain['domainName'], domain['regDate'], domain['expDate'] = domain_entry
        domain['status'] = 1
        domain['records'] = []

        for rec in self.__listRecords(domain['id']):

            domain['records'].append({
                'type': rec[0],
                'value': rec[1],
                'ttl': rec[2]
                })

        return domain

    def __check_outdate(self):
        while True:
            try:
                for domain in self.sql.searchOutdate():
                    domain = self.__getDomain(domain)
                    self.logger.info("%s owned by %s has expired!" % (domain['domainName'], domain['userId']))
                    self.releaseDomain(domain)
            except Exception as e:
                self.logger.warning(e.__repr__())
            time.sleep(5)

    def getDomain(self, domainName):

        domain_entry = self.sql.searchDomain(domainName)
        domain = {'domainName': domainName, 'status': 0}
    
        if domain_entry:
            domain.update(self.__getDomain(domain_entry[0]))

        return domain

    def applyDomain(self, uid, domain):

        self.sql.applyDomain(uid, domain['domainName'])

    def renewDomain(self, domain):

        self.sql.renewDomain(domain['id'])

    def releaseDomain(self, domain):

        for i in self.__listRecords(domain['id']):
            type_, value, ttl = i
            self.__delRecord(domain, type_, value)

        self.sql.releaseDomain(domain['id'])

    def addRecord(self, domain, type_, value, ttl):
        
        if type_ not in self.rectypes:
            raise DNSError(DNSErrors.NotAllowedRecordType, "You cannot add a new record with type %s" % (type_, ))

        for rec in domain['records']:
            if rec['type'] == type_ and rec['value'] == value:
                raise DNSError(DNSErrors.DuplicatedRecord, "You have created same record.")

        self.__addRecord(domain, type_, value, ttl)

    def delRecord(self, domain, type_, value):

        if type_ not in self.rectypes:
            raise DNSError(DNSErrors.NotAllowedRecordType, "You cannot have a record with type %s" % (type_, ))

        flag = 1
        for rec in domain['records']:
            if rec['type'] == type_ and rec['value'] == value:
                flag = 0

        if flag:
            raise DNSError(DNSErrors.NotAllowedOperation, "You haven't created same record.")

        self.__delRecord(domain, type_, value)