import socket
import time
import os
from config import SocketFilePath, ServiceName

if os.path.exists(FILE):
    os.path.unlink(FILE)

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
sock.bind(SocketFilePath)
sock.listen(1)

while True:
    conn, addr = sock.accept()
    data = conn.recv(1024)
    time.sleep(1)
    code = 1
    fail_count = 0
    while code and fail_count < 10:
        code = os.system(f"git pull && service {ServiceName} restart")
        fail_count += 1
