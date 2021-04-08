from test.conftest import jwt_token
import json

## 채팅 내역 불러오기 테스트 ##
def test_breakdown(flask_client, db_setting):
    resp = flask_client.get('/chat/1/breakdown', headers=jwt_token(1))

    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data[0].get('msg') == '두번째 채팅'
    assert data[0].get('user_type') == 'C'
    assert data[0].get('created_at') != None
    assert data[1].get('msg') == '첫번째 채팅'
    assert data[1].get('user_type') == 'U'
    assert data[1].get('created_at') != None