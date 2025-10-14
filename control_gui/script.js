
// -------------------------------------------
// TODO: Auto-reconnect on disconnect
// TODO: add checlist for landmarks + animals for each stage
// TODO: documentation to use the gui
// TODO: Log rework?
//        - applyLogFilter() is unfinished
//        - Logs grow indefinitely, should have a max length and remove old ones
// -------------------------------------------


// Setting up the PWM slider (noUISLider)
var pwm_slider = document.getElementById('pwm-slider');
noUiSlider.create(pwm_slider, {
    start: [40, 100],
    connect: true,
    step: 1,
    range: {
        'min': 0,
        'max': 100
    },
    tooltips: {
      to: function (value) {
        return `${Math.round(value)}%`;   // show integer
      },
      from: function (value) {
        return Number(value);       // parse back to number
      }
    },
    keyboardSupport: false,
    orientation: 'vertical',
    direction: 'rtl',
});


const modal = document.getElementById("config-modal");
const openBtn = document.getElementById("open-config-btn");
const closeBtn = modal.querySelector(".close");

openBtn.addEventListener("click", () => {
  // Load current config values into form
  document.getElementById("cfg-ip").value = CONFIG.RPI_IP;
  document.getElementById("cfg-cmd").value = CONFIG.CMD_PORT;
  document.getElementById("cfg-raw").value = CONFIG.RAW_VIDEO_PORT;
  document.getElementById("cfg-video").value = CONFIG.VIDEO_PORT;
  document.getElementById("cfg-auto").checked = CONFIG.CONNECT_ON_PAGE_LOAD;
  document.getElementById("cfg-yassify").checked = CONFIG.DEFAULT_TO_PINK;
  document.getElementById("cfg-FPSinterval").value = CONFIG.FPS_UPDATE_INTERVAL;

  modal.style.display = "block";
});

closeBtn.addEventListener("click", () => {
  closeConfigModal();
});

function closeConfigModal() {
  modal.style.display = "none";
}

// Close modal if user clicks outside of it
window.addEventListener("click", (event) => {
  if (event.target === modal) {
    closeConfigModal();
  }
});

// Save config
function saveConfig() {
  CONFIG.RPI_IP = document.getElementById("cfg-ip").value;
  CONFIG.CMD_PORT = parseInt(document.getElementById("cfg-cmd").value, 10);
  CONFIG.RAW_VIDEO_PORT = parseInt(document.getElementById("cfg-raw").value, 10);
  CONFIG.VIDEO_PORT = parseInt(document.getElementById("cfg-video").value, 10);
  CONFIG.FPS_UPDATE_INTERVAL = parseFloat(document.getElementById("cfg-FPSinterval").value);
  CONFIG.CONNECT_ON_PAGE_LOAD = document.getElementById("cfg-auto").checked;
  CONFIG.DEFAULT_TO_PINK = document.getElementById("cfg-yassify").checked;

  localStorage.setItem("robotConfig", JSON.stringify(CONFIG));
  addLogEntry("Config saved to local storage", "info");
  closeConfigModal();
}
function resetConfig() {
  localStorage.removeItem("robotConfig");
  location.reload(); // reloads with defaults
}
// ---------------------------------
// ON PAGE LOAD
// ---------------------------------
let camImg;
document.addEventListener("DOMContentLoaded", () => {
  camImg = document.querySelector(".camera-img");
  // Setup connection status icons
  let connection_info = document.getElementById('connection-info');
  connection_info.innerHTML += `
    CMD: ws://${CONFIG.RPI_IP}:${CONFIG.CMD_PORT} <span id="CMD-icon" class='material-icons disconnected'>circle</span><br>
    CAM: ws://${CONFIG.RPI_IP}:${CONFIG.RAW_VIDEO_PORT} <span id="CAM-icon" class='material-icons disconnected'>circle</span><br>                              
    DET: ws://localhost:${CONFIG.VIDEO_PORT}<span>&nbsp;&nbsp;&nbsp;</span><span id="DET-icon" class='material-icons disconnected'>circle</span>`;

  // If config set to connect on page load, do so
  if (CONFIG.CONNECT_ON_PAGE_LOAD == true) {
    webSocketReconnect()
  }
  if (CONFIG.DEFAULT_TO_PINK == true) {
    yassify()
  }
  else
    deyassify()
});



