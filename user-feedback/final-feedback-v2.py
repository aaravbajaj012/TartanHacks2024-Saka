from moviepy.editor import *
import os

# imports for deepgram
import asyncio
from dotenv import load_dotenv
from deepgram import Deepgram
import numpy as np

# imports for openai
from openai import OpenAI

# import for tone analysis
from hume import HumeBatchClient, HumeStreamClient, StreamSocket
from hume.models.config import ProsodyConfig

# imports for volume fluctuation calculator
from pydub import AudioSegment
import numpy as np

# imports for filler facial expression analysis
import cv2
from deepface import DeepFace

# imports for eye contact analysis
from gaze_tracking import GazeTracking


# Function to convert mp4 to mp3 gets automatically called at start of function I think
def MP4ToMP3(mp4, mp3):
    FILETOCONVERT = AudioFileClip(mp4)
    FILETOCONVERT.write_audiofile(mp3)
    FILETOCONVERT.close()

# Function to get prompt
def get_prompt():
    client = OpenAI(api_key="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")

    creative_system_prompt = "You are an administrator focused on generating prompts for a face-to-face improv \
        competition; two individuals will use this prompt to generate a thirty second speech. This prompt \
        would be two sentences, with the first sentence outlining the scenario and the second sentence \
        being some task that the individual needs to explain to the audience. It should generally be \
        of the format: You are a [...] that does [...]. Your goal is to [...]. \
        Here are a few examples: \
        You are a renowned scientist who has discovered a new superfood. Your goal is to convince the audience of its benefits and how it can replace coffee. \
        You are a time traveler from the future where music is used as currency. Your goal is to explain to the audience how this new economic system works. \
        You are a detective specialized in recovering lost memories. Your goal is to explain to the audience how you solve the mystery of forgotten birthdays."

    formal_system_prompt = "You are an administrator focused on generating prompts for a face-to-face improv \
        competition; two individuals will use this prompt to generate a thirty second speech. This prompt \
        would be two sentences, with the first sentence outlining the scenario and the second sentence \
        being some task that the individual needs to explain to the audience. It should generally be \
        of the format: You are a [...] that does [...]. Your goal is to [...]. Make sure that this prompt aims \
        at honing presentation skills and improving public speaking, having some formal undertone. \
        Here are a few examples: \
        You are a project manager tasked with leading a multinational team on a groundbreaking environmental initiative. Your goal is to present your project plan and collaboration strategy to the board of directors, emphasizing cross-cultural communication and teamwork. \
        You are a university lecturer who has developed an innovative teaching method that significantly improves student engagement and learning outcomes. Your goal is to persuade the academic committee to adopt this method across the curriculum, highlighting its benefits and implementation process. \
        You are a financial analyst who has identified an emerging market with significant investment potential. Your goal is to convince your firm's investment committee to allocate resources to this market, presenting your analysis and risk management strategy."

    user_prompt = "Generate a two sentence prompt for this face-to-face improv competition."

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": formal_system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    )

    print(completion.choices[0].message)
    return completion.choices[0].message

# Got the mp3 file, now we can use deepgram to transcribe it
async def get_transcript(AUDIO_FILE_PATH):
    load_dotenv()
    DEEPGRAM_API_KEY = os.getenv('5d7be873315c16dea99482a6faa46bc3a0a8e96c')
    deepgram = Deepgram('5d7be873315c16dea99482a6faa46bc3a0a8e96c')
    with open(AUDIO_FILE_PATH, 'rb') as audio:
        source = { 'buffer': audio, 'mimetype': 'audio/mp3' }
        transcription_options = { 'punctuate': True, 'diarize': True, 'paragraphs': True, 'filler_words': True}
        response = await deepgram.transcription.prerecorded(source, transcription_options)
        transcript = response['results']['channels'][0]['alternatives'][0]['transcript']
        return response, transcript

# Function to calculate Words Per Minute (WPM)
def calculate_wpm(words, duration):
    total_words = len(words)
    wpm = total_words / (duration / 60)
    return wpm

# Function to calculate Pause Duration and Frequency
def calculate_pause_metrics(words):
    pauses = [words[i]['start'] - words[i-1]['end'] for i in range(1, len(words))]
    avg_pause_duration = np.mean(pauses)
    total_pause_time = np.sum(pauses)
    std_pause_duration = np.std(pauses)
    number_of_pauses = len(pauses)
    return avg_pause_duration, total_pause_time, number_of_pauses, std_pause_duration

