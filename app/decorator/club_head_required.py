from app.models import User
from app.models import Club
from app import error
from flask_jwt_extended import get_jwt_identity
from functools import wraps

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
