
from conftest import jwt_token

## 채팅방 정보 반환 테스트##
def test_room_info(flask_client, db_setting):
    resp = flask_client.get('/room/1/info', headers=jwt_token(1))
    assert resp.status_code == 200
    data = resp.json

    assert data['id'] == '1118'
    assert data['name'] == '1118조호원'
    assert data['image'] == 'profile2'
    
    resp = flask_client.get('/room/1/info', headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.json
    
    assert data['id'] == '1'
    assert data['name'] == '세미콜론'
    assert data['image'] == 'https://api.semicolon.live/file/profile_image'
