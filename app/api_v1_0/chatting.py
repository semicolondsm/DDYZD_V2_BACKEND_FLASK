from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Room, ClubHead, Club
from flask_socketio import join_room
from app import logger
from app import websocket
from app.decorator import room_token_required
from config import Config
from flask import request
from datetime import datetime
from datetime import timedelta
import json
import jwt

# 채팅들 리스트 반환
@jwt_required()
def chat_list():
    user = User.query.get_or_404(get_jwt_identity())
    rooms = []
    for room in user.rooms:
        rooms.append(room.json())

    return json.dumps(rooms, ensure_ascii=False).encode('utf8')


# 소켓 연결
@jwt_required
def connect():
    logger.info('[Socket Connect Successfully] - '+str(request.headers).strip())
    websocket.emit('response', {'msg': 'Socket Connect Successfully'}, namespace='/chat')


# 방 입장
def event_join_room(user_id, room_id):
    join_room(room_id)
    websocket.emit('response', {'msg': 'join room'}, namespace='/chat')


# 채팅 보내기
def event_send_chat(data, user_id, room_id):
    logger.info(str(data))
    pass
    

# 소켓 연결 끊기
def disconnect():
    logger.info('[Socket Disconnected]')


# @api.route('/chat/<int:room_id>/breakdown', methods=['GET'])
# def breakdown(room_id):
#     pass
