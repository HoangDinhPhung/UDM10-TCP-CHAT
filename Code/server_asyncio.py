import asyncio

HOST = "127.0.0.1"
PORT = 5000

clients = {}

async def broadcast(message, sender=None):
    for writer, name in list(clients.items()):
        if name != sender:
            try:
                writer.write(message.encode())
                await writer.drain()
            except:
                writer.close()
                if writer in clients:
                    del clients[writer]

async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")

    writer.write("Enter username:\n".encode())
    await writer.drain()

    username = (await reader.readline()).decode().strip().lower()

    # check trùng username
    if username in clients.values():
        writer.write("Username already taken\n".encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return

    clients[writer] = username

    print(f"{username} connected from {addr}")

    writer.write(f"Welcome {username}!\n".encode())
    await writer.drain()

    # thông báo join
    await broadcast(f"{username} joined the chat\n", username)

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break

            msg = data.decode().strip()

            if msg.startswith("/list"):
                user_list = ", ".join(clients.values())
                writer.write(f"Online users: {user_list}\n".encode())
                await writer.drain()

            elif msg.startswith("/msg"):
                parts = msg.split(" ", 2)

                if len(parts) < 3:
                    writer.write("Usage: /msg <user> <message>\n".encode())
                    await writer.drain()
                    continue

                target_user = parts[1].lower()
                message = parts[2]

                if target_user == username:
                    writer.write("Cannot message yourself\n".encode())
                    await writer.drain()
                    continue

                found = False
                for w, name in clients.items():
                    if name == target_user:
                        w.write(f"[{username}] {message}\n".encode())
                        await w.drain()
                        found = True
                        break

                if not found:
                    writer.write("User not found\n".encode())
                    await writer.drain()

            elif msg.startswith("/exit"):
                break

            else:
                await broadcast(f"[{username}] {msg}\n", username)

    except Exception as e:
        print("Error:", e)

    finally:
        print(f"{username} disconnected")

        if writer in clients:
            del clients[writer]

        # thông báo rời
        await broadcast(f"{username} left the chat\n", username)

        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)

    print(f"Server running on {HOST}:{PORT}")

    async with server:
        await server.serve_forever()

asyncio.run(main())