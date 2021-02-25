from app.errors import websocket
from app.errors import http
from app.models import ClubHead 
from app.models import Room
from app.models import User
from app.models import Club
from app.fcm import fcm_alarm
from app import logger
from config import Config
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_socketio import emit
from functools import wraps
from flask import request
import jwt


def room_token_required(fn):
    '''
    요약: 채팅방 토큰을 요구하는 데코레이터
    send_chat, join_room, leave_room,
    helper_apply, helper_schedule, helper_result에 사용한다.
    '''
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


def room_member_required(fn):
    '''
    요약: 채팅방 맴버인지 확인하는 데코레이터
    room_info, breakdown, room_token, room_refresh에 사용한다.
    rest api에서 사용되는 것은 room_member_required 이고,
    websocket event를 비슷하게 처리하기위해 room_token_required를 사용해야한다.
    '''
    @wraps(fn)
    def wrapper(room_id):
        room = Room.query.get_or_404(room_id)
        user = User.query.get_or_404(get_jwt_identity())
        if not user.is_member(room=room):
            return http.BadRequest("You are not a member for the room: "+str(room.id))
        
        return fn(user, room)
    return wrapper


def club_member_required(fn):
    '''
    요약: 동아리 맴버인지 확인하는 데코레이터 
    applicant_list에서 사용한다.
    '''
    @wraps(fn)
    def wrapper(club_id):
        club = Club.query.get_or_404(club_id)
        user = User.query.get_or_404(get_jwt_identity())
        if not user.is_member(club=club):
            return http.BadRequest("You are not a member for the room: "+str(room.id))
        
        return fn(user, club)
    return wrapper   


def schedule_information_required(fn):
    '''
    요약: helper_schedule 이벤트에서 일정 정보를 처리하기 위한 데코레이터
    room_token_required과 같이 연계되어 사용되어야한다.
    '''
    @wraps(fn)
    def wrapper(json):
        json['date'] = json.get('args').get('date')
        json['location'] = json.get('args').get('location')
        if json['date'] is None or json['location'] is None:
            return emit('error', websocket.BadRequest('Please send with date and location'), namespace='/chat')
            
        return fn(json)
    return wrapper


def send_alarm(fn):
    '''
    요약: 알람 보내는 처리를 하는 데코레이터
    send_chat, helper_apply, helper_schedule, helper_result에서 사용한다.
    '''
    @wraps(fn)
    def wrapper(json):
        room = Room.query.get(json.get('room_id'))
        if json.get('user_type') == 'U':
            '''
            일반 유저가 메시지를 보낸 경우
            동아리장에게 알림이 간다
            '''
            user = room.club.club_head[0].club_head_user
        else:
            '''
            동아리장이 메시지를 보낸 경우
            일반 유저에게 알림이 간다
            '''
            user = room.user
        emit('alarm', {'room_id': str(json.get('room_id'))}, room=user.session_id)
        fcm_alarm(title=json.get('title'), msg=json.get('msg'), token=user.device_token)

        return fn(json)
    return wrapper

def room_read(fn):
    '''
    요약: 채팅방 읽음 처리 데코레이터
    join_room, leave_room 이벤트에서 사용한다. 
    '''
    @wraps(fn)
    def wrapper(json):
        room = Room.query.get(json.get('room_id'))
        room.read(user_type=json.get('user_type'))

        return fn(json)
    return wrapper


def room_writed(fn):
    '''
    요약: 채팅방 읽지 않음 처리 데코레이터
    send_chat, helper_apply, helper_schedule, helper_result에서 사용한다.
    일반 유저가 보낸경우 동아리장이 읽지 않음처리가 되고 동아리장이 보낸 경우엔 그 반대.
    room_read 데코레이터와 처리 방법이 반대다.(헷갈릴 수 있음)
    '''
    @wraps(fn)
    def wrapper(json):
        room = Room.query.get(json.get('room_id'))
        room.writed(user_type=json.get('user_type'))

        return fn(json)
    return wrapper


def apply_message_required(fn):
    '''
    요약: 동아리 지원 메시지 처리 데코레이터
    동아리 지원시 메시지를 처리해주는 데코레이터다(에러 처리 및 전처리 포함)
    helper_apply에서 사용한다.
    '''
    @wraps(fn)
    def wrapper(json):
        json['major'] = json.get('args').get('major')
        if json['major'] is None:
            return emit('error', websocket.BadRequest('Please send with major'), namespace='/chat')

        return fn(json)
    return wrapper


def chat_message_required(fn):    
    '''
    요약: 채팅 메시지 처리 데코레이터
    채팅시 메시지를 처리해주는 데코레이터다(에러 처리 및 전처리 포함)
    send_chat에서 사용한다.
    '''
    @wraps(fn)
    def wrapper(json):
        json['msg'] = json.get('args').get('msg')
        if json['msg'] is None:
            return emit('error', websocket.BadRequest('Please send with message'), namespace='/chat')
        
        return fn(json)
    return wrapper