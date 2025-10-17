#!/usr/bin/env python3
"""
video_receiver_tcp.py
---------------------
Receives JPEG-encoded video frames over a raw TCP socket
and displays them locally using OpenCV.

This matches a sender that transmits:
    [4-byte length prefix] + [JPEG frame bytes]

Dependencies:
- socket
- numpy
- cv2
"""

import socket
import cv2
import numpy as np
import struct
import time
from ultralytics import YOLO
# ----------------------------
# Config
# ----------------------------
RPI_IP = "192.168.177.148"  # Change to the sender’s IP
VIDEO_PORT = 5001          # Port where camera_stream.py sends frames
IN_URI = f"ws://{RPI_IP}:{VIDEO_PORT}"

MODEL_PATH = "models/best_NoIR_v1.pt"
model = YOLO(MODEL_PATH)

# ----------------------------
# Helper: receive exact number of bytes
# ----------------------------
def recvall(sock, count):
    """Receive exactly 'count' bytes from the socket."""
    data = b''
    while len(data) < count:
        packet = sock.recv(count - len(data))
        if not packet:
            return None
        data += packet
    return data

# ----------------------------
# Main receiver loop
# ----------------------------
def receive_and_display():
    while True:
        try:
            print(f"[INPUT] Connecting to {RPI_IP}:{VIDEO_PORT}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((RPI_IP, VIDEO_PORT))
            print("[INPUT] Connected to stream.")

            while True:
                # --- Read 4-byte frame length ---
                length_bytes = recvall(sock, 4)
                if not length_bytes:
                    print("[WARN] Stream ended.")
                    break

                frame_length = struct.unpack('>I', length_bytes)[0]

                # --- Read frame data ---
                frame_data = recvall(sock, frame_length)
                if not frame_data:
                    print("[WARN] Frame incomplete.")
                    break

                # --- Decode JPEG to OpenCV frame ---
                frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    continue
                #results = model.predict(frame, verbose=False)
                #annotated = results[0].plot()
                # --- Display frame ---
                cv2.imshow("Received Stream", frame)
                #cv2.imshow("YOLO Stream", annotated)

                # Exit cleanly on 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("[INFO] Exiting viewer.")
                    sock.close()
                    cv2.destroyAllWindows()
                    return

        except Exception as e:
            print(f"[WARN] Connection lost ({e}), retrying in 2s...")
            time.sleep(2)
            continue


# ----------------------------
# Main entry
# ----------------------------
if __name__ == "__main__":
    try:
        receive_and_display()
    except KeyboardInterrupt:
        print("\n[INFO] Receiver stopped by user.")
        cv2.destroyAllWindows()
