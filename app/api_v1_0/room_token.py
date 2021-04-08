from config import Config
from app.decorator.room_member_required import room_member_required
from app.models import kstnow
from app.models import timedelta
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
import jwt

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