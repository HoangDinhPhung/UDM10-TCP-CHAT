import asyncio
import websockets
import time
import logging
import os


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
            msg_text = message.strip()

    
            if msg_text.startswith("name:"):
                username = msg_text.split("name:", 1)[1]
                clients[websocket]["name"] = username

                await websocket.send(f"Your name set to {username}")
                print(f"Set name: {username}")
                continue

            sender = clients[websocket]["name"] or "Unknown"

            
            if msg_text.startswith("broadcast:"):
                content = msg_text.split("broadcast:", 1)[1]

                for client in clients:
                    if client != websocket:
                        await client.send(f"[BROADCAST] {sender}: {content}")

        
            elif msg_text.startswith("private:"):
                try:
                    _, target_name, content = msg_text.split(":", 2)

                    found = False
                    for client, info in clients.items():
                        if info["name"] == target_name:
                            await client.send(f"[PRIVATE] {sender}: {content}")
                            found = True
                            break

                    if not found:
                        await websocket.send("User not found")

                except:
                    await websocket.send("Format: private:username:message")

        
            else:
                for client in clients:
                    if client != websocket:
                        await client.send(f"{sender}: {msg_text}")

    except:
        pass

    finally:
        print("Client disconnected")
        logging.info("Client disconnected")
        del clients[websocket]


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
