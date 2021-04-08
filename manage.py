from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from app.models.club import ClubMember
from app.models.club import ClubHead
from app.models.club import Major
from app.models.club import Club
from app.models.chat import Room
from app.models.chat import Chat
from app.models.user import User
from app.models.feed import Feed 
from app import create_app
from app import db
import os

config = os.getenv('FLASK_CONFIG')
if config is None:
    config = 'default'
app = create_app(config)

migrate = Migrate(app, db)
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, Room=Room, Chat=Chat, ClubMember=ClubMember, 
                Club=Club, ClubHead=ClubHead, User=User, Major=Major, Feed=Feed)

manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=make_shell_context))


if __name__ == '__main__':
        manager.run()
