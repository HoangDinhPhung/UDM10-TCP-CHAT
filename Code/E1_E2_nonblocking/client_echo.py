import socket
import sys

HOST = '127.0.0.1' 
PORT = 5000
BUFFER_SIZE = 1024

def start_client():
    # Khởi tạo TCP socket 
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:

        client_socket.connect((HOST, PORT))
        print(f"[*] Đã kết nối thành công tới Server {HOST}:{PORT}")
        print("[*] Gõ '/exit' để đóng kết nối.")


        while True:
            msg = input("Client nói: ").strip()
            
            if not msg:
                continue
                
        
            if msg.lower() == "/exit":
                print("[!] Đang thoát...")
                break

        
            client_socket.sendall(msg.encode('utf-8'))

    
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
    
        client_socket.close()
        print("[*] Socket đã đóng.")

if __name__ == "__main__":
    start_client()
