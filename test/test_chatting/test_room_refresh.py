from conftest import jwt_token

## 채팅방 리프레시 테스트 ##
def test_room_refresh(flask_client, db_setting):
    resp = flask_client.get('/room/1/refresh', headers=jwt_token())
    assert resp.status_code == 200
    data = resp.json

    assert data.get('id') == '2' 
    assert data.get('name') == '1118조호원' 
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

