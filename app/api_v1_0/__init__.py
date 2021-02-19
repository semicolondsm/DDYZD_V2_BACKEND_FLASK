from flask import Blueprint
from app import websocket

api_v1_0 = Blueprint('apiv1.0', __name__)

from .chatting import *
from . import chathelper

@api_v1_0.route("/ping")
def ping():
    return {"msg": "ping successfully"}, 200

api_v1_0.add_url_rule('/chat/list', 'chat_list', chat_list, methods=['GET'])
api_v1_0.add_url_rule('/club/<int:club_id>/room', 'make_room', make_room, methods=['POST'])
api_v1_0.add_url_rule('/chat/<int:room_id>/breakdown', 'breakdown', breakdown, methods=['GET'])
api_v1_0.add_url_rule('/chat/section', 'chat_section', chat_section, methods=['GET'])

websocket.on_event('connect', connect, namespace='/chat')
websocket.on_event('disconnect', disconnect, namespace='/chat')
websocket.on_event('join_room', event_join_room, namespace='/chat')
websocket.on_event('leave_room', event_leave_room, namespace='/chat')
websocket.on_event('send_chat', event_send_chat, namespace='/chat')
