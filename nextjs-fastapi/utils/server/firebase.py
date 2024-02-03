import firebase_admin
from firebase_admin import auth
import os

cred_obj = firebase_admin.credentials.Certificate('firebaseCert.json')
default_app = firebase_admin.initialize_app(cred_obj)

def verify_id_token(token):
    return auth.verify_id_token(token)