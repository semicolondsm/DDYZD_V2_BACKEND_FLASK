from app import logger
from app import db
from conftest import jwt_token
from conftest import room_token
from config import Config
import json
import jwt
import pytest

## 테스트 핑 ## 
def test_ping(db_setting, flask_websocket):
    resp = flask_websocket.flask_test_client.get("ping")

    assert resp.status_code ==  200
    assert resp.json.get('msg') == 'ping successfully'


## 채팅 리스트 불러오기 테스트 ## 
def test_chat_list(flask_websocket, flask_client, db_setting):
    # 동아리장 채팅 테스트
    flask_websocket.emit('join_room', {'room_token': room_token()}, namespace='/chat')
    resp = flask_client.get("/chat/list", headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data['club_section'] == ['김수완', '세미콜론']
    assert data['rooms'][0].get('roomid') == '1'
    assert data['rooms'][0].get('id') == '2'
    assert data['rooms'][0].get('name') == '조호원'
    assert data['rooms'][0].get('image') == 'profile2'
    assert data['rooms'][0].get('lastdate') != None
    assert data['rooms'][0].get('isread') == True
    assert data['rooms'][0].get('index') == 1
    logger.info("CHATLIST END")

    # 일반 채팅 테스트
    resp = flask_client.get("/chat/list", headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data['club_section'] == ['조호원']
    assert data['rooms'][0].get('roomid') == '1'
    assert data['rooms'][0].get('id') == '1'
    assert data['rooms'][0].get('name') == '세미콜론'
    assert data['rooms'][0].get('image') == 'https://api.semicolon.live/file/profile_image'
    assert data['rooms'][0].get('lastmessage') == '두번째 채팅'
    assert data['rooms'][0].get('lastdate') != None
    assert data['rooms'][0].get('isread') == False
    assert data['rooms'][0].get('index') == 0


## 방 만들기 테스트 ##
def test_make_room(flask_client, db_setting):
    resp = flask_client.post('/chat/1/room', headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.json

    assert data.get('room_id') == '1'

    resp = flask_client.post('/chat/1/room', headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.json

    assert data.get('room_id') == '1'

    resp = flask_client.post('/chat/1/room', headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.json

    assert data.get('room_id') == '3'
    

## 채팅 내역 불러오기 테스트 ##
def test_breakdown(flask_client, db_setting):
    resp = flask_client.get('/chat/1/breakdown', headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data[0].get('msg') == '두번째 채팅'
    assert data[0].get('user_type') == 'C'
    assert data[0].get('created_at') != None
    assert data[1].get('msg') == '첫번째 채팅'
    assert data[1].get('user_type') == 'U'
    assert data[1].get('created_at') != None


## 룸 토큰 반환 테스트 ##
def test_room_token(flask_client, db_setting):
    # 동아리장 토큰 
    resp = flask_client.get('/room/1/token', headers=jwt_token(1))
    assert resp.status_code == 200
    token = resp.json['room_token']
    json = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms='HS256')
    
    assert json.get('room_id') == 1
    assert json.get('user_id') == 1
    assert json.get('user_type') == 'C' 

    # 일반 유저 토큰
    resp = flask_client.get('/room/1/token', headers=jwt_token(2))
    assert resp.status_code == 200
    token = resp.json['room_token']
    json = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms='HS256')
    
    assert json.get('room_id') == 1
    assert json.get('user_id') == 2
    assert json.get('user_type') == 'U' 


## 지원자 리스트 반환 테스트 ##
def test_applicant_list(flask_client, db_setting):
    resp = flask_client.get('/club/1/applicant', headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data[0]['roomid'] == '1'
    assert data[0]['id'] == '2'
    assert data[0]['name'] == '조호원'
    assert data[0]['image'] == 'profile2'
    assert data[0]['lastdate'] != None
    assert data[0]['lastmessage'] == '두번째 채팅'
    assert data[0]['index'] == 0
    

## 채팅방 정보 반환 테스트##
def test_room_info(flask_client, db_setting):
    resp = flask_client.get('/room/1/info', headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.json

    assert data['id'] == '1118'
    assert data['name'] == '조호원'
    assert data['image'] == 'profile2'
    
    resp = flask_client.get('/room/1/info', headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.json
    
    assert data['id'] == '1'
    assert data['name'] == '세미콜론'
    assert data['image'] == 'https://api.semicolon.live/file/profile_image'


## 채팅방 리프레시 테스트 ##
def test_room_refresh(flask_client, db_setting):
    resp = flask_client.get('/room/1/refresh', headers=jwt_token())
    assert resp.status_code == 200
    data = resp.json

    assert data.get('id') == '2' 
    assert data.get('name') == '조호원' 
    assert data.get('image') == 'profile2' 
    assert data.get('lastmessage') == '두번째 채팅' 
    assert data.get('lastdate') != None 
    assert data.get('index') == 0
    
    resp = flask_client.get('/room/1/refresh', headers=jwt_token(sub=2))
    assert resp.status_code == 200
    data = resp.json

    assert data.get('id') == '1' 
    assert data.get('name') == '세미콜론' 
    assert data.get('image') == 'https://api.semicolon.live/file/profile_image' 
    assert data.get('lastmessage') == '두번째 채팅' 
    assert data.get('lastdate') != None 
    assert data.get('index') == 0


## 방 들어가기 테스트 (채팅 보내기 전에 먼저 실행하자)## 
def test_join_room(flask_websocket, db_setting):
    flask_websocket.emit('join_room', {'room_token': room_token()}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]

    assert recv['args'][0]['msg'] == 'Join Room Success'


## 채팅 보내기 테스트 ## 
def test_send_chat(flask_websocket, db_setting):
    # 동아리장 채팅
    flask_websocket.emit('send_chat',{'msg': 'Hello \U0001f600', 'room_token': room_token()}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]

    assert recv['name'] == 'recv_chat'
    assert recv['args'][0]['msg'] == 'Hello \U0001f600'
    assert recv['args'][0]['user_type'] == 'C'
    assert recv['args'][0]['date'] != None

    # 동아리원 채팅
    flask_websocket.emit('send_chat', {'msg': 'World!', 'room_token': room_token(user_id=2, user_type='U')}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]

    assert recv['name'] == 'alarm'
    assert recv['args'][0]['room_id'] == '1'


## 방 나가기 테스트 (채팅 보내고 난 뒤에 실행 되어야함!) ## 
def test_leave_room(flask_websocket, db_setting):
    flask_websocket.emit('leave_room', {'room_token': room_token()}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]

    assert recv['args'][0]['msg'] == 'Leave Room Success'    
