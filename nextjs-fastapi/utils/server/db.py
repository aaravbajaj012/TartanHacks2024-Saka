from motor.motor_asyncio import AsyncIOMotorClient
import datetime
import utils.server.connection_manager

uri = "mongodb+srv://arjund:Zz0qmsu7kGy7FeR1@cluster0.2b6fzke.mongodb.net/?retryWrites=true&w=majority"
client = AsyncIOMotorClient(uri)
db = client['improv-royale']

manager = utils.server.connection_manager.manager

async def run_match(match_id: int):
    matches = db['matches']
    match = await matches.find_one({'match_id': match_id})

    if match:
        await matches.update_one({ 'match_id': match_id }, { '$set': { 'status': 'running' } })
        return match

    return None

async def add_to_queue(user_id: str):
    queue = db['queue']
    await queue.insert_one({ 'user_id': user_id, 'timestamp': datetime.datetime.now(), 'status': 'waiting' })
    await manager.send_personal_message("finding_match", user_id)

async def remove_from_queue(user_id: str):
    queue = db['queue']
    await queue.delete_one({ 'user_id': user_id, 'status': 'completed' })