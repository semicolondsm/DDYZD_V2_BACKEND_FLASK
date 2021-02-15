from dotenv import load_dotenv
from app import create_app
from app import db
import jwt
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
def headers():
    token = jwt.encode({"sub": 1}, os.getenv("SECRET"), algorithm="HS256")
    headers = {'Authorization': 'Bearer '+ token.decode('utf-8')}
    return headers