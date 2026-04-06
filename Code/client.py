import asyncio
import socket

# ===== CONFIG =====
HOST = "127.0.0.1"
TCP_PORT = 12345
WS_PORT = 5000

# ===== TCP CLIENT =====
def tcp_client(port):
    BUFFER_SIZE = 1024
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, port))
        print(f"[*] Đã kết nối tới TCP Server {HOST}:{port}")
        print("[*] Gõ '/exit' để thoát.")
        while True:
            msg = input("TCP >> ").strip()
            if not msg:
                continue
            if msg.lower() == "/exit":
                break
            client_socket.sendall(msg.encode())
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                print("[!] Server đã ngắt kết nối.")
                break
            print(f"[*] Server phản hồi: {data.decode()}")
    except Exception as e:
        print("[LỖI]", e)
    finally:
        client_socket.close()
        print("[*] Socket TCP đã đóng.")

# ===== WEBSOCKET CLIENT =====
async def ws_client(port):
    try:
        reader, writer = await asyncio.open_connection(HOST, port)
        print(f"[CONNECTED] Connected to WebSocket Server {HOST}:{port}")

        # Nhập username
        data = await reader.read(100)
        print(data.decode(), end="")
        username = await asyncio.to_thread(input)
        writer.write((username + "\n").encode())
        await writer.drain()

        data = await reader.readline()
        print(data.decode().strip())

        # Song song send/receive
        async def receive(reader):
            try:
                while True:
                    data = await reader.readline()
                    if not data:
                        break
                    print(f"\n{data.decode().strip()}\n>> ", end="", flush=True)
            except:
                pass

        async def send(writer):
            try:
                while True:
                    msg = await asyncio.to_thread(input, ">> ")
                    if not msg:
                        continue
                    if msg.lower() == "/exit":
                        writer.write((msg + "\n").encode())
                        await writer.drain()
                        break
                    writer.write((msg + "\n").encode())
                    await writer.drain()
            except:
                pass

        await asyncio.gather(receive(reader), send(writer))
        writer.close()
        await writer.wait_closed()
    except Exception as e:
        print("[ERROR] Cannot connect:", e)

# ===== MAIN =====
if __name__ == "__main__":
    choice = input("Chọn client (1=TCP, 2=WebSocket): ").strip()
    if choice == "1":
        tcp_client(TCP_PORT)
    elif choice == "2":
        asyncio.run(ws_client(WS_PORT))
    else:
        print("Lựa chọn không hợp lệ.")