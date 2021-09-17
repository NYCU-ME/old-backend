import subprocess
import _thread
from queue import Queue
import time

verbose = 1

def print_log(msg, v = 1):
    if verbose >= v:
        print(msg)

class DDNS:

    def __launch(self):
        pr = subprocess.Popen(
            ['nsupdate', '-k', self.keyFile],
            bufsize = 0,
            stdin   = subprocess.PIPE,
            stdout  = subprocess.PIPE)
        
        if self.nServer: 
            pr.stdin.write(f"server {self.nServer}\n".encode())

        if self.zone: 
            pr.stdin.write(f"zone {self.zone}\n".encode())
    
        return pr
    
    def __write(self):
        diff = 0
        while True:
            try:
                while self.queue.qsize():
                    cmd = self.queue.get()
                    self.nsupdate.stdin.write((cmd + "\n").encode())
                    diff = 1
                    print_log(cmd, 3)

                    if self.nsupdate.poll():
                        self.queue.put(cmd)
                        self.nsupdate = self.__launch()
                        print_log("Subprocess nsupdate is dead.", 1)
                
                if diff and self.nsupdate.poll() == None:
                    diff = 0
                    self.nsupdate.stdin.write(b"send\n")
            
            except Exception as e:
                print_log(e, 1)
                print(e)
                raise Exception(e)

            time.sleep(5)

    def __init__(self, logger, keyFile, nServer, zone):
        self.logger  = logger
        self.keyFile = keyFile
        self.nServer = nServer
        self.zone    = zone

        self.nsupdate = self.__launch()
        self.queue = Queue()

        _thread.start_new_thread(self.__write, tuple())

    def addRecord(self, domain, rectype, value, ttl = 5):
        if domain != "" and rectype != "" and value != "":
            self.queue.put("update add %s %d %s %s" % (domain, ttl, rectype, value))

    def delRecord(self, domain, rectype, value):
        if domain != "":
            self.queue.put("update delete %s %s %s" % (domain, rectype, value))

if __name__ == "__main__":
    # for test
    nsupdate = DDNS()
    nsupdate.queue.put("update add api.nycu.me. 5 A 140.113.89.35")
    # nsupdate.queue.put("update delete a.b.nycu.me. A")
    # nsupdate.queue.put("update add test6.nycu.me. 5 A 8.8.8.8")
    # nsupdate.queue.put("update add test7.nycu.me. 5 A 1.1.1.1")
    while nsupdate.queue.qsize():
        time.sleep(1)
    print("Exiting")
    time.sleep(1)