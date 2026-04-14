import asyncio

HOST = "127.0.0.1"
PORT = 5000

async def receive(reader):
    while True:
        data = await reader.readline()
        if not data:
            break
        print(data.decode().strip())

async def send(writer):
    while True:
        msg = await asyncio.to_thread(input, ">> ")

        if msg.lower() == "/exit":
            break

        writer.write((msg + "\n").encode())
        await writer.drain()

async def main():
    reader, writer = await asyncio.open_connection(HOST, PORT)

    print(f"[CONNECTED] {HOST}:{PORT}")

    await asyncio.gather(receive(reader), send(writer))

    writer.close()
    await writer.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
