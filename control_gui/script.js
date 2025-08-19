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
    socket.send(JSON.stringify({ action: cmd }));
    console.log("Command sent:", cmd);
  } else {
    console.error("WebSocket not connected");
  }
}

// --- Video Setup ---
document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("cam-stream");
  video.src = VIDEO_URL;
});

// --- Keyboard Controls ---
// Currently, if a key is held down it sends lots of commands. Could change to only send one if held down, and a stop after being released
document.addEventListener("keydown", (event) => {
  // Prevent page from scrolling with arrow keys
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
    event.preventDefault(); 
    console.log("Key pressed:", event.key); // <-- debug log

    switch (event.key) {
      case "ArrowUp":
        console.log("Command: forward");
        sendCommand("forward");
        break;
      case "ArrowDown":
        console.log("Command: backward");
        sendCommand("backward");
        break;
      case "ArrowLeft":
        console.log("Command: left");
        sendCommand("left");
        break;
      case "ArrowRight":
        console.log("Command: right");
        sendCommand("right");
        break;
    }
  }
});

document.addEventListener("keyup", (event) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
    event.preventDefault();
    console.log("Command: stop");
    sendCommand("stop");
  }
});