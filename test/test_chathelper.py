from app import logger
from conftest import room_token


def test_chathelper_apply(flask_websocket, db_setting):
    flask_websocket.emit('join_room', {'room_token': room_token(user_id=2, room_id=1, user_type='U')}, namespace='/chat')
    flask_websocket.emit('helper_apply', {'room_token': room_token(user_id=2, room_id=1, user_type='U')}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[1]

    assert recv['name'] == 'response'
    assert recv['args'][0]['msg'] == '1234'