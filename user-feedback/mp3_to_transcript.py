import asyncio
import os
from dotenv import load_dotenv
from deepgram import Deepgram
import numpy as np

# # The provided data structure
# data = {
#     'metadata': {
#         'duration': 44.17306,
#         # Other metadata fields
#     },
#     'results': {
#         'channels': [{
#             'alternatives': [{
#                 'words': [
#                     # List of words with start, end, etc.
#                 ]
#             }]
#         }]
#     }
# }

# Extract words data

# Function to calculate Words Per Minute (WPM)
def calculate_wpm(words, duration):
    total_words = len(words)
    wpm = total_words / (duration / 60)
    return wpm

# Function to calculate Average Word Duration
def calculate_avg_word_duration_and_variation(words):
    durations = [word['end'] - word['start'] for word in words]
    avg_duration = np.mean(durations)
    variation = np.std(durations)
    return avg_duration, variation

# Calculates the mean and standard deviation of the time difference between the end of one word and the start of the next.
def calculate_word_differences_stats(words):
    if len(words) < 2:
        return (0, 0)  # Cannot calculate differences with less than two words
    
    # Calculate time differences between the end of one word and the start of the next
    time_differences = [words[i]['start'] - words[i-1]['end'] for i in range(1, len(words))]
    # Calculate mean and standard deviation
    mean_diff = np.mean(time_differences)
    std_diff = np.std(time_differences)
    
    return mean_diff, std_diff

# Function to calculate Pause Duration and Frequency
def calculate_pause_metrics(words):
    pauses = [words[i]['start'] - words[i-1]['end'] for i in range(1, len(words))]
    avg_pause_duration = np.mean(pauses)
    total_pause_time = np.sum(pauses)
    number_of_pauses = len(pauses)
    return avg_pause_duration, total_pause_time, number_of_pauses


load_dotenv()
DEEPGRAM_API_KEY = os.getenv('5d7be873315c16dea99482a6faa46bc3a0a8e96c')

async def main():
    deepgram = Deepgram('5d7be873315c16dea99482a6faa46bc3a0a8e96c')
    with open('example2.mp3', 'rb') as audio:
        source = { 'buffer': audio, 'mimetype': 'audio/mp3' }
        transcription_options = { 'punctuate': True, 'diarize': True, 'paragraphs': True, 'filler_words': True}
        response = await deepgram.transcription.prerecorded(source, transcription_options)
        print(response)
        print()
        print()
        print(type(response))
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
    
    with open('transcript.txt', 'w') as f:
        f.write(transcript)


    print()
    print()
    print()
    # Perform calculations
    words_data = response['results']['channels'][0]['alternatives'][0]['words']
    wpm = calculate_wpm(words_data, response['metadata']['duration'])
    avg_word_duration, std_word_duration = calculate_avg_word_duration_and_variation(words_data)
    avg_interval_duration, std_interval_duration = calculate_word_differences_stats(words_data)
    avg_pause_duration, total_pause_time, number_of_pauses = calculate_pause_metrics(words_data)


    # Print results
    print(f"Words Per Minute: {wpm:.2f}")
    print(f"Average Word Duration: {avg_word_duration:.2f} seconds")
    print(f"Word Duration Variation: {std_word_duration:.2f} seconds")
    print(f"Average Interval Duration: {avg_interval_duration:.2f} seconds")
    print(f"Interval Duration Variation: {std_interval_duration:.2f} seconds")
    print(f"Average Pause Duration: {avg_pause_duration:.2f} seconds")
    print(f"Total Pause Time: {total_pause_time:.2f} seconds")
    print(f"Number of Pauses: {number_of_pauses}")

if __name__ == '__main__':
    asyncio.run(main())