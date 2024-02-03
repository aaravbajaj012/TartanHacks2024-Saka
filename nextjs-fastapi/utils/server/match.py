from motor.motor_asyncio import AsyncIOMotorClient
import datetime
import uuid
import json
from utils.server.connection_manager import manager
from utils.server.db import set_match_status, set_match_prompt, add_match_feedback, check_both_analysis_completed, calculate_and_update_result, db
from fastapi import File, UploadFile
from openai import OpenAI
from utils.server.speech_feedback import get_feedback_from_video

async def create_prompt(match_id: str, player_1_id: str, player_2_id: str):
    prompt = get_prompt(prompt_type="format")

    if prompt == None:
        await set_match_status(match_id, 'failed')

        await manager.send_personal_message("match_failed", player_1_id)
        await manager.send_personal_message("match_failed", player_2_id)

    else:
        # update prompt in the match entry
        await set_match_prompt(match_id, prompt)

        await manager.send_personal_message("match_ready", player_1_id)
        await manager.send_personal_message("match_ready", player_2_id)

# Function to get prompt
def get_prompt(prompt_type: str = "creative"):
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

    system_prompt = creative_system_prompt if prompt_type == "creative" else formal_system_prompt

    user_prompt = "Generate a two sentence prompt for this face-to-face improv competition."

    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )

    print(completion.choices[0].message.content)

    if completion.choices[0].message.content == "":
        return None
        
    return completion.choices[0].message.content

async def analyze_replay(match_id: str, user_id: str, replay_file_path: str):

    # strip the extension from the file path and verify it is 
    # a valid replay file

    stripped_file_path = replay_file_path.split('.')[0]

    print(stripped_file_path)

    assert replay_file_path.endswith('.mp4')

    print('Starting Processing')

    feedback = get_feedback_from_video(stripped_file_path)

    print('Completed Processing')

    # update the database with the analysis
    await add_match_feedback(match_id, user_id, feedback)

    # check if both feedbacks are received, if so calculate result, set status to completed and send result to both players

    is_analysis_completed, player_1_id, player_2_id = await check_both_analysis_completed(match_id)
    if is_analysis_completed:
        winner, player_feedback, opponent_feedback, player_updated_elo, opponent_updated_elo, player_elo_delta, opponent_elo_delta = await calculate_and_update_result(match_id, user_id)

        if winner:
            await set_match_status(match_id, 'completed')

            # create json with winner and feedback
            feedback_player_json = json.dumps({'player_feedback': player_feedback, 'opponent_feedback': opponent_feedback, 'winner': winner == user_id, 'player_rating': player_updated_elo, 'opponent_rating': opponent_updated_elo, 'player_rating_delta' : player_elo_delta, 'opponent_rating_delta' : opponent_elo_delta})
            feedback_opponent_json = json.dumps({'player_feedback': opponent_feedback, 'opponent_feedback': player_feedback, 'winner': winner != user_id, 'player_rating': opponent_updated_elo, 'opponent_rating': player_updated_elo, 'player_rating_delta' : opponent_elo_delta, 'opponent_rating_delta' : player_elo_delta})

            if user_id == player_1_id:
                await manager.send_personal_message("match_completed:" + feedback_player_json, player_1_id)
                await manager.send_personal_message("match_completed:" + feedback_opponent_json, player_2_id)
            else:
                await manager.send_personal_message("match_completed:" + feedback_player_json, player_2_id)
                await manager.send_personal_message("match_completed:" + feedback_opponent_json, player_1_id)

    # get the elo rating of the player and update it

    # upload file to s3 bucket