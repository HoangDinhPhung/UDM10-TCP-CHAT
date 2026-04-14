import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

def client():
    s = socket.socket()
    s.connect((HOST, PORT))
    s.sendall(b"hello")
    print(s.recv(1024))
    s.close()

for _ in range(20):
    threading.Thread(target=client).start()
