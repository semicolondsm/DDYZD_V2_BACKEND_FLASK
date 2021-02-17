from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Room, ClubHead, Club
from flask_socketio import join_room
from app import logger
from app import websocket
from config import Config
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


# 룸 토큰 반환
@jwt_required()
def room_token(club_id):
    club_head_id = ClubHead.query.filter_by(club_id=club_id).first().id
    room = Room.query.filter_by(user=get_jwt_identity(), club_head_id=club_head_id).first()
    if room is None:
        room = Room(user=get_jwt_identity(), club_head_id=club_head_id)
    token = jwt.encode({"room_id": room.id, 'sub': get_jwt_identity()}, Config.ROOM_SECRET_KEY, algorithm="HS256")

    return {'room-token': token}, 200


def connect():
    logger.info('Socket Connect Successfully')
    websocket.emit('response', {'msg': 'Socket Connect Successfully'}, namespace='/chat')


def join_room(json):
    logger.info('<Join Room> Data:'+str(json))
    websocket.emit('response', {'msg': 'join room'}, namespace='/chat')


def disconnect():
    logger.info('Socket Disconnected')

# @api.route('/chat/<int:room_id>/breakdown', methods=['GET'])
# def breakdown(room_id):
#     pass
