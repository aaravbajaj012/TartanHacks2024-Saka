from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import datetime
import uuid
from utils.server.connection_manager import manager
from utils.server.db import add_to_queue, run_match, db
import utils.server.firebase
import json
import requests
from pydantic import BaseModel
app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/database-ping")
async def database_ping():
    try:
        users = db['users']
        user = await users.find_one({'name': 'Jane Doe'})
        
        print(user)

        # return a message if the query was successful
        return {"message": "Pinged your deployment. You successfully connected to MongoDB!"}
    except Exception as e:
        return {"message": "Error connecting to MongoDB: " + str(e)}

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        print("websocket connection")
        await websocket.accept()
        token = await websocket.receive_text()
        print(token)
        decoded_token = utils.server.firebase.verify_id_token(token)
        print(decoded_token)

        user_id = decoded_token['user_id']
    except Exception as e:
        print('invalid token')
        await websocket.close()
        return

    try:
        manager.connect(user_id, websocket)

        while True:
            data = await websocket.receive_text()

            # split by the delimiter
            events = data.split(";")

            for event in events:
                print(event)

                params = event.split(":")

                event_type = params[0]

                if event_type == "add_to_queue":
                    # check if user is already in the queue
                    queue = db['queue']
                    user = await queue.find_one({'user_id': user_id, 'status': 'waiting'})

                    if user is None: # user is not in the queue
                        count = await queue.count_documents({'status': 'waiting'})

                        if count > 0: # there is a waiting opponent
                            first_user = await queue.find_one({'status': 'waiting'}, sort=[('timestamp', 1)])

                            if not await manager.check_connection(first_user['user_id']): # the other player is not connected
                                await queue.delete_one({'user_id': first_user['user_id'], 'status': 'waiting'}) # remove the other player from the queue
                                await add_to_queue(user_id) # add user back to the queue
                                continue
                                
                            # the user is matched
                            await queue.update_one({'user_id': first_user['user_id']}, {'$set': {'status': 'matched'}})

                            # create a match between the two players
                            matches = db['matches']
                            match_id = uuid.uuid4()
                            await matches.insert_one({ 'match_id': str(match_id), 'timestamp': datetime.datetime.now(), 'status': 'pending', 'players': [user_id, first_user['user_id']], 'result' : -1})
                            
                            users = db['users']
                            player = await users.find_one({'user_id': user_id})
                            opponent = await users.find_one({'user_id': first_user['user_id']})
                            
                            # put the player and opponent into a json object
                            player_json = json.dumps({'name': player['name'], 'profile_pic': player['profile_pic'], 'elo': player['elo']})
                            opponent_json = json.dumps({'name': opponent['name'], 'profile_pic': opponent['profile_pic'], 'elo': opponent['elo']})

                            player_reply_json = json.dumps({'player' : player_json, 'opponent': opponent_json})
                            opponent_reply_json = json.dumps({'player' : opponent_json, 'opponent': player_json})

                            # send the match id to both players
                            await manager.send_personal_message("match_found:" + player_reply_json, user_id)
                            await manager.send_personal_message("match_found:" + opponent_reply_json, first_user['user_id'])

                            await run_match(match_id)
                        else: # no waiting opponent
                            await add_to_queue(user_id) # add the user to the queue
                    else:
                        await manager.send_personal_message("finding_match", user_id)
                else:
                    await websocket.send_text("invalid_event_type")
    
    except Exception as e:
        print("reached disconnect block")
        print(user_id)
        manager.disconnect(user_id)


def get_token_from_header(Authorization: str = Header()):
    try:
        token = Authorization.split('Bearer ')[1]
        decoded_token = utils.server.firebase.verify_id_token(token)
        return decoded_token
    except Exception as e:
        # throw 403 if token is invalid
        raise HTTPException(status_code=403, detail="Invalid token")

class User(BaseModel):
    user_id: str
    name: str
    profile_pic: str

@app.post("/api/register")
async def register_user(user: User, decoded_token: str = Depends(get_token_from_header)):
    users = db['users']

    user_exists = await users.find_one({'user_id': user.user_id})
    if user_exists:
        raise HTTPException(status_code=403, detail="User already exists")
    
    user_id = user.user_id
    name = user.name
    profile_pic = user.profile_pic
    elo = 1200
    user = {'user_id': user_id, 'name': name, 'profile_pic': profile_pic, 'elo': elo}
    try:
        user = await users.insert_one(user)
        return {"message": "User successfully registered"}
    except Exception as e:
        raise HTTPException(status_code=403, detail="User already exists")
    
@app.get("/api/user-profile")
async def get_user_profile(decoded_token: str = Depends(get_token_from_header)):
    user_id = decoded_token['user_id']
    
    users = db['users']
    user = await users.find_one({'user_id': user_id})

    # return 403 if user is not found
    if not user:
        raise HTTPException(status_code=403, detail="User not found")
    
    # create json object with user data
    user_json = json.dumps({'name': user['name'], 'profile_pic': user['profile_pic'], 'elo': user['elo']})

    return user_json