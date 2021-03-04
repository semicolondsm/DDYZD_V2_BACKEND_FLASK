from app.decorator import schedule_information_required
from app.decorator import apply_message_required
from app.decorator import room_token_required
from app.decorator import result_required
from app.decorator import answer_required
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
    emit('recv_chat', {'title': json.get('title'), 'msg': json.get('msg'), 'user_type': UserType.H1.name, 'date': isoformat(kstnow())}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), title=json.get('title'), msg=json.get('msg'), user_type=UserType.H1.name))
    room.status = RoomStatus.A.name
    db.session.commit()


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
    emit('recv_chat', {'title': json.get('title'), 'msg': json.get('msg'), 'user_type': UserType.H2.name, 'date': isoformat(kstnow())}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), title=json.get('title'), msg=json.get('msg'), user_type=UserType.H2.name))
    room.status = RoomStatus.S.name
    db.session.commit()


@room_token_required
@result_required
@room_writed
@send_alarm
def helper_result(json):
    '''
    면접 결과를 공지하는 채팅 봇
    '''
    room = json.get('room')
    emit('recv_chat', {'title': json.get('title'), 'msg': json.get('msg'), 'user_type': UserType.H3.name, 'date': isoformat(kstnow())}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), title=json.get('title'), msg=json.get('msg'), user_type=UserType.H3.name))
    # 면접에 불합격인 사람은 룸상태를 "C" 혹은 "N"으로 변경한다.
    if json['result'] == False:
        if json.get('club').is_recruiting():
            json['room'].status = RoomStatus.N.name
        else:    
            json['room'].status = RoomStatus.C.name
    # 면접에 합격인 사람은 룸상태를 "R"로 변경한다.
    elif json['result'] == True:
        json['room'].status = RoomStatus.R.name
    db.session.commit()


@room_token_required
@answer_required
@room_writed
@send_alarm
def helper_answer(json):
    '''
    면접 결과 응답해주는 채팅 봇
    '''
    room = json.get('room')
    emit('recv_chat', {'title': json.get('title'), 'msg': json.get('msg'), 'user_type': UserType.H4.name, 'date': isoformat(kstnow())}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), title=json.get('title'), msg=json.get('msg'), user_type=UserType.H4.name))
    if json.get('answer'):
        db.session.add(ClubMember(user_id=json.get('user_id'), club_id=json.get('club_id')))
    if json.get('club').is_recruiting():
        json['room'].status = RoomStatus.N.name
    else:    
        json['room'].status = RoomStatus.C.name
    db.session.commit()

