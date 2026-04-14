let ws = new WebSocket("ws://127.0.0.1:8765"); 

let chat = document.getElementById("chat");

ws.onopen = () => {
    chat.innerHTML += "<p>[Connected]</p>";
};

ws.onmessage = (event) => {
    chat.innerHTML += "<p>" + event.data + "</p>";
};

function sendMsg() {
    let input = document.getElementById("msg");
    let msg = input.value;

    if (msg.trim() === "") return;

    ws.send(msg);
    chat.innerHTML += "<p><b>You:</b> " + msg + "</p>";

    input.value = "";
}
//thanhupdate
