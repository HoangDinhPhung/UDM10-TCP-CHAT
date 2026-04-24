import asyncio
import sys
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5000

username_set = False

def get_time():
    return datetime.now().strftime("%H:%M:%S")

async def receive(reader):
    global username_set
    while True:
        try:
            data = await reader.readline()
            if not data:
                print("\n[DISCONNECTED] Server closed connection.")
                break

            message = data.decode().strip()
            
            # phần xử lý lời mời hệ thống
            if message.startswith("SYSTEM|INVITE|"):
                parts = message.split("|")
                sender, group = parts[2], parts[3]
                print(f"\n[{get_time()}] [Notification] User '{sender}' invited you to group '{group}'")
                print(f"[{get_time()}] Type /accept to join or /reject to decline")
            # phần hiển thị tin nhắn thông thường
            else:
                print(f"\r{message}") 

            # phần cập nhật trạng thái prompt
            if "Welcome" in message or "You renamed to" in message:
                username_set = True
            
            prompt = ">> " if not username_set else f"[{get_time()}] "
            print(prompt, end="", flush=True)

        except: break
    sys.exit()

async def send(writer):
    global username_set
    while True:
        try:
            current_prompt = ">> " if not username_set else f"[{get_time()}] "
            
            msg = await asyncio.to_thread(input, current_prompt)
            if not msg: continue

            writer.write((msg + "\n").encode())
            await writer.drain()

            # phần thoát
            if msg.lower() in ["/exit", "/quit", "exit"]: break
        except: break

async def main():
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(f"[CONNECTED] Connected to {HOST}:{PORT}")
        await asyncio.gather(receive(reader), send(writer))
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\nClient closed.")
