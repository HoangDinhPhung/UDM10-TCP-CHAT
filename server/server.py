import socket
import threading

HOST = "0.0.0.0"
PORT = 5000

clients = {}
connections = []

def broadcast(message, sender=None):
    for conn in connections:
        if conn != sender:
            try:
                conn.send(message.encode())
            except:
                pass


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr}")

    # login username
    username = conn.recv(1024).decode()
    clients[conn] = username
    connections.append(conn)

    print(f"{username} joined the chat.")

    broadcast(f"{username} joined the chat.", conn)

    while True:
        try:
            message = conn.recv(1024).decode()

            if message == "/list":
                user_list = ", ".join(clients.values())
                conn.send(f"Online: {user_list}".encode())

            elif message.startswith("/msg"):
                parts = message.split(" ", 2)

                if len(parts) < 3:
                    conn.send("Usage: /msg username message".encode())
                    continue

                target_name = parts[1]
                msg = parts[2]

                for c, name in clients.items():
                    if name == target_name:
                        c.send(f"[Private] {clients[conn]}: {msg}".encode())
                        break

            elif message == "/exit":
                break

            else:
                broadcast(f"{clients[conn]}: {message}", conn)

        except:
            break

    print(f"{clients[conn]} disconnected.")
    connections.remove(conn)
    del clients[conn]
    conn.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print("Server started...")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(target=handle_client, args=(conn, addr))
    thread.start()
