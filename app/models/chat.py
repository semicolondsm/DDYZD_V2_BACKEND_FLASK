from app.models.function import kstnow
from app.models.function import isoformat
from app.models.type import UserType
from app.models.type import RoomType
from app import db
from datetime import datetime
import enum

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    user_looked = db.Column(db.Boolean(), default=False)
    club_looked = db.Column(db.Boolean(), default=False)
    status = db.Column(db.Enum(RoomType), default=RoomType(1))
    last_message = db.Column(db.String(512))
    last_date = db.Column(db.DateTime(6))

    chats = db.relationship('Chat', backref='room', lazy='dynamic')

    def __lt__(self, operand):  
        operand1 = self.last_date if self.last_date is not None else datetime(1,1,1,1,1,1,1)
        operand2 = operand.last_date if operand.last_date is not None else datetime(1,1,1,1,1,1,1)

        return operand1 < operand2

    def read(self, user_type):
        if user_type == 'C':
            self.club_looked = True
        else:
            self.user_looked = True
        db.session.commit()
            
    def writed(self, user_type):
        if user_type == 'C':
            self.user_looked = False
        else:
            self.club_looked = False
        db.session.commit()

    def update_room_message(self, msg, date, status=None):
        self.last_message = msg
        self.last_date = date
        if status is not None:
            self.status = status
        db.session.commit()

    def json(self, is_user, index=0):
        from app.models.user import User
        from app.models.club import Club
        if is_user:
            club = Club.query.get(self.club_id)
            id = club.id
            name = club.name
            image = 'https://api.semicolon.live/file/'+club.profile_image
            isread = self.user_looked
        else:
            user = User.query.get(self.user_id)
            id = user.id
            name = user.gcn+user.name
            image = user.image_path
            isread = self.club_looked

        return {
		    "roomid" : str(self.id),
		    "id" : str(id),
		    "name" : name,
		    "image" : image,
		    "lastdate" :  isoformat(self.last_date if self.last_date is not None else datetime(1,1,1,1,1,1,1)),
		    "lastmessage" : self.last_message,
            "isread": isread,
            "status": self.status.name,
            "index": index
        }

    def __repr__(self):
        return '<Room> {} {}'.format(self.club, self.user)


class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512))
    msg = db.Column(db.String(512))
    created_at = db.Column(db.DateTime(6),  default=kstnow)
    user_type = db.Column(db.Enum(UserType))
    result = db.Column(db.Boolean(), default=None)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

    def json(self):
        return {
            "title": self.title,
            "msg": self.msg,
            "user_type": self.user_type.name,
            "result": self.result,
            "created_at": isoformat(self.created_at)
        }

    def __repr__(self):
        return '<Chat> {}'.format(self.msg)
