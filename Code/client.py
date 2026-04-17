import socket
import threading

def receive(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break

            if data.startswith("MSG|"):
                _, sender, msg = data.split("|", 2)
                print(f"\n[{sender}]: {msg}")

            elif data.startswith("USER_LIST|"):
                users = data.split("|")[1]
                print(f"\n[Online]: {users}")

            elif data.startswith("ERROR|"):
                print(f"\n[Error]: {data.split('|')[1]}")

            else:
                print(f"\n[Server]: {data}")

        except:
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 9999))

    threading.Thread(target=receive, args=(client,), daemon=True).start()

    print("Commands: login <name> | list | msg <user> <message> | exit")

    while True:
        cmd = input("> ")

        if cmd.startswith("login "):
            username = cmd.split(" ", 1)[1]
            client.send(f"LOGIN|{username}".encode())

        elif cmd == "list":
            client.send("LIST".encode())

        elif cmd.startswith("msg "):
            parts = cmd.split(" ", 2)
            if len(parts) < 3:
                print("Sai cú pháp!")
                continue

            _, user, message = parts
            client.send(f"MSG|{user}|{message}".encode())

        elif cmd == "exit":
            break

        else:
            print("Lệnh không hợp lệ!")

    client.close()


if __name__ == "__main__":
    main()