# Function to determine the ideal pace for an improv delivery based on chat with GPT-3
def determine_improv_pace(prompt):
    # Initialize the OpenAI client with your API key
    client = OpenAI(api_key="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")

    # Define a system prompt that instructs the AI on the task
    system_prompt = "You are an AI designed to analyze improv prompts and suggest the ideal pace of delivery for the performance. Based on the content, context, and emotional tone of the prompt, determine whether the pace should be slow, medium, or fast. Consider factors such as the complexity of the language, the emotional impact of the content, and the desired audience engagement. \
        Only give one word inside of your prompt. Here is an example. \
        Example 1 Prompt: You are a time traveler from the future where music is used as currency. Your goal is to explain to the audience how this new economic system works. Example 1 Response: medium \
        Example 2 Prompt: You are a mourning son. Your goal is to give a funeral speech for your dead mother. Example 2 Response: slow"

    # User prompt: the actual improv prompt you want to analyze for pace
    user_prompt = "Generate a pace recommendation for this face-to-face improv scenario. Your answer can strictly only be 'slow', 'medium', or 'fast'. Give only one word."

    # Create the chat completion
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt + " " + str(prompt)}
        ]
    )

    # Print and return the suggested pace
    suggested_pace = completion.choices[0].message.content
    print(completion.choices[0].message.content)
    #strip whitespace and any sort of punctuation from volume
    suggested_pace = suggested_pace.strip()
    suggested_pace = suggested_pace.strip(".")
    print(f'suggested_pace: {suggested_pace}')
    #make the following test case insensitive
    if "slow" not in suggested_pace and "medium" not in suggested_pace and "fast" not in suggested_pace and "Slow" not in suggested_pace and "Medium" not in suggested_pace and "Fast" not in suggested_pace:
        return "medium"

    return suggested_pace

# Perform calculations for pace metrics
def calculate_metrics(response, prompt):
    pace_score = 0
    ideal_pace = determine_improv_pace(prompt)
    slow_pace = 115
    medium_pace = 145
    fast_pace = 180

    words_data = response['results']['channels'][0]['alternatives'][0]['words']
    wpm = calculate_wpm(words_data, response['metadata']['duration'])

    # whatever pace wpm is closest to, if its within 15 of that pace, then we set user_pace to that pace, and if user_pace is equal to ideal_pace, then pace_score is 1
    user_pace = ""
    if abs(wpm - slow_pace) <= 15:
        user_pace = "slow"
    elif abs(wpm - medium_pace) <= 15:
        user_pace = "medium"
    elif abs(wpm - fast_pace) <= 15:
        user_pace = "fast"

    # print(f'user pace: {user_pace} and ideal pace: {ideal_pace}')
    
    if user_pace == ideal_pace:
        pace_score = 1

    avg_pause_duration, total_pause_time, number_of_pauses, pause_variation = calculate_pause_metrics(words_data)

    return avg_pause_duration, total_pause_time, pause_variation
    
    # print(f'Pace Score: {pace_score}')
    # print(f'Average Pause Duration: {avg_pause_duration}')
    # print(f'Total Pause Time: {total_pause_time}')
    # print(f'Number of Pauses: {number_of_pauses}')
    # print(f'Pause Variation: {pause_variation}')

# Function to determine the tone of the speaker based on chat with GPT
def determine_tone(prompt):
    # Initialize the OpenAI client with your API key
    client = OpenAI(api_key="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")

    # Define a system prompt that instructs the AI on the task
    system_prompt = "You are an AI designed to analyze improv prompts and rank from a list of sevens, including angry, disgust, fear, happy, sad, surprise, neutral. \
        Based on the content and emotional tone of the prompt, determine which of the following tone/emotions fit best by ranking them using a list. \
        Let the first element of the list be the most relevant, the second element be the second most, and so on. The last element should be \
        the least relevant to the prompt. Consider factors such as the complexity of the language, the emotional impact of the content, and the desired audience engagement. \
        Here is an example: \
        Example 1 Prompt: You are a time traveler from the future where music is used as currency. Your goal is to explain to the audience how this new economic system works. \
        Example 1 Ranking: surprise, happy, neutral, curiosity, amusement, confusion, doubt \
        \
        "

    # User prompt: the actual improv prompt you want to analyze for pace
    user_prompt = "Generate a ranked list of values with commas for this face-to-face improv scenario. Your answer can strictly only be angry, disgust, fear, happy, sad, surprise, neutral. Don't add quotes around the list."

    # Create the chat completion
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt + " " + str(prompt)}
        ]
    )

    # Print and return the suggested pace
    tone = completion.choices[0].message.content
    print(completion.choices[0].message.content)

    gpt_tone = tone.replace(".", " ")
    gpt_tone = tone.replace(",", " ")
    gpt_tone = gpt_tone.split()
    #strip whitespace from gpt_tone
    gpt_tone = [word.strip() for word in gpt_tone]
    # put words in gpt_tone into a list of lowercase words in the same order as they are in the string
    gpt_tone = [word.lower() for word in gpt_tone]

    if 'angry' not in gpt_tone and 'disgust' not in gpt_tone and 'fear' not in gpt_tone and 'happy' not in gpt_tone and 'sad' not in gpt_tone and 'surprise' not in gpt_tone and 'neutral' not in gpt_tone:
        gpt_tone = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

    return gpt_tone
    #make the following test case insensitive
    #strip white space from tone
    # tone = tone.strip()
    # tone = tone.strip('.')

    # print(f'tone: {tone}')
    # #change it to be if any of the following are not in the string tone, then error
    
    # return tone.lower()

