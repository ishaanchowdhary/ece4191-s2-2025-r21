// Constants for interfacing with Raspberry Pi
const RPI_IP = "192.168.1.150";   // Pi's LAN IP (or hostname)
const WS_PORT = 9000;             // WebSocket server port on Pi
const VIDEO_URL = `http://${RPI_IP}:8889/cam`; // MediaMTX stream - or whatever we use to stream video

// --- WebSocket Setup ---
let socket = new WebSocket(`ws://${RPI_IP}:${WS_PORT}`);

socket.onopen = () => console.log("Successfully connected to Raspberry Pi WebSocket");
socket.onerror = (err) => console.error("WebSocket Error:", err);
socket.onclose = () => console.log("WebSocket closed");

function sendCommand(cmd) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ action: cmd })); // send command
    console.log("Command sent:", cmd);  
  } else {
    console.error("WebSocket not connected");
  }
}


// Command Logging !!!!!!!!!!!!!!!!! UNFINISHED
let n = 10
let commandHistoryArray = Array(n).fill("n/a")



// --- Video Setup ---
document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("cam-stream");
  video.src = VIDEO_URL;
});

// --- Keyboard Controls ---
let keyPressed = false; // Flag to indicate if a key is currently being pressed down

// If a keydown is detected and the keyPressed flag is not already true:
document.addEventListener("keydown", (event) => {
  if (!keyPressed && ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
    event.preventDefault(); // Needed to stops browser from thinking the arrow keys are to scroll
    keyPressed = true; // Flag that a key has been pressed

    console.log("Key pressed : ", event.key); // debug log

    switch (event.key) {
      case "ArrowUp": sendCommand("forward"); break;
      case "ArrowDown": sendCommand("backward"); break;
      case "ArrowLeft": sendCommand("left"); break;
      case "ArrowRight": sendCommand("right"); break;
    }
  }
});

document.addEventListener("keyup", (event) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
    event.preventDefault();
    keyPressed = false; // release flag
    console.log("Command: stop");
    sendCommand("stop");
  }
});