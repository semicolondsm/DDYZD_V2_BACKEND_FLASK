from conftest import jwt_token
import json

## 지원자 리스트 반환 테스트 ##
def test_applicant_list(flask_client, db_setting):
    resp = flask_client.get('/club/1/applicant', headers=jwt_token(1))
    
    assert resp.status_code == 200
    data = resp.data.decode('utf8').replace("'", '"')
    data = json.loads(data)

    assert data[0]['roomid'] == '2'
    assert data[0]['id'] == '3'
    assert data[0]['name'] == '1413안은결'
    assert data[0]['image'] == 'profile3'
    assert data[0]['lastdate'] != None
    assert data[0]['lastmessage'] == None
    assert data[0]['index'] == 0
    