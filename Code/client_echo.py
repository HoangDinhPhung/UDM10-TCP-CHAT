import socket

HOST = '127.0.0.1'
PORT = 12345

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

print("Connected to server")

while True:
    msg = input("Enter message: ")

    if msg.lower() == "exit":
        break

    s.sendall(msg.encode())

    data = s.recv(1024)
    print("Echo:", data.decode())

s.close()