// -------------------------------------------
// Websocket Setup
// -------------------------------------------
// Defining variables to hold WebSocket managers - class is setup on reconnect
let cmdManager;             // Command WebSocket manager
let rawVideoManager;        // Video WebSocket manager
let processedVideoManager;  // Processed Video WebSocket manager

class WebSocketManager {
  constructor({url, label, onMessage, iconId}) {
    this.url = url;              // WebSocket URL
    this.iconId = iconId;       // ID of the icon element to update connection status
    this.label = label;         // Shown in logs, e.g., "CMD" or "DET"
    this.onMessage = onMessage; // Message handler function
    this.socket = null;         // Create WebSocket instance
  }

  // Establish WebSocket connection
  connect() {
    this.socket = new WebSocket(this.url);
    updateIcon(this.iconId, "connecting");
    addLogEntry(`Attempting ${this.label} connection on ${this.url}`, "info");
    this.socket.onopen = () => {
      addLogEntry(`${this.label} WebSocket connected`, "info");
      document.getElementById("websocket-connect-button").disabled = true;
      updateIcon(this.iconId, "connected");

      // Latency checks for COMMAND websocket
      if (this.label == "Command"){
        startLatencyChecks(this.socket);
      }
    };

    this.socket.onerror = () => {
      addLogEntry(`${this.label} WebSocket connection error`, "error");
      document.getElementById("websocket-connect-button").disabled = false;
      updateIcon(this.iconId, "disconnected");
    };

    this.socket.onclose = () => {
      addLogEntry(`${this.label} WebSocket closed`, "warn");
      document.getElementById("websocket-connect-button").disabled = false;
      updateIcon(this.iconId, "disconnected");
    };

    this.socket.onmessage = this.onMessage;
  }

  // Send data if connection is open
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(data);
      addLogEntry(data, "transmission");
    } else {
      addLogEntry(`${this.label} WebSocket not connected`, "error");
    }
  }

  // Close the WebSocket connection
  close() {
    if (this.socket) {
      this.socket.close();
    }
  }

}

function startLatencyChecks(socket) {
  // Checks latency every 5 seconds
  setInterval(() => {
    if (socket.readyState == WebSocket.OPEN){
      const timestamp = Date.now();
      const payload = JSON.stringify({ action: "PING", timestamp});
      socket.send(payload);
    }
  }, 5000);
}

function sendCommand(cmd) {
  addLogEntry(cmd);
  const payload = JSON.stringify({ action: cmd });
  try {
    cmdManager.send(payload);
  } 
  catch (e) {
    if (e.message == "Cannot read properties of undefined (reading 'send')") {
      addLogEntry("cmdManager not defined yet", "error");
    }
    else {
      console.error(e);
      addLogEntry("Failed to send command, see console for details", "error");
    }
  }
}

// --------------------------------------------
// Websocket Connect / Reconnect
// --------------------------------------------

function webSocketReconnect() {
  addLogEntry("Connecting WebSockets...", "info");

   // Initialize WebSocket managers
  cmdManager = new WebSocketManager({
    url: `ws://${CONFIG.RPI_IP}:${CONFIG.CMD_PORT}`,
    iconId: "CMD-icon",
    label: "Command",
    onMessage: handleCommandMessage
  });
  rawVideoManager = new WebSocketManager({
    url: `ws://${CONFIG.RPI_IP}:${CONFIG.RAW_VIDEO_PORT}`,
    iconId: "CAM-icon",
    label: "Camera",
    onMessage: handleVideoMessage
  });
  processedVideoManager = new WebSocketManager({
    url: `ws://localhost:${CONFIG.VIDEO_PORT}`,
    iconId: "DET-icon",
    label: "YOLO",
    onMessage: handleVideoMessage
  });

  // Connect cmd and raw video websockets
  cmdManager.connect();
  rawVideoManager.connect();
}


