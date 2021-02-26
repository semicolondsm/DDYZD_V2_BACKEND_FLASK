from app.errors import websocket
from app.errors import http
from app.models import ClubHead 
from app.models import Room
from app.models import User
from app.models import Club
from app.models import MsgType
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
        logger.info('ROOM TOKEN REQUIRED: '+str(args))
        token = args[0].get('room_token')
        try:
            json = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms="HS256")
        except jwt.ExpiredSignatureError as e:
            return emit('error', websocket.Unauthorized('ExpiredSignatureError'), namespace='/chat')
        except Exception as e:
            return emit('error', websocket.Unauthorized(), namespace='/chat')
        json['args'] = args[0] # 나머지 argument는 처리하지 않고 'args' 키에 담아 넘겨준다
        
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


def send_alarm(fn):
    '''
    요약: 알람 보내는 처리를 하는 데코레이터
    send_chat, helper_apply, helper_schedule, helper_result에서 사용한다.
    '''
    @wraps(fn)
    def wrapper(json):
        room = Room.query.get(json.get('room_id'))
        #일반 유저가 메시지를 보낸 경우
        if json.get('user_type') == 'U':
            send_user = room.user.name
            recv_user = room.club.club_head[0].club_head_user
        #동아리장이 메시지를 보낸 경우
        else:
            send_user = room.club.club_name
            recv_user = room.user

        # 일반 채팅 메시지인 경우
        if json.get('msg_type') == MsgType(1):
            msg = json.get('msg')
        # 봇이 보낸 메시지인 경우
        else:
            msg = json.get('title')

        emit('alarm', {'room_id': str(json.get('room_id'))}, room=recv_user.session_id)
        # title: 보내는 사람 이름 혹은 보내는 동아리 이름
        # msg: 일반 유저인 경우 일반 메시지, 봇인 경우 제목을 전송
        fcm_alarm(sender=send_user, msg=msg, token=recv_user.device_token)

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


def get_apply_message(user, club, major):
    title = '{name}님이 동아리에 지원하셨습니다'.format(name=user.name) 
    msg = '{gcn} {name}님이 {club}에 {major} 분야로 지원하셨습니다'\
        .format(gcn=user.gcn, name=user.name, club=club.club_name, major=major)
    
    return title, msg


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
        user = User.query.get(json.get('user_id'))
        club = Club.query.get(json.get('club_id'))
        json['title'], json['msg'] = get_apply_message(user, club, json.get('major'))
        json['msg_type'] = MsgType(2)  # fcm 알림을 보낼 때 사용할 봇이 보낸 메시지임을 알려둠

        return fn(json)
    return wrapper


def get_schedule_message(user, club, date, location):
    title = '{user_name}님의 면접 일정'.format(user_name=user.name)
    msg = '''{gcn} {user_name}님의 {club_name} 동아리 면접 일정입니다
    
    일시: {date}
    장소: {location}'''.format(
    gcn=user.gcn, 
    user_name=user.name, 
    club_name=club.club_name,
    date=date,
    location=location)
    
    return title, msg


def schedule_information_required(fn):
    '''
    요약: helper_schedule 이벤트에서 일정 정보를 처리하는 데코레이터
    room_token_required과 같이 연계되어 사용되어야한다.
    '''
    @wraps(fn)
    def wrapper(json):
        if json.get('args').get('date') is None or json.get('args').get('location') is None:
            return emit('error', websocket.BadRequest('Please send with date and location'), namespace='/chat')
        user = Room.query.get(json.get('room_id')).user
        club = Club.query.get(json.get('club_id'))
        json['title'], json['msg'] = get_schedule_message(user, club, json.get('args').get('date'), json.get('args').get('location'))
        json['msg_type'] = MsgType(2)  # fcm 알림을 보낼 때 사용할 봇이 보낸 메시지임을 알려둠
    
        return fn(json)
    return wrapper


def get_result_message(user, club, result=False):
    if result:
        title = "{user}님 {club} 동아리 합격을 축하드립니다!".format(user=user.name, club=club.club_name)
        msg = "{user}님의 {club} 동아리 면접결과, 합격을 알려드립니다".format(user=user.name, club=club.club_name)
    else:
        title = "{user}님은 불합격하셨습니다".format(user=user.name)
        msg = "{user}님의 {club} 동아리 면접결과, 불합격을 알려드립니다".format(user=user.name, club=club.club_name)

    return title, msg    


def result_required(fn):
    '''
    요약: helper_result 동아리 면접 결과 처리하는 데코레이터
    마찬가지로 room_token_required와 같이 연계되어야 한다.
    '''
    @wraps(fn)
    def wrapper(json):
        json['result'] = json.get('args').get('result')
        if json.get('result') is None:
            return emit('error', websocket.BadRequest('Please send with result'), namespace='/chat')
        user = Room.query.get(json.get('room_id')).user
        club = Club.query.get(json.get('club_id'))
        json['title'], json['msg'] = get_result_message(user, club, result=json.get('result'))
        json['msg_type'] = MsgType(2) # fcm 알림을 보낼 때 사용할 봇이 보낸 메시지임을 알려둠

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
        logger.info('CHAT JSON: '+str(json))
        json['msg'] = json.get('args').get('msg')
        if json.get('msg') is None:
            return emit('error', websocket.BadRequest('Please send with message'), namespace='/chat')
        json['msg_type'] = MsgType(1) # fcm 알림을 보낼 때  일반 채팅 메시지 임을 알려둠
        
        return fn(json)
    return wrapper
