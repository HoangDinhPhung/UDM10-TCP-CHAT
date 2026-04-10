import socket

HOST = '127.0.0.1'
PORT = 12345
BUFFER_SIZE = 1024

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((HOST, PORT))
        print(f"[*] Kết nối thành công tới Server {HOST}:{PORT}")
        print("[*] Gõ '/exit' để thoát.\n")

        while True:
            try:
                msg = input("Client >> ").strip()
            except KeyboardInterrupt:
                print("\n[!] Người dùng thoát bằng Ctrl+C")
                break

            if not msg:
                continue

            if msg.lower() == "/exit":
                print("[!] Đang thoát...")
                break

            try:
                client_socket.sendall(msg.encode('utf-8'))
            except BrokenPipeError:
                print("[!] Server đã đóng kết nối.")
                break

            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                print("[!] Server đã ngắt kết nối.")
                break

            print(f"Server phản hồi: {data.decode('utf-8')}")

    except ConnectionRefusedError:
        print("[LỖI] Không thể kết nối. Hãy chắc chắn server đang chạy và port đúng!")
    except Exception as e:
        print(f"[LỖI] Đã xảy ra sự cố: {e}")
    finally:
        client_socket.close()
        print("[*] Socket đã đóng.")

if __name__ == "__main__":
    start_client()