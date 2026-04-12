import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

clients = {}
lock = threading.Lock()

def broadcast(message, sender=None):
    for client, name in clients.items():
        if name != sender:
            try:
                client.send(message.encode())
            except:
                client.close()

def handle_client(conn, addr):
    try:
        conn.send("Enter username: ".encode())
        username = conn.recv(1024).decode().strip()

        with lock:
            clients[conn] = username

        print(f"{username} connected from {addr}")

        conn.send(f"Welcome {username}!\n".encode())

        while True:
            msg = conn.recv(1024).decode()

            if not msg:
                break

            if msg.startswith("/list"):
                user_list = ", ".join(clients.values())
                conn.send(f"Online users: {user_list}\n".encode())

            elif msg.startswith("/msg"):
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    conn.send("Usage: /msg <user> <message>\n".encode())
                    continue

                target_user = parts[1]
                message = parts[2]

                found = False
                for client, name in clients.items():
                    if name == target_user:
                        client.send(f"[{username}] {message}\n".encode())
                        found = True
                        break

                if not found:
                    conn.send("User not found\n".encode())

            elif msg.startswith("/exit"):
                break

            else:
                broadcast(f"[{username}] {msg}", username)

    except:
        pass

    finally:
        with lock:
            if conn in clients:
                print(f"{clients[conn]} disconnected")
                del clients[conn]

        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server is running on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start_server() # TODO: improve input validation