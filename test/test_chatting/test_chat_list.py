from test.conftest import jwt_token
from app.models.chat import Room
from app.models.user import User
from app.models.type import UserType
import json

## 채팅 리스트 불러오기 테스트 ## 
def test_chat_list(flask_client, db_setting):
    # 동아리장 채팅 테스트
    resp = flask_client.get("/chat/list", headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data['club_section'] == ['김수완', '세미콜론']
    assert data['rooms'][0].get('roomid') == '1'
    assert data['rooms'][0].get('id') == '2'
    assert data['rooms'][0].get('name') == '1118조호원'
    assert data['rooms'][0].get('image') == 'profile2'
    assert data['rooms'][0].get('lastdate') != None
    assert data['rooms'][0].get('isread') == False
    assert data['rooms'][0].get('index') == 1

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

    # 채팅방 삭제시
    room = Room.query.get(1)
    room.delete_chats(UserType.C.name)

    resp = flask_client.get("/chat/list", headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)
    assert data['club_section'] == ['김수완', '세미콜론']
    assert data['rooms'] == []

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

    room = Room.query.get(1)
    room.delete_chats(UserType.U.name)
    resp = flask_client.get("/chat/list", headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data['club_section'] == ['조호원']
    assert data['rooms'] == []