const socket = io();


// SEND MESSAGE
function sendMessage(){

    let input = document.getElementById("message-input");

    let message = input.value;

    if(message.trim() === ""){
        return;
    }

    socket.emit("send_message", {

        sender: myName,

        receiver: receiver,

        message: message

    });

    input.value = "";

}


// RECEIVE MESSAGE
socket.on("receive_message", function(data){

    // ONLY CURRENT CHAT
    if(
        (data.sender === myName && data.receiver === receiver)

        ||

        (data.sender === receiver && data.receiver === myName)
    ){

        let chatArea = document.getElementById("chat-area");

        let msgBox = document.createElement("div");

        // OWN MESSAGE
        if(data.sender === myName){

            msgBox.classList.add("message", "me");

        }else{

            msgBox.classList.add("message", "other");

        }

        msgBox.innerHTML = `
            <p>${data.message}</p>
        `;

        chatArea.appendChild(msgBox);

        chatArea.scrollTop =
            chatArea.scrollHeight;

    }

});