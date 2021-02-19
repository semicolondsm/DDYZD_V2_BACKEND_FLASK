import pytest
import json
import jwt
from config import Config
from app import db
from app.models import Room, Chat, Club, ClubHead, User, Application


## 더미 데이터 세팅 ## 
@pytest.fixture(scope='module')
def db_setting():
    db.session.add(User(name='김수완', gcn='1103'))
    db.session.add(User(name='조호원', gcn='1118'))
    db.session.add(Club(club_name='세미콜론', profile_image='profile_image'))
    db.session.add(ClubHead(user_id=1, club_id=1))
    db.session.add(Room(user_id=1, club_id=1))
    db.session.add(Chat(room_id=1, msg='첫번째 채팅', user_type='U'))
    db.session.add(Chat(room_id=1, msg='두번째 채팅', user_type='C'))

    db.session.commit()


## 테스트 핑 ## 
def test_ping(flask_websocket):
    resp = flask_websocket.flask_test_client.get("ping")

    assert resp.status_code ==  200
    assert resp.json.get('msg') == 'ping successfully'


## 채팅 리스트 불러오기 테스트 ## 
def test_chat_list(flask_client, jwt_token, db_setting):
    resp = flask_client.get("/chat/list", headers=jwt_token)
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert resp.status_code == 200
    assert data[0].get('clubname') == '세미콜론'
    assert data[0].get('clubid') == 1
    assert data[0].get('roomid') == 1
    assert data[0].get('lastdate') != None
    assert data[0].get('lastmessage') == '두번째 채팅'


## 방 만들기 테스트 ## 
def test_make_room(flask_client, jwt_token, db_setting):
    resp = flask_client.post('/club/1/room', headers=jwt_token)
    data = resp.json

    assert resp.status_code == 200
    assert data.get('room_id') == 1


## 방 들어가기 테스트 (채팅 보내기 전에 먼저 실행하자)## 
def test_join_room(flask_websocket, db_setting):
    flask_websocket.emit('join_room', {'room_id': 1}, namespace='/chat')

    recv = flask_websocket.get_received(namespace='/chat')[0]
    assert recv['args'][0]['msg'] == 'Join Room Success'


## 채팅 보내기 테스트 ## 
def test_send_chat(flask_websocket, db_setting):
    flask_websocket.emit('send_chat', {'room_id': 1, 'data': 'Hello!'}, namespace='/chat')

    recv = flask_websocket.get_received(namespace='/chat')[0]
    assert recv['args'][0]['data'] == 'Hello!'


## 방 나가기 테스트 (채팅 보내고 난 뒤에 실행 되어야함!) ## 
def test_leave_room(flask_websocket, db_setting):
    flask_websocket.emit('leave_room', {'room_id': 1}, namespace='/chat')

    recv = flask_websocket.get_received(namespace='/chat')[0]
    assert recv['args'][0]['msg'] == 'Leave Room Success'


## 채팅 내역 테스트 ##
def test_breakdown(flask_client, jwt_token, db_setting):
    resp = flask_client.get('/chat/1/breakdown', headers=jwt_token)
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert resp.status_code == 200
    assert data[0].get('msg') == '두번째 채팅'
    assert data[0].get('user_type') == 'C'
    assert data[0].get('created_at') != None
    assert data[1].get('msg') == '첫번째 채팅'
    assert data[1].get('user_type') == 'U'
    assert data[1].get('created_at') != None


## 채팅 섹션 테스트 ##
def test_chat_section(flask_client, jwt_token, db_setting):
    resp = flask_client.get('/chat/section', headers=jwt_token)
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert resp.status_code == 200
    assert data[0].get('club_name') == '세미콜론'
    assert data[0].get('club_id') == 1
    assert data[0].get('club_profile') == 'profile_image'
    