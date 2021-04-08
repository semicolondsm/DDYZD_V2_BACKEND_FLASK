from app.decorator.room_member_required import room_member_required
from app.models import Chat
from flask_jwt_extended import jwt_required
import json

# 채팅 내역 보기
@jwt_required()
@room_member_required
def breakdown(user, room):
    chats = []
    for c in room.chats.order_by(Chat.created_at.desc()).all():
        chats.append(c.json())

    return json.dumps(chats, ensure_ascii=False).encode('utf8'), 200