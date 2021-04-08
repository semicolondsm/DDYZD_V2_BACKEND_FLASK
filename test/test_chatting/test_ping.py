## 테스트 핑 ## 
def test_ping(db_setting, flask_client):
    resp = flask_client.get("/ping")

    assert resp.status_code ==  200
    assert resp.json.get('msg') == 'ping successfully'
