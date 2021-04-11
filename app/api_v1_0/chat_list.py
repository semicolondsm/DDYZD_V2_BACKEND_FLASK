from app.models.chat import Chat
from app.models.chat import Room
from app.models.club import Club
from app.models.user import User
from app import error
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask import request
import json

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
        
        rs = club.select_rooms()
        # 채팅방 정렬
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
        rs = user.select_rooms()
        rs.sort(reverse=True)
        for r in rs:
            rooms.append(r.json(is_user=True, index=index))

        # 동아리장 권한의 채팅방 검색
        for c in user.get_clubs():
            index = index + 1
            rs = c.select_rooms()
            rs.sort(reverse=True)
            for r in rs:
                rooms.append(r.json(is_user=False, index=index))
        return {"club_section": club_section, "rooms": rooms}, 200
