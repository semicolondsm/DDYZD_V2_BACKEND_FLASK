from app.decorator import room_token_required
from app.decorator import chat_message_required
from app.decorator import room_member_required
from app.decorator import club_member_required
from app.errors import websocket
from app.errors import http
from app.models import Application
from app.models import ClubHead
from app.models import Club
from app.models import Chat
from app.models import User
from app.models import Room
from app.models import isoformat 
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
def chat_list():
    user = User.query.get_or_404(get_jwt_identity())
    club_id = request.args.get('club_id')
    rooms = []
    index = 0
    # club_id 파라미터가 있을 때 
    if club_id:
        club = Club.query.get_or_404(club_id)
        if not user.is_clubhead(club):
            return http.BadRequest('You do not have permission')
        for r in club.rooms:
            rooms.append(r.json(is_user=False, index=index))

        return {"club_section": club.club_name, "rooms": rooms}, 200
    else:
        # 채팅 섹션
        club_section = [user.name] 
        for club in user.get_clubs():
            club_section.append(club.club_name)

        # 유저 권한의 채팅방 검색

        for r in user.rooms.all().sort(reverse=True):    
            rooms.append(r.json(is_user=True, index=index))

        # 동아리장 권한의 채팅방 검색
        for c in user.get_clubs():
            index = index + 1
            for r in c.rooms.all().sort(reverse=True):
                rooms.append(r.json(is_user=False, index=index))

        return {"club_section": club_section, "rooms": rooms}, 200


# 채팅방 만들기
@jwt_required()
def make_room(club_id):
    room = Room.query.filter_by(user_id=get_jwt_identity(), club_id=club_id).first()
    if room is None:
        room = Room(user_id=get_jwt_identity(), club_id=club_id)
        db.session.add(room)
        db.session.commit()

    return {'room_id': str(room.id), }, 200


# 채팅방 정보
@jwt_required()
@room_member_required
def room_info(user, room):
    if user.is_user(room):
        return {'id': str(room.club.club_id), 'name': room.club.club_name,'image': 'https://api.semicolon.live/file/'+room.club.profile_image}
    else:
        return {'id': str(room.user.gcn), 'name': room.user.name, 'image': room.user.image_path}


# 채팅 내역 보기
@jwt_required()
@room_member_required
def breakdown(user, room):
    chats = []
    for c in room.chats.order_by(Chat.created_at.desc()).all():
        chats.append(c.json())

    return json.dumps(chats, ensure_ascii=False).encode('utf8'), 200


# 룸 토큰 반환
@jwt_required()
@room_member_required
def room_token(user, room):
    if user.is_user(room=room):
        token = jwt.encode({"room_id": room.id, 'user_id': get_jwt_identity(), "user_type": 'U', \
            'club_id': room.club_id ,"exp": datetime.utcnow()+timedelta(days=1)}, Config.ROOM_SECRET_KEY, algorithm="HS256")
    elif user.is_clubhead(room=room):
        token = jwt.encode({"room_id": room.id, 'user_id': get_jwt_identity(), "user_type": 'C', \
            'club_id': room.club_id, "exp": datetime.utcnow()+timedelta(days=1)}, Config.ROOM_SECRET_KEY, algorithm="HS256")
    
    return {'room_token': token}, 200


# 채팅방 리프레시
@jwt_required()
@room_member_required
def room_refresh(user, room):
    if user.is_user(room):
        is_user=True
    else:
        is_user=False
    return room.json(is_user=is_user), 200


# 지원자 리스트 반환
@jwt_required()
@club_member_required
def applicant_list(user, club):
    rooms = []
    for r in club.get_all_applicant_room():
        rooms.append(r.json(is_user=False))

    return json.dumps(rooms), 200 


# 소켓 연결
def connect():
    emit('response', {'msg': 'Socket Connect Successfully'}, namespace='/chat')
    logger.info('[Socket Connect Successfully]')


# 방 입장
@room_token_required
def event_join_room(json):
    join_room(json.get('room_id'))
    emit('response', {'msg': 'Join Room Success'}, namespace='/chat')
    logger.info('[Join Room]')


# 채팅 보내기
@room_token_required
@chat_message_required
def event_send_chat(json):
    emit('recv_chat', {'title': None,'msg': json.get('msg'), 'user_type': json.get('user_type'), 'date': datetime.utcnow().isoformat()}, room=json.get('room_id'))
    emit('alarm', {'room_id': json.get('room_id')}, namespace='/chat')
    db.session.add(Chat(room_id=json.get('room_id'), msg=json.get('msg'), user_type=json.get('user_type')))
    db.session.commit()    
    logger.info('[Send Chat]')


# 방 나가기
@room_token_required
def event_leave_room(json):
    leave_room(json.get('room_id'))
    emit('response', {'msg': 'Leave Room Success'}, namespace='/chat')
    logger.info('[Leave Room]')


# 소켓 연결 끊기
def disconnect():
    logger.info('[Socket Disconnected]')
