import socket, threading, queue, time

HOST, PORT = "127.0.0.1", 5000

clients = {}   # user -> conn
queues = {}    # user -> Queue
groups = {}    # group -> [users]
invites = {}   # user -> set(groups)

lock = threading.Lock()


def now():
    return time.strftime("%H:%M:%S")


def send_to(user, msg):
    if user in queues:
        queues[user].put(msg)


def broadcast(msg, exclude=None):
    for u in list(clients):
        if u != exclude:
            send_to(u, msg)


# SENDER THREAD 
def sender(u):
    while True:
        try:
            q = queues.get(u)
            if not q:
                break

            msg = q.get()

            with lock:
                if u in clients:
                    clients[u].sendall(msg.encode())
                else:
                    break
        except:
            break


# HANDLE CLIENT 
def handle(conn, addr):
    print(" CONNECT", addr)
    user, buffer = None, ""

    while True:
        try:
            data = conn.recv(1024).decode(errors="ignore")
            if not data:
                break

            buffer += data

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                # ===== LOGIN =====
                if line.startswith("LOGIN|"):
                    user = line.split("|")[1]

                    with lock:
                        clients[user] = conn
                        queues[user] = queue.Queue()

                    threading.Thread(target=sender, args=(user,), daemon=True).start()

                    conn.sendall(b"SYSTEM|Login success\n")
                    broadcast(f"SYSTEM|{user} joined\n", user)
                    continue

                #LIST
                if line == "LIST":
                    with lock:
                        ulist = ",".join(sorted(clients))
                    conn.sendall(f"USER_LIST|{ulist}\n".encode())
                    continue

                #PRIVATE 
                if line.startswith("SEND|"):
                    _, to, msg = line.split("|", 2)
                    with lock:
                        if to in queues:
                            send_to(to, f"MSG|{user}|[{now()}] {msg}\n")
                        else:
                            conn.sendall(b"ERROR|User not found\n")
                    continue

                # BROADCAST 
                if line.startswith("BROADCAST|"):
                    msg = line.split("|", 1)[1]
                    broadcast(f"MSG|{user}|[{now()}] {msg}\n", user)
                    continue

                # GROUP CREATE 
                if line.startswith("GROUP_CREATE|"):
                    g = line.split("|")[1]
                    with lock:
                        groups.setdefault(g, [])
                        if user not in groups[g]:
                            groups[g].append(user)

                    conn.sendall(f"SYSTEM|Group {g} created\n".encode())
                    continue

                # GROUP INVITE
                if line.startswith("GROUP_INVITE|"):
                    _, g, t = line.split("|", 2)
                    with lock:
                        if t not in clients:
                            conn.sendall(b"ERROR|User not online\n")
                            continue
                        invites.setdefault(t, set()).add(g)

                    # 
                    send_to(t, f"SYSTEM|INVITE|{g}|from|{user}\n")
                    continue

                # ACCEPT 
                if line.startswith("GROUP_ACCEPT|"):
                    g = line.split("|")[1]
                    with lock:
                        groups.setdefault(g, [])
                        if user not in groups[g]:
                            groups[g].append(user)
                        invites.get(user, set()).discard(g)

                    conn.sendall(f"SYSTEM|Joined {g}\n".encode())
                    continue

                # REJECT 
                if line.startswith("GROUP_REJECT|"):
                    g = line.split("|")[1]
                    invites.get(user, set()).discard(g)
                    conn.sendall(f"SYSTEM|Rejected {g}\n".encode())
                    continue

                # GROUP CHAT 
                if line.startswith("GROUP_MSG|"):
                    _, g, msg = line.split("|", 2)

                    with lock:
                        if g not in groups or user not in groups[g]:
                            conn.sendall(b"ERROR|Not in group\n")
                            continue

                        for u in groups[g]:
                            if u != user:
                                send_to(u, f"GROUP|{g}|{user}|[{now()}] {msg}\n")
                    continue

                # LOGOUT
                if line == "LOGOUT":
                    break

        except:
            break

    #  DISCONNECT
    if user:
        with lock:
            # remove khỏi group
            for g in list(groups.keys()):
                if user in groups[g]:
                    groups[g].remove(user)
                if len(groups[g]) == 0:
                    del groups[g]

            clients.pop(user, None)
            queues.pop(user, None)
            invites.pop(user, None)

        broadcast(f"SYSTEM|{user} left\n", user)
        print(" DISCONNECT", user)

    try:
        conn.shutdown(socket.SHUT_RDWR)
    except:
        pass

    conn.close()


#  START SERVER 
def start():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    print(" SERVER READY")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    start()
