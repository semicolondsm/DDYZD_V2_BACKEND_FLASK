from app.models.type import RoomType
from app.models.club import Club
from app.models.chat import Room
from app import db
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
import json


# 채팅방 만들기
@jwt_required()
def make_room(club_id):
    club = Club.query.get(club_id)
    room = Room.query.filter_by(user_id=get_jwt_identity(), club_id=club.id).first()
    if room is None:
        room = Room(user_id=get_jwt_identity(), club_id=club.id)
        if club.is_recruiting():
            room.status = RoomType.N.name
        db.session.add(room)
        db.session.commit()

    return {'room_id': str(room.id)}, 200