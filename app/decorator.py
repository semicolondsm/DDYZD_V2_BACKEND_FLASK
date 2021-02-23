from app.errors import websocket
from app.errors import http
from app.models import ClubHead 
from app.models import Room
from app.models import User
from app import logger
from config import Config
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_socketio import emit
from functools import wraps
from flask import request
import jwt


def room_token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        logger.info(str(args))
        token = args[0].get('room_token')
        try:
            json = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms="HS256")
        except jwt.ExpiredSignatureError as e:
            return emit('error', websocket.Unauthorized('ExpiredSignatureError'))
        except Exception as e:
            return emit('error', websocket.Forbidden())

        json['msg'] = args[0].get('msg')
        json['major'] = args[0].get('major')
        return fn(json)
    return wrapper
