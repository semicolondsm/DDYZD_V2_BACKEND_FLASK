from app.decorator import schedule_information_required
from app.decorator import apply_message_required
from app.decorator import room_token_required
from app.decorator import result_required
from app.decorator import room_writed
from app.decorator import send_alarm
from app.decorator import room_read
from app.errors import websocket
from app.models import ClubMember
from app.models import RoomStatus
from app.models import UserType
from app.models import Club
from app.models import User 
from app.models import Club
from app.models import Major
from app.models import Chat
from app.models import Room
from app.models import isoformat
from app.models import kstnow
from app import logger
from app import db
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_socketio import emit


# 동아리 지원
@room_token_required
@apply_message_required
@room_writed
@send_alarm
def helper_apply(json):
    '''
    동아리 면접에 지원하는 채팅 봇
    '''
    room = json.get('room')
    major = Major.query.filter_by(club_id=json.get('club_id'), major_name=json.get('major')).first()
    emit('recv_chat', {'title': json.get('title'), 'msg': json.get('msg'), 'user_type': 'H1', 'date': isoformat(kstnow())}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), title=json.get('title'), msg=json.get('msg'), user_type=UserType(3).name))
    room.status = RoomStatus(2)
    db.session.commit()
    logger.info('[Helper Apply] - '+ json.get('title'))


# 면접 스케쥴 
@room_token_required
@schedule_information_required
@room_writed
@send_alarm
def helper_schedule(json):
    '''
    면접 일정을 공지하는 채팅 봇
    '''
    room = json.get('room')
    emit('recv_chat', {'title': json.get('title'), 'msg': json.get('msg'), 'user_type': 'H2', 'date': isoformat(kstnow())}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), title=json.get('title'), msg=json.get('msg'), user_type=UserType(4).name))
    room.status = RoomStatus(3)
    db.session.commit()
    logger.info('[Helper Schedule] - '+ json.get('title'))


@room_token_required
@result_required
@room_writed
@send_alarm
def helper_result(json):
    '''
    면접 결과를 공지하는 채팅 봇
    '''
    room = json.get('room')
    emit('recv_chat', {'title': json.get('title'), 'msg': json.get('msg'), 'user_type': 'H3', 'date': isoformat(kstnow())}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), title=json.get('title'), msg=json.get('msg'), user_type=UserType(5).name))
    json.get('room').status = RoomStatus(4) # 합격됨
    room.status = RoomStatus(4)
    db.session.commit()
    logger.info('[Helper Result] - '+ json.get('title'))
 

def helper_answer(json):
    pass
