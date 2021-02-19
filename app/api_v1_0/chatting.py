from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Room, ClubHead, Club, Chat
from flask_socketio import leave_room
from flask_socketio import join_room
from flask_socketio import emit
from app import logger
from config import Config
from flask import request
from datetime import datetime
from datetime import timedelta
import json
import jwt


# 채팅들 리스트 반환
@jwt_required()
def chat_list():
    rs = User.query.get_or_404(get_jwt_identity()).rooms
    rooms = []
    for r in rs:
        rooms.append(r.json())

    return json.dumps(rooms, ensure_ascii=False).encode('utf8')


# 채팅방 만들기
@jwt_required()
def make_room(club_id):
    room = Room.query.filter_by(user_id=get_jwt_identity(), club_id=club_id).first_or_404()
    if room is None:
        room = Room(user=get_jwt_identity(), club_head_id=club_head_id, user_looked=False, head_looked=False)
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


# 채팅 섹션 보기
@jwt_required()
def chat_section():
    user = User.query.get_or_404(get_jwt_identity())
    sections = user.get_chat_section()

    return json.dumps(sections, ensure_ascii=False).encode('utf8'), 200

# 소켓 연결
@jwt_required()
def connect():
    logger.info('[Socket Connect Successfully] - '+str(request.headers).strip())
    emit('response', {'msg': 'Socket Connect Successfully'}, namespace='/chat')


# 방 입장
def event_join_room(json):
    join_room(json.get('room_id'))
    emit('response', {'msg': 'Join Room Success'}, namespace='/chat')


# 방 나가기
def event_leave_room(json):
    leave_room(json.get('room_id'))
    emit('response', {'msg': 'Leave Room Success'}, namespace='/chat')


# 채팅 보내기
def event_send_chat(json):
    emit('recv_chat', {'data': json.get('data')}, room=json.get('room_id'))
    logger.info(str(json))
    

# 소켓 연결 끊기
def disconnect():
    logger.info('[Socket Disconnected]')