function switchVideoFeed() {
  try {
    // If raw video is active, switch to processed, and vice versa
    if (rawVideoManager.socket.readyState == 1) {
      rawVideoManager.close();
      processedVideoManager.connect();
    }
    else if (processedVideoManager.socket.readyState == 1) {
      processedVideoManager.close();
      rawVideoManager.connect();
    }
    else {
      addLogEntry("No video feed active to switch, defaulting to raw feed", "warn");
      rawVideoManager.connect();
    }
  } catch (e) {
    addLogEntry("Error switching video feed, defaulting to raw feed", "error");
    rawVideoManager.connect();
    console.error(e);
  }
}





// -------------------------------------------
// Websocket Listening
// -------------------------------------------
let fpsFrameCount = 0;
let fps = 0;
let lastFpsUpdate = performance.now();
function handleVideoMessage(event) {
  if (event.data instanceof Blob) {
    const url = URL.createObjectURL(event.data);
    const videoEl = document.getElementById("video");
    videoEl.src = url;

    // Revoke old object URLs to save memory
    videoEl.onload = () => URL.revokeObjectURL(videoEl.src);
    // ----- FPS calculation -----
    fpsFrameCount++;
    const now = performance.now();
    const delta = (now - lastFpsUpdate) / 1000; // seconds since last FPS update

    if (delta >= CONFIG.FPS_UPDATE_INTERVAL) { // update FPS every 2 second
      fps = fpsFrameCount / delta;
      fpsFrameCount = 0;
      lastFpsUpdate = now;
      document.getElementById("fps-readout").textContent = `FPS: ${fps.toFixed(1)}`;}

  } else {
    console.warn("Unexpected video message type:", event.data);
  }

  

}

function handleCommandMessage(event) {
  try {
    const msg = JSON.parse(event.data);
    // Handle PONG message from server for latency checks
    if (msg.action == "PONG" && msg.timestamp){
      const latency = Date.now() - msg.timestamp;
      document.getElementById("latency-display").textContent = `Latency: ${latency.toFixed(1)} ms`;
      addLogEntry(`WebSocket latency: ${latency.toFixed(1)} ms`, "info")
      return;
    }
    if (msg.status === "ok") {
      addLogEntry(`${msg.command}, Velocities: ${msg.velocities.left.toFixed(2)}, ${msg.velocities.right.toFixed(2)}, Duty: ${msg.duty_cycles.left}`, "reception");
    } 
    else if (msg.status === "error") {
      addLogEntry(`${msg.msg}`, "error");
    }
    else if (msg.status_update) {
      const s = msg.status_update;
      updateThrottleStatus(s);
    }
    else if (msg.head == 'velocity_update') {
      updateVelocity(msg.vel, msg.l, msg.r);
    }
    else {
      console.warn("Unknown command message type:", msg);
    }
  } catch (e) {
    console.error("Failed to parse command message:", e);
  }
}


function updateThrottleStatus(s) {
  const uv = document.getElementById('uv-icon');
  const fr = document.getElementById('freq-icon');
  const th = document.getElementById('thr-icon');

  if (!uv || !fr || !th) return; // safety check

  uv.className = 'material-icons ' + (s.under_voltage_now ? 'err' : 'ok');
  fr.className = 'material-icons ' + (s.freq_capped_now ? 'warn' : 'ok');
  th.className = 'material-icons ' + (s.throttled_now ? 'err' : 'ok');

  uv.title = s.under_voltage_occurred ? 'Undervoltage occurred before' : 'Stable';
  fr.title = s.freq_capped_occurred ? 'Frequency was capped before' : 'Stable';
  th.title = s.throttled_occurred ? 'Throttling occurred before' : 'Stable';
}

