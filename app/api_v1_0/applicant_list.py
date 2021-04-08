from app.decorator import club_head_required
from flask_jwt_extended import jwt_required
import json

# 지원자 리스트 반환
@jwt_required()
@club_head_required
def applicant_list(user, club):
    rooms = []
    for r in club.get_all_applicant_room():
        rooms.append(r.json(is_user=False))

    return json.dumps(rooms), 200 
