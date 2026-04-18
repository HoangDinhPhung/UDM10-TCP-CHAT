from datetime import datetime
import socket
import threading

HOST = "127.0.0.1"
PORT = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

user = None
chat_target = None
mode = None
buffer = ""


def now():
    return datetime.now().strftime("%H:%M:%S")


def prompt():
    if not user:
        return "> "
    return f"[{user}{' -> ' + chat_target if chat_target else ''}] > "


def recv():
    global chat_target, mode, buffer

    while True:
        try:
            data = client.recv(1024).decode(errors="ignore")
            if not data:
                print("\n Mất kết nối server")
                break

            buffer += data

            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                msg = msg.strip()

                if not msg:
                    continue

                # PRIVATE 
                if msg.startswith("MSG|"):
                    _, sender, content = msg.split("|", 2)
                    print(f"\n {content} | from {sender}")

                # GROUP 
                elif msg.startswith("GROUP|"):
                    _, g, sender, content = msg.split("|", 3)
                    print(f"\n[{g}] {sender}: {content}")

                # LIST
                elif msg.startswith("USER_LIST|"):
                    raw = msg.split("|", 1)[1]
                    users = [u for u in raw.split(",") if u.strip()]

                    if users:
                        print("\n ONLINE:", ",".join(users))
                    else:
                        print("\n ONLINE: (no users)")

                #INVITE
                elif msg.startswith("SYSTEM|INVITE"):
                    parts = msg.split("|")
                    group = parts[2]
                    from_user = parts[4]

                    chat_target = group
                    mode = "invite"

                    print("\n======================")
                    print(" GROUP INVITE")
                    print("Group:", group)
                    print("From :", from_user)
                    print(" accept / reject")
                    print("======================")

                # ===== SYSTEM =====
                elif msg.startswith("SYSTEM|"):
                    print(f"\n[{now()}] {msg.replace('SYSTEM|', '').strip()}")

        except:
            break


def main():
    global user, chat_target, mode

    threading.Thread(target=recv, daemon=True).start()

    user = input("LOGIN: ").strip()
    client.send(f"LOGIN|{user}\n".encode())

    print("""
list
send <user> <msg>
broadcast <msg>

group create <name>
group invite <group> <user>
group chat <name>

accept
reject
logout
""")

    while True:
        cmd = input(prompt()).strip()

        # LIST 
        if cmd == "list":
            client.send("LIST\n".encode())
            continue

        # PRIVATE CHAT 
        if cmd.startswith("send "):
            try:
                _, to, msg = cmd.split(" ", 2)
                chat_target = to
                mode = "private"
                client.send(f"SEND|{to}|{msg}\n".encode())
            except:
                print(" sai cú pháp: send <user> <msg>")
            continue

        # BROADCAST
        if cmd.startswith("broadcast "):
            client.send(f"BROADCAST|{cmd.split(' ',1)[1]}\n".encode())
            continue

        # GROUP CREATE 
        if cmd.startswith("group create "):
            client.send(f"GROUP_CREATE|{cmd.split(' ',2)[2]}\n".encode())
            continue

        #  GROUP INVITE 
        if cmd.startswith("group invite "):
            try:
                _, _, g, t = cmd.split(" ", 3)
                client.send(f"GROUP_INVITE|{g}|{t}\n".encode())
            except:
                print(" sai cú pháp: group invite <group> <user>")
            continue

        # GROUP MODE 
        if cmd.startswith("group chat "):
            chat_target = cmd.split(" ", 2)[2]
            mode = "group"
            print(" GROUP MODE:", chat_target)
            continue

        # ACCEPT 
        if cmd == "accept":
            if mode == "invite":
                client.send(f"GROUP_ACCEPT|{chat_target}\n".encode())
                mode = "group"
            continue

        # REJECT
        if cmd == "reject":
            if mode == "invite":
                client.send(f"GROUP_REJECT|{chat_target}\n".encode())
                chat_target = None
                mode = None
            continue

        # LOGOUT
        if cmd == "logout":
            client.send("LOGOUT\n".encode())
            print(" Đã thoát server")
            break

        #  CHAT GROUP
        if mode == "group":
            if cmd:
                client.send(f"GROUP_MSG|{chat_target}|{cmd}\n".encode())
            continue

        # HAT PRIVATE
        if mode == "private":
            if cmd:
                client.send(f"SEND|{chat_target}|{cmd}\n".encode())
            continue

        print(" sai lệnh")


if __name__ == "__main__":
    main()
