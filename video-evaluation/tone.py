import asyncio

from hume import HumeBatchClient, HumeStreamClient, StreamSocket
from hume.models.config import ProsodyConfig

client = HumeBatchClient("kPRwB7YpdFaNqgrprMzHmAgiK0fAPAGcucdA3ZU53NvKyEUk")
config = [ProsodyConfig()]
files = ["example.mp3"]

job = client.submit_job([], config, files=files)

print(job)
print("Running...")

job.await_complete()
predictions = job.get_predictions()
prediction_outcomes = predictions[0]['results']['predictions'][0]['models']['prosody']['grouped_predictions'][0]['predictions']


for i in range(len(prediction_outcomes)):
    emotions = prediction_outcomes[i]['emotions']
    
    special_dict = {}
    for i in range(len(emotions)):
        special_dict[emotions[i]['name']] = emotions[i]['score']
    
    print(max(special_dict, key=special_dict.get))