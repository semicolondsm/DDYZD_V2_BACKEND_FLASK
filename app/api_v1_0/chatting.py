from app.decorator import room_member_required
from app.decorator import club_head_required
from app.models import RoomStatus
from app.models import ClubHead
from app.models import Club
from app.models import Chat
from app.models import User
from app.models import Room
from app.models import kstnow
from app import error
from app import db
from config import Config
from datetime import datetime
from datetime import timedelta
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
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
            return error.BadRequest('You do not have permission')
        
        # 채팅방 정렬
        rs = club.rooms
        rs.sort(reverse=True)
        for r in rs:
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
        return {'id': str(room.user.gcn), 'name': room.user.name, 'image': room.user.image_path, 'status': room.status.name}


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
@club_head_required
def applicant_list(user, club):
    rooms = []
    for r in club.get_all_applicant_room():
        rooms.append(r.json(is_user=False))

    return json.dumps(rooms), 200 
