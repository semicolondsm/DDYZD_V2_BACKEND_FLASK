from app import db
from datetime import datetime
from datetime import timedelta
import enum


def isoformat(date):
    try:
        date = date = date.isoformat()[:-7]+'.000+09:00'
    except:
        date = None
    return date


def kstnow():
    return datetime.utcnow()+timedelta(hours=9)


class UserType(enum.Enum):
    U = 1  # 유저
    C = 2  # 동아리장
    H1 = 3 # 동아리 지원
    H2 = 4 # 면접 일정
    H3 = 5 # 면접 결과

 
class MsgType(enum.Enum):
    C = 1 # 일반 채팅 메시지
    H = 2 # 봇이 보낸 메시지


class RoomStatus(enum.Enum):
    C = 1 # 일반 채팅방
    A = 2 # 지원자 채팅방
    S = 3 # 면접 일정을 받은 채팅방
    R = 4 # 면접 결과를 받은 채팅방


class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    user_looked = db.Column(db.Boolean(), default=False)
    club_looked = db.Column(db.Boolean(), default=False)
    status = db.Column(db.Enum(RoomStatus), default=RoomStatus(1))

    chats = db.relationship('Chat', backref='room', lazy='dynamic')

    def __lt__(self, operand):
        try:
            boolean = self.last_message()[1] < operand.last_message()[1]
        except TypeError:
            boolean = False
        return boolean

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

    def last_message(self):
        chat = self.chats.order_by(Chat.created_at.desc()).first()
        msg = chat.msg if chat is not None else None
        created_at = chat.created_at if chat is not None else None
        return msg, created_at 

    def json(self, is_user, index=0):
        msg, created_at = self.last_message()
        if is_user:
            club = Club.query.get(self.club_id)
            id = club.id
            name = club.name
            image = 'https://api.semicolon.live/file/'+club.profile_image
            isread = self.user_looked
        else:
            user = User.query.get(self.user_id)
            id = user.id
            name = user.name
            image = user.image_path
            isread = self.club_looked

        return {
		    "roomid" : str(self.id),
		    "id" : str(id),
		    "name" : name,
		    "image" : image,
		    "lastdate" :  isoformat(created_at),
		    "lastmessage" : msg,
            "isread": isread,
            "status": self.status.name,
            "index": index
        }

    def __repr__(self):
        return '<Room> {}'.format(self.id)


class Chat(db.Model):
    __tablename__ = 'chat'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(512))
    msg = db.Column(db.String(512))
    created_at = db.Column(db.DateTime(6),  default=kstnow)
    user_type = db.Column(db.Enum(UserType))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

    def json(self):
        return {
            "title": self.title,
            "msg": self.msg,
            "user_type": self.user_type.name,
            "created_at": isoformat(self.created_at)
        }

    def __repr__(self):
        return '<Chat> {}'.format(self.msg)


class Club(db.Model):
    __tablename__ = 'club'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
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

    def __lt__(self, operand):
        try:
            boolean = self.name < operand.name
        except TypeError:
            boolean = False
        return boolean

    def get_all_applicant_room(self):
        '''
        모든 동아리 신청자 반환하는 메서드
        '''
        return Room.query.filter_by(club_id=self.id).filter(Room.status != RoomStatus(1)).all()
    def is_recruiting(self):
        '''
        모집 기간인지 확인하는 메서드
        처음 100번째줄 if 문 코드는 공고한적 없는 동아리의 경우 False를 반환한다.
        '''
        if self.start_at == None or self.close_at == None:
            return False
        return kstnow() >= self.start_at and kstnow() <= self.close_at 

    def __repr__(self):
        return '<Club> {}>'.format(self.name)


class ClubHead(db.Model):
    __tablename__ = 'club_head'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id', ondelete='CASCADE'))

    def __repr__(self):
        return '<ClubHead> {},{}'.format(self.club_head_user.name, self.club.name)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    gcn = db.Column(db.String(5))
    image_path = db.Column(db.String(45))
    github_url = db.Column(db.String(45))
    email = db.Column(db.String(50))
    device_token = db.Column(db.String(4096))
    bio = db.Column(db.String(256))
    session_id = db.Column(db.String(256), nullable=True, default=False)

    rooms = db.relationship('Room', backref='user', lazy='dynamic')
    club_heads = db.relationship('ClubHead', backref='user')
    club_members = db.relationship('ClubMember', backref='user')

    def get_clubs(self):
        '''
        내가 동아리장인 동아리들 이름 출력하는 메서드
        '''
        clubs = []
        for ch in self.club_heads:
            clubs.append(Club.query.get_or_404(ch.club_id)) 
        try:
            clubs.sort()
        except TypeError:
            clubs = []
        return clubs

    def is_user(self, room):
        '''
        내가 채팅방의 일반 유저인지 확인하는 메서드
        '''
        return self.id == room.user_id
  
    def is_clubhead(self, club=None, room=None):
        '''
        내가 채팅방 혹은 동아리의 동아리장인지 확인하는 메서드
        '''
        club_head = None
        if room is not None:
            club_head = ClubHead.query.filter_by(user_id=self.id, club_id=room.club_id).first()
        if club is not None:
            club_head = ClubHead.query.filter_by(user_id=self.id, club_id=club.id).first()
       
        return club_head is not None

    def is_applicant(self, club, result=False):
        '''
        내가 동아리에 신청했는지 아는 메서드
        result가 False이면 신청중인 사람,
        result가 True이면 동아리에 합격한 사람
        '''
        return Application.query.filter_by(user_id=self.id, club_id=club.id, result=result).first()

    def is_member(self, club=None, room=None):
        '''
        내가 동아리의 맴버인지 아는 메서드
        '''
        if club is not None:
            if self.is_clubhead(club=club):
                return True
            if self.is_applicant(club=club, result=True):
                return True
            return False
        if room is not None:
            if self == room.user:
                return True
            if room.club.club_head[0].user_id == self.id:
                return True
            return False

    def __repr__(self):
        return '<User> {},{}'.format(self.name, self.gcn)


class ClubMember(db.Model):
    __tablename__ = 'club_member'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))

    def __repr__(self):
        return '<Application> {},{}'.format(User.query.get(self.user_id).name, Club.query.get(self.club_id).name)


class Major(db.Model):
    __tablename__ = 'major'
    id = db.Column(db.Integer, primary_key=True)
    major_name = db.Column(db.String(45))
    club_id = db.Column(db.Integer, db.ForeignKey("club.id"))
