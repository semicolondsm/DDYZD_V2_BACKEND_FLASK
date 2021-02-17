from flask import Blueprint
from app import websocket

api_v1_0 = Blueprint('apiv1.0', __name__)

from .chatting import *
from . import chathelper

@api_v1_0.route("/ping")
def ping():
    return {"msg": "ping successfully"}, 200

api_v1_0.add_url_rule('/chat/list', 'chat_list', chat_list, methods=['GET'])
api_v1_0.add_url_rule('/chat/<int:club_id>/token', 'room_token', room_token, methods=['POST'])

websocket.on_event('connect', connect, namespace='/chat')
websocket.on_event('disconnect', disconnect, namespace='/chat')
websocket.on_event('join_room', join_room, namespace='/chat')

# @api_v1_0.route("/join_room")
# def joinning():
#     pass
