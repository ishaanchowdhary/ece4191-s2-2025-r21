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

