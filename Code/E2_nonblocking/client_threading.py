import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break

            print(f"Received from {addr}: {data.decode()}")
            conn.sendall(data)

        except:
            break

    print(f"Disconnected {addr}")
    conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    print(f"Threading server listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()