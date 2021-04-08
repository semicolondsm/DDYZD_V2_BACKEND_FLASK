from flask import Blueprint

api_v1_0 = Blueprint('apiv1.0', __name__)


@api_v1_0.route("/ping")
def ping():
    return {"msg": "ping successfully"}, 200

from .chat_list import chat_list
from .make_room import make_room
from .breakdown import breakdown
from .room_token import room_token
from .applicant_list import applicant_list
from .room_info import room_info
from .room_refresh import room_refresh

# chatting api
api_v1_0.add_url_rule('/chat/list', 'chat_list', chat_list, methods=['GET'])
api_v1_0.add_url_rule('/chat/<int:club_id>/room', 'make_room', make_room, methods=['POST'])
api_v1_0.add_url_rule('/chat/<int:room_id>/breakdown', 'breakdown', breakdown, methods=['GET'])
api_v1_0.add_url_rule('/room/<int:room_id>/token', 'room_token', room_token, methods=['GET'])
api_v1_0.add_url_rule('/club/<int:club_id>/applicant', 'applicant_list', applicant_list, methods=['GET'])
api_v1_0.add_url_rule('/room/<int:room_id>/info', 'room_info', room_info, methods=['GET'])
api_v1_0.add_url_rule('/room/<int:room_id>/refresh', 'room_refresh', room_refresh, methods=['GET'])

from .report import report

# 추가기능
api_v1_0.add_url_rule('/report', 'report', report, methods=['POST'])
