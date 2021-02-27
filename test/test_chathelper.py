from app.models import Room
from app import logger
from conftest import room_token
from conftest import jwt_token
from app import websocket
import json


def test_helper_apply(db_setting, flask_websocket, flask_client, flask_app):
    # 웹 소켓 연결
    flask_websocket.emit('join_room', {'room_token': room_token(user_id=1, room_id=3, user_type='C')}, namespace='/chat')
    flask_websocket.emit('helper_apply', {'room_token': room_token(user_id=4, room_id=3, user_type='U'), 'major': '프론트엔드'}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[1]

    assert recv['name'] == 'alarm'
    assert recv['args'][0]['room_id'] == '3'

    flask_websocket.emit('helper_apply', {'room_token': room_token(user_id=3, room_id=2, user_type='U'), 'major': '프론트엔드'}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]
    for r in Room.query.all():
        logger.info(r.status)
    
    assert recv['name'] == 'error'
    assert recv['args'][0]['msg'] == '400: You are already apply to this club'
    
    resp = flask_client.get('/chat/3/breakdown', headers=jwt_token(sub=4))
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert resp.status_code == 200
    assert data[0]['title'] == '성예인님이 동아리에 지원하셨습니다' 
    assert data[0]['msg'] == '1110 성예인님이 세미콜론에 프론트엔드 분야로 지원하셨습니다'
    assert data[0]['user_type'] == 'H1' 
    assert data[0]['created_at'] != None 


def test_helper_schedule(db_setting, flask_websocket, flask_client):
    flask_websocket.emit('join_room', {'room_token': room_token(room_id=2)}, namespace='/chat')
    flask_websocket.emit('helper_schedule', {'date': '2020년 6월 18일 오후 6시 10분', 'location': '3층 그린존','room_token': room_token(room_id=2)}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[1]

    assert recv['name'] == 'recv_chat'
    assert recv['args'][0]['title'] == '안은결님의 면접 일정'
    assert recv['args'][0]['msg'] != None
        
    resp = flask_client.get('/chat/2/breakdown', headers=jwt_token(sub=3))
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert resp.status_code == 200
    assert data[0]['title'] == '안은결님의 면접 일정' 
    assert data[0]['msg'] != None
    assert data[0]['user_type'] == 'H2' 
    assert data[0]['created_at'] != None 


def test_helper_result(db_setting, flask_websocket, flask_client):
    logger.info(Room.query.get(2).status)
    flask_websocket.emit('join_room', {'room_token': room_token(room_id=2)}, namespace='/chat')
    flask_websocket.emit('helper_result', {'result': True, 'room_token': room_token(room_id=2)}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[1]

    assert recv['name'] == 'recv_chat'
    assert recv['args'][0]['title'] == '안은결님 세미콜론 동아리 합격을 축하드립니다!'
    assert recv['args'][0]['msg'] == '안은결님의 세미콜론 동아리 면접결과, 합격을 알려드립니다'
        
    flask_websocket.emit('helper_result', {'result': True, 'room_token': room_token(user_type='U')}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]

    assert recv['name'] == 'error'
    assert recv['args'][0]['msg'] == '403: Only club head use this helper'
