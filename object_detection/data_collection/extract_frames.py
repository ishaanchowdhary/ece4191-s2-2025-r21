import cv2
import os
from glob import glob

def extract_every_nth_frame(video_path, n=10, base_output_folder="frames"):
    # Get the video filename without extension
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    # Create a subfolder for this video inside the base output folder
    output_folder = os.path.join(base_output_folder, video_name)
    os.makedirs(output_folder, exist_ok=True)

    # Count how many frames already exist in that folder
    existing_frames = len(glob(os.path.join(output_folder, "*.jpg")))
    if existing_frames > 0:
        print(f"Skipping '{video_name}' — frames already extracted.")
        return

    # Open the video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_index = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        if frame_index % n == 0:
            filename = os.path.join(output_folder, f"frame_{frame_index:05d}.jpg")
            cv2.imwrite(filename, frame)
            saved_count += 1

        frame_index += 1

    cap.release()
    print(f"Extracted {saved_count} frames from '{video_name}' into '{output_folder}'.")

if __name__ == "__main__":
    # Folder containing your .mp4 videos
    video_folder = "videos"
    frame_interval = 100  # Change this to the N you want

    # Find all .mp4 files in the folder
    video_files = glob(os.path.join(video_folder, "*.mp4"))

    if not video_files:
        print("No MP4 videos found.")
    else:
        for video in video_files:
            extract_every_nth_frame(video, n=frame_interval)
