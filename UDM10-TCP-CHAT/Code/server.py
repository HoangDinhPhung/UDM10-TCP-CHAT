# server.py
# Author: Hoàng Đình Phùng Nhóm 7

# UDM-10 Project

import socket
import threading

clients = {}
lock = threading.Lock()

def handle_client(conn, addr):
    try:
        conn.send("Enter your username: ".encode())
        username = conn.recv(1024).decode().strip()

        with lock:
            if username in clients:
                conn.send("Username already taken. Disconnecting.".encode())
                conn.close()
                return
            clients[username] = conn

        conn.send(f"Welcome {username}! Type /exit to logout.".encode())
        print(f"{username} has connected from {addr}")

        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break

            if data.lower() == "/exit":
                break
            elif data.lower() == "/list":
                online_users = ", ".join(clients.keys())
                conn.send(f"Online users: {online_users}".encode())
            elif data.startswith("/msg"):
                parts = data.split()
                if len(parts) < 3:
                    conn.send("Usage: /msg username message".encode())
                    continue
                target_user = parts[1]
                message = " ".join(parts[2:])
                with lock:
                    if target_user in clients:
                        clients[target_user].send(f"{username}: {message}".encode())
                        conn.send(f"Message sent to {target_user}".encode())
                    else:
                        conn.send(f"User {target_user} not found.".encode())
            else:
                conn.send("Unknown command. Use /list, /msg, /exit".encode())
    finally:
        with lock:
            if username in clients:
                del clients[username]
        conn.close()
        print(f"{username} has disconnected.")

def main():
    host = "127.0.0.1"
    port = 5000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"Server is running on {host}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()