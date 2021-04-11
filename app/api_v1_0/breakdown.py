from app.decorator.room_member_required import room_member_required
from app.models.chat import Chat
from flask_jwt_extended import jwt_required
import json

# 채팅 내역 보기
@jwt_required()
@room_member_required
def breakdown(user, room):
    chats = room.breakdown(user)

    return json.dumps(chats, ensure_ascii=False).encode('utf8'), 200