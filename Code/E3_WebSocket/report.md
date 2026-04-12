# E3 WebSocket Chat System

## 1. Handshake
WebSocket sử dụng HTTP Upgrade request để chuyển sang giao thức WS.

## 2. Frame
Dữ liệu truyền theo frame binary/text, tối ưu hơn TCP raw.

## 3. API
- ws://localhost:5000
- send(message)
- onmessage(event)

## 4. System Architecture
Client (HTML/JS)
        ↓
WebSocket
        ↓
Python Server (asyncio + websockets)
        ↓
Broadcast to all clients

## 5. Features
- Real-time chat
- Multi-client support
- Broadcast message