import asyncio

from hume import HumeBatchClient, HumeStreamClient, StreamSocket
from hume.models.config import FaceConfig, ProsodyConfig

client = HumeBatchClient("kPRwB7YpdFaNqgrprMzHmAgiK0fAPAGcucdA3ZU53NvKyEUk")
config = [ProsodyConfig(), FaceConfig()]
files = ["example2.mp4"]

emotion_mapping = {
    "angry": ["Anger", "Annoyance", "Contempt", "Disapproval", "Frustration"],
    "disgust": ["Disgust"],
    "fear": ["Fear", "Anxiety", "Dread", "Terror"],
    "happy": ["Joy", "Amusement", "Contentment", "Pride", "Satisfaction", "Triumph", "Admiration", "Love"],
    "sad": ["Sadness", "Disappointment", "Empathic Pain", "Guilt", "Regret", "Shame"],
    "surprise": ["Surprise (positive)", "Surprise (negative)", "Amazement", "Astonishment"],
    "neutral": ["Neutral", "Calmness", "Indifference", "Apathy"]
}

job = client.submit_job([], config, files=files)

print(job)
print("Running...")

job.await_complete()
predictions = job.get_predictions()
prediction_outcomes = predictions[0]['results']['predictions'][0]['models']['prosody']['grouped_predictions'][0]['predictions']
prediction_face_outcomes = predictions[0]['results']['predictions'][0]['models']['face']['grouped_predictions'][0]['predictions']

for i in range(len(prediction_outcomes)):
    emotions = prediction_outcomes[i]['emotions']
    emotions_face = prediction_face_outcomes[i]['emotions']
    
    special_dict = {}
    special_face_dict = {}
    for i in range(len(emotions)):
        special_dict[emotions[i]['name']] = emotions[i]['score']
        special_face_dict[emotions_face[i]['name']] = emotions_face[i]['score']
    
    max_value = max(special_dict, key=special_dict.get)
    print(max_value)
    print(special_dict.items())
    
    keys = [key for key, value in emotions.items() if (max_value in value)]

    max_face_value = max(special_face_dict, key=special_face_dict.get)
    keys_face = [key for key, value in emotions_face.items() if max_face_value in value]

    print(keys, keys_face)