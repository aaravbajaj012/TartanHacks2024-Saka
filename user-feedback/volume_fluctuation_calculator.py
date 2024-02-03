from pydub import AudioSegment
import numpy as np

# Load the MP3 file
audio = AudioSegment.from_file("example2.mp3")

# Calculate volume for each second
volumes = []
for i in range(0, len(audio), 500):  # 1000ms = 1 second
    segment = audio[i:i+1000]
    loudness = segment.dBFS
    volumes.append(loudness)

print(len(volumes))
print(volumes)
