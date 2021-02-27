from app import create_app
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from app import db
from app import websocket
from app.models import Room, Chat, Club, ClubHead, User, ClubMember, Major
import os

config = os.getenv('FLASK_CONFIG')
if config is None:
    config = 'default'
app = create_app(config)

migrate = Migrate(app, db)
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, Room=Room, Chat=Chat, ClubMember=ClubMember, 
                Club=Club, ClubHead=ClubHead, User=User, Major=Major)

manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=make_shell_context))


if __name__ == '__main__':
    if config == 'production':
        websocket.run(app, host='0.0.0.0', port=8888)
    else:
        manager.run()