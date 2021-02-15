from flask import Blueprint

api_v1_0 = Blueprint('apiv1.0', __name__)

from .chatting import *
from . import chathelper

@api_v1_0.route("/ping")
def ping():
    return {"msg": "ping successfully"}, 200

api_v1_0.add_url_rule('/chat/list', 'chat_list', chat_list, methods=['GET'])
api_v1_0.add_url_rule('/chat/<int:club_id>/room', 'enter_room', enter_room, methods=['POST'])
