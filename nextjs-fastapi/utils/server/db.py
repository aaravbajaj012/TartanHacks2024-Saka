from motor.motor_asyncio import AsyncIOMotorClient
import datetime
import uuid
import json
from utils.server.connection_manager import manager
from utils.server.elo import calculate_new_elo

uri = "mongodb+srv://arjund:Zz0qmsu7kGy7FeR1@cluster0.2b6fzke.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(uri)
db = client['improv-royale']

async def calculate_and_update_result(match_id: str, user_id: str):
    matches = db['matches']
    match = await matches.find_one({'match_id': match_id})

    if match:
        new_players = match['players']
        if match['players'][0]['user_id'] == user_id:
            player_feedback = new_players[0]['feedback']
            opponent_feedback = new_players[1]['feedback']
        elif match['players'][1]['user_id'] == user_id:
            player_feedback = new_players[1]['feedback']
            opponent_feedback = new_players[0]['feedback']
        
        opponent_id = match['players'][0]['user_id'] if match['players'][0]['user_id'] != user_id else match['players'][1]['user_id']
        # calculate result
        if score in player_feedback and score in opponent_feedback:
            if player_feedback['score'] > opponent_feedback['score']:
                winner = user_id
            else:
                winner = opponent_id
        else:
            winner = 'Draw'

        await matches.update_one({ 'match_id': match_id }, { '$set': { 'result': winner } })

        # get the elo of the players
        users = db['users']
        player = await users.find_one({'user_id': user_id})
        opponent = await users.find_one({'user_id': opponent_id})

        player_elo = player['elo']
        opponent_elo = opponent['elo']

        elo_winner = 1 if winner == user_id else 0
        if winner == 'Draw':
            elo_winner = 0.5

        player_new_elo = calculate_new_elo(player_elo, opponent_elo, winner)
        opponent_new_elo = calculate_new_elo(opponent_elo, player_elo, 1 - winner)

        await users.update_one({ 'user_id': user_id }, { '$set': { 'elo': player_new_elo } })
        await users.update_one({ 'user_id': opponent_id }, { '$set': { 'elo': opponent_new_elo } })

        delta_player_elo = player_new_elo - player_elo
        delta_opponent_elo = opponent_new_elo - opponent_elo

        return winner, player_feedback, opponent_feedback, player_new_elo, opponent_new_elo, delta_player_elo, delta_opponent_elo

    return None, None, None

async def check_both_analysis_completed(match_id: str):
    matches = db['matches']
    match = await matches.find_one({'match_id': match_id})

    if match:
        if 'feedback' in match['players'][0] and 'feedback' in match['players'][1]:
            return True, match['players'][0]['user_id'], match['players'][1]['user_id']

    return False, None, None

async def add_match_feedback(match_id: str, user_id: str, feedback: dict):
    matches = db['matches']
    match = await matches.find_one({'match_id': match_id})

    if match:
        new_players = match['players']
        if match['players'][0]['user_id'] == user_id:
            new_players[0]['feedback'] = feedback

        elif match['players'][1]['user_id'] == user_id:
            new_players[1]['feedback'] = feedback

        await matches.update_one({ 'match_id': match_id }, { '$set': { 'players': new_players } })

        return True

    return False

async def update_player_ready(match_id: str, user_id: str):
    matches = db['matches']
    match = await matches.find_one({'match_id': match_id})

    if match:
        new_players = match['players']
        if match['players'][0]['user_id'] == user_id:
            new_players[0]['is_ready'] = True

        elif match['players'][1]['user_id'] == user_id:
            new_players[1]['is_ready'] = True

        await matches.update_one({ 'match_id': match_id }, { '$set': { 'players': new_players } })

async def check_both_ready(match_id: str):
    matches = db['matches']
    match = await matches.find_one({'match_id': match_id})

    if match:
        if match['players'][0]['is_ready'] and match['players'][1]['is_ready']:
            return True, match['players'][0]['user_id'], match['players'][1]['user_id']

    return False, None, None

async def get_match_prompt(match_id: str):
    matches = db['matches']
    match = await matches.find_one({'match_id': match_id})

    if match and match['prompt'] != '':
        return match['prompt']

    return None

async def set_match_prompt(match_id: str, prompt: str):
    matches = db['matches']
    await matches.update_one({ 'match_id': match_id }, { '$set': { 'prompt': prompt } })

async def set_match_status(match_id: str, status: str):
    matches = db['matches']
    match = await matches.find_one({'match_id': match_id})

    if match:
        await matches.update_one({ 'match_id': match_id }, { '$set': { 'status': status } })

async def add_to_queue(user_id: str):
    queue = db['queue']
    await queue.insert_one({ 'user_id': user_id, 'timestamp': datetime.datetime.now(), 'status': 'waiting' })
    await manager.send_personal_message("finding_match", user_id)

async def remove_from_queue(user_id: str):
    queue = db['queue']
    # update status to matched
    await queue.update_one({ 'user_id': user_id, 'status': 'waiting' }, { '$set': { 'status': 'matched' } })

async def create_match_entry(player_user_id: str, opponent_user_id: str):
    users = db['users']
    player = await users.find_one({'user_id': player_user_id})
    opponent = await users.find_one({'user_id': opponent_user_id})

    if player is None or opponent is None:
        return None, None, None
    
    matches = db['matches']
    match_id = str(uuid.uuid4())

    # players should be a list of two objects of the form
    # { 'user_id': '...', 'replay_file_url': '', 'is_ready': 'false'}

    players_list = [{'user_id': player_user_id, 'replay_file_url': '', 'is_ready': False}, {'user_id': opponent_user_id, 'replay_file_url': '', 'is_ready': False}]

    await matches.insert_one({ 'match_id': match_id, 'timestamp': datetime.datetime.now(), 'status': 'created', 'players': players_list, 'result' : '', 'prompt': ''})
    
    # put the player and opponent into a json object
    player_json = json.dumps({'name': player['name'], 'profile_pic': player['profile_pic'], 'elo': player['elo']})
    opponent_json = json.dumps({'name': opponent['name'], 'profile_pic': opponent['profile_pic'], 'elo': opponent['elo']})

    player_reply_json = json.dumps({'match_id': match_id, 'player' : player_json, 'opponent': opponent_json})
    opponent_reply_json = json.dumps({'match_id': match_id, 'player' : opponent_json, 'opponent': player_json})

    return match_id, player_reply_json, opponent_reply_json