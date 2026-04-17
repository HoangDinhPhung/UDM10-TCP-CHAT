import asyncio
import websockets
import time
import logging
import os
import json

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename='logs/client_events.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

HOST = "127.0.0.1"
PORT = 8765
TIMEOUT = 300

clients = {} 



async def send_user_list():
    users = [info["name"] for info in clients.values() if info["name"]]

    data = json.dumps({
        "type": "user_list",
        "users": users
    })

    for client in clients:
        try:
            await client.send(data)
        except:
            pass


async def handler(websocket):
    clients[websocket] = {
        "name": None,
        "last_active": time.time()
    }

    print("New connection")
    logging.info("New connection")

    try:
        async for message in websocket:
            clients[websocket]["last_active"] = time.time()

            try:
                data = json.loads(message)
            except:
                await websocket.send("Invalid JSON")
                continue

            msg_type = data.get("type")
            sender = clients[websocket]["name"] or "Unknown"

            if msg_type == "login":
                username = data.get("username")
                clients[websocket]["name"] = username

                await websocket.send(json.dumps({
                    "type": "status",
                    "message": f"Logged in as {username}"
                }))

                await send_user_list()
                continue

            elif msg_type == "message":
                content = data.get("content")

                for client in clients:
                    if client != websocket:
                        await client.send(json.dumps({
                            "type": "message",
                            "from": sender,
                            "content": content
                        }))

            elif msg_type == "broadcast":
                content = data.get("content")

                for client in clients:
                    if client != websocket:
                        await client.send(json.dumps({
                            "type": "broadcast",
                            "from": sender,
                            "content": content
                        }))

            elif msg_type == "private":
                target = data.get("to")
                content = data.get("content")

                found = False
                for client, info in clients.items():
                    if info["name"] == target:
                        await client.send(json.dumps({
                            "type": "private",
                            "from": sender,
                            "content": content
                        }))
                        found = True
                        break

                if not found:
                    await websocket.send(json.dumps({
                        "type": "status",
                        "message": "User not found"
                    }))

    except:
        pass

    finally:
        print("Client disconnected")
        logging.info("Client disconnected")

        if websocket in clients:
            del clients[websocket]

        await send_user_list()


async def check_timeout():
    while True:
        now = time.time()

        for client, info in list(clients.items()):
            if now - info["last_active"] > TIMEOUT:
                print("Timeout disconnect")
                logging.info("Timeout disconnect")
                await client.close()
                del clients[client]

        await asyncio.sleep(5)


async def main():
    server = await websockets.serve(handler, HOST, PORT)
    print(f"WebSocket server running at ws://{HOST}:{PORT}")

    asyncio.create_task(check_timeout())

    await server.wait_closed()


asyncio.run(main())
