document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {
    let userInput = document.getElementById("user-input").value;
    if (userInput.trim() === "") return;

    let chatBox = document.getElementById("chat-box");

    // Append user message
    let userMessage = document.createElement("div");
    userMessage.classList.add("user-message");
    userMessage.textContent = userInput;
    chatBox.appendChild(userMessage);

    fetch(`/get_response?query=${encodeURIComponent(userInput)}`)
        .then(response => response.json())
        .then(data => {
            // Append bot response
            let botMessage = document.createElement("div");
            botMessage.classList.add("bot-message");
            botMessage.textContent = data.response;
            chatBox.appendChild(botMessage);

            chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to bottom
        });

    document.getElementById("user-input").value = "";
}
