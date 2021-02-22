from app.decorator import clubhead_required
from app.decorator import room_token_required
from app.models import User, Room, ClubHead, Club, Chat
from app.errors import http
from app.errors import websocket
from app import db
from app import logger
from config import Config
from datetime import datetime
from datetime import timedelta
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_socketio import leave_room
from flask_socketio import join_room
from flask_socketio import emit
from flask import request
import json
import jwt


# 채팅들 리스트 반환
@jwt_required()
@clubhead_required
def chat_list():
    user = User.query.get_or_404(get_jwt_identity())
    # 유저 권한의 채팅방 검색
    rooms = []
    for r in user.rooms:
        rooms.append(r.json(is_user=True))

    # 동아리장 권한의 채팅방 검색
    for c in user.get_clubs():
        r = Room.query.filter_by(club_id=c.club_id).first_or_404()
        rooms.append(r.json(is_user=False))

    return json.dumps(rooms, ensure_ascii=False).encode('utf8')


# 채팅방 만들기
@jwt_required()
def make_room(club_id):
    room = Room.query.filter_by(user_id=get_jwt_identity(), club_id=club_id).first()
    if room is None:
        room = Room(user_id=get_jwt_identity(), club_id=club_id)
        db.session.add(room)
        db.session.commit()

    return {'room_id': room.id}, 200


# 채팅 내역 보기
@jwt_required()
def breakdown(room_id):
    cs = Chat.query.filter_by(room_id = room_id).order_by(Chat.created_at.desc()).all()
    chats = []
    for c in cs:
        chats.append(c.json())

    return json.dumps(chats, ensure_ascii=False).encode('utf8'), 200


# 룸 토큰 반환
@jwt_required()
def room_token(room_id):
    room = Room.query.get_or_404(room_id)
    user = User.query.get_or_404(get_jwt_identity()) 
    if user.is_user(room=room):
        token = jwt.encode({"room_id": room.id, 'user_id': get_jwt_identity(), "user_type": 'U', \
            'club_id': room.club_id ,"exp": datetime.utcnow()+timedelta(days=1)}, Config.ROOM_SECRET_KEY, algorithm="HS256")
    elif user.is_clubhead(room=room):
        token = jwt.encode({"room_id": room.id, 'user_id': get_jwt_identity(), "user_type": 'C', \
            'club_id': room.club_id, "exp": datetime.utcnow()+timedelta(days=1)}, Config.ROOM_SECRET_KEY, algorithm="HS256")
    else:
        return http.BadRequest("You are not a member for the room: "+str(room.id))
    return {'room_token': token}, 200


# 소켓 연결
def connect():
    logger.info('[Socket Connect Successfully] - '+str(request.headers).strip())
    emit('response', {'msg': 'Socket Connect Successfully'}, namespace='/chat')


# 방 입장
@room_token_required
def event_join_room(json):
    join_room(json.get('room_id'))
    emit('response', {'msg': 'Join Room Success'}, namespace='/chat')


# 채팅 보내기
@room_token_required
def event_send_chat(json):
    logger.info('JSON: '+str(json))
    emit('recv_chat', {'msg': json.get('msg')}, room=json.get('room_id'))
    db.session.add(Chat(room_id=json.get('room_id'), msg=json.get('msg'), user_type=json.get('user_type')))
    db.session.commit()    


# 방 나가기
@room_token_required
def event_leave_room(json):
    leave_room(json.get('room_id'))
    emit('response', {'msg': 'Leave Room Success'}, namespace='/chat')


# 소켓 연결 끊기
def disconnect():
    logger.info('[Socket Disconnected]')
