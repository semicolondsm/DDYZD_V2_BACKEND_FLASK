from app.decorator import room_token_required
from app.models import User, Club, Major, Application
from app.errors import websocket
from app import logger
from app import db
from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_socketio import emit


def get_apply_message(user, club, major):
    title= '{name}님이 지원하셨습니다.'.format(name=user.name) 
    msg = '{gcn} {name}님이 {club}에 {major}분야로 지원하셨습니다.'\
        .format(gcn=user.gcn, name=user.name, club=club.club_name, major=major.major_name)
    
    return {'title': title, 'msg': msg}


# 동아리 지원
@room_token_required
def helper_apply(json):
    if json.get('user_type') != 'U':
        return emit('error', BadRequest("Only user can do this!"))
    user = User.query.get(json.get('user_id'))
    club = Club.query.get(json.get('club_id'))
    major = Major.query.filter_by(club_id=json.get('club_id'), major_name=json.get('major')).first()
    
    # 동아리에 이미 가입한 경우
    if user.is_member(club):
        return emit('error', {'msg': websocket.BadRequest('You are already member of this club')}, namespace='/chat')
    # 동아리에 이미 신청한 경우
    if user.is_applicant(club=club, result=False):
        return emit('error', {'msg': websocket.BadRequest('You are already apply to this club')}, namespace='/chat')
    # 동아리 지원 기간이 아닌 경우
    if not club.is_recruiting():
        return emit('error', {'msg': websocket.BadRequest('Club is not recruiting now!')}, namespace='/chat')
    # 동아리가 모집하는 분야가 아닐 때 경우
    if major is None:
        return emit('error', {'msg': websocket.BadRequest('Club does not need '+str(json.get('major')))}, namespace='/chat')
    
    db.session.add(Application(club_id=json.get('club_id'), user_id=json.get('user_id'), result=False))
    db.session.commit()
    
    logger.info('[Helper Apply]'+str(get_apply_message(user=user, club=club, major=major)))
    emit('response', get_apply_message(user=user, club=club, major=major), room=json.get('room_id'))


def helper_schedule(json):
    pass


def helper_result(json):
    pass


def helper_answer(json):
    pass