let lastLeftVel = 0;
let lastRightVel = 0;
let lastTimestamp = performance.now();
let maxLeftAccel = 0;
let maxRightAccel = 0;
function updateVelocity(v, l, r) {
  const MAX_VELOCITY = 0.1082;  // adjust based on your robot’s top speed
  l = l * v;
  r = r * v;

  const now = performance.now();
  const dt = (now - lastTimestamp) / 1000.0; // seconds
  console.log(dt);

  if (dt > 0) {
    const aLeft = (l - lastLeftVel) / dt;
    const aRight = (r - lastRightVel) / dt;
    if (Math.abs(aLeft) > 0.3 || Math.abs(aRight) > 0.3) {
      // Ignore unrealistic spikes
      console.warn("Ignoring unrealistic acceleration spike:", aLeft, aRight);
    }
    else {
      // Update max acceleration
      maxLeftAccel = Math.max(maxLeftAccel, Math.abs(aLeft));
      maxRightAccel = Math.max(maxRightAccel, Math.abs(aRight));

      //Display max acceleration
      document.getElementById("left-accel-text").textContent = maxLeftAccel.toFixed(3);
      document.getElementById("right-accel-text").textContent = maxRightAccel.toFixed(3);
    }
  }

  lastLeftVel = l;
  lastRightVel = r;
  lastTimestamp = now;

  // Update text
  document.getElementById("left-wheel-text").textContent = l.toFixed(3) + " m/s";
  document.getElementById("right-wheel-text").textContent = r.toFixed(3) + " m/s";

  // Update bars
  const leftBar = document.getElementById("left-wheel-bar");
  const rightBar = document.getElementById("right-wheel-bar");

  const leftPercent = Math.min(Math.abs(l / MAX_VELOCITY) * 50, 50);
  const rightPercent = Math.min(Math.abs(r / MAX_VELOCITY) * 50, 50);

  if (l >= 0) {
    leftBar.style.left = "50%";
    leftBar.style.width = leftPercent + "%";
  } else {
    leftBar.style.left = 50 - leftPercent + "%";
    leftBar.style.width = leftPercent + "%";
  }

  if (r >= 0) {
    rightBar.style.left = "50%";
    rightBar.style.width = rightPercent + "%";
  } else {
    rightBar.style.left = 50 - rightPercent + "%";
    rightBar.style.width = rightPercent + "%";
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

    //console.log("Key pressed : ", event.key); // debug log

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
  if (event.key === " ") {  // Space key
    event.preventDefault();

    const camImg = document.querySelector(".camera-img");
    const camFlash = document.querySelector(".camera-flash");
    const videoEl = document.getElementById("video");

    // Save current frame
    try {
      if (videoEl.src && videoEl.naturalWidth > 0) {
        const canvas = document.createElement("canvas");
        canvas.width = videoEl.naturalWidth;
        canvas.height = videoEl.naturalHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(videoEl, 0, 0);

        // turn into downloadable image
        const link = document.createElement("a");
        link.download = `photo_${Date.now()}.png`;
        link.href = canvas.toDataURL("image/png");
        link.click();
      } else {
        console.warn("No video frame available to save");
      }
    }
    catch(err) {
      console.log(err);
      addLogEntry("Frame capture failed", type = "error")
    }

    // Animation
    camImg.classList.remove("animate-in", "animate-out");
    camFlash.style.opacity = 0;
    camImg.classList.add("animate-in");
    // After spinIn finishes, flash and then spinOut
    setTimeout(() => {
      // Show flash
      camFlash.style.opacity = 1;
      // Hide flash after 0.2s
      setTimeout(() => {
        camFlash.style.opacity = 0;
      }, 400);
      // Start spin out
      camImg.classList.remove("animate-in");
      camImg.classList.add("animate-out");
    }, 2500); // 2s spinIn + small buffer

    
  }
});