def analyze_tone(prompt, audio_file):
    emotion_mapping = {
        "angry": ["Anger", "Annoyance", "Contempt", "Disapproval", "Disgust", "Frustration", "Irritation"],
        "disgust": ["Disgust", "Contempt", "Revulsion"],
        "fear": ["Anxiety", "Fear", "Horror", "Panic", "Shock", "Terror"],
        "happy": ["Admiration", "Adoration", "Amusement", "Aesthetic Appreciation", "Contentment", "Ecstasy", "Enthusiasm", "Excitement", "Joy", "Love", "Pride", "Satisfaction", "Triumph"],
        "sad": ["Disappointment", "Empathic Pain", "Guilt", "Nostalgia", "Regret", "Sadness", "Shame", "Sorrow"],
        "surprise": ["Awe", "Surprise (negative)", "Surprise (positive)", "Amazement", "Astonishment"],
        "neutral": ["Boredom", "Calmness", "Curiosity", "Interest", "Neutral", "Serenity", "Stillness"]
    }
    
    tone_list = determine_tone(prompt)
    client = HumeBatchClient("kPRwB7YpdFaNqgrprMzHmAgiK0fAPAGcucdA3ZU53NvKyEUk")
    config = [ProsodyConfig()]
    files = [str(audio_file)]

    job = client.submit_job([], config, files=files)

    print(job)
    print("Running...")

    job.await_complete()
    predictions = job.get_predictions()
    prediction_outcomes = predictions[0]['results']['predictions'][0]['models']['prosody']['grouped_predictions'][0]['predictions']

    emotion_dict = {}
    for i in range(len(prediction_outcomes)):
        emotions = prediction_outcomes[i]['emotions']
        
        special_dict = {}
        for i in range(len(emotions)):
            special_dict[emotions[i]['name']] = emotions[i]['score']
        
        emotion_name = max(special_dict, key=special_dict.get)
        if emotion_name in emotion_dict:
            emotion_dict[emotion_name] += 1
        else:
            emotion_dict[emotion_name] = 1

    max_emotion = max(emotion_dict, key=emotion_dict.get)
    keys_face = [key for key, value in emotion_mapping.items() if max_emotion in value]

    if (keys_face == []):
        get_index = tone_list.index("neutral")
    else:
        get_index = tone_list.index(keys_face[0])

    return max_emotion, (10 - get_index)*10

# Function to determine the ideal volume levels for an improv delivery based on chat with GPT-3
def determine_volume_fluctuation(prompt):
    # Initialize the OpenAI client with your API key
    client = OpenAI(api_key="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")

    # Define a system prompt that instructs the AI on the task
    system_prompt = "You are an AI designed to analyze improv prompts and suggest the ideal volume level in delivery for the performance. Based on the content, context, and emotional tone of the prompt, determine whether the volume level should be low, medium, or high. Consider factors such as the complexity of the language, the emotional impact of the content, and the desired audience engagement."

    # User prompt: the actual improv prompt you want to analyze for pace
    user_prompt = "Generate a volume level for this face-to-face improv scenario. Your answer can strictly only be 'low', 'medium', or 'high'."

    # Example improv prompt to analyze
    improv_prompt = "You find yourself stranded on a deserted island with only a talking parrot for company. Your goal is to convince the parrot to help you find food and resources for survival."

    # Create the chat completion
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt + " " + str(prompt)}
        ]
    )

    # Print and return the suggested pace
    volume = completion.choices[0].message.content
    print(completion.choices[0].message.content)

    print(f'Volume: {volume}')
    #strip whitespace and any sort of punctuation from volume
    volume = volume.strip()
    volume = volume.strip(".")
    print(f'Volume: {volume}')

    if 'low' not in volume and 'medium' not in volume and 'high' not in volume and 'Low' not in volume and 'Medium' not in volume and 'High' not in volume:
        raise ValueError("Invalid volume suggested by GPT-3")

    if volume == "low" or volume == "Low":
        return -20
    elif volume == "medium" or volume == "Medium":
        return -10
    elif volume == "high" or volume == "High":
        return 0
    
    return volume

