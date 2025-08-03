async function sendMessage() {
    const inputBox = document.getElementById("user_input");
    const msg = inputBox.value.trim();
    if (!msg) return;

    const messagesDiv = document.getElementById("messages");

    // Show user message
    const userMsg = document.createElement("div");
    userMsg.className = "msg user";
    userMsg.textContent = "You: " + msg;
    messagesDiv.appendChild(userMsg);

    inputBox.value = "";

    // Send to backend
    const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: msg })
    });

    const data = await response.json();

    // Show bot message
    const botMsg = document.createElement("div");
    botMsg.className = "msg bot";
    botMsg.textContent = "AI: " + data.response;
    messagesDiv.appendChild(botMsg);
}
