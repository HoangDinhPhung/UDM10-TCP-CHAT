# server.py
# TCP Chat Server – Human Write Version
# Author: Hoàng Đình Phùng
# UDM-10 Project

import socket
import threading

clients = {}  # username -> socket
lock = threading.Lock()

def broadcast(sender, msg):
    """Gửi tin nhắn tới tất cả trừ sender"""
    with lock:
        for username, conn in clients.items():
            if username != sender:
                try:
                    conn.send(f"{sender} (all): {msg}".encode())
                except:
                    pass

def handle_client(conn, addr):
    username = None
    try:
        conn.send("Login using /login <username>\n".encode())
        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break

            if data.startswith("/login"):
                username_try = data.split()[1]
                with lock:
                    if username_try in clients:
                        conn.send("Username exists\n".encode())
                    else:
                        username = username_try
                        clients[username] = conn
                        conn.send("Login success\n".encode())
                        print(f"{username} connected from {addr}")

            elif data == "/list":
                with lock:
                    conn.send(("Online: " + ", ".join(clients.keys()) + "\n").encode())

            elif data.startswith("/msg"):
                parts = data.split()
                if len(parts) < 3:
                    conn.send("Usage: /msg <user> <message>\n".encode())
                    continue
                target = parts[1]
                msg = " ".join(parts[2:])
                with lock:
                    if target in clients:
                        clients[target].send(f"{username}: {msg}".encode())
                        conn.send(f"Message sent to {target}\n".encode())
                    else:
                        conn.send(f"User {target} not found\n".encode())

            elif data.startswith("/all"):
                msg = " ".join(data.split()[1:])
                broadcast(username, msg)
                conn.send("Message sent to all\n".encode())

            elif data == "/exit":
                break

            else:
                conn.send("Unknown command. Use /login, /list, /msg, /all, /exit\n".encode())

    finally:
        with lock:
            if username in clients:
                del clients[username]
        conn.close()
        if username:
            print(f"{username} disconnected")

def main():
    host = "127.0.0.1"
    port = 5000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"Server running at {host}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()