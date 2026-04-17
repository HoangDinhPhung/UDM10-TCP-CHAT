let ws = null;
let reconnectDelay = 2000;
let maxReconnectDelay = 10000;
let username = "";

const chatBox = document.getElementById("chat-box");
const input = document.getElementById("message-input");
const statusBox = document.getElementById("status");
const userListBox = document.getElementById("user-list");

function connect() {
    ws = new WebSocket("ws://127.0.0.1:8765");

    ws.onopen = () => {
        updateStatus("🟢 Connected");
        reconnectDelay = 2000;

        // gửi username 
        if (username) {
            ws.send(JSON.stringify({
                type: "login",
                username: username
            }));
        }
    };

    ws.onmessage = (event) => {
        handleMessage(event.data);
    };

    ws.onerror = () => {
        updateStatus("⚠️ Error");
    };

    ws.onclose = () => {
        updateStatus("🔴 Disconnected - reconnecting...");
        reconnect();
    };
}

function reconnect() {
    setTimeout(() => {
        reconnectDelay = Math.min(reconnectDelay * 2, maxReconnectDelay);
        connect();
    }, reconnectDelay);
}

function login() {
    username = prompt("Enter your username:");
    if (!username) {
        username = "Guest_" + Math.floor(Math.random() * 1000);
    }
}

function sendMessage() {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        alert("Not connected");
        return;
    }

    const message = input.value.trim();
    if (message === "") return;

    ws.send(JSON.stringify({
        type: "message",
        content: message
    }));

    addMessage(`You: ${message}`);
    input.value = "";
}

function broadcastMessage() {
    const message = input.value.trim();
    if (!message) return;

    ws.send(JSON.stringify({
        type: "broadcast",
        content: message
    }));

    addMessage(`[Broadcast] You: ${message}`);
    input.value = "";
}

function sendPrivateMessage(targetUser) {
    const message = input.value.trim();
    if (!message) return;

    ws.send(JSON.stringify({
        type: "private",
        to: targetUser,
        content: message
    }));

    addMessage(`[Private → ${targetUser}] You: ${message}`);
    input.value = "";
}

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
            addMessage(`${data.from}: ${data.content}`);
            break;

        case "broadcast":
            addMessage(`[Broadcast] ${data.from}: ${data.content}`);
            break;

        case "private":
            addMessage(`[Private] ${data.from}: ${data.content}`);
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

function addMessage(text) {
    if (!chatBox) return;

    const div = document.createElement("div");
    div.textContent = text;

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function updateUserList(users) {
    if (!userListBox) return;

    userListBox.innerHTML = "";

    users.forEach(user => {
        const item = document.createElement("div");
        item.textContent = user;

        item.onclick = () => {
            const msg = prompt(`Send private message to ${user}:`);
            if (msg) {
                ws.send(JSON.stringify({
                    type: "private",
                    to: user,
                    content: msg
                }));
            }
        };

        userListBox.appendChild(item);
    });
}

function updateStatus(text) {
    if (!statusBox) return;
    statusBox.textContent = text;
}

if (input) {
    input.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    });
}

login();
connect();

window.sendMessage = sendMessage;
window.broadcastMessage = broadcastMessage;
window.sendPrivateMessage = sendPrivateMessage;.
