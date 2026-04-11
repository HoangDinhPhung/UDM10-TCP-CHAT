import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if not message:
                break
            print(message)
        except:
            print("Disconnected from server")
            sock.close()
            break


def send_messages(sock):
    while True:
        try:
            message = input()
            sock.send(message.encode())

            if message == "/exit":
                sock.close()
                break
        except:
            break


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    send_messages(client)


if __name__ == "__main__":
    start_client()