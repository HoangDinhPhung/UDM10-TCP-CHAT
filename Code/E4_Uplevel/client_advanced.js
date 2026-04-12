// File: Code/E4_Uplevel/client_advanced.js
// Project: E4_Uplevel - Advanced WebSocket Client
// ONLY JavaScript (no HTML changes)

// Features required by E4:
// - Connect to advanced WebSocket server (server_ws_advanced.py)
// - onmessage, send, broadcast, private message
// - Realtime UI update
// - Handle reconnect, error
// - Handle user status + user list

let ws = null;
let reconnectDelay = 2000;
let maxReconnectDelay = 10000;

// ===== Existing HTML elements (assumed already created) =====
const chatBox = document.getElementById("chatBox");
const input = document.getElementById("input");
const statusBox = document.getElementById("status");
const userListBox = document.getElementById("userList");

// ===== Connect to WebSocket =====
function connect() {
    console.log("Connecting to advanced WebSocket server...");

    ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => {
        console.log("Connected");
        updateStatus("Connected");
        reconnectDelay = 2000;
    };

    ws.onmessage = (event) => {
        console.log("Message received:", event.data);
        handleMessage(event.data);
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        updateStatus("Error");
    };

    ws.onclose = () => {
        console.log("Connection closed");
        updateStatus("Disconnected - reconnecting...");
        reconnect();
    };
}

// ===== Reconnect logic =====
function reconnect() {
    setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, maxReconnectDelay);
        connect();
    }, reconnectDelay);
}

// ===== Send normal message =====
function sendMessage() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert("Not connected");
        return;
    }

    const message = input.value.trim();

    if (message === "") return;

    const data = {
        type: "message",
        content: message
    };

    ws.send(JSON.stringify(data));
    input.value = "";
}

// ===== Broadcast message =====
function broadcastMessage() {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    const message = input.value.trim();

    const data = {
        type: "broadcast",
        content: message
    };

    ws.send(JSON.stringify(data));
    input.value = "";
}

// ===== Private message =====
function sendPrivateMessage(username) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    const message = input.value.trim();

    const data = {
        type: "private",
        to: username,
        content: message
    };

    ws.send(JSON.stringify(data));
    input.value = "";
}

// ===== Handle incoming data =====
function handleMessage(raw) {
    let data;

    try {
        data = JSON.parse(raw);
    } catch {
        addMessage(raw);
        return;
    }

    switch (data.type) {
        case "message":
        case "broadcast":
        case "private":
            addMessage(`${data.from || "Server"}: ${data.content}`);
            break;

        case "user_list":
            updateUserList(data.users);
            break;

        case "status":
            updateStatus(data.message);
            break;

        default:
            addMessage(raw);
    }
}

// ===== Update chat UI =====
function addMessage(text) {
    if (!chatBox) return;

    const div = document.createElement("div");
    div.textContent = text;

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// ===== Update user list =====
function updateUserList(users) {
    if (!userListBox) return;

    userListBox.innerHTML = "";

    users.forEach(user => {
        const item = document.createElement("div");
        item.textContent = user;

        item.onclick = () => sendPrivateMessage(user);

        userListBox.appendChild(item);
    });
}

// ===== Update connection status =====
function updateStatus(text) {
    if (!statusBox) return;

    statusBox.textContent = text;
}

// ===== Enter key to send =====
if (input) {
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
}

// ===== Start connection automatically =====
connect();

// ===== Export functions (for buttons in HTML) =====
window.sendMessage = sendMessage;
window.broadcastMessage = broadcastMessage;
window.sendPrivateMessage = sendPrivateMessage;
