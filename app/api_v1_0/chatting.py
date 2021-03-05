from app.decorator import chat_message_required
from app.decorator import room_member_required
from app.decorator import club_member_required
from app.decorator import room_token_required
from app.decorator import room_writed
from app.decorator import send_alarm
from app.decorator import room_read
from app.errors import websocket
from app.errors import http
from app.models import RoomStatus
from app.models import ClubMember
from app.models import ClubHead
from app.models import Club
from app.models import Chat
from app.models import User
from app.models import Room
from app.models import isoformat 
from app.models import kstnow
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

        return {"club_section": club.name, "rooms": rooms}, 200
    else:
        # 채팅 섹션
        club_section = [user.name] 
        for club in user.get_clubs():
            club_section.append(club.name)

        # 유저 권한의 채팅방 검색
        rs = user.rooms.all()
        rs.sort(reverse=True)
        for r in rs:
            rooms.append(r.json(is_user=True, index=index))

        # 동아리장 권한의 채팅방 검색
        for c in user.get_clubs():
            index = index + 1
            rs = c.rooms
            rs.sort(reverse=True)
            for r in rs:
                rooms.append(r.json(is_user=False, index=index))

        return {"club_section": club_section, "rooms": rooms}, 200


# 채팅방 만들기
@jwt_required()
def make_room(club_id):
    club = Club.query.get(club_id)
    room = Room.query.filter_by(user_id=get_jwt_identity(), club_id=club.id).first()
    if room is None:
        room = Room(user_id=get_jwt_identity(), club_id=club.id)
        if club.is_recruiting():
            room.status = RoomStatus.N.name
        db.session.add(room)
        db.session.commit()

    return {'room_id': str(room.id)}, 200


# 채팅방 정보
@jwt_required()
@room_member_required
def room_info(user, room):
    if user.is_user(room):
        return {'id': str(room.club.id), 'name': room.club.name,'image': 'https://api.semicolon.live/file/'+room.club.profile_image, 'status': room.status.name}
    else:
        return {'id': str(room.user.gcn), 'name': str(room.user.gcn)+room.user.name, 'image': room.user.image_path, 'status': room.status.name}


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
            'club_id': room.club_id ,"exp": kstnow()+timedelta(days=1)}, Config.ROOM_SECRET_KEY, algorithm="HS256")
    elif user.is_clubhead(room.club):
        token = jwt.encode({"room_id": room.id, 'user_id': get_jwt_identity(), "user_type": 'C', \
            'club_id': room.club_id, "exp": kstnow()+timedelta(days=1)}, Config.ROOM_SECRET_KEY, algorithm="HS256")
    
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
@jwt_required()
def connect():
    emit('response', {'msg': 'Socket Connect Successfully'}, namespace='/chat')
    User.query.get(get_jwt_identity()).session_id = request.sid
    db.session.commit()
    logger.info('[Socket Connected]')


# 방 입장
@room_token_required
@room_read
def event_join_room(json):
    join_room(json.get('room_id'))
    emit('response', {'msg': 'Join Room Success'}, namespace='/chat')


# 채팅 보내기
@room_token_required
@chat_message_required
@room_writed
@send_alarm
def event_send_chat(json):
    emit('recv_chat', {'title': None, 'msg': json.get('msg'), 'user_type': json.get('user_type'), 'date': isoformat(kstnow())}, room=json.get('room_id')) 
    db.session.add(Chat(room_id=json.get('room_id'), msg=json.get('msg'), user_type=json.get('user_type')))
    db.session.commit()


# 방 나가기
@room_token_required
@room_read
def event_leave_room(json):
    leave_room(json.get('room_id'))
    emit('response', {'msg': 'Leave Room Success'}, namespace='/chat')


# 소켓 연결 끊기
def disconnect():
    logger.info('[Socket Disconnected]')