# Function to calculate volume fluctuation
# Function to calculate volume fluctuation
def calculate_volume_fluctuation(prompt, AUDIO_FILE_PATH):
    ideal_volume = determine_volume_fluctuation(prompt)
    ideal_volume = (float)(ideal_volume)
    audio = AudioSegment.from_file(AUDIO_FILE_PATH)

    # Calculate volume for each second
    volumes = []
    for i in range(0, len(audio), 500):  # 1000ms = 1 second
        segment = audio[i:i+1000]
        loudness = segment.dBFS
        volumes.append(loudness)

    # Calculate average volume difference
    volume_difference = abs(ideal_volume - np.mean(volumes))
    print(f'Volume Difference: {volume_difference}')
    volume_fluctuation = np.std(volumes) * 2
    print(f'Volume Fluctuation: {volume_fluctuation}')
    return volume_difference, volume_fluctuation

# Function to calculate filler words
def filler_word_calculator(transcript):
    # make it so that the deep_gram_fillers are not case sensitive by adding all possibiilities to the set
    deep_gram_fillers = {'uh', 'um', 'mhmm', 'mm-mm', 'uh-uh', 'uh-huh', 'nuh-uh', 'Uh', 'Um', 'Mhmm', 'Mm-mm', 'Uh-uh', 'Uh-huh', 'Nuh-uh'}
    # also give me a percentage of the total words in the transcript that are fillers
    transcript = transcript.replace(".", " ")
    words = transcript.split()
    #strip whitespace around words
    words = [word.strip() for word in words]
    print(words)
    filler_count = 0
    for word in words: 
        if word in deep_gram_fillers: 
            filler_count += 1 
    print(f'filler count: {filler_count} and percentage: {(filler_count / len(words)) * 100}')
    return filler_count, (filler_count / len(words)) * 100

# Function to get the relevance of the script based on chat with GPT-3
def get_script_relevance(transcript, prompt):
    client = OpenAI(api_key="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")

    # 85
    # script = "Esteemed members of the investment committee, today I present an opportunity that stands at the frontier of innovation and growth. Our extensive analysis has identified an emerging market poised for significant returns. This market, characterized by its robust economic indicators and untapped potential, offers a unique blend of risk and reward. We've conducted a thorough risk assessment, factoring in geopolitical, economic, and market-specific variables. Our strategy for risk management includes a phased investment approach, diversification across sectors, and continuous monitoring for agile adjustments. By capitalizing on this opportunity, we not only stand to gain substantial financial returns but also position our firm as a leader in recognizing and seizing global investment prospects. I urge us to move forward with a strategic allocation of resources, demonstrating our commitment to innovation, growth, and prudent risk management. Thank you for considering this transformative opportunity."
    # prompt = "You are a financial analyst who has identified an emerging market with significant investment potential. Your goal is to convince your firm's investment committee to allocate resources to this market, presenting your analysis and risk management strategy."

    # 35

    system_prompt = " \
        You are an administrator of a face-to-face improv competition, where you will be evaluating the relevance of the \
        script that an individual has made up in relation to the prompt given to them at the start. \
        \
        The rubric for rating the content relevance of the script to the prompt is as follows: \
        Keyword and Phrase Alignment: \
        Check for the presence of specific keywords and phrases from the prompt within the script. These could be technical terms, thematic vocabulary, or action words that directly relate to the prompt's subject or objectives. \
        Evaluate the frequency and context of these keywords and phrases, ensuring they are used in a manner that contributes meaningfully to the script's content, rather than being included superficially. \
        \
        Semantic and Thematic Relevance: \
        Assess the script for its adherence to the core themes and concepts introduced in the prompt. This involves looking beyond mere keywords to understand the underlying ideas and arguments being presented. \
        Consider whether the script explores the same topics, presents similar arguments or narratives, or engages with the same concepts as those outlined in the prompt, even if it uses different terminology or examples. \
        \
        Purpose and Objective Alignment: \
        Determine if the script's purpose and objectives align with those implied or stated in the prompt. This includes the intended outcome of the script (e.g., to persuade, inform, entertain) and whether it addresses the prompt's call to action or question. \
        Evaluate the script's structure, argumentation, and conclusion to ensure they collectively work towards achieving the goal set forth by the prompt, reflecting an understanding of the prompt's underlying intent. \
        \
        You should be extremely harsh with grading, with almost no scripts getting above a 90 for their rating."

    user_prompt = f"The script is {transcript} and the prompt is {prompt}. Rate the content relevance of the script to the prompt from a scale of 1 to 100. Give a singular number and no explanation."

    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    )

    print(f'Content Relevance: {completion.choices[0].message}')
    print(type(completion.choices[0].message))
    print(f'Content Relevance: {completion.choices[0].message.content}')
    return (int)(completion.choices[0].message.content)

