from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Header, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import datetime
import uuid
from utils.server.connection_manager import manager
from utils.server.db import add_to_queue, remove_from_queue, create_match_entry, set_match_status, update_player_ready, check_both_ready, get_match_prompt, db
from utils.server.match import create_prompt, get_prompt, analyze_replay
import utils.server.firebase
import json
import requests
import os
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
    
@app.get('/api/test-get-prompt')
async def test_get_prompt():
    prompt = get_prompt()

    # if prompt is not none return prompt with 200 status code
    if prompt:
        return prompt
    else:
        # else return 500 status code
        raise HTTPException(status_code=500, detail="Error generating prompt")

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        print("websocket connection")
        await websocket.accept()
        token = await websocket.receive_text()
        #print(token)
        decoded_token = utils.server.firebase.verify_id_token(token)
        #print(decoded_token)

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

                params = event.split(":")

                event_type = params[0]

                if event_type == "add_to_queue":
                    # check if user is already in the queue
                    queue = db['queue']
                    user = await queue.find_one({'user_id': user_id, 'status': 'waiting'})

                    if user is None: # user is not in the queue
                        count = await queue.count_documents({'status': 'waiting'})

                        if count > 0: # there is a waiting opponent
                            opponent = await queue.find_one({'status': 'waiting'}, sort=[('timestamp', 1)])

                            if not manager.check_connection(opponent['user_id']): # the other player is not connected
                                await queue.delete_one({'user_id': opponent['user_id'], 'status': 'waiting'}) # delete the other player from the queue
                                await add_to_queue(user_id) # add user back to the queue
                                continue
                                
                            # the user is matched
                            await remove_from_queue(opponent['user_id']) # remove the other player from the queue

                            # create a match between the two players
                            match_id, player_json_data, opponent_json_data = await create_match_entry(user_id, opponent['user_id'])

                            if match_id is None:
                                await manager.send_personal_message("error_creating_match", user_id)
                                await manager.send_personal_message("error_creating_match", opponent['user_id'])
                                continue
                            
                            # send the match id to both players
                            await manager.send_personal_message("match_found:" + player_json_data, user_id)
                            await manager.send_personal_message("match_found:" + opponent_json_data, opponent['user_id'])

                            await set_match_status(match_id, 'pending')
                            await create_prompt(match_id, user_id, opponent['user_id'])
                        else: # no waiting opponent
                            await add_to_queue(user_id) # add the user to the queue
                    else:
                        await manager.send_personal_message("finding_match", user_id)
                elif event_type == "player_ready":
                    match_id = params[1] # do manual lookup if this is not working
                    await update_player_ready(match_id, user_id)
                    # check if both players are ready
                    is_ready, player_1_id, player_2_id = await check_both_ready(match_id)
                    if is_ready:
                        prompt = await get_match_prompt(match_id)
                        if prompt:
                            await set_match_status(match_id, 'running')

                            await manager.send_personal_message("prompt:" + prompt, player_1_id)
                            await manager.send_personal_message("prompt:" + prompt, player_2_id)
                        else:
                            await set_match_status(match_id, 'failed')

                            await manager.send_personal_message("match_failed", player_1_id)
                            await manager.send_personal_message("match_failed", player_2_id)


                else:
                    await websocket.send_text("invalid_event_type")
    except Exception as e:
        print(e)
        print("reached disconnect block")
        #print(user_id)
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
        return {"message": "User already exists"}
        
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


@app.post('/api/upload-replay')
async def upload_replay(file: UploadFile = File(...), decoded_token: str = Depends(get_token_from_header)):
    UPLOAD_DIR = "./uploads"  # Specify the directory where you want to save the uploaded files

    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
        
    try:
        filename = file.filename

        file_location = f"{UPLOAD_DIR}/{filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())

        # parse the filename to get the match id and user id, they are delimited by a dash and the extension is .mp4
        sender_data = filename.split('_')
        match_id = sender_data[0]
        user_id = sender_data[1].split('.')[0]

        analyze_replay(match_id, user_id, file_location)

        return {"message": "Replay file successfully uploaded"}
    except:
        raise HTTPException(status_code=500, detail="Error analyzing replay file")