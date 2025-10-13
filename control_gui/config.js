
window.CONFIG = {
  RPI_IP: "192.168.20.9",   // Pi's LAN IP (or hostname)
  CMD_PORT: 9000,           // WebSocket Port for commands
  RAW_VIDEO_PORT: 9001,     // WebSocket Port for raw camera feed
  VIDEO_PORT: 9002,         // WebSocket Port for vision model feed
  CONNECT_ON_PAGE_LOAD: false,
  DEFAULT_TO_PINK: false,    // default to cute layout
  FPS_UPDATE_INTERVAL: 2   // seconds between FPS updates
};


// IP Address: Switch / change as required
// 172.20.10.2      Ishaan's iPhone
// 192.168.4.110    Ishaan's house wifi (i think)
// 192.168.20.9     Jaiden and Liv's house wifi (i think)
// 172.20.10.3      Jaiden's iPhone
// 192.168.20.50    Michael's house wifi
// 172.20.10.4      Michael's iPhone pi 3
// 192.168.20.15    Liv & Jaidens Apartment wifi - Raspberry Pi 4


// Try to load saved config from localStorage
document.addEventListener("DOMContentLoaded", () => {
  const savedConfig = localStorage.getItem("robotConfig");
  if (savedConfig) {
    Object.assign(window.CONFIG, JSON.parse(savedConfig));
  }
});