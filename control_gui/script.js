// Change to your Pi's IP
const RPI_IP = "192.168.1.100";
const WS_PORT = 9000;

// WebSocket connection for commands
let socket = new WebSocket(`ws://${RPI_IP}:${WS_PORT}`);

socket.onopen = () => console.log("✅ Connected to Raspberry Pi");
socket.onerror = (err) => console.error("❌ WebSocket Error:", err);
socket.onclose = () => console.log("🔌 Connection closed");

function sendCommand(cmd) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ action: cmd }));
    console.log("➡️ Sent:", cmd);
  } else {
    console.error("WebSocket not connected");
  }
}

// Video stream setup
document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("cam-stream");
  // MediaMTX will provide a WebRTC or HLS URL; start simple with HLS via <video>
  video.src = `http://${RPI_IP}:8889/cam`;
});