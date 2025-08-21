
// -------------------------------------------
// Config
// TODO: Add real values - everything here is a placeholder
// TODO: Auto-reconnect on disconnect - Jaiden
// TODO: Add e-stop command - Liv
// TODO: add rx to tx box + colours and filters - Jaiden / Liv
// TODO: add checlist for landmarks + animals for each stage
// TODO: Camera stream overlay with yolo  - Liv
// TODO: make it look pretty - Liv
// TODO: instructional for keys to move + keys to camera pan - Jaiden
// TODO: key to take a photo - Liv
// TODO: add connect after testing
// TODO: add info on connection status
// TODO: switch camera mode to IR - Liv
// TODO: button to rehome the camera - Liv
// TODO: documentation to use the gui - Liv

//------------------------
// TODO: Track camera position and not allow it to go out of bounds. Can be done in JS or on the Pi side.


// -------------------------------------------
const RPI_IP = "192.168.1.150";                 // Pi's LAN IP (or hostname)
const WS_PORT = 9000;                           // WebSocket server port on Pi
const VIDEO_URL = `http://${RPI_IP}:8889/cam`;  // stream of whatever we use to stream video

// -------------------------------------------
// Websocket Setup
// -------------------------------------------
let socket = new WebSocket(`ws://${RPI_IP}:${WS_PORT}`);
socket.onopen = () => console.log("Successfully connected to Raspberry Pi WebSocket");
socket.onerror = (err) => console.error("WebSocket Error:", err);
socket.onclose = () => console.log("WebSocket closed");

function sendCommand(cmd) {
  addTXLogEntry(cmd);
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ action: cmd })); // send command
    console.log("Command sent:", cmd);  
  } else {
    console.error("WebSocket not connected");
  }
}

// ------------------------------------------
// Transmission Handling - instead of this, maybe a scrolling box that shows everything in different cols, e.g.
// red text for errors, blue for transmission, green for received...
// ------------------------------------------
/**
 * Adds string into transmission log on GUI.
 * Creates a new div element in 'tx' element on webpage.
 */
function addTXLogEntry(message) {
  const log = document.getElementById('tx');
  const entry = document.createElement('div');
  const timestamp = new Date().toLocaleTimeString();
  entry.textContent = `[${timestamp}] ${message}`;
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight; // Auto-scroll to the bottom
}


// ------------------------------------------
// Video Stream
// ------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const video = document.getElementById("cam-stream");
  video.src = VIDEO_URL;
});

// ------------------------------------------
// Keyboard Controls
// TODO: make commands sent match expected commands in drive_server.py, maybe make it send back an acknowledge?
// ------------------------------------------

// ARROW KEYs
let arrowKeyPressed = false; // Flag to indicate if a key is currently being pressed down
// If a keydown is detected and the keyPressed flag is not already true:
document.addEventListener("keydown", (event) => {
  if (!arrowKeyPressed && ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
    event.preventDefault(); // Needed to stops browser from thinking the arrow keys are to scroll
    arrowKeyPressed = true; // Flag that a key has been pressed

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
    arrowKeyPressed = false; // release flag
    sendCommand("DRIVE_STOP"); // send stop command
  }
});

// CAMERA KEYS
let cameraKeyPressed = false; // Flag to indicate if a key is currently being pressed down
// If a keydown is detected and the keyPressed flag is not already true:
document.addEventListener("keydown", (event) => {
  if (!cameraKeyPressed && ["w", "a", "s", "d"].includes(event.key)) {
    //event.preventDefault(); // Needed to stops browser from thinking the arrow keys are to scroll
    cameraKeyPressed = true; // Flag that a key has been pressed

    console.log("Key pressed : ", event.key); // debug log

    switch (event.key) {
      case "w": sendCommand("CAM_UP"); break;
      case "a": sendCommand("CAM_LEFT"); break;
      case "s": sendCommand("CAM_DOWN"); break;
      case "d": sendCommand("CAM_RIGHT"); break;
    }
  }
});
document.addEventListener("keyup", (event) => {
  if (["w", "a", "s", "d"].includes(event.key)) {
    event.preventDefault();
    cameraKeyPressed = false; // release flag
    sendCommand("CAM_STOP");
  }
});