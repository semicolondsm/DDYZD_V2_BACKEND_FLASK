from app.models import Room
from app.models import User
from app import error
from config import Config
from flask_jwt_extended import get_jwt_identity
from functools import wraps

def room_member_required(fn):
    '''
    요약: 채팅방 맴버인지 확인하는 데코레이터
    room_info, breakdown, room_token, room_refresh에 사용한다.
    rest api에서 사용되는 것은 room_member_required 이고,
    websocket event를 비슷하게 처리하기위해 room_token_required를 사용해야한다.
    '''
    @wraps(fn)      
    def wrapper(room_id):
        room = Room.query.get_or_404(room_id)
        user = User.query.get_or_404(get_jwt_identity())
        if not user.is_room_member(room):
            return error.BadRequest("You are not a member for the room: "+str(room_id))
        
        return fn(user, room)
    return wrapper