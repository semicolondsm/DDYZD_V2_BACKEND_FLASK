from . import api_v1_0 as api
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Room, ClubHead, Club
from app import websocket
from flask_socketio import join_room
from flask_socketio import emit
from app import logger
import json

# 채팅들 리스트 반환
@jwt_required()
def chat_list():
    user = User.query.get_or_404(get_jwt_identity())
    rooms = []
    for room in user.rooms:
        rooms.append(room.json())

    return json.dumps(rooms, ensure_ascii=False).encode('utf8')


# 채팅방 입장
@jwt_required()
def enter_room(club_id):
    club_head_id = ClubHead.query.filter_by(club_id=club_id).first().id
    room = Room.query.filter_by(user=get_jwt_identity(), club_head_id=club_head_id).first()
    if room is None:
        room = Room(user=get_jwt_identity(), club_head_id=club_head_id)
    join_room(room.id)

    return {"room_id": room.id}, 200
    

@api.route('/club/<int:room_id>/chat', methods=['POST'])
def post_chat(room_id):
    pass 

@api.route('/chat/<int:room_id>/breakdown', methods=['GET'])
def breakdown(room_id):
    pass

@websocket.on('connect', namespace='/chat')
def connect():
    logger.info('Socket Connection')

@websocket.on('request', namespace='/chat')
def response(data):
    print('response: ', data)
