import socket
import ssl

HOST = "127.0.0.1"
PORT = 9000

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

print(f"[E5] SSL Server running at {PORT}")

while True:
    client_socket, addr = server.accept()
    ssl_client = context.wrap_socket(client_socket, server_side=True)

    print("Client connected:", addr)

    try:
        while True:
            data = ssl_client.recv(1024).decode()
            if not data:
                break

            print("Client:", data)
            ssl_client.send(f"Server: {data}".encode())

    except:
        pass

    ssl_client.close()
