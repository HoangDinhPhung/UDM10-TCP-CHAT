import asyncio

# ===== CONFIG =====
HOST = "127.0.0.1"
PORT = 5000


# ===== RECEIVE =====
async def receive(reader):
    try:
        while True:
            data = await reader.readline()
            if not data:
                print("\n[DISCONNECTED] Server closed connection.")
                break

            message = data.decode().strip()

            print(f"\n{message}")
            print(">> ", end="", flush=True)

    except Exception as e:
        print("\n[ERROR] Receive failed:", e)


# ===== SEND =====
async def send(writer):
    try:
        while True:
            msg = await asyncio.to_thread(input, ">> ")

            if not msg:
                continue

            if msg.lower() == "/exit":
                writer.write((msg + "\n").encode())
                await writer.drain()
                print("[EXIT] Disconnected.")
                break

            writer.write((msg + "\n").encode())
            await writer.drain()

    except Exception as e:
        print("[ERROR] Send failed:", e)


# ===== MAIN =====
async def main():
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(f"[CONNECTED] Connected to {HOST}:{PORT}")
    except Exception as e:
        print("[ERROR] Cannot connect:", e)
        return

    # ===== nhận prompt KHÔNG xuống dòng =====
    data = await reader.read(100)
    print(data.decode(), end="")   # ⚠️ không xuống dòng

    # ===== nhập username cùng dòng =====
    username = await asyncio.to_thread(input)
    writer.write((username + "\n").encode())
    await writer.drain()

    # ===== nhận welcome =====
    data = await reader.readline()
    print(data.decode().strip())

    # ===== chạy song song =====
    await asyncio.gather(
        receive(reader),
        send(writer)
    )

    writer.close()
    await writer.wait_closed()


# ===== RUN =====
if __name__ == "__main__":
    asyncio.run(main())
