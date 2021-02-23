from app import logger
from conftest import room_token


def test_helper_apply(flask_websocket, db_setting):
    flask_websocket.emit('join_room', {'room_token': room_token(user_id=3, room_id=1, user_type='U')}, namespace='/chat')
    flask_websocket.emit('helper_apply', {'room_token': room_token(user_id=3, room_id=1, user_type='U'), 'major': '프론트엔드'}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[1]

    assert recv['name'] == 'response'
    assert recv['args'][0]['title'] == '안은결님이 지원하셨습니다.'
    assert recv['args'][0]['msg'] == '1413 안은결님이 세미콜론에 프론트엔드분야로 지원하셨습니다.'