from app.models import Room, Chat, Club, ClubHead, User, Application
from app import logger
from app import db
from conftest import jwt_token
from conftest import room_token
from config import Config
import json
import jwt
import pytest

## 더미 데이터 세팅 ## 
@pytest.fixture(scope='module')
def db_setting():
    db.session.add(User(name='김수완', gcn='1103', image_path='profile1'))
    db.session.add(User(name='조호원', gcn='1118', image_path='profile2'))
    db.session.add(Club(club_name='세미콜론', total_budget=3000, current_budget=2000, banner_image='banner image', hongbo_image='hongbo image', profile_image='profile_image'))
    db.session.add(ClubHead(user_id=1, club_id=1))
    db.session.add(Room(user_id=2, club_id=1))
    db.session.add(Chat(room_id=1, msg='첫번째 채팅', user_type='U'))
    db.session.add(Chat(room_id=1, msg='두번째 채팅', user_type='C'))

    db.session.commit()


## 테스트 핑 ## 
def test_ping(flask_websocket):
    resp = flask_websocket.flask_test_client.get("ping")

    assert resp.status_code ==  200
    assert resp.json.get('msg') == 'ping successfully'


## 채팅 리스트 불러오기 테스트 ## 
def test_chat_list(flask_client, db_setting):
    # 일반 채팅 테스트
    resp = flask_client.get("/chat/list", headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data[0].get('roomid') == 1
    assert data[0].get('clubid') == 1
    assert data[0].get('clubname') == '세미콜론'
    assert data[0].get('clubimage') == 'profile_image'
    assert data[0].get('userid') == 2
    assert data[0].get('username') == '조호원'
    assert data[0].get('userimage') == 'profile2'
    assert data[0].get('lastdate') != None
    assert data[0].get('lastmessage') == '두번째 채팅'


    # 동아리장 채팅 테스트
    resp = flask_client.get("/chat/list?club_id=1", headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    
    assert data[0].get('roomid') == 1
    assert data[0].get('clubid') == 1
    assert data[0].get('clubname') == '세미콜론'
    assert data[0].get('clubimage') == 'profile_image'
    assert data[0].get('userid') == 2
    assert data[0].get('username') == '조호원'
    assert data[0].get('userimage') == 'profile2'
    assert data[0].get('lastdate') != None
    assert data[0].get('lastmessage') == '두번째 채팅'


## 방 만들기 테스트 ## 
def test_make_room(flask_client, db_setting):
    resp = flask_client.post('/club/1/room', headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.json

    assert data.get('room_id') == 1

    resp = flask_client.post('/club/1/room', headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.json

    assert data.get('room_id') == 1

    resp = flask_client.post('/club/1/room', headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.json

    assert data.get('room_id') == 2
    

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


## 채팅 섹션 테스트 ##
def test_chat_section(flask_client, db_setting):
    resp = flask_client.get('/chat/section', headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data[0].get('club_name') == '세미콜론'
    assert data[0].get('club_id') == 1
    assert data[0].get('club_profile') == 'profile_image'


## 룸 토큰 반환 테스트 ##
def test_room_token(flask_client, db_setting):
    # 동아리장 토큰 
    resp = flask_client.post('/room/1/token', headers=jwt_token(1))
    assert resp.status_code == 200
    token = resp.json['room_token']
    json = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms='HS256')
    
    assert json.get('room_id') == 1
    assert json.get('user_id') == 1
    assert json.get('user_type') == 'C' 

    # 일반 유저 토큰
    resp = flask_client.post('/room/1/token', headers=jwt_token(2))
    assert resp.status_code == 200
    token = resp.json['room_token']
    json = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms='HS256')
    
    assert json.get('room_id') == 1
    assert json.get('user_id') == 2
    assert json.get('user_type') == 'U' 


## 방 들어가기 테스트 (채팅 보내기 전에 먼저 실행하자)## 
def test_join_room(flask_websocket, db_setting):
    flask_websocket.emit('join_room', {'room_token': room_token()}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]

    assert recv['args'][0]['msg'] == 'Join Room Success'


## 채팅 보내기 테스트 ## 
def test_send_chat(flask_websocket, db_setting):
    # 동아리장 채팅
    flask_websocket.emit('send_chat', {'data': 'Hello', 'room_token': room_token()}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]

    assert recv['name'] != 'error'
    assert recv['args'][0]['data'] == 'Hello'

    # 동아리원 채팅
    flask_websocket.emit('send_chat', {'data': 'World!', 'room_token': room_token(user_id=2, user_type='U')}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]

    assert recv['name'] != 'error'
    assert recv['args'][0]['data'] == 'World!'


## 방 나가기 테스트 (채팅 보내고 난 뒤에 실행 되어야함!) ## 
def test_leave_room(flask_websocket, db_setting):
    flask_websocket.emit('leave_room', {'room_token': room_token()}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]

    assert recv['args'][0]['msg'] == 'Leave Room Success'    
