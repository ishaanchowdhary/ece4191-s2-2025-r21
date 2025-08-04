import cv2
import numpy as np

# Open the two cameras (0 and 1 — change as needed)
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

# Optional: Set frame resolution
#width, height = 640, 480
#cap1.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
#cap2.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

if not cap1.isOpened() or not cap2.isOpened():
    print("Error: Could not open one or both camera streams.")
    cap1.release()
    cap2.release()
    exit(1)

while True:
    try:
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            print("Error: Could not read from one or both cameras.")
            break

        # Resize both frames to be the same size (if not already)
        #frame1 = cv2.resize(frame1, (width, height))
        #frame2 = cv2.resize(frame2, (width, height))

        # Combine frames side by side
        combined = np.hstack((frame1, frame2))

        # Show the combined frame
        cv2.imshow("Dual Camera View", combined)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(f"[ERROR] {e}")
        break


# Cleanup
cap1.release()
cap2.release()
cv2.destroyAllWindows()
