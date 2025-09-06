
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

// IP Address: Switch / change as required
const RPI_IP = "172.20.10.2"; // Pi's LAN IP (or hostname): Ishaan's iPhone
// const RPI_IP = "192.168.4.110"; // Pi's LAN IP (or hostname): Ishaan's house wifi (i think)
// const RPI_IP = "192.168.20.12"; // Pi's LAN IP (or hostname): Jaiden and Liv's house wifi (i think)
//const RPI_IP = "172.20.10.3"; // Pi's LAN IP (or hostname): Jaiden's iPhone
//const RPI_IP = "192.168.20.50"; // Pi's LAN IP (or hostname): Michael's house wifi
//const RPI_IP = "172.20.10.4"; // Pi's LAN IP (or hostname): Michael's iPhone pi 3

// Websocket Ports
const CMD_PORT = 9000;        // WebSocket Port for commands
const RAW_VIDEO_PORT = 9001;   // WebSocket Port for raw camera feed
const VIDEO_PORT = 9002;      // WebSocket Port for vision model feed


// ---------------------------------
// On page load
// ---------------------------------

document.addEventListener("DOMContentLoaded", () => {

  // Setup connection status icons
  let connection_info = document.getElementById('connection-info');
  connection_info.innerHTML += `
    CMD: ws://${RPI_IP}:${CMD_PORT} <span id="CMD-icon" class='material-icons disconnected'>circle</span><br>
    CAM: ws://${RPI_IP}:${RAW_VIDEO_PORT} <span id="CAM-icon" class='material-icons disconnected'>circle</span><br>                              
    DET: ws://localhost:${VIDEO_PORT}<span>&nbsp;&nbsp;&nbsp;</span><span id="DET-icon" class='material-icons disconnected'>circle</span>`;

  // If config set to connect on page load, do so
  if (CONFIG.CONNECT_ON_PAGE_LOAD == true) {
    webSocketReconnect()
  }
});





// -------------------------------------------
// Websocket Setup
// -------------------------------------------
// ON PAGE LOAD
let video_socket;
let cmd_socket;

document.addEventListener("DOMContentLoaded", () => {
  if (CONFIG.CONNECT_ON_PAGE_LOAD == true) {
    webSocketReconnect()
  }
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

// --------------------------------------------
// Websocket Connect / Reconnect
// --------------------------------------------
function webSocketReconnect() {

  addLogEntry("Connecting WebSockets...", "info");

  // Command socket
  cmd_socket = new WebSocket(`ws://${RPI_IP}:${CMD_PORT}`);
  updateIcon("CMD-icon", "connecting");
  addLogEntry(`Attempting CMD connection on ${cmd_socket.url}`, "info");
  cmd_socket.onopen = () => {
    addLogEntry("Reconnected to command WebSocket", "info");
    document.getElementById("websocket-connect-button").disabled = true;
    updateIcon("CMD-icon", "connected");
  }
  cmd_socket.onerror = () => {
    addLogEntry("Command WebSocket reconnection failed", "error");
    document.getElementById("websocket-connect-button").disabled = false;
    updateIcon("CMD-icon", "disconnected");
  }
  cmd_socket.onclose = () => {
    addLogEntry("Command WebSocket closed", "warn");
    document.getElementById("websocket-connect-button").disabled = false;
    updateIcon("CMD-icon", "disconnected");
  }
  cmd_socket.onmessage = handleCommandMessage;

  // Vision Model socket
  //video_socket = new WebSocket(`ws://${RPI_IP}:${VIDEO_PORT}`); // Raw Feed
  video_socket = new WebSocket(`ws://localhost:${VIDEO_PORT}`); // Yolo Feed = new WebSocket(`ws://localhost:${VIDEO_PORT}`); // Yolo Feed
  updateIcon("DET-icon", "connecting");
  addLogEntry(`Attempting DET connection on ${video_socket.url}`, "info");
  video_socket.onopen = () => {
    addLogEntry("Reconnected to YOLO WebSocket", "info");
    document.getElementById("websocket-connect-button").disabled = true;
    updateIcon("DET-icon", "connected");
  }
  video_socket.onerror = () => {
    addLogEntry("YOLO WebSocket reconnection failed", "error");
    document.getElementById("websocket-connect-button").disabled = false;
    updateIcon("DET-icon", "disconnected");
  }
  video_socket.onclose = () => {
    addLogEntry("YOLO WebSocket closed", "warn");
    document.getElementById("websocket-connect-button").disabled = false;
    updateIcon("DET-icon", "disconnected");
  }
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
    if (msg.status === "ok") {
      addLogEntry(`Message received OK`, "reception");
      addLogEntry(`Command received: ${msg.command}, Velocities: ${JSON.stringify(msg.velocities)}, Duty: ${msg.duty_cycles}`, "reception");
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




// Update connection status icons
function updateIcon(id, state) {
  const icon = document.getElementById(id);
  if (!icon) return;

  // Remove any old state classes
  icon.classList.remove("connected", "disconnected", "connecting");

  // Add new state
  icon.classList.add(state);

  switch (state) {
    case "connected":   icon.textContent = "circle"; break;
    case "connecting":  icon.textContent = "sync"; break;
    case "disconnected": default: icon.textContent = "circle"; break;
  }
}