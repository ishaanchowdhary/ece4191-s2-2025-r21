#!/usr/bin/env python3
'''
Written by: Ishaan Chowdhary (33115303)
Last edited: 26/08/2025

Testing script for testing trained YOLO Models through camera feed or stored video.
Additionally measures latency to run model and display image feed.
'''
from ultralytics import YOLO
import cv2
import numpy as np
import time

VIDEO_PATH = "object_detection/data_collection/videos/second_batch.mp4"  # Change to your test video file
MODEL_PATH = "models/best_v1.pt"  # Change to your YOLO model file
USE_CAM = False


def annotate_image(image, detections):
    """Annotates the image with bounding boxes."""
    for det in detections:
        x1, y1, x2, y2 = det["x1"], det["y1"], det["x2"], det["y2"]
        label = f"{det['label']}: {det['confidence']:.2f}"
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)        
    return image

def run_yolo(model, images):
    """Runs YOLO model on a batch of images."""
    results = model(images,verbose=False)
    detections = []

    for result in results:
        detection_list = []
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            confidence = box.conf.item()
            class_id = int(box.cls)
            detection_list.append({
                "label": model.names[class_id],
                "confidence": confidence,
                "x1": x1, "y1": y1, "x2": x2, "y2": y2
            })

        detections.append(detection_list)

    return detections

if __name__ == '__main__':
    print("Get on the beers bruh\n|\|\ \n(-.-)\n|> >\n\|\|")
    model = YOLO(MODEL_PATH)
    if USE_CAM == True:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(VIDEO_PATH)
    
    while cap.isOpened():
        try:
            start = time.time()
            ret, frame = cap.read()

            if not ret:
                break

            detections = run_yolo(model, frame)            
            annotated_frame = annotate_image(frame, detections[0])
            cv2.imshow("YOLO Animal Detection", annotated_frame)
            print(f"Latency: {(time.time() - start)*1000:.2f} ms")
            cv2.waitKey(1)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        except KeyboardInterrupt:
            print("Terminating Script ...")
            break
    
    cap.release()
    cv2.destroyAllWindows()