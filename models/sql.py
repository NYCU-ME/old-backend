import datetime, time
import pymysql
import _thread
from pymysql.converters import escape_string

def check(func):
    def wrap(self, *args, **kwargs):
        try:
            res = func(self, *args, **kwargs)
            return res
        except pymysql.err.InterfaceError as e:
            self.status = False
            self._MySQL__connect()
            self.logger.critical(e.__str__())
    return wrap


class MySQL():

    @check
    def __commit(self):
        while True:
            self.db.commit()
            time.sleep(3)

    def __connect(self):
        while not self.status:
            try:
                self.db = pymysql.connect(
                    host = self.conf[0], 
                    user = self.conf[1], 
                    password = self.conf[2], 
                    database = self.conf[3])
                self.status = True
                _thread.start_new_thread(self.__commit, tuple())
            except Exception as e:
                self.logger.warning(e.__str__())
                time.sleep(2)
        self.logger.info("SQL connection established.")
        # raise Exception()

    def __init__(self, logger, host, user, password, database):
        self.conf = (host, user, password, database)
        self.status = False
        self.logger = logger
        self.__connect()

    @check
    def getUser(self, uid):
        with self.db.cursor() as cur:
            cur.execute("SELECT `id`, `name`, `username`, `status`, `email`, `limit` FROM `users` WHERE `id` = %s", (uid, ))
            return cur.fetchall()

    @check
    def newUser(self, uid, email, name = 'none', status = 'none'):
        with self.db.cursor() as cur:
            cur.execute("INSERT INTO `users` (`id`, `username`, `email`, `name`, `status`) VALUES (%s, %s, %s, %s, %s)", (uid, uid, email, name, status))

    @check
    def changeName(self, uid, name):
        with self.db.cursor() as cur:
            cur.execute("UPDATE `users` SET `username` = %s WHERE `id` = %s", (name, uid))

    @check
    def updateEmail(self, uid, email):
        with self.db.cursor() as cur:
            cur.execute("UPDATE `users` SET `email` = %s WHERE `id` = %s", (email, uid))

    @check
    def updateStatus(self, uid, status):
        with self.db.cursor() as cur:
            cur.execute("UPDATE `users` SET `status` = %s WHERE `id` = %s", (status, uid))

    @check
    def searchOutdate(self):
        with self.db.cursor() as cur:
            cur.execute("SELECT `id`, `userId`, `domain`, `regDate`, `expDate` FROM `domains` WHERE expDate < now() and status = 1;")
            return cur.fetchall()
    @check
    def listUserDomains(self, uid):
        with self.db.cursor() as cur:
            cur.execute("SELECT `id`, `userId`, `domain`, `regDate`, `expDate` FROM `domains` WHERE `userId` = %s and `status` = 1", (uid, ))
            return cur.fetchall()

    @check
    def searchDomain(self, domain):
        with self.db.cursor() as cur:
            cur.execute("SELECT `id`, `userId`, `domain`, `regDate`, `expDate` FROM `domains` WHERE `expDate` >= NOW() AND `domain` = %s", (domain, ))
            return cur.fetchall()

    @check
    def applyDomain(self, uid, domain):
        with self.db.cursor() as cur:
            cur.execute("INSERT INTO `domains` (`userID`, `domain`, `regDate`, `expDate`) VALUES (%s, %s, NOW(), DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 90 DAY), '%%Y-%%m-%%d 00:00:00'))", (uid, domain))

    @check
    def releaseDomain(self, domainId):
        with self.db.cursor() as cur:
            cur.execute("UPDATE `domains` SET `expDate` = NOW(), `status` = 0 WHERE `id` = %s", (domainId, ))

    @check
    def renewDomain(self, domainId):
        with self.db.cursor() as cur:
            cur.execute("UPDATE `domains` SET `expDate` = DATE_FORMAT(DATE_ADD(NOW(), INTERVAL 90 DAY), '%%Y-%%m-%%d 00:00:00') WHERE `id` = %s", (domainId, ))

    @check
    def listRecords(self, domainId, type_ = None):
        with self.db.cursor() as cur:
            if not type_:
                cur.execute("SELECT `type`, `value`, `ttl` FROM `records` WHERE expDate IS NULL and domain = %s", (domainId, ))
            else:
                cur.execute("SELECT `type`, `value`, `ttl` FROM `records` WHERE expDate IS NULL and domain = %s and type = %s", (domainId, type_))
            return cur.fetchall()
    @check
    def searchRecord(self, domainId, type_, value):
        with self.db.cursor() as cur:
            cur.execute("SELECT `type`, `value`, `ttl` FROM `records` WHERE expDate IS NULL AND domain = %s AND type = %s AND value = %s", (domainId, type_, value))
            return cur.fetchall()

    @check
    def addRecord(self, domainId, type_, value, ttl):
        with self.db.cursor() as cur:
            cur.execute("INSERT INTO `records` (`domain`, `type`, `value`, `ttl`, `regDate`) VALUES (%s, %s, %s, %s, NOW())", (domainId, type_, value, ttl))

    @check
    def delRecord(self, domainId, type_, value):
        with self.db.cursor() as cur:
            cur.execute("UPDATE `records` SET `expDate` = NOW(), `status` = 0 WHERE domain = %s and type = %s and value = %s", (domainId, type_, value))