//Turn on Night Vision 
document.addEventListener("keydown", (event) => {
  if (["i"].includes(event.key)){
    event.preventDefault();
    sendCommand("NIGHT_MODE_ON");
  }
});

//Turn off Night Vision 
document.addEventListener("keydown", (event) => {
  if (["p"].includes(event.key)){
    event.preventDefault();
    sendCommand("NIGHT_MODE_OFF");
  }
});

// Change Camera Modes
document.addEventListener("keydown", (event) => {
  if (["1"].includes(event.key)){
    event.preventDefault();
    sendCommand("CAM_MODE_1");
  }
});
document.addEventListener("keydown", (event) => {
  if (["2"].includes(event.key)){
    event.preventDefault();
    sendCommand("CAM_MODE_2");
  }
});
document.addEventListener("keydown", (event) => {
  if (["3"].includes(event.key)){
    event.preventDefault();
    sendCommand("CAM_MODE_3");
  }
});

// Increase/Decrease Camera Parameter Values
// BRIGHTNESS
document.addEventListener("keydown", (event) => {
  if (event.key === "b") {
    event.preventDefault();
    sendCommand("INCREASE_BRIGHTNESS");
  }
  if (event.key === "B") {
    event.preventDefault();
    sendCommand("DECREASE_BRIGHTNESS");
  }
});
// CONTRAST
document.addEventListener("keydown", (event) => {
  if (event.key === "n") {
    event.preventDefault();
    sendCommand("INCREASE_CONTRAST");
  }
  if (event.key === "N") {
    event.preventDefault();
    sendCommand("DECREASE_CONTRAST");
  }
});
// GAMMA
document.addEventListener("keydown", (event) => {
  if (event.key === "m") {
    event.preventDefault();
    sendCommand("INCREASE_GAMMA");
  }
  if (event.key === "M") {
    event.preventDefault();
    sendCommand("DECREASE_GAMMA");
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


// PWM Slider
pwm_slider.noUiSlider.on("change", function (values, handle) {
  let val = values;
  console.log("Slider updated to:", val);
  sendCommand(`SET_DUTY ${Math.round(val[0])} ${Math.round(val[1])}`);
});


// Toggle switch
const toggle = document.getElementById("display-toggle-switch");

toggle.addEventListener("change", () => {
  if (toggle.checked) {
    yassify()
  } else {
    deyassify()
  }
});

function deyassify() {
  document.getElementById("display-toggle-switch").checked = false;
  document.getElementById("title").innerHTML = `<h1>ECE4191 Robot Control GUI</h1>`;
  document.getElementById("title").classList.remove("yassify");
  document.getElementById("sub-title").classList.remove("yassify");
  document.getElementById("video").src = `img/no-cam-feed.png`

  var elements = document.querySelectorAll(`.${'options-button'}`);
  // Iterate through the selected elements and add the 'newClass'
  elements.forEach(element => {
    element.classList.remove("yassify");
  });

  var elements = document.querySelectorAll(`.${'noUi-connect'}`);
  // Iterate through the selected elements and add the 'newClass'
  elements.forEach(element => {
    element.classList.remove("yassify");
  });
}

function yassify() {
  document.getElementById("display-toggle-switch").checked = true;
  document.getElementById("title").innerHTML = `<h1>It's C.U.N.T.I.N.G Season!!!</h1>`;
  document.getElementById("title").classList.add("yassify");
  document.getElementById("sub-title").classList.add("yassify");
  document.getElementById("video").src = `img/fallback.png`

  var elements = document.querySelectorAll(`.${'options-button'}`);
  // Iterate through the selected elements and add the 'newClass'
  elements.forEach(element => {
    element.classList.add("yassify");
  });

  var elements = document.querySelectorAll(`.${'noUi-connect'}`);
  // Iterate through the selected elements and add the 'newClass'
  elements.forEach(element => {
    element.classList.add("yassify");
  });
}