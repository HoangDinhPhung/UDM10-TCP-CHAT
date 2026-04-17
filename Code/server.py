import socket
import threading

clients = {}  # username -> socket

def handle_client(conn, addr):
    username = None

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            # LOGIN
            if data.startswith("LOGIN|"):
                username = data.split("|")[1]
                clients[username] = conn
                print(f"{username} connected")
                conn.send("OK".encode())

            # LIST
            elif data == "LIST":
                user_list = ",".join(clients.keys())
                conn.send(f"USER_LIST|{user_list}".encode())

            # SEND
            elif data.startswith("SEND|"):
                _, target, message = data.split("|", 2)

                if target in clients:
                    send_msg = f"MSG|{username}|{message}"
                    clients[target].send(send_msg.encode())
                else:
                    conn.send("ERROR|User not found".encode())

        except:
            break

    if username and username in clients:
        del clients[username]
        print(f"{username} disconnected")

    conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8888))
    server.listen(5)

    print("Server running...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()


if __name__ == "__main__":
    main()
