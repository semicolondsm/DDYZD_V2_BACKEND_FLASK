from conftest import jwt_token
from config import Config
import jwt

## 룸 토큰 반환 테스트 ##
def test_room_token(flask_client, db_setting):
    # 동아리장 토큰 
    resp = flask_client.get('/room/1/token', headers=jwt_token(1))
    assert resp.status_code == 200
    token = resp.json['room_token']
    json = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms='HS256')
    
    assert json.get('room_id') == 1
    assert json.get('user_id') == 1
    assert json.get('user_type') == 'C' 

    # 일반 유저 토큰
    resp = flask_client.get('/room/1/token', headers=jwt_token(2))
    assert resp.status_code == 200
    token = resp.json['room_token']
    json = jwt.decode(token, Config.ROOM_SECRET_KEY, algorithms='HS256')
    
    assert json.get('room_id') == 1
    assert json.get('user_id') == 2
    assert json.get('user_type') == 'U' 
