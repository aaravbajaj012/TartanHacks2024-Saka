import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Load your audio file
audio = AudioSegment.from_file("example.mp3")

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Calculate the number of 5-second chunks
num_chunks = len(audio) // 5000  # 5000 ms = 5 seconds

for i in range(num_chunks + 1):  # +1 to include the last chunk which may be less than 5 seconds
    # Extract 5-second chunk
    start_ms = i * 5000
    end_ms = start_ms + 5000
    chunk = audio[start_ms:end_ms]

    # Export chunk to a temporary file
    chunk.export(f"chunk_{i}.wav", format="wav")
    
    with sr.AudioFile(f"chunk_{i}.wav") as source:
        audio_listened = recognizer.record(source)
        # Try recognizing the chunk
        try:
            text = recognizer.recognize_google(audio_listened)
            words = text.split()
            # Calculate pace (words per minute)
            pace = len(words) / (5 / 60)  # Since each chunk is 5 seconds long
            print(f"Chunk {i+1}: Words = {len(words)}, Pace = {pace:.2f} WPM")
        except sr.UnknownValueError:
            print(f"Chunk {i+1}: Speech not understood")
        except sr.RequestError as e:
            print(f"Chunk {i+1}: Could not request results; {e}")
