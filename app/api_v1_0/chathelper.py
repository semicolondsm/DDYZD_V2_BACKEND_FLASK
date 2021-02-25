from app.decorator import schedule_information_required
from app.decorator import apply_message_required
from app.decorator import room_token_required
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


def get_apply_message(user, club, major):
    title = '{name}님이 동아리에 지원하셨습니다'.format(name=user.name) 
    msg = '{gcn} {name}님이 {club}에 {major} 분야로 지원하셨습니다'\
        .format(gcn=user.gcn, name=user.name, club=club.club_name, major=major.major_name)
    
    return title, msg


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
    
    title, msg = get_apply_message(user=user, club=club, major=major)
    emit('recv_chat', {'title': title, 'msg': msg, 'user_type': 'H1'}, room=json.get('room_id'))
    
    db.session.add(Application(club_id=json.get('club_id'), user_id=json.get('user_id'), result=False))
    db.session.add(Chat(room_id=json.get('room_id'), title=title, msg=msg, user_type='H1'))
    db.session.commit()
    
    logger.info('[Helper Apply] - '+ title)


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
        return emit('error', websocket.BadRequest('Only club head use this helper'), namespace='/chat') 
    # 신청자가 아닌 사람에게 보낸 경우
    if not user.is_applicant(club, result=False):
        return emit('error', websocket.BadRequest('The user is not applicant'), namespace='/chat') 

    title, msg = get_schedule_message(user, club, json.get('date'), json.get('location'))
    emit('recv_chat', {'title': title, 'msg': msg, 'user_type': json.get('user_type')}, room=json.get('room_id'))
 
    db.session.add(Chat(room_id=json.get('room_id'), title=title, msg=msg, user_type='H2'))
    db.session.commit()
    
    logger.info('[Helper Schedule] - '+ title)


@room_writed
def helper_result(json):
    pass

def helper_answer(json):
    pass
