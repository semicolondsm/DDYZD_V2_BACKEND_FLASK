import pytest
import json
import jwt
from config import Config
from app import db
from app.models import Room, Chat, Club, ClubHead, User, Application


def json_load(data):
    data = data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    return data


@pytest.fixture(scope='module')
def db_setting():
    db.session.add(User(name='김수완', gcn='1103'))
    db.session.add(User(name='조호원', gcn='1118'))
    db.session.add(Club(club_name='세미콜론'))
    db.session.add(ClubHead(user_id=2, club_id=1))
    db.session.add(Room(user_id=1, club_id=1))
    db.session.add(Chat(room_id=1, msg='첫번째 채팅', user_type='U'))

    db.session.commit()


def test_ping(flask_websocket):
    resp = flask_websocket.flask_test_client.get("ping")

    assert resp.status_code ==  200
    assert resp.json.get('msg') == 'ping successfully'


def test_chat_list(flask_client, jwt_token, db_setting):
    resp = flask_client.get("/chat/list", headers=jwt_token)
    data = json_load(resp.data)

    assert resp.status_code == 200
    assert data[0].get('clubname') == '세미콜론'
    assert data[0].get('clubid') == 1
    assert data[0].get('roomid') == 1
    assert data[0].get('lastdate') != None
    assert data[0].get('lastmessage') == '첫번째 채팅'


def test_make_room(flask_client, jwt_token, db_setting):
    resp = flask_client.post('/club/1/room', headers=jwt_token)
    data = resp.json

    assert resp.status_code == 200
    assert data.get('room_id') == 1

def test_join_room(flask_websocket, db_setting):
    flask_websocket.emit('join_room', {'room_id': 1}, namespace='/chat')
    recv = flask_websocket.get_received(namespace='/chat')[0]
   
    assert recv['args'][0]['room_id'] == 1


def test_send_chat(flask_websocket, db_setting):
    flask_websocket.emit('send_chat', {'room_id': 1, 'data': 'Hello!'}, namespace='/chat')

    recv = flask_websocket.get_received(namespace='/chat')[0]
    assert recv['args'][0]['data'] == 'Hello!'
