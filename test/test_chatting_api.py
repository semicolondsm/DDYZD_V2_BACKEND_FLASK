import pytest
import json
import jwt
from config import Config
from app import db
from app.models import Room, Chat, Club, ClubHead, User, Application

@pytest.fixture(scope='module')
def db_setting():
    db.session.add(User(name='김수완', gcn='1103'))
    db.session.add(User(name='조호원', gcn='1118'))
    db.session.add(Club(club_name='세미콜론'))
    db.session.add(ClubHead(user_id=2, club_id=1))
    db.session.add(Room(user=1, club_head_id=1))
    db.session.add(Chat(room_id=1, msg='첫번째 채팅', user_type='U'))

    db.session.commit()


def test_ping(flask_websocket):
    resp = flask_websocket.flask_test_client.get("ping")
    assert resp.status_code ==  200
    assert resp.json.get('msg') == 'ping successfully'


def test_chat_list(flask_websocket, headers, db_setting):
    resp = flask_websocket.flask_test_client.get("/chat/list", headers=headers)
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert resp.status_code == 200
    assert data[0].get('lastmessage') == '첫번째 채팅'
    assert data[0].get('lastdate') != None
    assert data[0].get('roomid') == 1
    assert data[0].get('clubid') == 1
    assert data[0].get('clubname') == '세미콜론'


def test_room_token(flask_websocket, headers, db_setting):  
    resp = flask_websocket.flask_test_client.post("/chat/1/token", headers=headers)
    token = resp.json['room-token']
    payload = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms=["HS256"])

    assert resp.status_code == 200
    assert payload['room_id'] == 1
    assert payload['sub'] == 1


def test_join_room(flask_websocket, db_setting):
    flask_websocket.emit('join_room', {'abc': 'def'}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]
    assert recv['args'][0]['msg'] == 'join room'
