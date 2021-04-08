from app.models.function import isoformat
from app.models.function import kstnow
from app.models.club import ClubMember
from app.models.club import ClubHead
from app.models.club import Club
from app.models.club import Major
from app.models.chat import Chat 
from app.models.chat import Room 
from app.models.type import UserType 
from app.models.feed import Feed
from app.models.user import User
from app import create_app
from app import db
from config import Config
from datetime import datetime
from datetime import timedelta
from dotenv import find_dotenv
import jwt
import os
import pytest
find_dotenv('ddyzd.env')


def jwt_token(sub=1):
    token = jwt.encode({"sub": sub}, os.getenv("SECRET"), algorithm="HS256")
    headers = {'Authorization': 'Bearer '+ token}
    return headers


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


## 더미 데이터 세팅 ## 
@pytest.fixture(scope='session')
def db_setting(flask_app):
    with flask_app.app_context():
        db.session.add(User(name='김수완', gcn='1103', image_path='profile1'))
        db.session.add(User(name='조호원', gcn='1118', image_path='profile2'))
        db.session.add(User(name='안은결', gcn='1413', image_path='profile3'))
        db.session.add(User(name='성예인', gcn='1110', image_path='profile4'))
        db.session.add(Club(name='세미콜론', total_budget=3000, current_budget=2000, banner_image='banner image', hongbo_image='hongbo image', profile_image='profile_image', start_at=datetime.now()-timedelta(days=1), close_at=datetime.now()+timedelta(days=1)))
        db.session.add(ClubHead(user_id=1, club_id=1))
        r1 = Room(id=1, user_id=2, club_id=1)
        r2 = Room(id=2, user_id=3, club_id=1, status='A')
        r3 = Room(id=3, user_id=4, club_id=1)
        db.session.add(r1)
        db.session.add(r2)
        db.session.add(r3)
        db.session.add(Chat(room_id=1, msg='첫번째 채팅', user_type=UserType(1)))
        r1.update_room_message('첫번째 채팅', kstnow())
        db.session.add(Chat(room_id=1, msg='두번째 채팅', user_type=UserType(2)))
        r1.update_room_message('두번째 채팅', kstnow())
        db.session.add(Major(club_id=1, major_name='프론트엔드'))
        db.session.add(ClubMember(user_id=1, club_id=1))
        db.session.add(Feed(club_id=1, contents="헬로우 월드"))

        db.session.commit()
