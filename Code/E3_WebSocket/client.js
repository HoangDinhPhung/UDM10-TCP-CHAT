const sendBtn = document.getElementById('send-btn');
const input = document.getElementById('message-input');
const chatBox = document.getElementById('chat-box');
const status = document.getElementById('status');

const ws = new WebSocket("ws://127.0.0.1:8765");

ws.onopen = () => {
    status.textContent = "Đã kết nối WebSocket";
};

ws.onclose = () => {
    status.textContent = "Mất kết nối";
};

ws.onmessage = (event) => {
    appendMessage(event.data, 'received');
};
function appendMessage(text, type) {
    if (text.trim() !== "") {
        const newMsg = document.createElement('div');
        newMsg.classList.add('message', type);
        newMsg.textContent = text;
        chatBox.appendChild(newMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// ===== GỬI =====
function sendMessage() {
    const text = input.value.trim();
    if (text === "") return;

    ws.send(text);
    appendMessage(text, 'sent');
    input.value = "";
}

sendBtn.onclick = sendMessage;

input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});0
