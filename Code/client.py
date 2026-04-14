import socket
import threading
import asyncio

HOST = "127.0.0.1"
TCP_PORT = 12345
WS_PORT = 5000

def receive_messages(sock):
    try:
        while True:
            message = sock.recv(1024).decode()
            if not message:
                break
            print(message)
    except:
        pass
    finally:
        print("Disconnected from server")
        sock.close()


def send_messages(sock):
    try:
        while True:
            message = input()
            sock.send(message.encode())

            if message == "/exit":
                sock.close()
                break
    except:
        pass


def tcp_thread_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, WS_PORT))  # dùng 5000 cho chat server

    threading.Thread(
        target=receive_messages,
        args=(client,),
        daemon=True
    ).start()

    send_messages(client)


def tcp_client(port):
    BUFFER_SIZE = 1024
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, port))
        print(f"[*] Connected TCP {HOST}:{port}")

        while True:
            msg = input("TCP >> ").strip()
            if not msg:
                continue
            if msg.lower() == "/exit":
                break

            client_socket.sendall(msg.encode())
            data = client_socket.recv(BUFFER_SIZE)

            if not data:
                break

            print("SERVER:", data.decode())

    except Exception as e:
        print("[ERROR]", e)

    finally:
        client_socket.close()


#
async def ws_client(port):
    try:
        reader, writer = await asyncio.open_connection(HOST, port)

        print(f"[CONNECTED] {HOST}:{port}")

        data = await reader.read(100)
        print(data.decode(), end="")

        username = await asyncio.to_thread(input)
        writer.write((username + "\n").encode())
        await writer.drain()

        async def receive():
            while True:
                data = await reader.readline()
                if not data:
                    break
                print("\n" + data.decode().strip())

        async def send():
            while True:
                msg = await asyncio.to_thread(input, ">> ")
                if msg == "/exit":
                    writer.write(b"/exit\n")
                    await writer.drain()
                    break
                writer.write((msg + "\n").encode())
                await writer.drain()

        await asyncio.gather(receive(), send())

        writer.close()
        await writer.wait_closed()

    except Exception as e:
        print("[ERROR]", e)


if __name__ == "__main__":
    print("1. TCP Thread Client")
    print("2. TCP Simple Client")
    print("3. Async Client")

    choice = input("Choose: ").strip()

    if choice == "1":
        tcp_thread_client()
    elif choice == "2":
        tcp_client(TCP_PORT)
    elif choice == "3":
        asyncio.run(ws_client(WS_PORT))
    else:
        print("Invalid choice")