def analyze_facial_expression(prompt, MP4_FILE_PATH):
    tone_list = determine_tone(prompt)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    vidcap = cv2.VideoCapture(MP4_FILE_PATH)
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
            analyze = DeepFace.analyze(image, enforce_detection=False, actions=['emotion'])[0]['emotion']

            max_expression = max(analyze, key=analyze.get)

            keys = list(analyze.keys())
            if (index_in == 0):
                analyze_dict = analyze
                analyze_dict = dict.fromkeys(analyze_dict, 0)
            else:
                analyze_dict[max_expression] += 1

            total_count += 1

    max_emotion = max(analyze_dict, key=analyze_dict.get)
    print(max_emotion)
    get_index = tone_list.index(max_emotion)

    return max_emotion, (10 - get_index)*10


def get_eye_contact_percent(VIDEO_FILE):
    gaze = GazeTracking()
    vidcap = cv2.VideoCapture(VIDEO_FILE)
    fps_in = vidcap.get(cv2.CAP_PROP_FPS)
    fps_out = 3

    vidcap.set(cv2.CAP_PROP_FPS, 3)
    success, image = vidcap.read()
    total_count = 0
    gaze_count = 0
    center_count = 0

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
            if gaze.is_center():
                center_count += 1

            total_count += 1

    print(gaze_count / total_count)
    threshold = 0.85
    non_gaze_percent = 1 - (gaze_count / total_count)
    return non_gaze_percent, abs(threshold - non_gaze_percent) * 100

def main(file_name):
    # Get the prompt
    score = 0
    prompt = get_prompt()

    VIDEO_FILE_PATH = file_name + ".mp4"
    AUDIO_FILE_PATH = file_name + ".mp3"
    MP4ToMP3(VIDEO_FILE_PATH, AUDIO_FILE_PATH)
    print("example.mp3 made successfully!")
    

    # Convert the video to mp3 shuold have been done already


    # Get the transcript
    response, transcript = asyncio.run(get_transcript(AUDIO_FILE_PATH))
    # print(f'response: {response}')
    # print(f'transcript: {transcript}')

    # Analyze the eye contact from the video
    gaze_contact_percent, eye_contact_score = get_eye_contact_percent(VIDEO_FILE_PATH)
    score += eye_contact_score

    # Analyze facial emotions from the video
    max_facial_expression, emotions_score = analyze_facial_expression(prompt, VIDEO_FILE_PATH)
    score += emotions_score

    # Calculate pace and pause metrics
    avg_pause_duration, total_pause_time, pause_variation = calculate_metrics(response, prompt)
    score -= (avg_pause_duration*20 + total_pause_time*2 + pause_variation/2)

    # Analyze the tone of the speaker
    audio_tone, tone_score = analyze_tone(prompt, AUDIO_FILE_PATH)
    score += tone_score

    # Calculate volume fluctuation
    volume_difference, volume_fluctuation = calculate_volume_fluctuation(prompt, AUDIO_FILE_PATH)
    score -= (volume_difference/3 + volume_fluctuation/4)

    # Calculate filler words
    filler_count, filler_percentage = filler_word_calculator(transcript)
    score -= (filler_count*10)

    # Get the relevance of the script based on chat with GPT-3
    content_relevance = get_script_relevance(transcript, prompt)
    score += content_relevance

    final_score = score / 4

    print(f'Final score: {final_score}!!')

    # Organize the metrics into a dictionary
    feedback = {
        "score": final_score,
        "eye_contact_percentage": gaze_contact_percent*100,
        "eye_percent_away_from_threshold": eye_contact_score,
        "max_facial_emotion": max_facial_expression,
        "facial_emotion_score": emotions_score,
        "gpt-tone": determine_tone(prompt)[0],
        "avg_pause_duration": avg_pause_duration,
        "total_pause_time": total_pause_time,
        "pause_variation": pause_variation,
        "audio_tone": audio_tone,
        "tone_score": tone_score,
        "volume_difference": volume_difference,
        "volume_fluctuation": volume_fluctuation,
        "filler_count": filler_count,
        "filler_percentage": filler_percentage,
        "content_relevance": content_relevance
    }

    print(f'Feedback: {feedback}')
    return feedback

main("dad1")