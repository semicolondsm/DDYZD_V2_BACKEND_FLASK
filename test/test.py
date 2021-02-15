import pytest
import os
import jwt
import json
from app import create_app
from app import db
from app.models import Room, Chat, Club, ClubHead, User, Application
from dotenv import load_dotenv
load_dotenv()


@pytest.fixture(scope='session')
def flask_app():
    app = create_app('test')
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()
    app_context.pop()

@pytest.fixture(scope='session')
def flask_client(flask_app):
    return flask_app.test_client()

@pytest.fixture
def login():
    request/dsmauth/login

@pytest.fixture(scope='session')
def headers():
    token = jwt.encode({"sub": 1}, os.getenv("SECRET"), algorithm="HS256")
    headers = {'Authorization': 'Bearer '+ token.decode('utf-8')}
    return headers

def test_ping(flask_client):
    resp = flask_client.get("ping")
    assert resp.status_code ==  200
    assert resp.json.get('msg') == 'ping successfully'

def test_chat_list(flask_client, headers):
    db.session.add(User(name='김수완', gcn='1103'))
    db.session.add(User(name='조호원', gcn='1118'))
    db.session.add(Club(club_name='세미콜론'))
    db.session.add(ClubHead(user_id=2, club_id=1))
    db.session.add(Room(user=1, club_head_id=1))
    db.session.add(Chat(room_id=1, msg='첫번째 채팅', user_type='U'))
    db.session.commit()

    resp = flask_client.get("/chat/list", headers=headers)
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    
    assert resp.status_code == 200
    assert data[0].get('lastmessage') == '첫번째 채팅'
    assert data[0].get('lastdate') != None
    assert data[0].get('roomid') == 1
    assert data[0].get('clubid') == 1
    assert data[0].get('clubname') == '세미콜론'
