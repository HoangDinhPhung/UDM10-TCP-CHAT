import selectors
import socket

HOST, PORT = '0.0.0.0', 5000
sel = selectors.DefaultSelector()

def accept(sock):
    conn, addr = sock.accept()
    print(f"Connected: {addr}")
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)

def read(conn):
    try:
        data = conn.recv(1024)
        if data:
            conn.sendall(data)  # echo back
        else:
            sel.unregister(conn)
            conn.close()
    except ConnectionResetError:
        sel.unregister(conn)
        conn.close()

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    server_sock.setblocking(False)
    sel.register(server_sock, selectors.EVENT_READ, accept)

    print(f"Server listening on {HOST}:{PORT}")
    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj)

if __name__ == "__main__":
    main()
