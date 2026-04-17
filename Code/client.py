import socket
import threading

HOST = "127.0.0.1"
PORT = 8888

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            msg = client.recv(1024).decode()

            if not msg:
                break

            # CHAT RIÊNG
            if msg.startswith("MSG|"):
                _, sender, content = msg.split("|", 2)
                print(f"\n💬 {sender}: {content}")

            # LIST USER
            elif msg.startswith("USER_LIST|"):
                users = msg.split("|")[1]
                print(f"\n👥 Online users: {users}")

            # ERROR
            elif msg.startswith("ERROR|"):
                print(f"\n❌ {msg}")

            # OK login
            else:
                print(f"\n📩 {msg}")

        except:
            print("\n❌ Disconnected from server")
            client.close()
            break




def main():
    threading.Thread(target=receive, daemon=True).start()

    # LOGIN
    username = input("Enter username: ")
    client.send(f"LOGIN|{username}".encode())

    print("\nCommands:")
    print("list → xem user online")
    print("send <user> <message> → chat riêng")

    while True:
        cmd = input("> ")

        # LIST USER
        if cmd == "list":
            client.send("LIST".encode())

        # CHAT RIÊNG
        elif cmd.startswith("send "):
            try:
                _, target, message = cmd.split(" ", 2)
                client.send(f"SEND|{target}|{message}".encode())
            except:
                print("❌ Format: send <user> <message>")

        else:
            print("❌ Unknown command")


if __name__ == "__main__":
    main()
