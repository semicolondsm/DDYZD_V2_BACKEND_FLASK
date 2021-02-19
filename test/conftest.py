from dotenv import load_dotenv
from app import create_app
from app import websocket
from app import db
import jwt
import os
import pytest
load_dotenv()

@pytest.fixture(scope='session')
def flask_app():
    app = create_app('test')
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture(scope='session')
def flask_client(flask_app):
    return flask_app.test_client()


@pytest.fixture(scope='session')
def flask_websocket(flask_app, jwt_token, flask_client):
    # 웹 소켓 테스트 클라이언트 생성
    flask_websocket = websocket.test_client(flask_app, flask_test_client=flask_client)
    # 웹 소켓 연결
    flask_websocket.connect('/chat', headers=jwt_token)
    recv = flask_websocket.get_received(namespace='/chat')[0]
    assert recv['args'][0]['msg'] == 'Socket Connect Successfully'
    
    yield flask_websocket
    
    # 웹 소켓 연결 끊기 
    flask_websocket.disconnect(namespace='/chat')


@pytest.fixture(scope='session')
def jwt_token():
    token = jwt.encode({"sub": 1}, os.getenv("SECRET"), algorithm="HS256")
    headers = {'Authorization': 'Bearer '+ token}
    return headers
