import socket
import select
import time
import logging

# --- Logging client events ---
logging.basicConfig(
    filename='logs/client_events.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

HOST = '127.0.0.1'
PORT = 8765
TIMEOUT = 300  # giây

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
server_socket.setblocking(False)

clients = {}  # {socket: {"addr": addr, "name": str, "last_active": timestamp}}

print(f"Server started on {HOST}:{PORT}")
logging.info(f"Server started on {HOST}:{PORT}")

while True:
    read_sockets, _, exception_sockets = select.select([server_socket]+list(clients.keys()), [], list(clients.keys()), 1)

    for notified_socket in read_sockets:
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            client_socket.setblocking(False)
            clients[client_socket] = {"addr": client_address, "name": None, "last_active": time.time()}
            logging.info(f"New connection from {client_address}")
        else:
            try:
                message = notified_socket.recv(1024)
                if not message:
                    raise ConnectionResetError()
                
                clients[notified_socket]["last_active"] = time.time()
                msg_text = message.decode('utf-8')

                # Broadcast
                if msg_text.startswith("broadcast:"):
                    content = msg_text.split("broadcast:",1)[1]
                    for sock in clients:
                        if sock != notified_socket:
                            sock.send(f"BROADCAST: {content}".encode())
                    logging.info(f"BROADCAST from {clients[notified_socket]['addr']}: {content}")

                # Private message
                elif msg_text.startswith("private:"):
                    _, target_name, content = msg_text.split(":", 2)
                    for sock, info in clients.items():
                        if info["name"] == target_name:
                            sock.send(f"PRIVATE from {clients[notified_socket]['addr']}: {content}".encode())
                            logging.info(f"PRIVATE from {clients[notified_socket]['addr']} to {target_name}: {content}")
                            break
            except:
                logging.info(f"Connection closed: {clients[notified_socket]['addr']}")
                del clients[notified_socket]
                notified_socket.close()

    # Timeout
    for sock, info in list(clients.items()):
        if time.time() - info["last_active"] > TIMEOUT:
            logging.info(f"Timeout: {info['addr']}")
            sock.close()
            del clients[sock]

    # Exceptions
    for sock in exception_sockets:
        logging.info(f"Exception: {clients[sock]['addr']}")
        sock.close()
        del clients[sock]