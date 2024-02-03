import cv2
from deepface import DeepFace

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

vidcap = cv2.VideoCapture("example2.mp4")
fps_in = vidcap.get(cv2.CAP_PROP_FPS)
fps_out = 1

vidcap.set(cv2.CAP_PROP_FPS, 3)
success, image = vidcap.read()
total_count = 0
gaze_count = 0

index_in = -1
index_out = -1
analyze_dict = {}

while success:
    success = vidcap.grab()
    if not success: break
    index_in += 1

    out_due = int(index_in / fps_in * fps_out)
    if out_due > index_out:
        success, image = vidcap.retrieve()
        if not success: break
        index_out += 1

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        analyze = DeepFace.analyze(image, actions=['emotion'])[0]['emotion']

        max_expression = max(analyze, key=analyze.get)

        keys = list(analyze.keys())
        # for i in range(len(keys)):
        #     if (index_in == 0):
        #         analyze_dict = analyze
        #         analyze_dict = dict.fromkeys(analyze_dict, 0)
        #     else:
        #         analyze_dict[keys[i]] += analyze[keys[i]]
        #         # analyze_dict[keys[i]] += 1
        if (index_in == 0):
            analyze_dict = analyze
            analyze_dict = dict.fromkeys(analyze_dict, 0)
        else:
            analyze_dict[max_expression] += 1

        total_count += 1
    # print(index_in)

# total = sum(list(analyze_dict.values()), 0.0)
# new_dict = {k: v / total for k, v in analyze_dict.items()}

print(analyze_dict)
print(max(analyze_dict, key=analyze_dict.get))
