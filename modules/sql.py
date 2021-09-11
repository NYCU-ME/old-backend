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
            if self.diff:
                self.diff = False
                self.db.commit()
            time.sleep(2)


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
        self.diff = False
        self.logger = logger
        self.__connect()

    @check
    def getUser(self, uid):
        cur = self.db.cursor()
        cur.execute("SELECT `id`, `name`, `username`, `status`, `email` FROM `users` WHERE `id` = %s", (uid, ))
        
        return cur.fetchall()

    @check
    def newUser(self, uid, email, name = 'none', status = 'none'):
        cur = self.db.cursor()
        cur.execute("INSERT INTO `users` (`id`, `username`, `email`, `name`, `status`) VALUES (%s, %s, %s, %s, %s)", (uid, uid, email, name, status))
        self.diff = True

    @check
    def changeName(self, uid, name):
        cur = self.db.cursor()
        cur.execute("UPDATE `users` SET `username` = %s WHERE `id` = %s", (name, uid))
        self.diff = True

    @check
    def updateEmail(self, uid, email):
        cur = self.db.cursor()
        cur.execute("UPDATE `users` SET `email` = %s WHERE `id` = %s", (email, uid))
        self.diff = True

    @check
    def updateStatus(self, uid, status):
        cur = self.db.cursor()
        cur.execute("UPDATE `users` SET `status` = %s WHERE `id` = %s", (status, uid))
        self.diff = True

    @check
    def listUserDomains(self, uid):
        cur = self.db.cursor()
        cur.execute("SELECT `id`, `domain`, `regDate` FROM `domains` WHERE `userId` = %s and `expDate` >= NOW()", (uid, ))
        return cur.fetchall()

    @check
    def searchDomain(self, domain):
        cur = self.db.cursor()
        cur.execute("SELECT `id`, `userID`, `regDate`, `expDate` FROM `domains` WHERE `expDate` >= NOW() AND `domain` = %s", (domain, ))
        return cur.fetchall()

    @check
    def applyDomain(self, uid, domain):
        cur = self.db.cursor()
        cur.execute("INSERT INTO `domains` (`userID`, `domain`, `regDate`, `expDate`) VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY))", (uid, domain))
        self.diff = True
