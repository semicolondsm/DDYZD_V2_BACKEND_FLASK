from app.models import ClubHead 
from app.models import RoomStatus
from app.models import Room
from app.models import User
from app.models import Club
from app import error
from config import Config
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from flask import request
import jwt


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


def club_head_required(fn):
    '''
    요약: 동아리 장인지 확인하는 데코레이터 
    applicant_list에서 사용한다.
    '''
    @wraps(fn)
    def wrapper(club_id):
        club = Club.query.get_or_404(club_id)
        user = User.query.get_or_404(get_jwt_identity())
        if not user.is_clubhead(club=club):
            return error.BadRequest("You are not a member for the club "+str(club_id))
        
        return fn(user, club)
    return wrapper   
