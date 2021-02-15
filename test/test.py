import pytest
import os
import json
from app import db
from app.models import Room, Chat, Club, ClubHead, User, Application

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

def 