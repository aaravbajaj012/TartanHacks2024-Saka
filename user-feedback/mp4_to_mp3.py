from moviepy.editor import *
import os

def MP4ToMP3(mp4, mp3):
    FILETOCONVERT = AudioFileClip(mp4)
    FILETOCONVERT.write_audiofile(mp3)
    FILETOCONVERT.close()

VIDEO_FILE_PATH = "example2.mp4"
AUDIO_FILE_PATH = "example2.mp3"

print(f'directory: f{os.getcwd()}')
MP4ToMP3(VIDEO_FILE_PATH, AUDIO_FILE_PATH)
print("example.mp3 made successfully!")