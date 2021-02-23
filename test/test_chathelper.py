from app import logger
from conftest import room_token
from conftest import jwt_token
import json


def test_helper_apply(flask_websocket, flask_client, db_setting):
    flask_websocket.emit('join_room', {'room_token': room_token(user_id=3, room_id=1, user_type='U')}, namespace='/chat')
    flask_websocket.emit('helper_apply', {'room_token': room_token(user_id=3, room_id=1, user_type='U'), 'major': '프론트엔드'}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[1]

    assert recv['name'] == 'recv_chat'
    assert recv['args'][0]['title'] == '안은결님이 동아리에 지원하셨습니다.'
    assert recv['args'][0]['msg'] == '1413 안은결님이 세미콜론에 프론트엔드 분야로 지원하셨습니다.'
    assert recv['args'][0]['user_type'] == 'H1'
    
    resp = flask_client.get('/chat/1/breakdown', headers=jwt_token(sub=3))
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert resp.status_code == 200
    assert data[0]['title'] == '안은결님이 동아리에 지원하셨습니다.' 
    assert data[0]['msg'] == '1413 안은결님이 세미콜론에 프론트엔드 분야로 지원하셨습니다.'
    assert data[0]['user_type'] == 'H1' 
    assert data[0]['created_at'] != None 
    