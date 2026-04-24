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

            # phần /list
            if msg.startswith("/list"):
                user_list = ", ".join(clients.values())
                writer.write(f"[{current_t}] Online users: {user_list}\n".encode())
                await writer.drain()

            # phần /msg
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

            # phần /create
            elif msg.startswith("/create "):
                g_name = msg.split(" ", 1)[1].strip().lower()
                groups[g_name] = [writer]
                print(f"[{current_t}] [SERVER INFO] Group '{g_name}' created by {username}") 
                writer.write(f"[{current_t}] [Notification] Group '{g_name}' created.\n".encode())
                await writer.drain()

            # phần /invite
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
                        if target_writer in groups[g_name]: # đã thêm 2 điều kiện kiểm tra này để tránh mời người đã là thành viên hoặc đã có lời mời
                            writer.write(f"[{current_t}] [Notification] User '{target}' is already in the group.\n".encode())
                        elif target in invites and invites[target][0] == g_name:
                            writer.write(f"[{current_t}] [Notification] User '{target}' already has a pending invite to this group.\n".encode())
                        else:
                            invites[target] = (g_name, username)
                            target_writer.write(f"SYSTEM|INVITE|{username}|{g_name}\n".encode())
                            await target_writer.drain()
                            writer.write(f"[{current_t}] [Notification] Invitation sent to {target}.\n".encode())
                    else:
                        writer.write(f"[{current_t}] [Notification] User not found.\n".encode())
                else:
                    writer.write(f"[{current_t}] [Notification] Group doesn't exist or you're not a member.\n".encode())
                await writer.drain()

            # phần /accept
            elif msg == "/accept":
                if username in invites:
                    g_name, inviter = invites.pop(username)
                    if g_name in groups:
                        if writer in groups[g_name]: #chỉnh sửa chỗ này
                            writer.write(f"[{current_t}] [Notification] You are already a member of group '{g_name}'.\n".encode())
                        else:
                            groups[g_name].append(writer)
                            await broadcast(f"[{current_t}] [Notification] {username} joined the group '{g_name}'\n", target_writers=groups[g_name])
                    else:
                        writer.write(f"[{current_t}] [Notification] Group '{g_name}' no longer exists.\n".encode())
                else:
                    writer.write(f"[{current_t}] [Notification] No pending invites.\n".encode())
                await writer.drain()

            # phần /reject
            elif msg == "/reject":
                if username in invites:
                    g_name, inviter = invites.pop(username)
                    inviter_writer = next((w for w, n in clients.items() if n == inviter), None)
                    if inviter_writer:
                        inviter_writer.write(f"[{current_t}] [Notification] {username} rejected your invite to group '{g_name}'.\n".encode())
                        await inviter_writer.drain()
                    
                    writer.write(f"[{current_t}] [Notification] Invite rejected.\n".encode())
                else:
                    writer.write(f"[{current_t}] [Notification] No pending invites.\n".encode())
                await writer.drain()

            # phần /leave
            elif msg.startswith("/leave "):
                parts = msg.split(" ", 1)
                if len(parts) < 2:
                    writer.write(f"[{current_t}] [Notification] Usage: /leave <group_name>\n".encode())
                    await writer.drain()
                    continue
                g_name = parts[1].strip().lower()
                if g_name in groups and writer in groups[g_name]:
                    groups[g_name].remove(writer)
                    writer.write(f"[{current_t}] [Notification] You left the group '{g_name}'.\n".encode())
                    await writer.drain()
                    await broadcast(f"[{current_t}] [Notification] {username} has left the group '{g_name}'\n", target_writers=groups[g_name])
                else:
                    writer.write(f"[{current_t}] [Notification] You are not in group '{g_name}'.\n".encode())
                await writer.drain()

            # phần /kick
            elif msg.startswith("/kick "):
                parts = msg.split(" ")
                if len(parts) < 3:
                    writer.write(f"[{current_t}] [Notification] Usage: /kick <group_name> <username>\n".encode())
                    await writer.drain()
                    continue
                g_name, target_name = parts[1].lower(), parts[2].lower()
                
                if g_name in groups:
                    if groups[g_name][0] == writer: # Kiểm tra chủ nhóm
                        target_writer = next((w for w, n in clients.items() if n == target_name), None)
                        if target_writer and target_writer in groups[g_name]:
                            if target_writer == writer:
                                writer.write(f"[{current_t}] [Notification] You cannot kick yourself.\n".encode())
                            else:
                                groups[g_name].remove(target_writer)
                                target_writer.write(f"[{current_t}] [Notification] You have been kicked from group '{g_name}' by owner.\n".encode())
                                await target_writer.drain()
                                await broadcast(f"[{current_t}] [Notification] {target_name} has been kicked from the group by owner.\n", target_writers=groups[g_name])
                        else:
                            writer.write(f"[{current_t}] [Notification] User '{target_name}' is not in this group.\n".encode())
                    else:
                        writer.write(f"[{current_t}] [Notification] Quyen han: Chi chu nhom moi co quyen kick thành viên.\n".encode())
                else:
                    writer.write(f"[{current_t}] [Notification] Nhom '{g_name}' khong ton tai.\n".encode())
                await writer.drain()

            # phần /delete
            elif msg.startswith("/delete "):
                parts = msg.split(" ", 1)
                if len(parts) < 2:
                    writer.write(f"[{current_t}] [Notification] Usage: /delete <group_name>\n".encode())
                    await writer.drain()
                    continue
                g_name = parts[1].strip().lower()
                if g_name in groups:
                    if groups[g_name][0] == writer:
                        await broadcast(f"[{current_t}] [Notification] Group '{g_name}' has been deleted by owner.\n", target_writers=groups[g_name])
                        del groups[g_name]
                        print(f"[{current_t}] [SERVER INFO] Group '{g_name}' was deleted by {username}")
                    else:
                        writer.write(f"[{current_t}] [Notification] Quyen han: Chi chu nhom moi co the xoa nhom nay.\n".encode())
                else:
                    writer.write(f"[{current_t}] [Notification] Nhom '{g_name}' khong ton tai.\n".encode())
                await writer.drain()

            # phần /members
            elif msg.startswith("/members "):
                parts = msg.split(" ", 1)
                if len(parts) < 2:
                    writer.write(f"[{current_t}] [Notification] Usage: /members <group_name>\n".encode())
                    await writer.drain()
                    continue
                g_name = parts[1].strip().lower()
                if g_name in groups:
                    member_names = [clients[w] for w in groups[g_name] if w in clients]
                    writer.write(f"[{current_t}] Members in '{g_name}': {', '.join(member_names)}\n".encode())
                else:
                    writer.write(f"[{current_t}] [Notification] Group '{g_name}' does not exist.\n".encode())
                await writer.drain()

            # phần /groups
            elif msg == "/groups":
                joined_groups = [name for name, members in groups.items() if writer in members]
                if joined_groups:
                    writer.write(f"[{current_t}] You are in groups: {', '.join(joined_groups)}\n".encode())
                else:
                    writer.write(f"[{current_t}] You haven't joined any groups yet.\n".encode())
                await writer.drain()

            # phần /g
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

            # phần /rename
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

            # phần /exit
            elif msg.startswith("/exit") or msg.startswith("/quit"):
                break

            # phần báo lỗi lệnh lạ
            elif msg.startswith("/"):
                writer.write(f"[{current_t}] [Notification] Loi cu phap: Lenh '{msg.split()[0]}' khong ton tai.\n".encode())
                await writer.drain()

            # phần chat chung
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
