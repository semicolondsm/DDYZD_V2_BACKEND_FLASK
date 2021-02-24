from app.errors import websocket
from app.errors import http
from app.models import ClubHead 
from app.models import Room
from app.models import User
from app.models import Club
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
        token = args[0].get('room_token')
        try:
            json = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms="HS256")
        except jwt.ExpiredSignatureError as e:
            return emit('error', websocket.Unauthorized('ExpiredSignatureError'), namespace='/chat')
        except Exception as e:
            return emit('error', websocket.Unauthorized(), namespace='/chat')
        json['args'] = args[0]
        
        return fn(json)
    return wrapper


def room_read(fn):
    @wraps(fn)
    def wrapper(json):
        room = Room.query.get(json.get('room_id'))
        room.read(user_type=json.get('user_type'))

        return fn(json)
    return wrapper


def room_writed(fn):
    @wraps(fn)
    def wrapper(json):
        room = Room.query.get(json.get('room_id'))
        room.writed(user_type=json.get('user_type'))

        return fn(json)
    return wrapper


def apply_message_required(fn):
    @wraps(fn)
    def wrapper(json):
        json['major'] = json.get('args').get('major')
        if json['major'] is None:
            return emit('error', websocket.BadRequest('Please send with major'), namespace='/chat')

        return fn(json)
    return wrapper


def chat_message_required(fn):
    @wraps(fn)
    def wrapper(json):
        json['msg'] = json.get('args').get('msg')
        if json['msg'] is None:
            return emit('error', websocket.BadRequest('Please send with message'), namespace='/chat')
        
        return fn(json)
    return wrapper


def schedule_information_required(fn):
    @wraps(fn)
    def wrapper(json):
        json['date'] = json.get('args').get('date')
        json['location'] = json.get('args').get('location')
        if json['date'] is None or json['location'] is None:
            return emit('error', websocket.BadRequest('Please send with date and location'), namespace='/chat')
            
        return fn(json)
    return wrapper


def room_member_required(fn):
    @wraps(fn)
    def wrapper(room_id):
        room = Room.query.get_or_404(room_id)
        user = User.query.get_or_404(get_jwt_identity())
        if not user.is_member(room=room):
            return http.BadRequest("You are not a member for the room: "+str(room.id))
        
        return fn(user, room)
    return wrapper


def club_member_required(fn):
    @wraps(fn)
    def wrapper(club_id):
        club = Club.query.get_or_404(club_id)
        user = User.query.get_or_404(get_jwt_identity())
        if not user.is_member(club=club):
            return http.BadRequest("You are not a member for the room: "+str(room.id))
        
        return fn(user, club)
    return wrapper   
