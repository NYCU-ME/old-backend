import datetime, time
import pymysql
import _thread
from pymysql.converters import escape_string

def check(func):
    def wrap(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except pymysql.OperationalError as e:
            self.status = False
            self.__connect()
            self.logger.warning(e.__str__())
        except Exception as e:
            self.logger.warning(e.__str__())
            self.db.rollback()
    return wrap

class MySQL():

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

    def __init__(self, logger, host, user, password, database):
        self.conf = (host, user, password, database)
        self.status = False
        self.diff = False
        self.logger = logger
        self.__connect()

    @check
    def getUser(self, uid):
        if type(uid) != int:
            x
            raise TypeError("wrong type for field `id`")

        cur = self.db.cursor()
        cur.execute("SELECT `id`, `name`, `username`, `status`, `email` FROM `users` WHERE `id` = %s", (uid, ))
        
        return cur.fetchall()

    @check
    def newUser(self, uid, email, name = 'none', status = 'none'):
        if type(uid) != int:
            raise TypeError("wrong type for field `id`")

        cur = self.db.cursor()
        cur.execute("INSERT INTO `users` (`id`, `username`, `email`, `name`, `status`) VALUES (%s, %s, %s, %s, %s)", (uid, uid, email, name, status))
        self.diff = True

    @check
    def changeName(self, uid, name):
        if type(uid) != int:
            raise TypeError("wrong type for field `id`")

        cur = self.db.cursor()
        cur.execute("UPDATE `users` SET `username` = %s WHERE `id` = %s", (name, uid))
        self.diff = True

    @check
    def updateEmail(self, uid, email):
        if type(uid) != int:
            raise TypeError("wrong type for field `id`")

        cur = self.db.cursor()
        cur.execute("UPDATE `users` SET `email` = %s WHERE `id` = %s", (email, uid))
        self.diff = True

    @check
    def updateStatus(self, uid, status):
        if type(uid) != int:
            raise TypeError("wrong type for field `id`")

        cur = self.db.cursor()
        cur.execute("UPDATE `users` SET `status` = %s WHERE `id` = %s", (status, uid))
        self.diff = True