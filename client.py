# client.py
# TCP Chat Client – Human Write Version
# Author: Hoàng Đình Phùng
# UDM-10 Project

import socket
import threading

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print(msg)
        except:
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("127.0.0.1", 5000))  # phải trùng với port server

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    print("Commands: /login <username> | /list | /msg <user> <message> | /all <message> | /exit")
    
    while True:
        msg = input()
        if msg.lower() == "/exit":
            sock.send("/exit".encode())
            break
        sock.send(msg.encode())

if __name__ == "__main__":
    main()