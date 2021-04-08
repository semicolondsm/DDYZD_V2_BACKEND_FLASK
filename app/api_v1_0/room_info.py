from app.decorators import room_member_required
from flask_jwt_extended import jwt_required


# 채팅방 정보
@jwt_required()
@room_member_required
def room_info(user, room):
    if user.is_user(room):
        return {'id': str(room.club.id), 'name': room.club.name,'image': 'https://api.semicolon.live/file/'+room.club.profile_image, 'status': room.status.name}
    else:
        return {'id': str(room.user.gcn), 'name': str(room.user.gcn)+room.user.name, 'image': room.user.image_path, 'status': room.status.name}

