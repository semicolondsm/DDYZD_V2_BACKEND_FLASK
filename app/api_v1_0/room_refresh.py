from app.decorator.room_member_required import room_member_required
from flask_jwt_extended import jwt_required

# 채팅방 리프레시
@jwt_required()
@room_member_required
def room_refresh(user, room):
    if user.is_user(room):
        is_user=True
    else:
        is_user=False
    return room.json(is_user=is_user), 200
