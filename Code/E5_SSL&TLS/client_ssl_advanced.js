// client_ssl_advanced.js
// Advanced SSL/TLS WebSocket Client

let socket = null;
let username = "";
let reconnectInterval = 3000;
let isConnected = false;

// ================= CONNECT =================

function connect() {
    username = document.getElementById("username").value;

    if (!username) {
        alert("Enter username");
        return;
    }

    console.log("Connecting to SSL server...");

    // SSL WebSocket (wss)
    socket = new WebSocket("wss://localhost:8765");

    socket.onopen = function () {
        console.log("Connected to SSL server");
        isConnected = true;

        updateStatus("Connected");

        sendSystemMessage("JOIN", username);
    };

    socket.onmessage = function (event) {
        console.log("Message received:", event.data);

        handleIncomingMessage(event.data);
    };

    socket.onerror = function (error) {
        console.error("WebSocket error:", error);
        updateStatus("Error");
    };

    socket.onclose = function () {
        console.log("Connection closed");
        isConnected = false;

        updateStatus("Disconnected");

        reconnect();
    };
}

// ================= RECONNECT =================

function reconnect() {
    console.log("Reconnecting in 3 seconds...");

    setTimeout(function () {
        if (!isConnected) {
            connect();
        }
    }, reconnectInterval);
}

// ================= SEND MESSAGE =================

function sendMessage() {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
        alert("Not connected");
        return;
    }

    let messageInput = document.getElementById("message");
    let message = messageInput.value;

    if (!message) return;

    let data = {
        type: "broadcast",
        from: username,
        message: message
    };

    socket.send(JSON.stringify(data));

    appendMessage("Me", message);

    messageInput.value = "";
}

// ================= PRIVATE MESSAGE =================

function sendPrivateMessage() {
    let toUser = document.getElementById("privateUser").value;
    let message = document.getElementById("message").value;

    if (!toUser || !message) {
        alert("Enter user and message");
        return;
    }

    let data = {
        type: "private",
        from: username,
        to: toUser,
        message: message
    };

    socket.send(JSON.stringify(data));

    appendMessage("To " + toUser, message);

    document.getElementById("message").value = "";
}

// ================= SYSTEM MESSAGE =================

function sendSystemMessage(action, user) {
    let data = {
        type: "system",
        action: action,
        user: user
    };

    socket.send(JSON.stringify(data));
}

// ================= HANDLE INCOMING =================

function handleIncomingMessage(data) {
    try {
        let msg = JSON.parse(data);

        switch (msg.type) {
            case "broadcast":
                appendMessage(msg.from, msg.message);
                break;

            case "private":
                appendMessage(
                    "[Private] " + msg.from,
                    msg.message
                );
                break;

            case "system":
                handleUserStatus(msg);
                break;

            default:
                console.log("Unknown message type");
        }
    } catch (e) {
        console.error("Invalid message:", data);
    }
}

// ================= USER STATUS =================

function handleUserStatus(msg) {
    let userList = document.getElementById("userList");

    if (!userList) return;

    if (msg.action === "JOIN") {
        let li = document.createElement("li");
        li.id = "user-" + msg.user;
        li.textContent = msg.user;

        userList.appendChild(li);

        appendMessage("System", msg.user + " joined");
    }

    if (msg.action === "LEAVE") {
        let userItem = document.getElementById(
            "user-" + msg.user
        );

        if (userItem) {
            userItem.remove();
        }

        appendMessage("System", msg.user + " left");
    }
}

// ================= UI UPDATE =================

function appendMessage(sender, message) {
    let chatBox = document.getElementById("chatBox");

    if (!chatBox) return;

    let div = document.createElement("div");

    div.innerHTML =
        "<b>" + sender + ":</b> " + message;

    chatBox.appendChild(div);

    chatBox.scrollTop = chatBox.scrollHeight;
}

function updateStatus(status) {
    let statusLabel =
        document.getElementById("status");

    if (statusLabel) {
        statusLabel.textContent = status;
    }
}

// ================= DISCONNECT =================

function disconnect() {
    if (socket) {
        socket.close();
    }
}

// ================= ENTER KEY =================

document.addEventListener("DOMContentLoaded", function () {
    let messageInput =
        document.getElementById("message");

    if (messageInput) {
        messageInput.addEventListener(
            "keypress",
            function (event) {
                if (event.key === "Enter") {
                    sendMessage();
                }
            }
        );
    }
});
