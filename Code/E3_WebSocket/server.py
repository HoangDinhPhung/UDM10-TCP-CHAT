import asyncio
import websockets

clients = set()

async def register(ws):
    clients.add(ws)
    print(f"[CONNECT] {ws.remote_address}")

async def unregister(ws):
    clients.remove(ws)
    print(f"[DISCONNECT] {ws.remote_address}")

async def broadcast(message, sender):
    for client in clients:
        if client != sender:
            try:
                await client.send(message)
            except:
                pass

async def handler(ws):
    await register(ws)

    try:
        async for message in ws:
            print(f"[RECEIVED] {message}")
            await broadcast(message, ws)
    except:
        pass
    finally:
        await unregister(ws)

async def main():
    print("🚀 Server chạy tại ws://localhost:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # chạy mãi

if __name__ == "__main__":
    asyncio.run(main())