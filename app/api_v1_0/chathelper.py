from app.decorator import schedule_information_required
from app.decorator import apply_message_required
from app.decorator import room_token_required
from app.decorator import result_required
from app.decorator import room_writed
from app.decorator import send_alarm
from app.decorator import room_read
from app.errors import websocket
from app.models import User 
from app.models import Club
from app.models import Major
from app.models import Application
from app.models import Chat
from app.models import Room
from app import logger
from app import db
from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_socketio import emit


# 동아리 지원
@room_token_required
@apply_message_required
@room_writed
@send_alarm
def helper_apply(json):
    user = User.query.get(json.get('user_id'))
    club = Club.query.get(json.get('club_id'))
    major = Major.query.filter_by(club_id=json.get('club_id'), major_name=json.get('major')).first()
    
    # 일반 유저가 아닌 사람이 사용한 경우인지
    if json.get('user_type') != 'U':
        return emit('error', websocket.BadRequest('Only common user use this helper'), namespace='/chat') 
    # 동아리에 이미 가입한 경우인지
    if user.is_member(club):
        return emit('error', websocket.BadRequest('You are already member of this club'), namespace='/chat')
    # 동아리에 이미 신청한 경우인지
    if user.is_applicant(club=club, result=False):
        return emit('error', websocket.BadRequest('You are already apply to this club'), namespace='/chat')
    # 동아리 지원 기간이 아닌 경우인지
    if not club.is_recruiting():
        return emit('error', websocket.BadRequest('Club is not recruiting now!'), namespace='/chat')
    # 동아리가 모집하는 분야가 아닐 때 경우인지
    if major is None:
        return emit('error', websocket.BadRequest('Club does not need '+str(json.get('major'))), namespace='/chat')
    
    emit('recv_chat', {'title': json.get('title'), 'msg': json.get('msg'), 'user_type': 'H1'}, room=json.get('room_id'))
    db.session.add(Application(club_id=json.get('club_id'), user_id=json.get('user_id'), result=False))
    db.session.add(Chat(room_id=json.get('room_id'), title=json.get('title'), msg=json.get('msg'), user_type='H1'))
    db.session.commit()
    
    logger.info('[Helper Apply] - '+ json.get('title'))


# 면접 스케쥴 
@room_token_required
@schedule_information_required
@room_writed
@send_alarm
def helper_schedule(json):
    user = Room.query.get(json.get('room_id')).user
    club = Club.query.get(json.get('club_id'))    
 
    # 동아리 장이 아닌 사람이 호출한 경우
    if json.get('user_type') != 'C':
        return emit('error', websocket.Forbidden('Only club head use this helper'), namespace='/chat') 
    # 신청자가 아닌 사람에게 보낸 경우
    if not user.is_applicant(club, result=False):
        return emit('error', websocket.BadRequest('The user is not applicant'), namespace='/chat') 

    emit('recv_chat', {'title': title, 'msg': msg, 'user_type': 'H2'}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), title=title, msg=msg, user_type='H2'))
    db.session.commit()
    
    logger.info('[Helper Schedule] - '+ title)


@room_token_required
@result_required
@room_writed
@send_alarm
def helper_result(json):
    user = Room.query.get(json.get('room_id')).user
    club = Club.query.get(json.get('club_id'))   

    # 동아리 장이 아닌 사람이 호출한 경우
    if json.get('user_type') != 'C':
        return emit('error', websocket.Forbidden('Only club head use this helper'), namespace='/chat') 
     # 신청자가 아닌 사람에게 보낸 경우
    if not user.is_applicant(club, result=False):
        return emit('error', websocket.BadRequest('The user is not applicant'), namespace='/chat') 
    
    emit('recv_chat', {'title': title, 'msg': msg, 'user_type': 'H3'}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), title=title, msg=msg, user_type='H3'))
    db.session.commit()
 

def helper_answer(json):
    pass
