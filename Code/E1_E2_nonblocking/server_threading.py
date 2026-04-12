import socket
import threading

HOST = "127.0.0.1"
PORT = 12345


def handle_client(conn, addr):
    print(f"[CONNECTED] {addr}")

    try:
        while True:
            data = conn.recv(1024)

            if not data:
                break

            try:
                message = data.decode("utf-8")
            except:
                message = str(data)

            print(f"[RECV] {addr}: {message}")

            conn.sendall(data)

    except Exception as e:
        print(f"[ERROR] {addr}: {e}")

    finally:
        print(f"[DISCONNECTED] {addr}")
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen()

    print(f"[SERVER STARTED] {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr),
            daemon=True
        )
        thread.start()


if __name__ == "__main__":
    start_server()