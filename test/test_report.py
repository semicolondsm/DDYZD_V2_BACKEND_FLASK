from config import Config
import json
import jwt


## 테스트 핑 ## 
def test_ping(db_setting, flask_client):
    # resp = flask_client.post("/report", json={'feed_id': 1, 'reason': '너무 야해서'})

    # assert resp.status_code ==  201
    # assert resp.json.get('msg') ==  '신고가 성공적으로 작성되었습니다.'
    pass