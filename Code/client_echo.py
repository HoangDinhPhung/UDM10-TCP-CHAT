import socket
import sys

HOST = '127.0.0.1' 
PORT = 12345
BUFFER_SIZE = 1024

def start_client():
    # Khởi tạo TCP socket 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Kết nối tới server
        client_socket.connect((HOST, PORT))
        print(f"[*] Đã kết nối thành công tới Server {HOST}:{PORT}")
        print("[*] Gõ '/exit' để đóng kết nối.")

        # Vòng lặp gửi/nhận 
        while True:
            msg = input("Client nói: ").strip()
            
            if not msg:
                continue
                
            # Xử lý lệnh thoát
            if msg.lower() == "/exit":
                print("[!] Đang thoát...")
                break

            # Gửi dữ liệu đi
            client_socket.sendall(msg.encode('utf-8'))

            # Nhận phản hồi (Echo) từ server
            data = client_socket.recv(BUFFER_SIZE)
            
            if not data:
                print("[!] Server đã ngắt kết nối.")
                break
                
            print(f"[*] Server phản hồi: {data.decode('utf-8')}")

    except ConnectionRefusedError:
        print("[LỖI] Không thể kết nối. Hãy chắc chắn server_selectors.py đang chạy!")
    except Exception as e:
        print(f"[LỖI] Đã xảy ra sự cố: {e}")
    finally:
        # Đóng socket an toàn
        client_socket.close()
        print("[*] Socket đã đóng.")

if __name__ == "__main__":
    start_client()
