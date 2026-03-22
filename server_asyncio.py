import asyncio

clients = {}  # {writer: username}


# ================= LOGIN =================
async def login(reader, writer):
    writer.write("Enter username: ".encode())
    await writer.drain()

    data = await reader.readline()
    username = data.decode().strip()

    clients[writer] = username

    print(f"[LOGIN] {username}")
    await broadcast(f"[SERVER] {username} joined\n", writer)

    return username


# ================= BROADCAST =================
async def broadcast(message, sender_writer=None):
    for writer in list(clients.keys()):
        try:
            if writer != sender_writer:
                writer.write(message.encode())
                await writer.drain()
        except:
            # client chết
            await disconnect(writer)


# ================= COMMAND HANDLER =================
async def handle_command(message, writer):
    username = clients.get(writer)

    # /list
    if message == "/list":
        user_list = ", ".join(clients.values())
        writer.write(f"[SERVER] Online: {user_list}\n".encode())
        await writer.drain()

    # /msg user message
    elif message.startswith("/msg"):
        parts = message.split(" ", 2)
        if len(parts) < 3:
            writer.write("[SERVER] Usage: /msg <user> <message>\n".encode())
            await writer.drain()
            return

        target_user = parts[1]
        msg = parts[2]

        for w, u in clients.items():
            if u == target_user:
                w.write(f"[PM] {username}: {msg}\n".encode())
                await w.drain()
                return

        writer.write("[SERVER] User not found\n".encode())
        await writer.drain()

    # /exit
    elif message == "/exit":
        await disconnect(writer)

    else:
        writer.write("[SERVER] Unknown command\n".encode())
        await writer.drain()


# ================= DISCONNECT =================
async def disconnect(writer):
    username = clients.get(writer, "Unknown")

    if writer in clients:
        del clients[writer]

    print(f"[DISCONNECT] {username}")

    try:
        writer.close()
        await writer.wait_closed()
    except:
        pass

    await broadcast(f"[SERVER] {username} left\n")


# ================= HANDLE CLIENT =================
async def handle_client(reader, writer):
    try:
        username = await login(reader, writer)

        while True:
            data = await reader.readline()

            if not data:
                break

            message = data.decode().strip()

            # COMMAND
            if message.startswith("/"):
                await handle_command(message, writer)
            else:
                # NORMAL CHAT
                await broadcast(f"[{username}] {message}\n", writer)

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        await disconnect(writer)


# ================= MAIN =================
async def main():
    server = await asyncio.start_server(handle_client, "127.0.0.1", 5000)

    print("[SERVER] Running on 127.0.0.1:5000")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())