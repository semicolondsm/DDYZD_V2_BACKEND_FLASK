from app.decorator import room_token_required
from app.models import User, Club, Major
from app.errors import websocket
from app import logger
from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_socketio import emit


def get_apply_message(user, club, field=None):
    title= '{name}님이 지원하셨습니다.'.format(name=user.name) 
    msg = '{gcn} {name}님이 {club}에 {field}분야로 지원하셨습니다.'\
        .format(gcn=user.gcn, name=user.name, club=club.club_name, field=field)
    
    return {'title': title, 'msg': msg}


# 채팅들 리스트 반환
@room_token_required
def helper_apply(json):
    if json.get('user_type') != 'U':
        return emit('error', BadRequest("Only user can do this!"))
    user = User.query.get(json.get('user_id'))
    club = Club.query.get(json.get('club_id'))
    major = Major.query.filter_by(club_id=json.get('club_id'), major_name=json.get('major')).first()

    if not club.is_recruiting():
        return emit('error', {'msg': websocket.BadRequest('Club is not recruiting now!')}, namespace='/chat')
    if major not in club.majors:
        return emit('error', {'msg': websocket.BadRequest('Club does not need '+major.major_name)}, namespace='/chat')
    
    emit('response', get_apply_message(user, club, json.get('field')), room=json.get('room_id'))
    logger.info(json.get('room_id'))


def helper_schedule(json):
    pass


def helper_result(json):
    pass


def helper_answer(json):
    pass
