import enum
import datetime
from app import db

class ChatEnum(enum.Enum):
    U = 1  # 유저
    C = 2  # 동아리장
    H = 3  # 봇

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    user_looked = db.Column(db.Boolean(), default=False)
    club_looked = db.Column(db.Boolean(), default=False)

    chats = db.relationship('Chat', backref='room', lazy='dynamic')

    def last_message(self):
        chat = self.chats.order_by(Chat.created_at.desc()).first()
        msg = chat.msg if chat is not None else None
        created_at = isoformat(chat.created_at) if chat is not None else None
        return msg, created_at 

    def json(self, is_user):
        msg, created_at = self.last_message()
        user = User.query.get(self.user_id)
        club = Club.query.get(self.club_id)
        if is_user:
            id = club.club_id
            name = club.club_name
            image = club.profile_image
            authority = club.club_name
        else:
            id = user.user_id
            name = user.name
            image = user.image_path
            authority = user.name
        return {
		    "roomid" : self.id,
		    "id" : id,
		    "name" : name,
		    "image" : image,
		    "lastdate" : created_at,
		    "lastmessage" : msg,
            "authority": authority
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

    def json(self):
        return {
            "msg": self.msg,
            "user_type": self.user_type.name,
            "created_at": isoformat(self.created_at)
        }

    def __repr__(self):
        return '<Chat> {}'.format(self.msg)
    
class Club(db.Model):
    __tablename__ = 'club'
    club_id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(45), nullable=False)
    total_budget = db.Column(db.Integer, nullable=False)
    current_budget = db.Column(db.Integer, nullable=False)
    start_at = db.Column(db.DateTime())
    close_at = db.Column(db.DateTime())
    banner_image = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=False)
    hongbo_image = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))

    club_head = db.relationship('ClubHead', backref='club')
    rooms = db.relationship('Room', backref='club')
    majors = db.relationship('Major', backref='club')

    def is_recruiting(self):
        return datetime.now() >= self.start_at and datetime.now() <= self.close_at 

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
    bio = db.Column(db.String(256))

    club_heads = db.relationship('ClubHead', backref='club_head_user')
    rooms = db.relationship('Room', backref='user')

    def get_clubs(self):
        '''
        내가 동아리장인 동아리들 리스트 출력하는 함수.
        '''
        clubs = []
        clubs.append(Club.query.get_or_404(ch.club_id)) for ch in self.club_heads

        return clubs

    def is_user(self, room):
        return self.user_id == room.user_id

    def is_clubhead(self, room):
        club_head = ClubHead.query.filter_by(user_id=self.user_id, club_id=room.club_id).first()
        return club_head is not None

    def __repr__(self):
        return '<User> {},{}'.format(self.name, self.gcn)

class Application(db.Model):
    __tablename__ = 'application'
    application_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.club_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    result = db.Column(db.Boolean(), nullable=False)

class Major(db.Model):
    __tablename__ = 'major'
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("club.club_id"))
    major_name = db.Column(db.String(45))


def isoformat(date):
    return date.isoformat()+'.000+09:00'