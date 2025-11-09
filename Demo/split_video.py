import cv2
import os

input_folder = "1-1 frames"
output_folder = "frames"
os.makedirs(output_folder, exist_ok=True)

frame_interval_sec = 1  # ambil setiap detik

for file in os.listdir(input_folder):
    if not file.endswith(".mp4"):
        continue

    video_path = os.path.join(input_folder, file)
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = int(fps * frame_interval_sec)

    print(f"🎥 {file}: {total_frames} frames, {fps:.2f} FPS")

    count = 0
    saved = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if count % frame_interval == 0:
            filename = f"{os.path.splitext(file)[0]}_t{saved*frame_interval_sec:.0f}s.jpg"
            cv2.imwrite(os.path.join(output_folder, filename), frame)
            saved += 1

        count += 1

    cap.release()
    print(f"✅ {saved} frames disimpan (setiap {frame_interval_sec} detik)\n")
