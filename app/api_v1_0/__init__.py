from flask import Blueprint

api_v1_0 = Blueprint('apiv1.0', __name__)

from .chatting import *
from .report import *

@api_v1_0.route("/ping")
def ping():
    return {"msg": "ping successfully"}, 200


# chatting api
api_v1_0.add_url_rule('/chat/list', 'chat_list', chat_list, methods=['GET'])
api_v1_0.add_url_rule('/chat/<int:club_id>/room', 'make_room', make_room, methods=['POST'])
api_v1_0.add_url_rule('/chat/<int:room_id>/breakdown', 'breakdown', breakdown, methods=['GET'])
api_v1_0.add_url_rule('/room/<int:room_id>/token', 'room_token', room_token, methods=['GET'])
api_v1_0.add_url_rule('/club/<int:club_id>/applicant', 'applicant_list', applicant_list, methods=['GET'])
api_v1_0.add_url_rule('/room/<int:room_id>/info', 'room_info', room_info, methods=['GET'])
api_v1_0.add_url_rule('/room/<int:room_id>/refresh', 'room_refresh', room_refresh, methods=['GET'])

# 추가기능
api_v1_0.add_url_rule('/report', 'report', report, methods=['POST'])
