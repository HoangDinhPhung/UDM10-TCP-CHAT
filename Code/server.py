import asyncio
from datetime import datetime

HOST = "127.0.0.1"
PORT = 5000

clients = {} 
groups = {}  
invites = {} 

def get_time():
    return datetime.now().strftime("%H:%M:%S")

async def broadcast(message, sender=None, target_writers=None):
    targets = target_writers if target_writers is not None else list(clients.keys())
    for writer in targets:
        if clients.get(writer) != sender:
            try:
                writer.write(message.encode())
                await writer.drain()
            except:
                writer.close()
                if writer in clients: del clients[writer]

async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    writer.write("Enter username:\n".encode())
    await writer.drain()

    data_name = await reader.readline()
    if not data_name:
        writer.close()
        return
    username = data_name.decode().strip().lower()

    if username in clients.values() or not username:
        writer.write("Username already taken or invalid\n".encode())
        await writer.drain()
        writer.close()
        return

    clients[writer] = username
    print(f"[{get_time()}] [SERVER INFO] {username} connected from {addr}")
    writer.write(f"Welcome {username}!\n".encode())
    await writer.drain()

    try:
        while True:
            data = await reader.read(1024)
            if not data: break
            msg = data.decode().strip()
            if not msg: continue

            current_t = get_time()

            if msg.startswith("/list"):
                user_list = ", ".join(clients.values())
                writer.write(f"[{current_t}] Online users: {user_list}\n".encode())
                await writer.drain()

            elif msg.startswith("/msg"):
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    writer.write(f"[{current_t}] Usage: /msg <user> <message>\n".encode())
                    await writer.drain()
                    continue
                target_user = parts[1].lower()
                message = parts[2]
                found = False
                for w, name in clients.items():
                    if name == target_user:
                        w.write(f"[{current_t}] [{username} (private)] {message}\n".encode())
                        await w.drain()
                        found = True
                        break
                if not found:
                    writer.write(f"[{current_t}] User not found\n".encode())
                    await writer.drain()

            elif msg.startswith("/create "):
                g_name = msg.split(" ", 1)[1].strip().lower()
                groups[g_name] = [writer]
                writer.write(f"[{current_t}] [Notification] Group '{g_name}' created.\n".encode())
                await writer.drain()

            elif msg.startswith("/invite "):
                parts = msg.split(" ")
                if len(parts) < 3:
                    writer.write(f"[{current_t}] [Notification] Usage: /invite <group> <user>\n".encode())
                    await writer.drain()
                    continue
                g_name, target = parts[1].lower(), parts[2].lower()
                
                if target == username:
                    writer.write(f"[{current_t}] [Notification] You cannot invite yourself.\n".encode())
                elif g_name in groups and writer in groups[g_name]:
                    target_writer = next((w for w, n in clients.items() if n == target), None)
                    if target_writer:
                        invites[target] = g_name
                        target_writer.write(f"SYSTEM|INVITE|{username}|{g_name}\n".encode())
                        await target_writer.drain()
                        writer.write(f"[{current_t}] [Notification] Invitation sent to {target}.\n".encode())
                    else:
                        writer.write(f"[{current_t}] [Notification] User not found.\n".encode())
                else:
                    writer.write(f"[{current_t}] [Notification] Group doesn't exist or you're not a member.\n".encode())
                await writer.drain()

            elif msg == "/accept":
                if username in invites:
                    g_name = invites.pop(username)
                    if g_name in groups:
                        groups[g_name].append(writer)
                        await broadcast(f"[{current_t}] [Notification] {username} joined the group '{g_name}'\n", target_writers=groups[g_name])
                else:
                    writer.write(f"[{current_t}] [Notification] No pending invites.\n".encode())
                await writer.drain()

            elif msg == "/reject":
                if username in invites:
                    invites.pop(username)
                    writer.write(f"[{current_t}] [Notification] Invite rejected.\n".encode())
                else:
                    writer.write(f"[{current_t}] [Notification] No pending invites.\n".encode())
                await writer.drain()

            elif msg.startswith("/g "):
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    writer.write(f"[{current_t}] [Notification] Usage: /g <group> <message>\n".encode())
                    await writer.drain()
                    continue
                g_name, g_msg = parts[1].lower(), parts[2]
                if g_name in groups and writer in groups[g_name]:
                    await broadcast(f"[{current_t}] [{g_name}] {username}: {g_msg}\n", sender=username, target_writers=groups[g_name])
                else:
                    writer.write(f"[{current_t}] [Notification] Not a member of this group.\n".encode())
                await writer.drain()

            elif msg.startswith("/rename "):
                parts = msg.split(" ", 1)
                if len(parts) < 2:
                    writer.write(f"[{current_t}] [Notification] Usage: /rename <new_username>\n".encode())
                    await writer.drain()
                    continue
                new_username = parts[1].strip().lower()
                if not new_username:
                    writer.write(f"[{current_t}] [Notification] Invalid username.\n".encode())
                elif new_username in clients.values():
                    writer.write(f"[{current_t}] [Notification] Username '{new_username}' is already taken.\n".encode())
                else:
                    old_username = clients[writer]
                    clients[writer] = new_username
                    username = new_username
                    writer.write(f"[{current_t}] [Notification] You renamed to '{new_username}'.\n".encode())
                    await broadcast(f"[{current_t}] [Notification] '{old_username}' changed name to '{new_username}'\n", sender=new_username)
                await writer.drain()

            elif msg.startswith("/exit") or msg.startswith("/quit"):
                break

            # --- TÍNH NĂNG MỚI: BÁO LỖI LỆNH LẠ ---
            elif msg.startswith("/"):
                writer.write(f"[{current_t}] [Notification] Loi cu phap: Lenh '{msg.split()[0]}' khong ton tai.\n".encode())
                await writer.drain()
            # ------------------------------------

            else:
                await broadcast(f"[{current_t}] [{username}] {msg}\n", username)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if writer in clients:
            print(f"[{get_time()}] [SERVER INFO] {clients[writer]} disconnected")
            del clients[writer]
        for g_members in groups.values():
            if writer in g_members: g_members.remove(writer)
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    print(f"Server running on {HOST}:{PORT}")
    async with server: await server.serve_forever()

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\nServer stopped.")
