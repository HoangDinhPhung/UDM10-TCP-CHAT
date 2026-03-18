<<<<<<< HEAD
import asyncio
import sys

# ===== CONFIG =====
HOST = "127.0.0.1"
PORT = 5000



# ===== RECEIVE =====
async def receive(reader):
    while True:
        try:
            data = await reader.readline()
            if not data:
                print("\n[DISCONNECTED] Server closed connection.")
                break

            message = data.decode().strip()

            # In ra không đè dòng input
            print(f"\n{message}")
            print(">> ", end="", flush=True)

        except Exception as e:
            print("\n[ERROR] Lost connection:", e)
            break

    sys.exit()


# ===== SEND =====
async def send(writer):
    while True:
        try:
            msg = await asyncio.to_thread(input, ">> ")

            if not msg:
                continue

            # exit
            if msg.lower() == "exit":
                writer.write((msg + "\n").encode())
                await writer.drain()
                print("[EXIT] Disconnected.")
                break

            # gửi command
            writer.write((msg + "\n").encode())
            await writer.drain()

        except Exception as e:
            print("[ERROR]", e)
            break


# ===== MAIN =====
async def main():
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(f"[CONNECTED] Connected to {HOST}:{PORT}")
    except Exception as e:
        print("[ERROR] Cannot connect to server:", e)
        return

    # chạy song song gửi và nhận
    await asyncio.gather(
        receive(reader),
        send(writer)
    )

    writer.close()
    await writer.wait_closed()


# ===== RUN =====
if __name__ == "__main__":
    asyncio.run(main())
=======
import asyncio
import sys

# ===== CONFIG =====
HOST = "127.0.0.1"
PORT = 5000



# ===== RECEIVE =====
async def receive(reader):
    while True:
        try:
            data = await reader.readline()
            if not data:
                print("\n[DISCONNECTED] Server closed connection.")
                break

            message = data.decode().strip()

            # In ra không đè dòng input
            print(f"\n{message}")
            print(">> ", end="", flush=True)

        except Exception as e:
            print("\n[ERROR] Lost connection:", e)
            break

    sys.exit()


# ===== SEND =====
async def send(writer):
    while True:
        try:
            msg = await asyncio.to_thread(input, ">> ")

            if not msg:
                continue

            # exit
            if msg.lower() == "exit":
                writer.write((msg + "\n").encode())
                await writer.drain()
                print("[EXIT] Disconnected.")
                break

            # gửi command
            writer.write((msg + "\n").encode())
            await writer.drain()

        except Exception as e:
            print("[ERROR]", e)
            break


# ===== MAIN =====
async def main():
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(f"[CONNECTED] Connected to {HOST}:{PORT}")
    except Exception as e:
        print("[ERROR] Cannot connect to server:", e)
        return

    # chạy song song gửi và nhận
    await asyncio.gather(
        receive(reader),
        send(writer)
    )

    writer.close()
    await writer.wait_closed()


# ===== RUN =====
if __name__ == "__main__":
    asyncio.run(main())
>>>>>>> ef36a3b2c04d4bf217361474315d85e729bcfbf2
