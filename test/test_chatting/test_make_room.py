from conftest import jwt_token

## 방 만들기 테스트 ##
def test_make_room(db_setting, flask_client):
    resp = flask_client.post('/chat/1/room', headers=jwt_token(2))
    assert resp.status_code == 200
    data = resp.json

    assert data.get('room_id') == '1'

    resp = flask_client.post('/chat/1/room', headers=jwt_token(4))
    assert resp.status_code == 200
    data = resp.json

    assert data.get('room_id') == '3'
