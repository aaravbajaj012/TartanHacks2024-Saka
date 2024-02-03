from roboflow import Roboflow
import cv2
import os

rf = Roboflow(api_key="FmFpluCmGyTQeo5gRM3z")
project = rf.workspace().project("emotion-recognition-elft3")
model = project.version(20).model

vidcap = cv2.VideoCapture("example.mp4")
fps_in = vidcap.get(cv2.CAP_PROP_FPS)
fps_out = 3

vidcap.set(cv2.CAP_PROP_FPS, 3)
success, image = vidcap.read()
total_count = 0
gaze_count = 0

index_in = -1
index_out = -1

while success:
    success = vidcap.grab()
    if not success: break
    index_in += 1

    out_due = int(index_in / fps_in * fps_out)
    if out_due > index_out:
        success, image = vidcap.retrieve()
        if not success: break
        index_out += 1

        cv2.imwrite("image.jpg", image)
        print(model.predict("image.jpg", confidence=40, overlap=30).json())
        os.remove("image.jpg") 

        total_count += 1

