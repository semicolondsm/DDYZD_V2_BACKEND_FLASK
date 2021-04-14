from app.decorator.room_member_required import room_member_required
from flask_jwt_extended import jwt_required
from app.models.type import UserType

@jwt_required()
@room_member_required
def delete_room(user, room):
    if user.is_user(room):
        room.delete_chats(UserType.U.name)
    else:
        room.delete_chats(UserType.C.name)
    
    return {'msg': 'success deleting room'}, 200

