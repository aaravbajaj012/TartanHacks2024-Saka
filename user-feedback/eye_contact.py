import cv2
from gaze_tracking import GazeTracking

def get_eye_contact_percent(VIDEO_FILE):

    gaze = GazeTracking()
    vidcap = cv2.VideoCapture(VIDEO_FILE)
    fps_in = vidcap.get(cv2.CAP_PROP_FPS)
    fps_out = 3

    vidcap.set(cv2.CAP_PROP_FPS, 3)
    success, image = vidcap.read()
    total_count = 0
    gaze_count = 0

    index_in = -1
    index_out = -1

    looking_away = []

    while success:
        success = vidcap.grab()
        if not success: break
        index_in += 1

        out_due = int(index_in / fps_in * fps_out)
        if out_due > index_out:
            # print(index_in)
            success, image = vidcap.retrieve()
            if not success: break
            index_out += 1

            gaze.refresh(image)
            new_frame = gaze.annotated_frame()

            text = ""

            if gaze.is_right() or gaze.is_left():
                looking_away.append(total_count)
                gaze_count += 1

            total_count += 1

    return gaze_count / total_count, looking_away

eye_contact_percent, look_aways  = get_eye_contact_percent('example.mp4')

print(eye_contact_percent)