import enum
import datetime
from app import db

class ChatEnum(enum.Enum):
    U = 1  # 유저
    C = 2  # 봇
    H = 3  # 방장

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    user_looked = db.Column(db.Boolean(), default=False)
    club_looked = db.Column(db.Boolean(), default=False)

    chats = db.relationship('Chat', backref='room', lazy='dynamic')

    # 유저에 대한 json
    def json(self):
        chat = self.chats.order_by(Chat.created_at.desc()).first()
        chat_created_at = chat.created_at.isoformat()+'.000+09:00' if chat is not None else None
        chat_msg = chat.msg if chat is not None else None
        return {
		    "roomid" : self.id,
		    "clubid" : self.club_id,
		    "clubname" : self.club.club_name,
		    "clubimage" : self.club.profile_image,
		    "userid": self.user.user_id,
		    "username": self.user.name,
		    "userimage": self.user.image_path,
		    "lastdate" : chat_created_at,
		    "lastmessage" : chat_msg
        }

    def __repr__(self):
        return '<Room> {}'.format(self.id)

class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    msg = db.Column(db.String(512))
    created_at = db.Column(db.DateTime(),  default=datetime.datetime.now)
    user_type = db.Column(db.Enum(ChatEnum))

    def __repr__(self):
        return '<Chat> {}'.format(self.msg)
    
class Club(db.Model):
    __tablename__ = 'club'
    club_id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(45))
    total_budget = db.Column(db.Integer)
    current_budget = db.Column(db.Integer)
    start_at = db.Column(db.DateTime())
    close_at = db.Column(db.DateTime())
    banner_image = db.Column(db.String(255))
    profile_image = db.Column(db.String(255))
    hongbo_image = db.Column(db.String(255))

    club_head = db.relationship('ClubHead', backref='club')
    rooms = db.relationship('Room', backref='club')

    def __repr__(self):
        return '<Club> {}>'.format(self.club_name)

class ClubHead(db.Model):
    __tablename__ = 'club_head'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id', ondelete='CASCADE'))

    def __repr__(self):
        return '<ClubHead> {},{}'.format(self.club_head_user.name, self.club.club_name)

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    gcn = db.Column(db.String(5))
    image_path = db.Column(db.String(45))
    github_url = db.Column(db.String(45))
    email = db.Column(db.String(50))
    device_token = db.Column(db.String(4096))

    club_heads = db.relationship('ClubHead', backref='club_head_user')
    rooms = db.relationship('Room', backref='user')

    def __repr__(self):
        return '<User> {},{}'.format(self.name, self.gcn)

class Application(db.Model):
    __tablename__ = 'application'
    application_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    result = db.Column(db.Boolean())