
// -------------------------------------------
// Config
// TODO: Add real values - everything here is a placeholder
// TODO: Auto-reconnect on disconnect - Jaiden
// TODO: add checlist for landmarks + animals for each stage
// TODO: Camera stream overlay with yolo  - Liv
// TODO: make it look pretty - Liv
// TODO: add connect after testing
// TODO: add info on connection status
// TODO: documentation to use the gui - Liv

//------------------------
// TODO: Track camera position and not allow it to go out of bounds. Can be done in JS or on the Pi side.


// -------------------------------------------
//const RPI_IP = "172.20.10.2"; // Pi's LAN IP (or hostname)
const RPI_IP = "192.168.20.12"; // Pi's LAN IP (or hostname)
const CMD_PORT = 9000;        // WebSocket Port for commands
const VIDEO_PORT = 9001;      // WebSocket Port for camera feed

// -------------------------------------------
// Websocket Setup
// -------------------------------------------
// ON PAGE LOAD
let video_socket;
let cmd_socket;
document.addEventListener("DOMContentLoaded", () => {
  addLogEntry("Attempting Connection to Camera Feed WebSocket...", "info");
  video_socket = new WebSocket(`ws://${RPI_IP}:${VIDEO_PORT}`);
  video_socket.onopen   = () => addLogEntry("Connected to camera WebSocket", "info");
  video_socket.onerror  = () => addLogEntry("Camera WebSocket connection failed", "error");
  video_socket.onclose  = () => addLogEntry("Camera WebSocket connection closed", "warn");

  // video message handler
  video_socket.onmessage = handleVideoMessage;

  addLogEntry("Attempting Connection to Command WebSocket...", "info");
  cmd_socket = new WebSocket(`ws://${RPI_IP}:${CMD_PORT}`);
  cmd_socket.onopen   = () => addLogEntry("Connected to command feed WebSocket", "info");
  cmd_socket.onerror  = () => addLogEntry("Command WebSocket connection failed", "error");
  cmd_socket.onclose  = () => addLogEntry("Command WebSocket connection closed", "warn");

  // command message handler
  cmd_socket.onmessage = handleCommandMessage;
});


function sendCommand(cmd) {
  addLogEntry(cmd);
  if (cmd_socket.readyState === WebSocket.OPEN) {
    let payload = JSON.stringify({ action: cmd });
    cmd_socket.send(payload);  
    addLogEntry(payload, "transmission");
  } else {
    addLogEntry("WebSocket not connected", "error");
  }
}

function webSocketReconnect() {
  addLogEntry("Reconnecting WebSockets...", "warn");

  cmd_socket = new WebSocket(`ws://${RPI_IP}:${CMD_PORT}`);
  cmd_socket.onopen = () => addLogEntry("Reconnected to command WebSocket", "info");
  cmd_socket.onerror = () => addLogEntry("Command WebSocket reconnection failed", "error");
  cmd_socket.onclose = () => addLogEntry("Command WebSocket closed", "warn");
  cmd_socket.onmessage = handleCommandMessage;

  video_socket = new WebSocket(`ws://${RPI_IP}:${VIDEO_PORT}`);
  video_socket.onopen = () => addLogEntry("Reconnected to video WebSocket", "info");
  video_socket.onerror = () => addLogEntry("Video WebSocket reconnection failed", "error");
  video_socket.onclose = () => addLogEntry("Video WebSocket closed", "warn");
  video_socket.onmessage = handleVideoMessage;
}
// -------------------------------------------
// Websocket Listening
// -------------------------------------------
function handleVideoMessage(event) {
  if (event.data instanceof Blob) {
    const url = URL.createObjectURL(event.data);
    const videoEl = document.getElementById("video");
    videoEl.src = url;

    // Revoke old object URLs to save memory
    videoEl.onload = () => URL.revokeObjectURL(videoEl.src);
  } else {
    console.warn("Unexpected video message type:", event.data);
  }
}

function handleCommandMessage(event) {
  try {
    const msg = JSON.parse(event.data);
    console.log("Command message:", msg);
    if (msg.status === "OK") {
      addLogEntry(`Message received OK`, "reception");
      addLogEntry(`Command received: ${msg.command}, Velocities: ${msg.velocities}`, "reception");
    } 
    else if (msg.status === "error") {
      addLogEntry(`${msg.msg}`, "error");
    } 
    else {
      console.warn("Unknown command message type:", msg);
    }
  } catch (e) {
    console.error("Failed to parse command message:", e);
  }
}

// ------------------------------------------
// Log Handling
// ------------------------------------------

// Listen for checkbox changes
document.querySelectorAll("#log-filter .log-filter-checkbox").forEach(cb => {
  cb.addEventListener("change", applyLogFilter);
});

function applyLogFilter() {
  // TODO
}


/** Function addLogEntry(message, type) 
 * message : unique event text to be displayed
 * type : type of log entry, default 'info'
 *            info - low importance infomation about operation
 *            error - important, critical fault
 *            warn - medium importance, fault that does not end operation
*/

function addLogEntry(message, type = "info") {
  const log = document.getElementById('log');         // Fetch 'log' element from HTML
  const entry = document.createElement('div');        // New div inside 'log' for a new entry
  const timestamp = new Date().toLocaleTimeString();  // Fetch date/time for timestamp
  // Change message attributes based on 'type' variable
  switch (type) {
      case "info": 
        entry.textContent = `[${timestamp}] ${message}`;
        entry.classList.add("log-info");
        break;
      case "error": 
        entry.textContent = `[${timestamp}] ERROR | ${message}`;
        entry.classList.add("log-error");
        break;
      case "warn": 
        entry.textContent = `[${timestamp}] warn | ${message}`;
        entry.classList.add("log-warn");
        break;
      case "transmission":
        entry.textContent = `[${timestamp}] transmitted: | ${message}`;
        entry.classList.add("log-transmission");
        break;
      case "reception":
        entry.textContent = `[${timestamp}] received: | ${message}`;
        entry.classList.add("log-reception");
        break;
  }
  log.appendChild(entry);
  log.scrollTop = log.scrollHeight; // Auto-scroll to the bottom
}



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
      case "ArrowUp": sendCommand("FORWARD"); break;
      case "ArrowDown": sendCommand("REVERSE"); break;
      case "ArrowLeft": sendCommand("LEFT"); break;
      case "ArrowRight": sendCommand("RIGHT"); break;
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

//E-STOP
document.addEventListener("keydown", (event) => {
  if (["x"].includes(event.key)){
    event.preventDefault();
    sendCommand("CAM_STOP");
    sendCommand("DRIVE_STOP");
  }
});

//Rehome camera
document.addEventListener("keydown", (event) => {
  if (["Home"].includes(event.key)){
    event.preventDefault();
    sendCommand("CAM_STOP");
    sendCommand("CAM_REHOME");
  }
});

//Take photo
document.addEventListener("keydown", (event) => {
  if ([" "].includes(event.key)){
    event.preventDefault();
    sendCommand("CAM_STOP");
    sendCommand("CAM_TAKE_PHOTO");
  }
});

//Turn on IR LED 
document.addEventListener("keydown", (event) => {
  if (["i"].includes(event.key)){
    event.preventDefault();
    sendCommand("IR_ON");
  }
});