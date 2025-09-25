#!/usr/bin/env python3
"""
video_enhancer.py
-------------
Takes video frame and allows manipulation of:
- Brightness
- Contrast
- Gamma

To call externally:
    enhance_frame(frame, mode=1, brightness=50, contrast=50, gamma_val=100)

Best values in the dark:
    enhance_frame(frame, mode=1, brightness=50, contrast=50, gamma_val=300)

Dependencies:
- cv2
- numpy
"""

'''   DEPENDENCIES   '''

import cv2
import numpy as np


'''   PROCESS FUNCTIONS   '''

def adjust_brightness_contrast_gamma(frame, brightness=0, contrast=0, gamma=1.0):
    """Manual brightness, contrast, gamma adjustment."""
    frame = cv2.convertScaleAbs(frame, alpha=1 + (contrast / 100.0), beta=brightness)

    # Gamma correction
    invGamma = 1.0 / gamma if gamma > 0 else 1.0
    table = np.array([(i / 255.0) ** invGamma * 255 for i in np.arange(0, 256)]).astype("uint8")
    frame = cv2.LUT(frame, table)

    return frame

def auto_histogram_equalization(frame):
    """Global histogram equalization per channel."""
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
    return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

def auto_clahe(frame, clip=2.0, tile=8):
    """Adaptive histogram equalization (CLAHE)."""
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
    l = clahe.apply(l)

    lab = cv2.merge((l, a, b))
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

def nothing(x):
    pass


'''   CALLER FUNCTION   '''

def enhance_frame(frame, mode:int=2, brightness:int=50, contrast:int=50, gamma_val:int=100):
    '''
    Modes:\n
        0:  OFF : No image enhancements applied\n
        1:  MANUAL : Manual Adjustment (modify input parameters brightness, contrast, gamma_val)\n
        2:  HISTOGRAM EQUALIZATION : Enhances global brightness/contrast (good for underexposed frames).\n
        3:  CLACHE : Enhances contrast locally while avoiding over-saturation (best for uneven lighting)\n
    Parameter Scales:\n
        int brightness  :   [0,100]\n
        int contrast    :   [0,100]\n
        int gamma_val   :   [0,300]\n
    input:\n
        -> frame\n
        -> mode\n
        -> brightness\n
        -> contrast\n
        -> gamma_val\n
    returns:\n
        -> enhanced_frame
    '''
    if mode == 0:   # OFF
        return frame
    
    elif mode == 1: # Manual
        brightness -= 50
        contrast -= 50
        gamma_val /= 100.0
        gamma_val = max(0.1, gamma_val)

        enhanced = adjust_brightness_contrast_gamma(frame, brightness, contrast, gamma_val)

    elif mode == 2: # Histogram Equalization
        enhanced = auto_histogram_equalization(frame)

    elif mode == 3: # CLAHE
        enhanced = auto_clahe(frame)

    # Resize both frames for consistency
    h, w = frame.shape[:2]
    enhanced_resized = cv2.resize(enhanced, (w, h))
    return enhanced_resized


'''   TESTING   '''

def main():
    cap = cv2.VideoCapture(0)

    cv2.namedWindow("Comparison")

    # Manual adjustment sliders
    cv2.createTrackbar("Brightness", "Comparison", 50, 100, nothing)
    cv2.createTrackbar("Contrast", "Comparison", 50, 100, nothing)
    cv2.createTrackbar("Gamma", "Comparison", 10, 300, nothing)

    # Auto-enhance mode: 0=Manual, 1=HistEq, 2=CLAHE
    cv2.createTrackbar("Mode", "Comparison", 0, 2, nothing)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        mode = cv2.getTrackbarPos("Mode", "Comparison")

        if mode == 0:  # Manual
            brightness = cv2.getTrackbarPos("Brightness", "Comparison") - 50
            contrast = cv2.getTrackbarPos("Contrast", "Comparison") - 50
            gamma_val = cv2.getTrackbarPos("Gamma", "Comparison") / 100.0
            gamma_val = max(0.1, gamma_val)

            enhanced = adjust_brightness_contrast_gamma(frame, brightness, contrast, gamma_val)

        elif mode == 1:  # Histogram Equalization
            enhanced = auto_histogram_equalization(frame)

        elif mode == 2:  # CLAHE
            enhanced = auto_clahe(frame)

        # Resize both frames for consistency
        h, w = frame.shape[:2]
        enhanced_resized = cv2.resize(enhanced, (w, h))
        comparison = np.hstack((frame, enhanced_resized))

        # Add labels
        comparison = cv2.putText(comparison.copy(), "Original", (30, 30),
                                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        comparison = cv2.putText(comparison.copy(), "Enhanced", (w + 30, 30),
                                 cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Comparison", comparison)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()