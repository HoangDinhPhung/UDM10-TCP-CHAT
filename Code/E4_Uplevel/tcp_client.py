import socket #giaodienchatcoban
import threading

HOST = "127.0.0.1"
PORT = 8765

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            print("\nServer:", msg)
        except:
            print("Mat ket noi server")
            break

def send():
    while True:
        msg = input("Nhap tin nhan: ")
        client.send(msg.encode())

threading.Thread(target=receive).start()
threading.Thread(target=send).start()
